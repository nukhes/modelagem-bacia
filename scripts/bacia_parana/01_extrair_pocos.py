import pandas as pd
from pyproj import Transformer

"""
Este script realiza a extração de poços da bacia do Paraná, convertendo suas coordenadas geográficas (latitude e longitude) para o sistema de coordenadas UTM (SIRGAS 2000, zona 22S, EPSG:31982). O processo inclui a leitura de um arquivo CSV bruto, filtragem dos dados para a bacia específica, transformação das coordenadas e exportação do resultado para um novo arquivo CSV. A abordagem é orientada à clareza e eficiência, utilizando bibliotecas robustas como pandas para manipulação de dados e pyproj para reprojeção espacial.
"""

input_file='data/raw/20260503_pocos.csv'
output_file='data/processed/20260503_pocos_parana.csv'

transformer = Transformer.from_crs("epsg:4326", "epsg:31982")
target_cols = ['POCO', 'BACIA', 'LATITUDE_BASE_DD', 'LONGITUDE_BASE_DD', 'GEOLOGIA_FORMACAO_FINAL', 'COTA_ALTIMETRICA_M', 'PROFUNDIDADE_VERTICAL_M']

df = pd.read_csv(input_file, encoding='latin1', decimal=',', usecols=target_cols, low_memory=False)

# copia as entradas que correspondem aos pocos de interesse
pr = df[df['BACIA'] == 'Paraná'].copy()

# adiciona as colunas de coordenadas UTM
x_utm, y_utm = transformer.transform(pr['LONGITUDE_BASE_DD'].values, pr['LATITUDE_BASE_DD'].values)
pr['X_UTM'] = x_utm
pr['Y_UTM'] = y_utm

pr.to_csv(output_file, index=False)
