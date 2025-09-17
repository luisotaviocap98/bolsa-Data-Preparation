import zipfile
import pandas as pd
from pathlib import Path
import regex
import unicodedata
from concurrent.futures import ProcessPoolExecutor  # Import para paralelização

diretorio = '.'

candidatos = f'{diretorio}/candidatos_match.csv'

df = pd.read_csv(candidatos)

zips = [{'pais':'USA',
         'arq':'datasets_USA.zip'},
        {'pais':'CAN',
         'arq':'datasets_CAN.zip'},
        {'pais':'UK',
         'arq':'datasets_UK.zip'}]

# Cache para padronização de colunas
coluna_cache = {}

def padronizar_coluna(colunas_cabecalho):
    global coluna_cache
    colunas_str = tuple(colunas_cabecalho)  # Converter para tupla para usar como chave
    if colunas_str in coluna_cache:
        return coluna_cache[colunas_str]
    
    lista_padronizada = []
    
    for texto in colunas_cabecalho:
        
        texto = texto.lower().strip() # Trasnformar para minúsculo e remover espaços no ínicio e fim
        texto = ''.join(regex.findall(r'[a-zA-ZÀ-ÿ0-9]', texto)) # Remover caracteres especiais e espaços internos
        texto_normalizado = unicodedata.normalize('NFKD', texto) # Normaliza o texto para separar acentos das letras
        texto = ''.join(c for c in texto_normalizado if not unicodedata.combining(c)) # Remove os caracteres que não são ASCII (ou seja, os acentos)
        
        lista_padronizada.append(texto)
    
    coluna_cache[colunas_str] = set(lista_padronizada)
    return set(lista_padronizada)

def comparar_arquivos(source, compare):
    source_p = padronizar_coluna(source)
    compare_p = padronizar_coluna(compare)
    
    colunas_em_ambos = source_p & compare_p
    colunas_diferentes = source_p ^ compare_p
    
    return (colunas_em_ambos, colunas_diferentes)

def processar_zip(z, df, diretorio):
    arquivo = z['arq']
    caminho = f'{diretorio}/{arquivo}'
    matchs = []
    try:
        with zipfile.ZipFile(caminho) as archive:
            # Criar um índice de nomes de arquivos CSV
            csv_files = {Path(filename).stem + Path(filename).suffix: filename
                         for filename in archive.namelist() if Path(filename).suffix == '.csv'}
            
            for i,r in df[df.country == z['pais']].iterrows():
                df_source = None
                df_compare = None
                file_source = None
                file_compare = None
                
                # Acessar os arquivos diretamente pelo índice
                file_source_name = r['source']
                file_compare_name = r['compare']
                
                if file_source_name in csv_files:
                    filename = csv_files[file_source_name]
                    with archive.open(filename)  as f:
                        df_source = pd.read_csv(f,low_memory=False,nrows=3)
                        if df_source.empty:
                            continue
                        df_source = list(df_source.columns)
                        file_source = file_source_name
                
                if file_compare_name in csv_files:
                    filename = csv_files[file_compare_name]
                    with archive.open(filename)  as f:
                        df_compare = pd.read_csv(f,low_memory=False,nrows=3)
                        if df_compare.empty:
                            continue
                        df_compare = list(df_compare.columns)
                        file_compare = file_compare_name
                
                if df_compare != None and df_source != None:
                    igual, diferente = comparar_arquivos(df_source, df_compare)
                    for i in igual:
                        matchs.append(
                            {
                                'source':file_source,
                                'compare':file_compare,
                                'coluna':i,
                                'tipo':'match'
                            }
                        )
                    for d in diferente:
                        matchs.append(
                            {
                                'source':file_source,
                                'compare':file_compare,
                                'coluna':d,
                                'tipo':'diferente'
                            }
                        )
                        
    except zipfile.BadZipFile as error:
        print('error',error)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{arquivo}' não encontrado no diretório '{diretorio}'.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    return matchs

# Paralelizar o processamento dos arquivos ZIP
if __name__ == '__main__':
    matchs = []
    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(processar_zip, zip_info, df, diretorio)
            for zip_info in zips
        ]
        
        for future in futures:
            try:
                result = future.result(timeout=300)  # timeout de 5 minutos
                matchs.extend(result)
            except TimeoutError:
                print("Timeout ao processar arquivo - execução excedeu 5 minutos")
                continue
            except Exception as e:
                print(f"Erro ao processar arquivo: {e}")
                continue
        
    if len(matchs) > 0:
        df = pd.DataFrame(matchs)
        df.to_csv('./gabarito_lakebench.csv', index=False)