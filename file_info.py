import pandas as pd
import os
import re

def valores_combinam(serie, pattern):
    return all(re.fullmatch(pattern, v.strip()) for v in serie)

def parece_data(serie):
    if not valores_combinam(serie, r"[0-9/\-]+"): # Verificar se a coluna contém apenas números e / ou -
        return False
    convertidos = pd.to_datetime(serie, format='%d/%m/%Y', errors='coerce')
    return convertidos.notna().all()

def parece_hora(serie):
    if not valores_combinam(serie, r"[0-9:]+"): # Verficiar se a coluna contém apenas números e :
        return False
    convertidos = pd.to_timedelta(serie, errors='coerce')
    return convertidos.notna().all()

def gerar_infos(caminho, codec=None, separador=None, csv = True):
    diretorio = os.path.dirname(caminho) # Obter diretorio do arquivo
    arquivo = os.path.splitext(os.path.basename(caminho))[0] # Obter nome do arquivo
    
    if csv:
        df = pd.read_csv(caminho, nrows=1000, encoding=codec, sep=separador) # Ler CSV
    else:
        df = pd.read_excel(caminho, nrows=1000) # Ler excel
        
    df_info = df.dtypes.to_frame().reset_index().rename(columns={'index':'Coluna'}) # Obter os tipos de dados
    
    column_type = {
        'object':'String',
        'int64':'Inteiro',
        'float64':'Float',  
        'bool':'Booleano',
        'datetime64':'Data/hora',
        'category':'Categorico'
    }
    
    os.makedirs(diretorio, exist_ok=True)
    
    nome_arquivo = os.path.join(diretorio, f'{arquivo}_info.csv')
    df_info['Tipo'] = df_info[0].astype(str).map(column_type).fillna('Indefinido') # Criar nova coluna mapeando os tipos de dados 
    
    for i, row in df_info.iterrows():
        if row['Tipo'] == 'String':
            colname = row['Coluna']
            serie = df[colname].dropna().astype(str).head(100)

            if parece_data(serie):
                df_info.at[i, 'Tipo'] = 'Data' # Identficar formato de data
            elif parece_hora(serie):
                df_info.at[i, 'Tipo'] = 'Hora' # Identficar formato de timestamp

    
    df_info[['Coluna','Tipo']].to_csv(nome_arquivo,index=False) # Salvar as informações de tipos de dados

    nome_arquivo = os.path.join(diretorio, f'{arquivo}_sample.csv')
    df.sample(n=min(100, int(len(df)/2)), random_state=42).to_csv(nome_arquivo,index=False) # Gerar um sample do arquivo original
    