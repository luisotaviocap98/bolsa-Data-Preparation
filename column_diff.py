import os
import pandas as pd
from datetime import datetime
import re
import unicodedata
import jellyfish as jf
from file_info import gerar_infos

def padronizar_string(texto):
    """
    Padroniza uma string, removendo caracteres indevidos e tornando-a minúscula.

    Args:
        texto (str): String a ser padronizada.

    Returns:
        str: String padronizada.
    """
    
    texto = texto.lower().strip() # Trasnformar para minúsculo e remover espaços no ínicio e fim
    texto = re.sub('[-_. ]','',texto) # Remover caracteres especiais e espaços internos
    texto_normalizado = unicodedata.normalize('NFKD', texto) # Normaliza o texto para separar acentos das letras
    texto = ''.join(c for c in texto_normalizado if not unicodedata.combining(c)) # Remove os caracteres que não são ASCII (ou seja, os acentos)
    
    return texto


def mapeamento_padronizacao(colunas_cabecalho):
    """
    Dicionário para mapear coluna original com a versão padronizada.

    Args:
        colunas (list): Lista de colunas a serem mapeadas.

    Returns:
        dict: Dicionário de mapeamento, a chave é a versão padronizada.
    """
    dicionario = {}
    lista_padronizada = []
    
    for c in colunas_cabecalho:
        padronizada = padronizar_string(c)
        dicionario[padronizada] = c
        lista_padronizada.append(padronizada)
        
    return dicionario, lista_padronizada


def colunas_candidatas(coluna_origem, colunas_destino, dicionario_equivalencia):
    """
    Encontrar as possíveis colunas candidatas à correspondência com a coluna desejada.

    Args:
        coluna_origem (str): Coluna a ser usada como referência.
        colunas_destino (list): Lista com as possíveis colunas candaditas.
        dicionario_equivalencia (dict): Dicionário para o nome original das colunas candidatas.

    Returns:
        str: String com todas as colunas candidatas.
    """
    candidatas = [] # Colunas candidatas
    tamanho = len(coluna_origem) # Tamanho da coluna original
    
    for c in colunas_destino:
        distancia = jf.levenshtein_distance(coluna_origem, c) # Calcular a distância entre as strings
        fonema_a = jf.metaphone(coluna_origem)
        fonema_b = jf.metaphone(c)
        
        if (distancia > 0 and distancia <= (tamanho/2)) or (fonema_a == fonema_b) or (coluna_origem in c) or (c in coluna_origem): # Só considera como candidato apenas caso a diferença seja de até metade da quantidade de caracteres
            candidatas.append(dicionario_equivalencia.get(c))
            
    return '/'.join(candidatas) if len(candidatas) else None # Transforma a lista em um string

def encontrar_arquivos_csv_xlsx(diretorio_inicial):
    """
    Encontra todos os arquivos CSV e XLSX em um diretório e seus subdiretórios.

    Args:
        diretorio_inicial (str): O caminho do diretório a ser pesquisado.

    Returns:
        list: Uma lista de caminhos completos para os arquivos encontrados.
    """
    
    arquivos = []
    
    try:
        for file in os.listdir(diretorio_inicial):
            if file.lower().endswith((".csv", ".xlsx", '.xls')) and not file.lower().startswith('comparacao_cabecalhos') and not file.lower().endswith('info.csv') and not file.lower().endswith('sample.csv'):
                arquivos.append(os.path.join(diretorio_inicial, file))
    except Exception:
        return arquivos
    
    return arquivos

def tentativa_leitura(path, sep=','):
    """
    Tenta ler as primeiras linhas de um arquivo CSV com um separador específico
    para inferir o cabeçalho.
    
    Para criar strings de diretórios use raw strings
    
    Para diretórios no Windows use: \\
        
    Para diretórios no Linux use: /

    Args:
        path (str): O caminho do arquivo CSV.
        sep (str): O separador a ser usado (padrão é ',').

    Returns:
        (pandas.DataFrame or None): Um DataFrame com as primeiras linhas (apenas para cabeçalho)
        ou None em caso de erro.
    """
    encodings_to_try = ['utf-8',  'latin1', 'latin2', 'cp1252','ascii']
    for codec in encodings_to_try:
        try:
            df = pd.read_csv(path, sep=sep, nrows=0, encoding=codec)
            gerar_infos(path, codec= codec, separador= sep)
            return df 
        except UnicodeDecodeError:
            continue
        except Exception:
            return None
    
    return None


def ler_cabecalho(arquivo):
    """
    Lê o cabeçalho de um arquivo CSV ou XLSX. Para CSV, tenta diferentes separadores.

    Args:
        arquivo (str): O caminho completo do arquivo.

    Returns:
        list or None: Uma lista de strings representando o cabeçalho do arquivo,
        ou None se o cabeçalho não puder ser lido.
    """
    
    try:
        if arquivo.lower().endswith(".csv"): # Ler CSV
            df = tentativa_leitura(arquivo)  # Tenta com separador padrão (,)

            if df is None or len(df.columns) <= 1:
                # Tenta com outros separadores se só uma coluna for detectada
                for sep in [';', '|', '\t']:
                    df_alt = tentativa_leitura(arquivo, sep=sep)
                    if df_alt is not None and len(df_alt.columns) > 1:
                        df = df_alt
                        break
                    
        elif arquivo.lower().endswith(".xlsx") or arquivo.lower().endswith(".xls"): #Ler Excel
            df = pd.read_excel(arquivo, nrows=0)
            gerar_infos(arquivo, csv=False)
                        
        else:
            return None
        
        return list(df.columns) if df is not None else None
    
    except Exception as e:
        return None

