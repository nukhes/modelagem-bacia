import bpy
import csv
import numpy as np
from collections import defaultdict

try:
    from scipy.interpolate import RBFInterpolator
    SCIPY_DISPONIVEL = True
except Exception:
    SCIPY_DISPONIVEL = False

# PARA FAZER: no futuro seria util adicionar texturas e colocar todas as formações num arquivo separado
CORES_FORMACOES = {
    'Serra Geral': (0.85, 0.35, 0.35, 1.0),
    'Botucatu': (0.76, 0.64, 0.40, 1.0),
    'Piramboia': (0.82, 0.58, 0.31, 1.0),
    'Irati': (0.20, 0.25, 0.20, 1.0),
    'Rio do Rasto': (0.55, 0.25, 0.20, 1.0),
    'DESCONHECIDA': (0.5, 0.5, 0.5, 1.0)
}

# configuração do modelo
EXAGERO_VERTICAL = 100.0
ESCALA_XY = 0.001
RESOLUCAO_GRID = 60
MIN_PONTOS_FORMACAO = 4
PROFUNDIDADE_PADRAO_VISUALIZACAO = 100.0

def valor_float(valor):
    if not valor: return None
    try:
        return float(str(valor).replace(',', '.').strip())
    except ValueError:
        return None

def limpar_nome(nome):
    if not nome or not str(nome).strip():
        return 'DESCONHECIDA'
    return str(nome).strip()

def criar_material_simples(nome, rgba):
    material = bpy.data.materials.get(nome)
    if material: return material
    material = bpy.data.materials.new(nome)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = rgba
        bsdf.inputs['Roughness'].default_value = 0.8
    return material

def carregar_pocos(input_file):
    pocos = []
    with open(input_file, 'r', encoding='utf-8', errors='replace') as file:
        reader = csv.DictReader(file)
        headers = {k.strip().upper(): k for k in reader.fieldnames} if reader.fieldnames else {}
        for row in reader:
            x_key = headers.get('X_UTM') or headers.get('X') or headers.get('LONGITUDE_BASE_DD')
            y_key = headers.get('Y_UTM') or headers.get('Y') or headers.get('LATITUDE_BASE_DD')
            elev_key = headers.get('ELEVACAO') or headers.get('COTA_ALTIMETRICA_M')
            prof_key = headers.get('PROFUNDIDADE_VERTICAL_M') or headers.get('PROFUNDIDADE')
            form_key = headers.get('GEOLOGIA_FORMACAO_FINAL') or headers.get('FORMACAO')
            
            x = valor_float(row.get(x_key)) if x_key else None
            y = valor_float(row.get(y_key)) if y_key else None
            elevacao = valor_float(row.get(elev_key)) if elev_key else None
            
            if x is None or y is None or elevacao is None: 
                continue
                
            profundidade = valor_float(row.get(prof_key)) if prof_key else None
            formacao = limpar_nome(row.get(form_key)) if form_key else 'DESCONHECIDA'
            
            tem_profundidade = profundidade is not None
            prof_real = profundidade if tem_profundidade else PROFUNDIDADE_PADRAO_VISUALIZACAO
            
            pocos.append({
                'id': row.get('POCO', 'POCO_SEM_NOME'),
                'x': x, 'y': y, 'elevacao': elevacao,
                'cota_formacao': elevacao - prof_real,
                'formacao': formacao, 'tem_profundidade': tem_profundidade
            })
    return pocos

def obter_grid_interpolado(pontos_x, pontos_y, valores_z, dx, dy, min_x, min_y):
    pts = np.column_stack((pontos_x, pontos_y))
    z_vals = np.array(valores_z)
    
    mean_z = np.mean(z_vals)
    corners = np.array([
        [min_x, min_y], [min_x + dx, min_y],
        [min_x, min_y + dy], [min_x + dx, min_y + dy]
    ])
    corner_z = np.full(4, mean_z)
    
    pts_ext = np.vstack((pts, corners))
    z_ext = np.concatenate((z_vals, corner_z))
    
    pts_norm = pts_ext.copy()
    pts_norm[:, 0] = (pts_ext[:, 0] - min_x) / (dx if dx > 0 else 1)
    pts_norm[:, 1] = (pts_ext[:, 1] - min_y) / (dy if dy > 0 else 1)
    
    rbf = RBFInterpolator(pts_norm, z_ext, kernel='linear')
    
    grid_x = np.linspace(0, 1, RESOLUCAO_GRID)
    grid_y = np.linspace(0, 1, RESOLUCAO_GRID)
    X, Y = np.meshgrid(grid_x, grid_y)
    grid_pts = np.column_stack((X.ravel(), Y.ravel()))
    
    z_grid = rbf(grid_pts).reshape(RESOLUCAO_GRID, RESOLUCAO_GRID)
    return z_grid

