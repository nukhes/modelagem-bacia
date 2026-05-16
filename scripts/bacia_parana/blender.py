import sys
import bpy
from pathlib import Path

# CAMINHOS ESSENCIAIS
REPO_ROOT = Path('/home/user/src/modelagem-bacia')
SCRIPTS_PATH = REPO_ROOT / 'scripts' / 'modelador'
DATA_PATH = REPO_ROOT / 'data' / 'processed'

if str(SCRIPTS_PATH) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_PATH))

import main as modelador

PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"
SYSTEM_PACKAGES = Path(f"/usr/lib/python3/dist-packages") 

if SYSTEM_PACKAGES.exists() and str(SYSTEM_PACKAGES) not in sys.path:
    sys.path.append(str(SYSTEM_PACKAGES))

def run():
    """
    Executa a pipeline de modelagem.
    """
    dataset_path = DATA_PATH / '20260503_pocos_parana.csv'
    
    # Parâmetros de Geoprocessamento
    config = {
        "input_file": str(dataset_path),
        "yolo": False,
        "exagero_vertical": 100,
        "resolucao_grid": 500,
        "angulo_graus": 45,
        "razao_anisotropia": 2.0,
        "suavizacao": 0.05
    }

    print(f"\n[INFO] Iniciando modelagem: {dataset_path.name}")
    
    try:
        modelador.main(**config)
        print("[SUCESSO] Malha gerada. Salvando arquivo...")
        bpy.ops.wm.save_as_mainfile(filepath=str(REPO_ROOT / 'data' / 'processed' / f'{dataset_path.stem}.blend'))
        
    except Exception as e:
        print(f"[ERRO] Falha na execução: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run()