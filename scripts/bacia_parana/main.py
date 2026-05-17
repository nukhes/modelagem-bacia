import subprocess

"""
Este script orquestra a execução do fluxo de processamento de dados para a bacia do Paraná, coordenando a extração de poços e a cruzagem de altitude.

O resultado final é um arquivo CSV atualizado com as coordenadas UTM e as elevações correspondentes, pronto para ser utilizado na modelagem 'data/processed/20260503_pocos_parana.csv'.
"""

subprocess.run(["python", "scripts/bacia_parana/01_extrair_pocos.py"], check=True)
subprocess.run(
    ["python", "scripts/bacia_parana/02_cruzar_altitude_pocos.py"], check=True
)
print(
    "fluxo de processamento concluído com sucesso, arquivo final em 'data/processed/20260503_pocos_parana.csv'."
)
