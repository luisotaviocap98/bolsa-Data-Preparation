import requests
import pandas as pd
import time
from datetime import datetime

inicio = datetime.now()

# Cabeçalhos da API
headers = {
    'accept': 'application/json',
    'chave-api-dados-abertos': ''
}

# lista com todos datasets
dados_extraidos = []

# Início da contagem de páginas
pagina = 1  

print('Iniciando')

while True:
    # print(f"Processando página {pagina}...")
    # 667 pgs ; 15 registros

    # url pra listar todos datasets
    url_lista = f'https://dados.gov.br/dados/api/publico/conjuntos-dados?dadosAbertos=true&isPrivado=false&pagina={pagina}'
    resposta_lista = requests.get(url_lista, headers=headers)

    if resposta_lista.status_code != 200:
        print(f"Erro ao acessar página {pagina}: {resposta_lista.status_code}")
        break

    registros = resposta_lista.json()

    # Parar o loop se não houver mais registros
    if not registros:
        print("Fim da extração.")
        break
        
    # acessar cada dataset    
    for item in registros:
        
        # pular dados descontinuados
        title = item.get('title', '')
        if 'descontinuado' in title.lower():
            continue
        
        # obter id do dataset
        id_registro = item.get('id')
        if not id_registro:
            continue
        
        # url com mais informações do dataset
        url_detalhe = f'https://dados.gov.br/dados/api/publico/conjuntos-dados/{id_registro}'
        resposta_detalhe = requests.get(url_detalhe, headers=headers)

        if resposta_detalhe.status_code != 200:
            print(f"Erro ao acessar detalhes do ID {id_registro}: {resposta_detalhe.status_code}")
            continue

        detalhe = resposta_detalhe.json()
        
        # dicionario para armazenar as informações de um dataset
        dados = {
                    'id': detalhe.get('id',''),
                    'titulo': detalhe.get('titulo',''),
                    'periodicidade': detalhe.get('periodicidade',''),
                    'visibilidade': detalhe.get('visibilidade',''),
                    'descontinuado': detalhe.get('descontinuado',''),
                    'link':  None,
                    'formato': None,
                    'tamanho': None,
                    'nomeRecurso': None,
                    'dataCadatroRecurso': None,
                    'lastUpdateRecurso': None,
                    'dataUltimaAtualizacaoMetadados': detalhe.get('dataUltimaAtualizacaoMetadados',''),
                    'dataUltimaAtualizacaoArquivo': detalhe.get('dataUltimaAtualizacaoArquivo',''),
                    'atualizado': detalhe.get('atualizado',''),
                }

        # obter informações dos recursos (arquivos de dados)
        if detalhe.get('recursos'):

            for r in detalhe.get('recursos'):                
                dados['link'] = r.get('link','') 
                dados['formato'] = r.get('formato','') 
                dados['tamanho'] = r.get('tamanho','') 
                dados['nomeRecurso'] = r.get('titulo','') 
                dados['dataCadatroRecurso'] = r.get('dataCatalogacao','') 
                dados['lastUpdateRecurso'] = r.get('dataUltimaAtualizacaoArquivo','') 

                dados_extraidos.append(dados.copy())
        else:
            dados_extraidos.append(dados.copy())
            
        time.sleep(0.5)  # Delay para não sobrecarregar a API

    pagina += 1  # Avança para a próxima página

# Gera DataFrame e salva em CSV
df = pd.DataFrame(dados_extraidos)
df.to_csv('C:/Users/user/Desktop/bolsa estudo/dados_conjuntos.csv', index=False, encoding='utf-8')

final = datetime.now()  

print("✅ Arquivo CSV gerado com sucesso: dados_conjuntos.csv , tempo:", str(final - inicio))
