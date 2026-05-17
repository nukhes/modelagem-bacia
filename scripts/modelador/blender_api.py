import bpy
import numpy as np
import bmesh

def criar_material(nome, rgba, roughness=0.6):
    mat = bpy.data.materials.new(nome)
    mat.use_nodes = True

    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = rgba
    shader.inputs['Roughness'].default_value = roughness

    return mat

def criar_solido_camada(nome, z_top, z_bot, centro_x, centro_y, dx, dy, min_x,
    min_y, escala_z, material, resolucao_grid, escala_xy, colecao):

    y_idx, x_idx = np.mgrid[0:resolucao_grid, 0:resolucao_grid]

    x_real = (x_idx / (resolucao_grid - 1)) * dx + min_x
    y_real = (y_idx / (resolucao_grid - 1)) * dy + min_y

    xb = (x_real - centro_x) * escala_xy
    yb = (y_real - centro_y) * escala_xy
    
    zt = z_top * escala_z
    zb = z_bot * escala_z
    
    verts_top = np.stack((xb, yb, z_top * escala_z), axis=-1).reshape(-1, 3)
    verts_bot = np.stack((xb, yb, z_bot * escala_z), axis=-1).reshape(-1, 3)
    todos_vertices = np.vstack((verts_top, verts_bot))
    num_vertices = len(todos_vertices)
    
    offset = resolucao_grid * resolucao_grid
    
    # índices para os cantos superiores esquerdos de cada quadrado
    y_f, x_f = np.mgrid[0:resolucao_grid-1, 0:resolucao_grid-1]
    
    idx_0 = y_f * resolucao_grid + x_f
    idx_1 = idx_0 + 1
    idx_2 = (y_f + 1) * resolucao_grid + (x_f + 1)
    idx_3 = (y_f + 1) * resolucao_grid + x_f
    
    faces_top = np.stack((idx_0, idx_1, idx_2, idx_3), axis=-1).reshape(-1, 4)
    faces_bot = np.stack((idx_0 + offset, idx_3 + offset, idx_2 + offset, idx_1 + offset), axis=-1).reshape(-1, 4)
    
    faces_laterais = []
    def idx_t(x, y): return y * resolucao_grid + x
    def idx_b(x, y): return offset + y * resolucao_grid + x
    
    for x in range(resolucao_grid - 1):
        faces_laterais.append([idx_t(x, 0), idx_b(x, 0), idx_b(x+1, 0), idx_t(x+1, 0)])
        faces_laterais.append([idx_t(x, resolucao_grid-1), idx_t(x+1, resolucao_grid-1), idx_b(x+1, resolucao_grid-1), idx_b(x, resolucao_grid-1)])
        
    for y in range(resolucao_grid - 1):
        faces_laterais.append([idx_t(0, y), idx_t(0, y+1), idx_b(0, y+1), idx_b(0, y)])
        faces_laterais.append([idx_t(resolucao_grid-1, y), idx_b(resolucao_grid-1, y), idx_b(resolucao_grid-1, y+1), idx_t(resolucao_grid-1, y+1)])
        
    all_faces = np.vstack((faces_top, faces_bot, np.array(faces_laterais)))
    num_faces = len(all_faces)

    malha = bpy.data.meshes.new(nome)

    malha.vertices.add(num_vertices)
    malha.polygons.add(num_faces)
    malha.loops.add(num_faces * 4)

    malha.vertices.foreach_set("co", todos_vertices.ravel())

    malha.loops.foreach_set("vertex_index", all_faces.ravel())
    malha.polygons.foreach_set("loop_start", np.arange(0, num_faces * 4, 4))
    malha.polygons.foreach_set("loop_total", np.full(num_faces, 4, dtype=np.int32))

    malha.polygons.foreach_set("use_smooth", np.full(num_faces, True, dtype=bool))
    
    malha.update(calc_edges=True)
    
    obj = bpy.data.objects.new(nome, malha)
    if material: 
        obj.data.materials.append(material)

    colecao.objects.link(obj)