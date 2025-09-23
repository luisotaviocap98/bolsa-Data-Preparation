import requests
import pandas as pd
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

headers = {
    'accept': 'application/json'
}

# Configure session with retry strategy
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

url_lista = 'https://data.gov.uk/api/action/package_list'

lista_dataset =[]

resposta_lista = session.get(url_lista, headers=headers, timeout=10)

if resposta_lista.status_code == 200:

    registros = resposta_lista.json()

    if registros.get('result'):

        datasets = registros.get('result')

        for r in datasets:
            id = r
            
            url_package = f'https://data.gov.uk/api/action/package_show?id={id}'
            try:
                resposta_package = session.get(url_package, headers=headers, timeout=10)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {id}: {e}")
                continue
            
            if resposta_package.status_code != 200:
                continue

            package = resposta_package.json()
            
            if not package or not package.get('result'):
                continue

            p = package.get('result')
            
            if not p.get('resources'):
                continue
            
            for f in p.get('resources'):
                dicionario = {
                    'dataset_aberto':p.get('isopen',''),
                    'dataset_nome':p.get('name',''),
                    'dataset_obs':p.get('notes',''),
                    'dataset_data_start':p.get('temporal_coverage-from',''),
                    'dataset_data_end':p.get('temporal_coverage-to',''),
                    'dataset_titulo':p.get('title',''),
                    'dataset_tipo':p.get('type',''),
                    'recurso_data_criado':f.get('created',''),
                    'recurso_data':f.get('date',''),
                    'recurso_descricao':f.get('description',''),
                    'recurso_formato':f.get('format',''),
                    'recurso_id':f.get('id',''),
                    'recurso_nome':f.get('name',''),
                    'recurso_tipo':f.get('resource_type',''),
                    'recurso_url':f.get('url','')
                }
                
                lista_dataset.append(dicionario)
            
            time.sleep(0.1)

    
df = pd.DataFrame(lista_dataset)
df.to_csv('C:/Users/user/Desktop/bolsa estudo/datasets/novo/datasets_datagov_uk.csv', index=False, encoding='utf-8',sep='|')