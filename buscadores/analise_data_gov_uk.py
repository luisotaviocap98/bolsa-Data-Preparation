import pandas as pd
from urllib.parse import urlparse
import requests

df = pd.read_csv('./datasets_datagov_uk.csv',sep='|')

df = df[df.dataset_aberto == True]

df_valido = df[(df.recurso_formato.str.contains(r'csv|cvs|xls|zip|rar|comma|tsv|excel|gz|file|open data site', case=False, na=True)) | 
               (df.recurso_nome.str.contains(r'csv|cvs|xls|zip|rar|comma|tsv|excel|gz|file|open data site', case=False, na=True)) |
               (df.recurso_tipo.str.contains(r'csv|cvs|xls|zip|rar|comma|tsv|excel|gz|file|open data site', case=False, na=True))]

df_varios_dataset = df_valido[['dataset_nome','recurso_id']].groupby('dataset_nome')['recurso_id'].count().reset_index()
df_varios_dataset = df_varios_dataset[df_varios_dataset.recurso_id >= 2]
df_interesse = df_valido[df_valido.dataset_nome.isin(df_varios_dataset.dataset_nome)]

df_varios_dataset = df_interesse[['dataset_nome','recurso_id','recurso_nome','recurso_formato']].groupby(['dataset_nome','recurso_nome','recurso_formato'])['recurso_id'].count().reset_index()
df_varios_dataset = df_varios_dataset[df_varios_dataset.recurso_id < 2]
df_interesse = df_interesse[df_interesse.dataset_nome.isin(df_varios_dataset.dataset_nome)]

df_filtrado = df_interesse.groupby("dataset_nome").filter(lambda g: g["recurso_url"].notna().any())
df_filtrado = df_filtrado[['dataset_nome','dataset_obs','dataset_titulo','recurso_descricao','recurso_id','recurso_nome','recurso_tipo','recurso_url']]

def normalize_and_fix_url(url: str, default_scheme: str = "https") -> str | None:
    """
    Normaliza uma URL:
    - Se for NaN ou string vazia, retorna None
    - Se não tiver esquema (http/https), adiciona
    - Se não for URL válida (sem domínio), retorna None
    """
    if pd.isna(url) or not isinstance(url, str):
        return None

    s = url.strip()
    if s == "":
        return None

    # Se começar com // → adiciona esquema
    if s.startswith("//"):
        s = f"{default_scheme}:{s}"

    # Se não tiver esquema, adiciona
    parsed = urlparse(s)
    if not parsed.scheme:
        s = f"{default_scheme}://{s}"
        parsed = urlparse(s)

    # Se não tem domínio → não é URL válida
    if not parsed.netloc:
        return None

    return s

# df_filtrado["recurso_url"] = df_filtrado["recurso_url"].apply(normalize_and_fix_url)

# session = requests.Session()

# def url_valida(url: str) -> int:
#     if pd.isna(url) or url.strip() == "":  # Se for NaN, já retorna False (ou None se preferir)
#         return 0
#     try:
#         r = session.head(url, allow_redirects=True, timeout=5)
#         return 1 if r.status_code < 400 else 0
#     except requests.RequestException:
#         return 0
    
# df_filtrado["url_valida"] = df_filtrado["recurso_url"].apply(url_valida)
# session.close()

# df_varios_dataset = df_filtrado[['dataset_nome','recurso_url']].groupby('dataset_nome')['recurso_url'].sum().reset_index()
# df_varios_dataset = df_varios_dataset[df_varios_dataset.recurso_url > 0]
# df_filtrado = df_filtrado[df_filtrado.dataset_nome.isin(df_varios_dataset.dataset_nome)]

df_filtrado["dataset_obs"] = df_filtrado["dataset_obs"].str.replace(";", ",", regex=False)

df_filtrado[['dataset_nome','dataset_titulo','dataset_obs']].drop_duplicates().to_csv('./lista_dataset_datagov_uk.csv',sep=';', index=False)
