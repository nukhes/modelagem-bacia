import bpy
import csv
import math
import numpy as np
from collections import defaultdict

try:
    from scipy.interpolate import Rbf
    SCIPY_DISPONIVEL = True
except Exception:
    SCIPY_DISPONIVEL = False


# =========================================================
# CONFIGURAÇÕES GERAIS
# =========================================================

EXAGERO_VERTICAL = 10.0
ESCALA_XY = 0.001
RESOLUCAO_GRID = 60
MIN_PONTOS_FORMACAO = 4
DISTANCIA_MAX_EXTRAPOLACAO = 0.25


# =========================================================
# CORES POR FORMAÇÃO
# =========================================================

CORES_FORMACOES = {
    'Serra Geral': (0.15, 0.15, 0.15, 1.0),
    'Botucatu': (0.76, 0.64, 0.40, 1.0),
    'Piramboia': (0.82, 0.58, 0.31, 1.0),
    'Irati': (0.20, 0.25, 0.20, 1.0),
    'Rio do Rasto': (0.55, 0.25, 0.20, 1.0),
    'DESCONHECIDA': (0.5, 0.5, 0.5, 1.0)
}


# =========================================================
# UTILIDADES
# =========================================================


def valor_float(valor):
    if valor is None:
        return None

    valor = str(valor).strip()

    if valor == '':
        return None

    try:
        return float(valor)
    except Exception:
        return None



def distancia_2d(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)



def limpar_nome(nome):
    if not nome:
        return 'DESCONHECIDA'

    nome = nome.strip()

    if nome == '':
        return 'DESCONHECIDA'

    return nome


# =========================================================
# MATERIAIS
# =========================================================


def criar_material(nome, rgba):
    material = bpy.data.materials.get(nome)

    if material:
        return material

    material = bpy.data.materials.new(nome)
    material.use_nodes = True

    bsdf = material.node_tree.nodes.get('Principled BSDF')

    if bsdf:
        bsdf.inputs['Base Color'].default_value = rgba
        bsdf.inputs['Roughness'].default_value = 0.7

    material.diffuse_color = rgba

    return material


# =========================================================
# LEITURA DOS DADOS
# =========================================================


def carregar_pocos(input_file):

    pocos = []

    with open(input_file, 'r', encoding='utf-8') as file:

        reader = csv.DictReader(file)

        for row in reader:

            x = valor_float(row.get('X_UTM'))
            y = valor_float(row.get('Y_UTM'))

            elevacao = valor_float(
                row.get('ELEVACAO') or
                row.get('COTA_ALTIMETRICA_M')
            )

            if x is None or y is None or elevacao is None:
                continue

            profundidade = valor_float(
                row.get('PROFUNDIDADE_VERTICAL_M')
            )

            formacao = limpar_nome(
                row.get('GEOLOGIA_FORMACAO_FINAL')
            )

            poco = {
                'id': row.get('POCO', 'POCO_SEM_NOME'),
                'x': x,
                'y': y,
                'elevacao': elevacao,
                'profundidade': profundidade,
                'formacao': formacao,
                'confianca': 1.0 if profundidade else 0.5
            }

            pocos.append(poco)

    return pocos


# =========================================================
# ORGANIZAÇÃO POR FORMAÇÃO
# =========================================================


def agrupar_formacoes(pocos):

    grupos = defaultdict(list)

    for poco in pocos:
        grupos[poco['formacao']].append(poco)

    return grupos


# =========================================================
# NORMALIZAÇÃO
# =========================================================


def normalizar(v, vmin, vmax):

    if vmax == vmin:
        return 0.5

    return (v - vmin) / (vmax - vmin)


# =========================================================
# SUPERFÍCIE GEOLÓGICA
# =========================================================


