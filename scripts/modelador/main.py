import os
import sys
import bpy
import numpy as np
from collections import defaultdict
from pathlib import Path

# Imports do projeto
from carregar_pocos import carregar_pocos
from blender_api import criar_material, criar_solido_camada
import geometria

# Hierarquia Estratigráfica da Bacia do Paraná (De cima para baixo)
# Isso evita que o modelo "vcie" ou esmague camadas por erro de média.
ORDEM_ESTRATIGRAFICA = [
    'Serra Geral', 
    'Botucatu', 
    'Piramboia', 
    'Rio do Rasto', 
    'Irati', 
    'Palermo', 
    'Rio Bonito', 
    'Itararé'
]

CORES_FORMACOES = {
    'Serra Geral': (0.35, 0.35, 0.35, 1.0), # Basalto
    'Botucatu': (0.85, 0.65, 0.25, 1.0),    # Arenito
    'Piramboia': (0.82, 0.50, 0.20, 1.0),
    'Irati': (0.15, 0.15, 0.15, 1.0),       # Folhelho Negro
    'Rio do Rasto': (0.55, 0.25, 0.20, 1.0),
    'DESCONHECIDA': (0.5, 0.5, 0.5, 1.0)
}

# Parâmetros de escala
ESCALA_XY = 0.001 
MIN_PONTOS_FORMACAO = 4

def main(input_file, yolo, exagero_vertical=100, resolucao_grid=500, angulo_graus=45, razao_anisotropia=2, suavizacao=0.05):
    pocos = carregar_pocos(input_file)
    
    if not pocos: 
        raise ValueError('Dataset vazio ou inválido.')
    
    xs = np.array([p['x'] for p in pocos])
    ys = np.array([p['y'] for p in pocos])
    elevacoes = [p['elevacao'] for p in pocos]
    
    min_x, max_x = xs.min(), xs.max()
    min_y, max_y = ys.min(), ys.max()
    dx, dy = max_x - min_x, max_y - min_y
    centro_x, centro_y = (min_x + max_x) / 2.0, (min_y + max_y) / 2.0
    escala_z = ESCALA_XY * exagero_vertical

    colecao = bpy.data.collections.new('Bacia_Parana_3D')
    bpy.context.scene.collection.children.link(colecao)
    
    z_topo_grid = geometria.obter_grid_interpolado(
        pontos_x=xs, pontos_y=ys, valores_z=elevacoes,
        dx=dx, dy=dy, min_x=min_x, min_y=min_y,
        resolucao_grid=resolucao_grid,
        angulo_graus=angulo_graus,
        razao_anisotropia=razao_anisotropia,
        suavizacao=suavizacao
    )
    
    grupos = defaultdict(list)
    for p in pocos:
        # ignora se o poço tem profundidade completa, confia na formação mapeada
        if (p['tem_profundidade'] or yolo) and p['formacao'] != 'DESCONHECIDA':
            grupos[p['formacao']].append(p)

    camadas_interpoladas = {}
    for formacao, lista_pocos in grupos.items():
        if len(lista_pocos) < MIN_PONTOS_FORMACAO and not yolo:
            continue

        z_f = [p['cota_formacao'] for p in lista_pocos]
        xf = [p['x'] for p in lista_pocos]
        yf = [p['y'] for p in lista_pocos]

        # interpola o contato (base) da formação
        z_formacao_grid = geometria.obter_grid_interpolado(
            pontos_x=xf, pontos_y=yf, valores_z=z_f,
            dx=dx, dy=dy, min_x=min_x, min_y=min_y,
            resolucao_grid=resolucao_grid,
            angulo_graus=angulo_graus,
            razao_anisotropia=razao_anisotropia,
            suavizacao=suavizacao
        )
        camadas_interpoladas[formacao] = z_formacao_grid
        
    # montamos a pilha respeitando a geologia real
    grids_ordem = [('Topografia', z_topo_grid)]
    
    for nome in ORDEM_ESTRATIGRAFICA:
        if nome in camadas_interpoladas:
            grids_ordem.append((nome, camadas_interpoladas[nome]))
    
    # adiciona o embasamento (base do modelo)
    min_global_z = np.min(z_topo_grid)
    for g in camadas_interpoladas.values():
        min_global_z = min(min_global_z, np.min(g))
    
    z_base_absoluto = min_global_z - (np.max(z_topo_grid) - min_global_z) * 0.2
    grid_base = np.full((resolucao_grid, resolucao_grid), z_base_absoluto)
    grids_ordem.append(('Embasamento', grid_base))

    for i in range(1, len(grids_ordem)):
        # np.minimum impede que o contato inferior "fure" o contato superior
        grids_ordem[i] = (grids_ordem[i][0], np.minimum(grids_ordem[i][1], grids_ordem[i-1][1]))

    for i in range(len(grids_ordem) - 1):
        nome_camada = grids_ordem[i][0]
        nome_proxima = grids_ordem[i+1][0]
        
        # Define nome e cor do objeto 3D
        idx = f"{i:02d}"
        nome_obj = f"{idx}_{nome_camada}_Ate_{nome_proxima}"
        
        if i == 0:
            cor = (0.4, 0.3, 0.2, 1.0)
        else:
            cor = CORES_FORMACOES.get(nome_camada, (0.7, 0.1, 0.7, 1.0)) # Roxo se desconhecido
            
        mat = criar_material(f"Mat_{nome_camada}", cor)
        
        criar_solido_camada(
            nome_obj, 
            grids_ordem[i][1],    # Topo
            grids_ordem[i+1][1],  # Base
            centro_x, centro_y, dx, dy, min_x, min_y, 
            escala_z, mat, resolucao_grid, ESCALA_XY, colecao
        )

    print(f"\n[SUCESSO] {len(grids_ordem)-1} camadas geradas no Blender.")