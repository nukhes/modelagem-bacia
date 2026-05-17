import csv
from helpers import str2float


def carregar_pocos(input_file):
    """
    Carrega poços aplicando validações rígidas de consistência geométrica.
    Retorna a estrutura exata esperada pelo script de interpolação e modelagem Blender.
    """
    pocos = []

    print("[DEBUG]: INÍCIO LOG DE POÇOS")
    with open(input_file, "r", encoding="utf-8", errors="replace") as file:
        reader = csv.DictReader(file)
        headers = {field.strip().upper(): field for field in reader.fieldnames if field}

        x_key = headers.get("X_UTM")
        y_key = headers.get("Y_UTM")
        elev_key = headers.get("ELEVACAO")
        prof_key = headers.get("PROFUNDIDADE_VERTICAL_M")
        cot_key = headers.get("COTA_ALTIMETRICA_M")
        form_key = headers.get("GEOLOGIA_FORMACAO_FINAL")

        for row in reader:
            x = str2float(row.get(x_key)) if x_key else None
            y = str2float(row.get(y_key)) if y_key else None
            elevacao = str2float(row.get(elev_key)) if elev_key else None

            if x is None or y is None or elevacao is None:
                continue

            profundidade = str2float(row.get(prof_key)) if prof_key else None
            cota_alt = str2float(row.get(cot_key)) if cot_key else None

            formacao = (
                str(row.get(form_key)).strip()
                if form_key and row.get(form_key)
                else "DESCONHECIDA"
            )
            if formacao.lower() in ["none", "nan", "null", ""]:
                formacao = "DESCONHECIDA"

            cota_formacao = 0.0
            prof_calculada = 0.0
            tem_profundidade = False

            if profundidade is not None and profundidade > 0:
                prof_calculada = profundidade
                cota_formacao = elevacao - profundidade
                tem_profundidade = True

            elif cota_alt is not None:
                if cota_alt == 0.0 and elevacao != 0.0:
                    tem_profundidade = False
                else:
                    cota_formacao = cota_alt
                    prof_calculada = elevacao - cota_alt
                    tem_profundidade = True

            if tem_profundidade and prof_calculada < 0:
                tem_profundidade = False

            if not tem_profundidade:
                cota_formacao = elevacao
                prof_calculada = 0.0

            poco = {
                "id": row.get("POCO", "POCO_SEM_NOME").strip(),
                "x": x,
                "y": y,
                "elevacao": elevacao,
                "cota_formacao": cota_formacao,
                "profundidade": prof_calculada,
                "formacao": formacao,
                "tem_profundidade": tem_profundidade,
            }
            pocos.append(poco)
            print(
                f"[DEBUG] Poço carregado: {poco['id']} - X: {x}, Y: {y}, Elev: {elevacao}, Cota: {cota_formacao}, Prof: {prof_calculada}, Form: {formacao}"
            )
    print("[DEBUG]: FIM LOG DE POÇOS")
    return pocos
