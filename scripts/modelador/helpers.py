'''
helpers.py contém métodos que não fazem parte da lógica principal
'''


def str2float(valor):
    '''
    Converte um valor para float, aceitando vírgula decimal no formato BR.
    '''
    if valor is None:
        return None

    texto = str(valor).strip()
    if texto == '':
        return None

    try:
        return float(texto.replace(',', '.'))
    except ValueError:
        return None
