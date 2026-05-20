import os
import sys
from pathlib import Path
import pandas as pd

# ==============================================================================
# 1. ANCORAGEM DE DIRETÓRIOS E COMPATIBILIDADE SGB (SISTEMA GERENCIAL BLENDER)
# ==============================================================================
# Define o caminho raiz absoluto baseado no ambiente do usuário
REPO_PATH = Path("/home/user/src/modelagem-bacia")

modelador_path = REPO_PATH / "scripts" / "modelador"
sys.path.append(str(modelador_path))

try:
    from main import main
except ImportError as e:
    print(f"[ERRO]: Falha ao importar main.py, verifique o caminho do repositório.")
    sys.exit(1)

# ==============================================================================
# 2. DICIONÁRIO DE TRADUÇÃO E EQUIVALÊNCIA ESTRATIGRÁFICA (CPRM -> RBF)
# ==============================================================================
DICIONARIO_GEOLOGICO = {
    # Membros e Formações equivalentes ou pertencentes ao Grupo Passa Dois / Rio do Rasto
    "Teresina": "Rio do Rasto",
    "Corumbataí": "Rio do Rasto",
    "Rio do Rasto": "Rio do Rasto",
    "Vale do Sol": "Rio do Rasto",
    "Pitanga": "Rio do Rasto",
    # Unidades do Grupo São Bento / Magmatismo Serra Geral
    "Goio Erê": "Serra Geral",
    "Serra Geral": "Serra Geral",
    "Botucatu": "Botucatu",
    "Piramboia": "Piramboia",
    # Subgrupo Itararé e Unidades Permo-Carboníferas da Base
    "Palermo": "Palermo",
    "Rio Bonito": "Rio Bonito",
    "Itararé": "Itararé",
    # Coberturas Cenozoicas/Cretáceas do topo (Agrupadas na unidade guia superior para amarração)
    "Coberturas detrito-lateríticas ferruginosas": "Serra Geral",
}

# Ordem Estrita de Empilhamento Geológico (Do Topo mais jovem para a Base mais antiga)
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
    "Serra Geral": (0.25, 0.25, 0.25, 1.0),  # Cinza Escuro (Basalto)
    "Botucatu": (0.90, 0.75, 0.30, 1.0),  # Amarelo Vivo (Arenito Eólico)
    "Piramboia": (0.85, 0.55, 0.20, 1.0),  # Laranja Arenoso
    "Rio do Rasto": (0.60, 0.30, 0.25, 1.0),  # Vermelho/Castanho (Argilitos/Siltitost)
    "Irati": (0.10, 0.10, 0.10, 1.0),  # Preto (Folhelhos Pirobetuminosos)
    "Palermo": (0.50, 0.55, 0.45, 1.0),  # Cinza Esverdeado
    "Rio Bonito": (0.75, 0.65, 0.55, 1.0),  # Cinza Claro / Tons de Carvão
    "Itararé": (0.40, 0.40, 0.45, 1.0),  # Azul-acinzentado (Sedimentos Glaciais)
    "Embasamento": (0.15, 0.15, 0.15, 1.0),  # Granito/Gnaisse basal
    "DESCONHECIDA": (0.5, 0.5, 0.5, 1.0),
}


# ==============================================================================
# 3. PIPELINE DE LIMPEZA E PADRONIZAÇÃO DE INGESTÃO
# ==============================================================================
def doctor():
    """
    Garante que o arquivo tenha as formações geológicas padronizadas e agrupadas conforme o dicionário de equivalências.
    """
    csv_input = REPO_PATH / "data" / "processed" / "20260503_pocos_parana_final.csv"
    csv_output = (
        REPO_PATH / "data" / "processed" / "20260503_pocos_parana_blender_ready.csv"
    )

    if not csv_input.exists():
        print(f"[ERRO] O arquivo {csv_input} não foi encontrado no diretório de dados.")
        sys.exit(1)

    print(f"[INFO] Lendo base de dados unificada: {csv_input.name}")
    df = pd.read_csv(csv_input)

    df["GEOLOGIA_FORMACAO_FINAL"] = (
        df["GEOLOGIA_FORMACAO_FINAL"].astype(str).str.strip()
    )

    def aplicar_equivalencia(nome_original):
        if nome_original in DICIONARIO_GEOLOGICO:
            return DICIONARIO_GEOLOGICO[nome_original]

        for chave, macro_unidade in DICIONARIO_GEOLOGICO.items():
            if chave.lower() in nome_original.lower():
                return macro_unidade
        return "DESCONHECIDA"

    print("[INFO] Executando conversão e agrupamento litoestratigráfico...")
    df["GEOLOGIA_FORMACAO_FINAL"] = df["GEOLOGIA_FORMACAO_FINAL"].apply(
        aplicar_equivalencia
    )

    print("\n" + "=" * 40)
    print(" AUDITORIA DE ENTRADAS PARA O MOTOR RBF ")
    print("=" * 40)
    print(df["GEOLOGIA_FORMACAO_FINAL"].value_counts())
    print("=" * 40 + "\n")

    df.to_csv(csv_output, index=False)
    print(f"[INFO] Exportação concluída com sucesso: {csv_output.name}")


# ==============================================================================
# 4. EXECUÇÃO DO MOTOR DE MODELAGEM
# ==============================================================================
if __name__ == "__main__":
    doctor()

    config = {
        "repo_path": str(REPO_PATH),
        "input_file": "20260503_pocos_parana_blender_ready.csv",
        "yolo": True,
        "exagero_vertical": 25,  # Exagero ideal para compensar a escala regional da bacia
        "resolucao_grid": 250,  # Resolução matemática da malha de interpolação
        "angulo_graus": 45,  # Alinhamento estrutural NW-SE predominante na bacia
        "razao_anisotropia": 2.0,
        "suavizacao": 0.1,
        "escala_xy": 0.00005,
        "ordem_estratigrafica": ORDEM_ESTRATIGRAFICA,
        "cores_formacoes": CORES_FORMACOES,
    }

    print("[INFO] Disparando main(config) dentro do ecossistema do Blender...")
    main(config)
    print("[SUCESSO] Processamento geométrico concluído. Camadas geradas na Scene.")
