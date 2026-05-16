import bpy
import numpy as np

def criar_material(nome, rgba, roughness=1):
    mat = bpy.data.materials.new(nome)
    mat.use_nodes = True

    # usamos Principled BSDF como shader pra renderizar materiais
    # no futuro seria interessante usar propriedades de shader
    # avançadas para cada camada estatigrafica
    shader = mat.node_tree.nodes.get('Principled BSDF')
    if shader is None:
        raise RuntimeError('Principled BSDF node not found in the material.')

    shader.inputs['Base Color'].default_value = rgba
    shader.inputs['Roughness'].default_value = roughness

    return mat
    

def criar_solido_camada(nome, z_top, z_bot, centro_x, centro_y, dx, dy, min_x,
    min_y, escala_z, material, resolucao_grid, escala_xy, colecao):
    
    vertices = []
    faces = []
    
    grid_x = np.linspace(0, 1, resolucao_grid)
    grid_y = np.linspace(0, 1, resolucao_grid)
    
    for y in range(resolucao_grid):
        for x in range(resolucao_grid):
            x_real = grid_x[x] * dx + min_x
            y_real = grid_y[y] * dy + min_y
            xb = (x_real - centro_x) * escala_xy
            yb = (y_real - centro_y) * escala_xy
            zt = z_top[y, x] * escala_z
            vertices.append((xb, yb, zt))
            
    offset = resolucao_grid * resolucao_grid
    
    for y in range(resolucao_grid):
        for x in range(resolucao_grid):
            x_real = grid_x[x] * dx + min_x
            y_real = grid_y[y] * dy + min_y
            xb = (x_real - centro_x) * escala_xy
            yb = (y_real - centro_y) * escala_xy
            zb = z_bot[y, x] * escala_z
            vertices.append((xb, yb, zb))
            
    def idx_t(x, y): return y * resolucao_grid + x
    def idx_b(x, y): return offset + y * resolucao_grid + x

    for y in range(resolucao_grid - 1):
        for x in range(resolucao_grid - 1):
            faces.append((idx_t(x, y), idx_t(x+1, y), idx_t(x+1, y+1), idx_t(x, y+1)))
            
    for y in range(resolucao_grid - 1):
        for x in range(resolucao_grid - 1):
            faces.append((idx_b(x, y), idx_b(x, y+1), idx_b(x+1, y+1), idx_b(x+1, y)))
            
    y = 0
    for x in range(resolucao_grid - 1):
        faces.append((idx_t(x, y), idx_b(x, y), idx_b(x+1, y), idx_t(x+1, y)))
        
    y = resolucao_grid - 1
    for x in range(resolucao_grid - 1):
        faces.append((idx_t(x, y), idx_t(x+1, y), idx_b(x+1, y), idx_b(x, y)))
        
    x = 0
    for y in range(resolucao_grid - 1):
        faces.append((idx_t(x, y), idx_t(x, y+1), idx_b(x, y+1), idx_b(x, y)))
        
    x = resolucao_grid - 1
    for y in range(resolucao_grid - 1):
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
