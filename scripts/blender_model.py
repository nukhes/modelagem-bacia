import bpy
import bmesh
import csv
import numpy as np
from scipy.interpolate import Rbf

def processar_modelo_geologico(caminho_csv):
    formacoes = {}
    pocos = {}
    min_x = float('inf')
    min_y = float('inf')

    with open(caminho_csv, 'r', encoding='utf-8') as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            x = float(linha['x_utm'])
            y = float(linha['y_utm'])
            z = float(linha['z_abs'])
            formacao = linha['formation_name']
            id_poco = linha['well_id']

            if x < min_x: 
                min_x = x
            if y < min_y: 
                min_y = y

            if formacao not in formacoes:
                formacoes[formacao] = {'x': [], 'y': [], 'z': []}
            formacoes[formacao]['x'].append(x)
            formacoes[formacao]['y'].append(y)
            formacoes[formacao]['z'].append(z)

            if id_poco not in pocos:
                pocos[id_poco] = []
            pocos[id_poco].append((x, y, z))

    colecao_principal = bpy.data.collections.new("Modelo_Estratigrafico")
    bpy.context.scene.collection.children.link(colecao_principal)

    colecao_formacoes = bpy.data.collections.new("Superficies_Interpoladas")
    colecao_principal.children.link(colecao_formacoes)

    res = 20

    for nome_formacao, dados in formacoes.items():
        x_dados = np.array(dados['x']) - min_x
        y_dados = np.array(dados['y']) - min_y
        z_dados = np.array(dados['z'])

        grid_x, grid_y = np.meshgrid(
            np.linspace(np.min(x_dados), np.max(x_dados), res),
            np.linspace(np.min(y_dados), np.max(y_dados), res)
        )

        rbf = Rbf(x_dados, y_dados, z_dados, function='linear')
        grid_z = rbf(grid_x, grid_y)

        mesh = bpy.data.meshes.new(nome_formacao)
        obj = bpy.data.objects.new(nome_formacao, mesh)
        colecao_formacoes.objects.link(obj)

        bm = bmesh.new()

        for i in range(res):
            for j in range(res):
                bm.verts.new((grid_x[i, j], grid_y[i, j], grid_z[i, j]))

        bm.verts.ensure_lookup_table()

        for i in range(res - 1):
            for j in range(res - 1):
                bm.faces.new((
                    bm.verts[i * res + j],
                    bm.verts[i * res + (j + 1)],
                    bm.verts[(i + 1) * res + (j + 1)],
                    bm.verts[(i + 1) * res + j]
                ))

        bm.to_mesh(mesh)
        bm.free()

    colecao_pocos = bpy.data.collections.new("Tracos_Pocos")
    colecao_principal.children.link(colecao_pocos)

    for id_poco, coordenadas in pocos.items():
        curva = bpy.data.curves.new(id_poco, type='CURVE')
        curva.dimensions = '3D'
        curva.bevel_depth = 2
        curva.bevel_resolution = 4

        spline = curva.splines.new('POLY')
        spline.points.add(len(coordenadas) - 1)

        coordenadas.sort(key=lambda item: item[2], reverse=True)
        for i, c in enumerate(coordenadas):
            spline.points[i].co = (c[0] - min_x, c[1] - min_y, c[2], 1)

        objeto_curva = bpy.data.objects.new(id_poco, curva)
        colecao_pocos.objects.link(objeto_curva)

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.clip_end = 500000.0

processar_modelo_geologico("./caminho/para/dados.csv")