import bpy
import csv
import numpy as np
from scipy.interpolate import Rbf

"""
Este script gera uma superfície com interpolação e cria objetos de curva para cada poço no Blender. O resultado é uma coleção organizada de objetos representando a superfície e os poços, facilitando a visualização geológica. O script é flexível e pode ser adaptado para diferentes conjuntos de dados, desde que sigam as especificações técnicas do CSV de exemplo 'data/example/modelo_poco.csv'.
"""


def processar_modelo_geologico(input_file, exagero_vertical=10.0):
    pontos_brutos = {}
    pocos = []
    
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                x = float(row['X_UTM'])
                y = float(row['Y_UTM'])
                z = float(row['ELEVACAO'])
            except ValueError:
                continue

            id_poco = row['POCO']
            prof_str = row.get('PROFUNDIDADE_VERTICAL_M', '').strip()
            prof = float(prof_str) if prof_str else 500.0
            if prof <= 0.0:
                prof = 500.0
            
            pocos.append((x, y, z, id_poco, prof))
            
            coord_key = (x, y)
            if coord_key not in pontos_brutos:
                pontos_brutos[coord_key] = []
            pontos_brutos[coord_key].append(z)

    pontos_x = []
    pontos_y = []
    pontos_z = []
    
    for (x, y), zs in pontos_brutos.items():
        pontos_x.append(x)
        pontos_y.append(y)
        pontos_z.append(sum(zs) / len(zs))

    min_x, max_x = min(pontos_x), max(pontos_x)
    min_y, max_y = min(pontos_y), max(pontos_y)
    min_z, max_z = min(pontos_z), max(pontos_z)

    x_norm = [(x - min_x) / (max_x - min_x) for x in pontos_x]
    y_norm = [(y - min_y) / (max_y - min_y) for y in pontos_y]
    z_norm = [(z - min_z) / (max_z - min_z) for z in pontos_z]

    rbf = Rbf(x_norm, y_norm, z_norm, function='thin_plate', smooth=0.01)

    centro_x = (min_x + max_x) / 2.0
    centro_y = (min_y + max_y) / 2.0
    escala_xy = 0.001
    escala_z = escala_xy * exagero_vertical

    colecao_principal = bpy.data.collections.new('modelo')
    bpy.context.scene.collection.children.link(colecao_principal)

    colecao_pocos = bpy.data.collections.new('pocos')
    colecao_principal.children.link(colecao_pocos)

    for pt in pocos:
        x, y, z, id_poco, prof = pt
        xn = (x - centro_x) * escala_xy
        yn = (y - centro_y) * escala_xy
        zn = z * escala_z
        pn = prof * escala_z
        
        curva = bpy.data.curves.new(id_poco, type='CURVE')
        curva.dimensions = '3D'
        curva.bevel_depth = 10 * escala_xy
        curva.bevel_resolution = 4

        spline = curva.splines.new('POLY')
        spline.points.add(1)
        spline.points[0].co = (xn, yn, zn, 1)
        spline.points[1].co = (xn, yn, zn - pn, 1)

        objeto_curva = bpy.data.objects.new(id_poco, curva)
        colecao_pocos.objects.link(objeto_curva)

    res = 50
    grid_x_norm = np.linspace(0, 1, res)
    grid_y_norm = np.linspace(0, 1, res)
    
    vertices = []
    for gy_n in grid_y_norm:
        gy_real = gy_n * (max_y - min_y) + min_y
        yn_blender = (gy_real - centro_y) * escala_xy
        
        for gx_n in grid_x_norm:
            gx_real = gx_n * (max_x - min_x) + min_x
            xn_blender = (gx_real - centro_x) * escala_xy
            
            gz_n = float(rbf(gx_n, gy_n))
            gz_real = gz_n * (max_z - min_z) + min_z
            zn_blender = gz_real * escala_z
            
            vertices.append((xn_blender, yn_blender, zn_blender))

    faces = []
    for i in range(res - 1):
        for j in range(res - 1):
            v1 = i * res + j
            v2 = v1 + 1
            v3 = v1 + res + 1
            v4 = v1 + res
            faces.append((v1, v2, v3, v4))

    malha_superficie = bpy.data.meshes.new('malha_superficie')
    malha_superficie.from_pydata(vertices, [], faces)
    malha_superficie.update()

    objeto_superficie = bpy.data.objects.new('obj_superficie', malha_superficie)
    colecao_superficie = bpy.data.collections.new('superficies')
    colecao_principal.children.link(colecao_superficie)
    colecao_superficie.objects.link(objeto_superficie)

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.clip_end = 100000.0

# exemplo de uso para um CSV seguindo as especificações técnicas
# processar_modelo_geologico('data/example/modelo_poco.csv')