def criar_solido_camada(nome, z_top, z_bot, centro_x, centro_y, dx, dy, min_x, min_y, escala_z, material, colecao):
    vertices = []
    faces = []
    
    grid_x = np.linspace(0, 1, RESOLUCAO_GRID)
    grid_y = np.linspace(0, 1, RESOLUCAO_GRID)
    
    for y in range(RESOLUCAO_GRID):
        for x in range(RESOLUCAO_GRID):
            x_real = grid_x[x] * dx + min_x
            y_real = grid_y[y] * dy + min_y
            xb = (x_real - centro_x) * ESCALA_XY
            yb = (y_real - centro_y) * ESCALA_XY
            zt = z_top[y, x] * escala_z
            vertices.append((xb, yb, zt))
            
    offset = RESOLUCAO_GRID * RESOLUCAO_GRID
    
    for y in range(RESOLUCAO_GRID):
        for x in range(RESOLUCAO_GRID):
            x_real = grid_x[x] * dx + min_x
            y_real = grid_y[y] * dy + min_y
            xb = (x_real - centro_x) * ESCALA_XY
            yb = (y_real - centro_y) * ESCALA_XY
            zb = z_bot[y, x] * escala_z
            vertices.append((xb, yb, zb))
            
    def idx_t(x, y): return y * RESOLUCAO_GRID + x
    def idx_b(x, y): return offset + y * RESOLUCAO_GRID + x

    for y in range(RESOLUCAO_GRID - 1):
        for x in range(RESOLUCAO_GRID - 1):
            faces.append((idx_t(x, y), idx_t(x+1, y), idx_t(x+1, y+1), idx_t(x, y+1)))
            
    for y in range(RESOLUCAO_GRID - 1):
        for x in range(RESOLUCAO_GRID - 1):
            faces.append((idx_b(x, y), idx_b(x, y+1), idx_b(x+1, y+1), idx_b(x+1, y)))
            
    y = 0
    for x in range(RESOLUCAO_GRID - 1):
        faces.append((idx_t(x, y), idx_b(x, y), idx_b(x+1, y), idx_t(x+1, y)))
        
    y = RESOLUCAO_GRID - 1
    for x in range(RESOLUCAO_GRID - 1):
        faces.append((idx_t(x, y), idx_t(x+1, y), idx_b(x+1, y), idx_b(x, y)))
        
    x = 0
    for y in range(RESOLUCAO_GRID - 1):
        faces.append((idx_t(x, y), idx_t(x, y+1), idx_b(x, y+1), idx_b(x, y)))
        
    x = RESOLUCAO_GRID - 1
    for y in range(RESOLUCAO_GRID - 1):
        faces.append((idx_t(x, y), idx_b(x, y), idx_b(x, y+1), idx_t(x, y+1)))

    malha = bpy.data.meshes.new(nome)
    malha.from_pydata(vertices, [], faces)
    malha.update()
    
    obj = bpy.data.objects.new(nome, malha)
    if material: 
        obj.data.materials.append(material)
    
    for poly in obj.data.polygons: 
        poly.use_smooth = True
        
    colecao.objects.link(obj)

def processar_modelo_impressao(input_file, yolo, exagero_vertical=EXAGERO_VERTICAL):
    if not SCIPY_DISPONIVEL: 
        raise RuntimeError("SciPy necessário para interpolação.")
    
    pocos = carregar_pocos(input_file)
    if not pocos: 
        raise ValueError("Nenhum poço válido encontrado no conjunto de dados.")

    xs = [p['x'] for p in pocos]
    ys = [p['y'] for p in pocos]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    dx = max_x - min_x
    dy = max_y - min_y
    centro_x = (min_x + max_x) / 2.0
    centro_y = (min_y + max_y) / 2.0
    escala_z = ESCALA_XY * exagero_vertical

    colecao = bpy.data.collections.new('Modelo_Impressao_3D')
    bpy.context.scene.collection.children.link(colecao)

    z_topo_grid = obter_grid_interpolado(xs, ys, [p['elevacao'] for p in pocos], dx, dy, min_x, min_y)
    
    grupos = defaultdict(list)
    for p in pocos:
        if p['tem_profundidade'] and p['formacao'] != 'DESCONHECIDA' or yolo and p['formacao'] != 'DESCONHECIDA':
            grupos[p['formacao']].append(p)

    camadas = []
    for formacao, lista in grupos.items():
        if len(lista) < MIN_PONTOS_FORMACAO and not yolo:
            continue
        z_grid = obter_grid_interpolado(
            [p['x'] for p in lista], [p['y'] for p in lista], [p['cota_formacao'] for p in lista],
            dx, dy, min_x, min_y
        )
        camadas.append({'nome': formacao, 'grid': z_grid, 'media': np.mean(z_grid)})

    camadas.sort(key=lambda c: c['media'], reverse=True)
    
    min_global_z = np.min(z_topo_grid)
    for c in camadas: 
        min_global_z = min(min_global_z, np.min(c['grid']))
        
    z_base_absoluto = min_global_z - (np.max(z_topo_grid) - min_global_z) * 0.2
    grid_base = np.full((RESOLUCAO_GRID, RESOLUCAO_GRID), z_base_absoluto)

    grids_ordem = [('Topografia', z_topo_grid)]
    for c in camadas: 
        grids_ordem.append((c['nome'], c['grid']))
    grids_ordem.append(('Embasamento', grid_base))

    for i in range(1, len(grids_ordem)):
        grids_ordem[i] = (grids_ordem[i][0], np.minimum(grids_ordem[i][1], grids_ordem[i-1][1]))

    for i in range(len(grids_ordem) - 1):
        nome_topo = grids_ordem[i][0]
        nome_base = grids_ordem[i+1][0]
        
        if i == 0:
            nome_obj = f"00_Cobertura_Ate_{nome_base}"
            cor = (0.6, 0.7, 0.4, 1.0)
        else:
            nome_obj = f"{i:02d}_{nome_topo}_Ate_{nome_base}"
            cor = CORES_FORMACOES.get(nome_topo, (0.8, 0.2, 0.8, 1.0))
            
        mat = criar_material_simples(f"Mat_{nome_obj}", cor)
        criar_solido_camada(
            nome_obj, grids_ordem[i][1], grids_ordem[i+1][1],
            centro_x, centro_y, dx, dy, min_x, min_y, escala_z, mat, colecao
        )