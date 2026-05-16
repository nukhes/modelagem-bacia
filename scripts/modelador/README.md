[Voltar ao README](../../README.md)

# Modelagem
A modelagem é feita em etapas e consolidada `main.py`, o processo busca ser preciso e flexível, lidando com dados ausentes usando matemática, o modelo ainda está em ajustes, no futuro seria importante implementar algum tipo de machine learning para preencher a ausência de dados com a "média de conhecimento geológico correlato".

## 1. Carregando os dados
`carregando_pocos.py` entrypoint do processo de modelagem, ela percorre o dataset, aplicando regras e operações para normalizar o arquivo, lidando com dados ausentes e escrevando um CSV final com as colunas `id, x, y, elevacao, cota_formacao, formacao, tem_profundidade`.

## 2. Organizando e ajustando os dados
`geometria.py` manipula as informações para criar uma superfície plana com interpolação por Funções de Base Radial (RBF) e suavização, tratando casos de erro em que não é possível determinar uma solução para a superfície, a interpolação nos ajuda a preencher espaços entre poços de modo matematicamente preciso, por fim, com anisotropia podemos "moldar" os pontos para uma elipse com angulo e razão diferente.

## 3. Criando as camadas
`blender_api.py` se comunica diretamente com o blender por meio da biblioteca `bpy` para criar os modelos, usando um shader BSDF para uma representação visualmente valorosa, o método `criar_solido_camada()` faz o trabalho de montar a superfície a partir dos dados geométricos.
