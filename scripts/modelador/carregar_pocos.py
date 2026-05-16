import csv
from helpers import str2float

def carregar_pocos(input_file):
    '''
    essa função é o entrypoint do processo de modelagem, ela le o dataset em CSV
    (nossa planilha) e aplica algumas regras e operações para normalizar o 
    arquivo, lidando com dados ausentes.
    '''

    pocos = []
    with open(input_file, 'r', encoding='utf-8', errors='replace') as file:
        reader = csv.DictReader(file)
        headers = {field.strip().upper(): field for field in reader.fieldnames}
        for row in reader:
            x_key = headers.get('X_UTM')
            y_key = headers.get('Y_UTM')
            elev_key = headers.get('ELEVACAO')
            prof_key = headers.get('PROFUNDIDADE_VERTICAL_M')
            cot_key = headers.get('COTA_ALTIMETRICA_M')
            form_key = headers.get('GEOLOGIA_FORMACAO_FINAL')

            x = str2float(row.get(x_key)) if x_key else None
            y = str2float(row.get(y_key)) if y_key else None
            elevacao = str2float(row.get(elev_key)) if elev_key else None
            
            if x is None or y is None or elevacao is None: 
                continue
            
            profundidade = str2float(row.get(prof_key))
            elevacao = str2float(row.get(elev_key))
            cota_alt = str2float(row.get(cot_key))
            formacao = str(row.get(form_key)).strip() if form_key else 'DESCONHECIDA'
            cota_formacao = abs(elevacao-cota_alt) if cota_alt else 20.0 # REVER ESSA LOGICA
            tem_profundidade = profundidade is not None
            
            pocos.append({
                'id': row.get('POCO', 'POCO_SEM_NOME'),
                'x': x, 'y': y, 'elevacao': elevacao,
                'cota_formacao': cota_formacao,
                'formacao': formacao, 'tem_profundidade': tem_profundidade
            })
    
    return pocos
