# Modelagem

A modelagem é feita em etapas e consolidada `main.py`

## 1. Carregando os dados
`carregando_pocos.py` entrypoint do processo de modelagem, ela percorre o dataset, aplicando regras e operações para normalizar o arquivo, lidando com dados ausentes e escrevando um CSV final com as colunas `id, x, y, elevacao, cota_formacao, formacao, tem_profundidade`.

## 2. Organizando e ajustando os dados
`geometria.py` manipula as informações para criar uma superfície plana com interpolação por Funções de Base Radial (RBF) e suavização, tratando casos de erro em que não é possível determinar uma solução para a superfície.

## 3. Criando as camadas
`blender_api.py`