def criar_superficie_formacao(
    nome_formacao,
    pocos,
    centro_x,
    centro_y,
    escala_z,
    colecao_superficies
):

    if len(pocos) < MIN_PONTOS_FORMACAO:
        print(f'[AVISO] Formação {nome_formacao} ignorada: poucos dados')
        return

    if not SCIPY_DISPONIVEL:
        print('[ERRO] SciPy não disponível')
        return

    pontos_x = [p['x'] for p in pocos]
    pontos_y = [p['y'] for p in pocos]
    pontos_z = [p['elevacao'] for p in pocos]

    min_x = min(pontos_x)
    max_x = max(pontos_x)

    min_y = min(pontos_y)
    max_y = max(pontos_y)

    min_z = min(pontos_z)
    max_z = max(pontos_z)

    x_norm = [normalizar(x, min_x, max_x) for x in pontos_x]
    y_norm = [normalizar(y, min_y, max_y) for y in pontos_y]
    z_norm = [normalizar(z, min_z, max_z) for z in pontos_z]

    try:

        rbf = Rbf(
            x_norm,
            y_norm,
            z_norm,
            function='multiquadric',
            smooth=0.08
        )

    except Exception as e:

        print(f'[ERRO] Falha RBF em {nome_formacao}: {e}')
        return

    grid_x = np.linspace(0, 1, RESOLUCAO_GRID)
    grid_y = np.linspace(0, 1, RESOLUCAO_GRID)

    vertices = []
    faces = []

    for iy, gy in enumerate(grid_y):

        for ix, gx in enumerate(grid_x):

            gx_real = gx * (max_x - min_x) + min_x
            gy_real = gy * (max_y - min_y) + min_y

            # --------------------------------------------
            # CONTROLE DE EXTRAPOLAÇÃO
            # --------------------------------------------

            menor_dist = min([
                distancia_2d(gx_real, gy_real, px, py)
                for px, py in zip(pontos_x, pontos_y)
            ])

            diagonal = math.sqrt(
                (max_x - min_x)**2 +
                (max_y - min_y)**2
            )

            distancia_normalizada = menor_dist / diagonal

            if distancia_normalizada > DISTANCIA_MAX_EXTRAPOLACAO:
                vertices.append(None)
                continue

            try:
                gz_norm = float(rbf(gx, gy))
            except Exception:
                vertices.append(None)
                continue

            gz_real = gz_norm * (max_z - min_z) + min_z

            x_blender = (gx_real - centro_x) * ESCALA_XY
            y_blender = (gy_real - centro_y) * ESCALA_XY
            z_blender = gz_real * escala_z

            vertices.append((x_blender, y_blender, z_blender))

    # --------------------------------------------
    # CONECTIVIDADE DA MALHA
    # --------------------------------------------

    def idx(x, y):
        return y * RESOLUCAO_GRID + x

    for y in range(RESOLUCAO_GRID - 1):
        for x in range(RESOLUCAO_GRID - 1):

            i1 = idx(x, y)
            i2 = idx(x + 1, y)
            i3 = idx(x + 1, y + 1)
            i4 = idx(x, y + 1)

            quad = [
                vertices[i1],
                vertices[i2],
                vertices[i3],
                vertices[i4]
            ]

            if any(v is None for v in quad):
                continue

            faces.append((i1, i2, i3, i4))

    vertices_finais = [
        v if v is not None else (0, 0, 0)
        for v in vertices
    ]

    malha = bpy.data.meshes.new(f'malha_{nome_formacao}')
    malha.from_pydata(vertices_finais, [], faces)
    malha.update()

    obj = bpy.data.objects.new(nome_formacao, malha)

    cor = CORES_FORMACOES.get(
        nome_formacao,
        CORES_FORMACOES['DESCONHECIDA']
    )

    material = criar_material(nome_formacao, cor)

    obj.data.materials.append(material)

    colecao_superficies.objects.link(obj)


# =========================================================
# POÇOS
# =========================================================


def criar_pocos(
    pocos,
    centro_x,
    centro_y,
    escala_z,
    colecao_pocos
):

    for poco in pocos:

        x = poco['x']
        y = poco['y']
        elevacao = poco['elevacao']
        profundidade = poco['profundidade']

        xn = (x - centro_x) * ESCALA_XY
        yn = (y - centro_y) * ESCALA_XY
        zn = elevacao * escala_z

        curva = bpy.data.curves.new(poco['id'], type='CURVE')
        curva.dimensions = '3D'
        curva.bevel_depth = 6 * ESCALA_XY
        curva.bevel_resolution = 4

        spline = curva.splines.new('POLY')

        if profundidade:
            spline.points.add(1)
            spline.points[0].co = (xn, yn, zn, 1)
            spline.points[1].co = (
                xn,
                yn,
                zn - (profundidade * escala_z),
                1
            )
        else:
            spline.points.add(0)
            spline.points[0].co = (xn, yn, zn, 1)

        obj = bpy.data.objects.new(poco['id'], curva)

        colecao_pocos.objects.link(obj)


# =========================================================
# PRINCIPAL
# =========================================================


def processar_modelo_geologico(
    input_file,
    exagero_vertical=EXAGERO_VERTICAL
):

    pocos = carregar_pocos(input_file)

    if len(pocos) == 0:
        raise Exception('Nenhum poço válido encontrado')

    xs = [p['x'] for p in pocos]
    ys = [p['y'] for p in pocos]

    centro_x = (min(xs) + max(xs)) / 2
    centro_y = (min(ys) + max(ys)) / 2

    escala_z = ESCALA_XY * exagero_vertical

    # --------------------------------------------
    # COLEÇÕES
    # --------------------------------------------

    colecao_principal = bpy.data.collections.new('modelo_geologico')
    bpy.context.scene.collection.children.link(colecao_principal)

    colecao_pocos = bpy.data.collections.new('pocos')
    colecao_principal.children.link(colecao_pocos)

    colecao_superficies = bpy.data.collections.new('superficies')
    colecao_principal.children.link(colecao_superficies)

    # --------------------------------------------
    # POÇOS
    # --------------------------------------------

    criar_pocos(
        pocos,
        centro_x,
        centro_y,
        escala_z,
        colecao_pocos
    )

    # --------------------------------------------
    # FORMAÇÕES
    # --------------------------------------------

    grupos = agrupar_formacoes(pocos)

    for formacao, lista_pocos in grupos.items():

        criar_superficie_formacao(
            formacao,
            lista_pocos,
            centro_x,
            centro_y,
            escala_z,
            colecao_superficies
        )

    # --------------------------------------------
    # VIEWPORT
    # --------------------------------------------

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.clip_end = 100000.0

    print('Modelo geológico incremental concluído')


# =========================================================
# EXEMPLO
# =========================================================

# processar_modelo_geologico(
#     '20260503_pocos_parana.csv'
# )
