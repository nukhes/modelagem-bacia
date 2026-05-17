import pandas as pd
import rasterio
from pyproj import Transformer

"""
Este script realiza a extração de elevação de um modelo digital (GTOPO30 HYDRO1k South America, ver fonte em 'data/FONTES.md') para coordenadas geográficas. A abordagem emprega tratamento defensivo para higienizar coordenadas e reprojeção espacial dinâmica (de EPSG:4326 para o CRS projetado nativo do raster), garantindo a precisão posicional sem a necessidade de arquivos intermediários. O fluxo executa a ingestão e sanitização tabular, leitura de metadados do raster, conversão dos eixos para o plano cartesiano correspondente, amostragem em lote dos valores dos pixels e persistência do dataset atualizado.
"""

file = "data/processed/20260503_pocos_parana.csv"
raster_path = "data/raw/gt30h1ksa/sa_dem.bil"

df = pd.read_csv(file)

df["LONGITUDE_BASE_DD"] = pd.to_numeric(
    df["LONGITUDE_BASE_DD"].astype(str).str.replace(",", "."), errors="coerce"
)
df["LATITUDE_BASE_DD"] = pd.to_numeric(
    df["LATITUDE_BASE_DD"].astype(str).str.replace(",", "."), errors="coerce"
)

df = df.dropna(subset=["LONGITUDE_BASE_DD", "LATITUDE_BASE_DD"])

with rasterio.open(raster_path) as src:
    raster_crs = src.crs
    transformer = Transformer.from_crs("EPSG:4326", raster_crs, always_xy=True)

    x_proj, y_proj = transformer.transform(
        df["LONGITUDE_BASE_DD"].values, df["LATITUDE_BASE_DD"].values
    )

    coords_proj = zip(x_proj, y_proj)
    amostras = list(src.sample(coords_proj))

    df["ELEVACAO"] = [val[0] for val in amostras]

df.to_csv(file, index=False)
