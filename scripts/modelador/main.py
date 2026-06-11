import sys
from pathlib import Path
import bpy
import numpy as np
from datetime import datetime
from collections import defaultdict
from carregar_pocos import carregar_pocos
from blender_api import criar_material, criar_solido_camada
import geometria


def run(
    input_file,
    yolo,
    exagero_vertical,
    resolucao_grid,
    angulo_graus,
    razao_anisotropia,
    suavizacao,
    ordem_estratigrafica,
    cores_formacoes,
    repo_path,
    escala_xy=1.0,
):

    csv_path = Path(f"{repo_path}/data/processed/{input_file}")

    if not csv_path.exists():
        raise FileNotFoundError(f"O arquivo {csv_path} não existe.")

    pocos = carregar_pocos(csv_path)

    if not pocos:
        raise ValueError("Dataset vazio ou inválido.")

    print(f"[INFO] Total de poços: {len(pocos)}")

    xs = np.array([p["x"] for p in pocos])
    ys = np.array([p["y"] for p in pocos])
    elevacoes = np.array([p["elevacao"] for p in pocos])

    min_x, max_x = xs.min(), xs.max()
    min_y, max_y = ys.min(), ys.max()
    dx, dy = max_x - min_x, max_y - min_y
    centro_x, centro_y = (min_x + max_x) / 2.0, (min_y + max_y) / 2.0

    escala_z = escala_xy * exagero_vertical

    colecao = bpy.data.collections.new("Bacia_Parana_3D")
    bpy.context.scene.collection.children.link(colecao)

    z_topo_grid = geometria.obter_grid_interpolado(
        pontos_x=xs,
        pontos_y=ys,
        valores_z=elevacoes,
        dx=dx,
        dy=dy,
        min_x=min_x,
        min_y=min_y,
        resolucao_grid=resolucao_grid,
        angulo_graus=angulo_graus,
        razao_anisotropia=razao_anisotropia,
        suavizacao=suavizacao,
    )

    grupos = defaultdict(list)
    for p in pocos:
        if (p["tem_profundidade"] or yolo) and p["formacao"] != "DESCONHECIDA":
            grupos[p["formacao"]].append(p)

    grids_contatos = {}
    for formacao, lista_pocos in grupos.items():
        num_pontos = len(lista_pocos)

        if num_pontos < 3 and not yolo:
            continue

        xf = np.array([p["x"] for p in lista_pocos])
        yf = np.array([p["y"] for p in lista_pocos])
        zf = np.array([p["cota_formacao"] for p in lista_pocos])

        z_contato_grid = geometria.obter_grid_interpolado(
            pontos_x=xf,
            pontos_y=yf,
            valores_z=zf,
            dx=dx,
            dy=dy,
            min_x=min_x,
            min_y=min_y,
            resolucao_grid=resolucao_grid,
            angulo_graus=angulo_graus,
            razao_anisotropia=razao_anisotropia,
            suavizacao=suavizacao,
        )

        grids_contatos[formacao] = z_contato_grid

    z_min_global = np.min(z_topo_grid)
    for grid in grids_contatos.values():
        z_min_global = min(z_min_global, np.min(grid))

    z_embasamento = z_min_global - (np.max(z_topo_grid) - z_min_global) * 0.2

    stack = [("Topografia", z_topo_grid)]

    for formacao_nome in ordem_estratigrafica:
        if formacao_nome in grids_contatos:
            stack.append((formacao_nome, grids_contatos[formacao_nome]))

    stack.append(
        ("Embasamento", np.full((resolucao_grid, resolucao_grid), z_embasamento))
    )

    # impede que a base de uma camada atravesse a camada superior
    for i in range(1, len(stack)):
        stack[i] = (stack[i][0], np.minimum(stack[i][1], stack[i - 1][1]))

    print(f"[INFO] Camadas: {[s[0] for s in stack]}")

    for i in range(len(stack) - 1):
        grid_superior = stack[i][1]
        grid_inferior = stack[i + 1][1]

        # Correção no nome para refletir a espessura da camada de cima até a de baixo
        nome_camada = stack[i][0]
        nome_proxima = stack[i + 1][0]
        idx = f"{i:02d}"
        nome_obj = f"{idx}_{nome_camada}_Ate_{nome_proxima}"

        cor = cores_formacoes.get(nome_camada, (0.5, 0.5, 0.5, 1.0))
        mat = criar_material(f"Mat_{nome_camada}", cor)

        print(
            f"[INFO] Criando camada: {nome_obj} (poços base: {len(grupos.get(nome_camada, []))})"
        )

        criar_solido_camada(
            nome_obj,
            grid_superior,
            grid_inferior,
            centro_x,
            centro_y,
            dx,
            dy,
            min_x,
            min_y,
            escala_z,
            mat,
            resolucao_grid,
            escala_xy,
            colecao,
        )

    print(f"[INFO] {len(stack)-1} camadas criadas")


# pipeline principal
def main(config=None):
    if config is None:
        raise ValueError("Configuração inválida.")

    try:
        repo_path = Path(config.get("repo_path"))
        input_file = config.get("input_file")

        print(f"[INFO] Iniciando modelagem")
        print(f"[INFO] Carregando: {repo_path / 'data' / 'processed' / input_file}")

        run(
            input_file=input_file,
            yolo=config.get("yolo", True),
            exagero_vertical=config.get("exagero_vertical", 100),
            resolucao_grid=config.get("resolucao_grid", 500),
            angulo_graus=config.get("angulo_graus", 0),
            razao_anisotropia=config.get("razao_anisotropia", 1.0),
            suavizacao=config.get("suavizacao", 0.1),
            ordem_estratigrafica=config.get("ordem_estratigrafica", []),
            cores_formacoes=config.get("cores_formacoes", {}),
            repo_path=repo_path,
            escala_xy=config.get("escala_xy", 1.0),
        )

        print("[INFO] Salvando modelo...")

        # gerando o caminho de saída com timestamp para evitar sobrescrita
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = (
            repo_path / "data" / f"{Path(input_file).stem}_{timestamp}.blend"
        )

        bpy.ops.wm.save_as_mainfile(filepath=str(output_path))
        print(f"[SUCESSO] Modelo salvo em: {output_path}")

    except Exception as e:
        print(f"[ERRO] {e}")
        sys.exit(1)
