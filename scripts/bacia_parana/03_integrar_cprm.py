from pathlib import Path
import geopandas as gpd
import pandas as pd

REPO_ROOT = Path("/home/user/src/modelagem-bacia")
ARQUIVO_SHP = (
    REPO_ROOT
    / "data"
    / "raw"
    / "bacia_do_parana"
    / "Litologia"
    / "bacia_do_parana_lito.shp"
)
CSV_ORIGINAL = REPO_ROOT / "data" / "processed" / "20260503_pocos_parana.csv"
CSV_DESTINO = REPO_ROOT / "data" / "processed" / "20260503_pocos_parana_final.csv"


def integrar_geologia_cprm():
    print("[PRE-PROCESSAMENTO] Carregando poços originais...")
    df_pocos = pd.read_csv(CSV_ORIGINAL)

    print("[PRE-PROCESSAMENTO] Convertendo poços para GeoDataFrame.")

    gdf_pocos = gpd.GeoDataFrame(
        df_pocos,
        geometry=gpd.points_from_xy(
            df_pocos["LONGITUDE_BASE_DD"], df_pocos["LATITUDE_BASE_DD"]
        ),
        crs="EPSG:4326",
    )

    print(f"[PRE-PROCESSAMENTO] Carregando Shapefile da CPRM: {ARQUIVO_SHP.name}")
    gdf_mapa = gpd.read_file(ARQUIVO_SHP)

    if gdf_mapa.crs != gdf_pocos.crs:
        print(f"Reprojetando mapa de {gdf_mapa.crs} para EPSG:4326...")
        gdf_mapa = gdf_mapa.to_crs("EPSG:4326")

    print("Realizando o Cruzamento Espacial (Spatial Join)...")
    pocos_cruzados = gpd.sjoin(gdf_pocos, gdf_mapa, how="left", predicate="intersects")

    df_pocos["GEOLOGIA_FORMACAO_FINAL"] = pocos_cruzados["NOME_UNIDA"]

    CSV_DESTINO.parent.mkdir(parents=True, exist_ok=True)

    df_pocos.to_csv(CSV_DESTINO, index=False)
    print(f"[SUCESSO] Arquivo pronto para o modelador em: {CSV_DESTINO}")


if __name__ == "__main__":
    integrar_geologia_cprm()
