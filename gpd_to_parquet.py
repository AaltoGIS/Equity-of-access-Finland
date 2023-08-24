import geopandas as gpd
grid = gpd.read_file('streamlit/data/suomi.gpkg', encoding='utf-8')

grid.to_parquet('streamlit/data/suomi.parquet')