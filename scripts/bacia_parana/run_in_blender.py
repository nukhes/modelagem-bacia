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
