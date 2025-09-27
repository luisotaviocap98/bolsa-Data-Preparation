import requests
import pandas as pd
import time

headers = {
    'accept': 'application/json'
}

url_datasets = 'https://catalog.data.gov/api/3/action/package_list?rows=1000'

session = requests.Session()
session.headers.update(headers)

lista_dataset =[]

for i in range(0, 363):
    url_lista = f'{url_datasets}&start={i*1000}'
    
    try:
        response = session.get(url_lista, timeout=30)
        response.raise_for_status()
        registros = response.json().get('result', {}).get('results', [])
    except:
        continue

    if not registros:
        continue
    
    
    for r in registros:
        resources = r.get('resources')
        if not resources:
            continue
        
        # Cache valores reutilizados
        id = r.get('id', '')
        qtd_arquivos = len(resources)
        privado = r.get('private','')
        tipo = r.get('type','')
        nome = r.get('name', '')
        titulo = r.get('title','')
        descricao = r.get('notes','')
        url = f'https://catalog.data.gov/dataset/{r.get('name','')}'
        extras = r.get('extras', [])
        nivel_acesso = next((item["value"] for item in extras if item["key"] == "accessLevel"), None)
        
        for f in resources:
            lista_dataset.append({
                'dataset_id':id,
                'qtd_arquivos':qtd_arquivos,
                'privado':privado,
                'tipo':tipo,
                'nome':nome,
                'titulo':titulo,
                'descricao':descricao,
                'url':url,
                'nivel_acesso':nivel_acesso,
                'formato_arquivo':f.get('format') or f.get('mimetype', ''),
                'id_arquivo':f.get('id',''),
                'url_arquivo':f.get('url','')
            })
            
        
    time.sleep(0.05)
    
df = pd.DataFrame(lista_dataset)
df.to_csv('C:/Users/user/Desktop/bolsa estudo/datasets_datagov_eua.csv', index=False, encoding='utf-8',sep='|')