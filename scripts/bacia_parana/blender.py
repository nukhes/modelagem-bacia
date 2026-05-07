import sys
import importlib

"""
Rode este script dentro do Blender em um projeto em branco.
"""

CAMINHO_REPOSITORIO = '/home/pedrohenrique/src/modelagem-bacia'
NOME_DATASET='20260503_pocos_parana.csv'

sys.path.append(f'{CAMINHO_REPOSITORIO}/scripts')

import modelador
importlib.reload(modelador)

modelador.processar_modelo_impressao(f'{CAMINHO_REPOSITORIO}/data/processed/{NOME_DATASET}', True, 100)