def comparar_cabecalhos(lista_arquivos):
    """
    Compara os cabeçalhos de todos os pares de arquivos na lista.

    Args:
        lista_arquivos (list): Uma lista de caminhos completos para os arquivos.

    Returns:
        list: Uma lista de dicionários, onde cada dicionário descreve a comparação
        entre dois arquivos (colunas presentes em ambos, somente em um, etc.).
    """
    
    resultados = [] # Resulto das diferenças
    num_arquivos = len(lista_arquivos)
    
    for i in range(num_arquivos):
        for j in range(i + 1, num_arquivos): # Começa de i + 1 para evitar comparações redundantes e consigo mesmo
            arquivo_a = lista_arquivos[i]
            arquivo_b = lista_arquivos[j]
            
            arquivo_a_nome = os.path.basename(arquivo_a)
            arquivo_b_nome = os.path.basename(arquivo_b)
            
            cabecalho_a = ler_cabecalho(arquivo_a)
            cabecalho_b = ler_cabecalho(arquivo_b)

            if cabecalho_a is None or cabecalho_b is None:
                continue
            
            # cabecalho_a_padronizado = [padronizar_string(s) for s in cabecalho_a] 
            # cabecalho_b_padronizado = [padronizar_string(s) for s in cabecalho_b] 
            
            # set_a = set(cabecalho_a)
            # set_b = set(cabecalho_b)
            
            dicionario_a, cabecalho_a_padronizado = mapeamento_padronizacao(cabecalho_a)
            dicionario_b, cabecalho_b_padronizado = mapeamento_padronizacao(cabecalho_b)

            set_a = set(cabecalho_a_padronizado)
            set_b = set(cabecalho_b_padronizado)
            
            colunas_em_ambos = set_a & set_b
            apenas_em_a = set_a - set_b
            apenas_em_b = set_b - set_a
            # colunas_diferentes = set_a ^ set_b
            
            for coluna in sorted(colunas_em_ambos):
                resultados.append({
                    'arquivo_1': arquivo_a_nome,
                    'arquivo_2': arquivo_b_nome,
                    'coluna': dicionario_a.get(coluna, ''),
                    'comparacao': 'presente em ambos arquivos',
                    'possiveis_candidatas': None
                })

            for coluna in sorted(apenas_em_a):
                resultados.append({
                    'arquivo_1': arquivo_a_nome,
                    'arquivo_2': arquivo_b_nome,
                    'coluna': dicionario_a.get(coluna, ''),
                    'comparacao': 'somente no arquivo_1',
                    'possiveis_candidatas': colunas_candidatas(coluna, apenas_em_b, dicionario_b)
                })

            for coluna in sorted(apenas_em_b):
                resultados.append({
                    'arquivo_1': arquivo_a_nome,
                    'arquivo_2': arquivo_b_nome,
                    'coluna': dicionario_b.get(coluna, ''),
                    'comparacao': 'somente no arquivo_2',
                    'possiveis_candidatas': colunas_candidatas(coluna, apenas_em_a, dicionario_a)
                })

    return resultados

def salvar_resultados_csv(resultados, nome_diretorio, output_dir):
    """
    Salva os resultados da comparação de cabeçalhos em um arquivo CSV.

    Args:
        resultados (list): A lista de dicionários com os resultados da comparação.
        nome_diretorio (str): O nome do diretório que foi analisado (usado para nomear o arquivo de saída).
        output_dir (str): O diretório onde o arquivo CSV será salvo. 
    """
    
    df_resultados = pd.DataFrame(resultados)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Garantir que o diretório de saída existe
    os.makedirs(output_dir, exist_ok=True)
    nome_arquivo = os.path.join(output_dir, f'comparacao_cabecalhos_{nome_diretorio}_{timestamp}.csv')
    df_resultados.to_csv(nome_arquivo, index=False)
    

def executar(diretorio='./', output_dir='./'):
    """
    Função principal para executar o processo de comparação de cabeçalhos.

    Args:
        diretorio (str, optional): O diretório inicial para procurar arquivos. Padrão é o diretório atual.
        output_dir (str, optional): O diretório onde o arquivo CSV de resultados será salvo. Padrão é o diretório atual.
    """
    
    nome_diretorio = os.path.basename(os.path.abspath(diretorio))
    # diretorio = input("Informe o diretório inicial: ")
    arquivos_encontrados = encontrar_arquivos_csv_xlsx(diretorio)
    
    if not arquivos_encontrados:
        return
    
    resultados_comparacao = comparar_cabecalhos(arquivos_encontrados)
    salvar_resultados_csv(resultados_comparacao, nome_diretorio, output_dir)

# Uso
if __name__ == "__main__":
    executar()
