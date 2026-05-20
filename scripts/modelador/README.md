[Voltar ao README](../../README.md)

# Sobre
A modelagem é feita em etapas e consolidada `main.py`, o processo busca ser preciso e flexível, lidando com dados ausentes usando matemática, o modelo ainda está em ajustes, no futuro seria importante implementar algum tipo de machine learning para preencher a ausência de dados com a "média de conhecimento geológico correlato".

# Uso
Para importar e usar o modelador dentro do blender é necessário instalar as dependências ("scipy" e "numpy"), após isso coloque o código abaixo na aba scripting do programa, note que o caminho (`config["repo_path"]`) para o repositório precisa ser absoluto, e o nome do dataset (`config["input_file"]`) se refere a um arquivo dentro de `<repo_path>/data/processed`, ao executar aguarde alguns segundos até que o modelo esteja pronto.

```python
# === CONFIGURAÇÕES ===
ORDEM_ESTRATIGRAFICA = [
    "Serra Geral",
    "Botucatu",
    "Piramboia",
    "Rio do Rasto",
    "Irati",
    "Palermo",
    "Rio Bonito",
    "Itararé",
]

CORES_FORMACOES = {
    "Topografia": (0.4, 0.3, 0.2, 1.0),
    "Serra Geral": (0.35, 0.35, 0.35, 1.0),
    "Botucatu": (0.85, 0.65, 0.25, 1.0),
    "Piramboia": (0.82, 0.50, 0.20, 1.0),
    "Rio do Rasto": (0.55, 0.25, 0.20, 1.0),
    "Irati": (0.15, 0.15, 0.15, 1.0),
    "Palermo": (0.6, 0.4, 0.3, 1.0),
    "Rio Bonito": (0.7, 0.5, 0.4, 1.0),
    "Itararé": (0.45, 0.35, 0.25, 1.0),
    "Embasamento": (0.2, 0.2, 0.2, 1.0),
    "DESCONHECIDA": (0.5, 0.5, 0.5, 1.0),
}

config = {
    "input_file": "20260503_pocos_parana.csv",
    "yolo": True,
    "exagero_vertical": 100,
    "escala_xy": 0.001,
    "resolucao_grid": 500,
    "angulo_graus": 45,
    "razao_anisotropia": 2.0,
    "suavizacao": 0.05,
    "ordem_estratigrafica": ORDEM_ESTRATIGRAFICA,
    "cores_formacoes": CORES_FORMACOES,
    "repo_path": "/home/user/src/modelagem-bacia",
}

# === EXECUÇÃO ===
import sys
sys.path.insert(0, f"{config['repo_path']}/scripts/modelador")
from main import main
main(config)
```

# Detalhes

## 1. Carregando os dados
`carregando_pocos.py` entrypoint do processo de modelagem, ela percorre o dataset, aplicando regras e operações para normalizar o arquivo, lidando com dados ausentes e escrevando um CSV final com as colunas `id, x, y, elevacao, cota_formacao, formacao, tem_profundidade`.

## 2. Organizando e ajustando os dados
`geometria.py` manipula as informações para criar uma superfície plana com interpolação por Funções de Base Radial (RBF) e suavização, tratando casos de erro em que não é possível determinar uma solução para a superfície, a interpolação nos ajuda a preencher espaços entre poços de modo matematicamente preciso, por fim, com anisotropia podemos "moldar" os pontos para uma elipse com angulo e razão diferente.

## 3. Criando as camadas
`blender_api.py` se comunica diretamente com o blender por meio da biblioteca `bpy` para criar os modelos, usando um shader BSDF para uma representação visualmente valorosa, o método `criar_solido_camada()` faz o trabalho de montar a superfície a partir dos dados geométricos.
