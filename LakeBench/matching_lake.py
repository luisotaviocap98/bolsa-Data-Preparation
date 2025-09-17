import zipfile
import pandas as pd
from pathlib import Path
import regex
import unicodedata
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from dataclasses import dataclass
from typing import List, Dict, Set, Optional
import sys

@dataclass
class ArquivoZip:
    pais: str
    arquivo: str

@dataclass
class Match:
    source: str
    compare: str
    col_iguais: int
    col_diferentes: int
    col_dificuldade : float

class ProcessadorColunas:
    def __init__(self):
        self.cache = {}

    def padronizar_coluna(self, colunas: List[str]) -> Set[str]:
        colunas_str = tuple(colunas)
        if colunas_str in self.cache:
            return self.cache[colunas_str]

        lista_padronizada = []
        for texto in colunas:
            texto = self._processar_texto(texto)
            lista_padronizada.append(texto)

        self.cache[colunas_str] = set(lista_padronizada)
        return self.cache[colunas_str]

    def _processar_texto(self, texto: str) -> str:
        texto = texto.lower().strip()
        texto = ''.join(regex.findall(r'[a-zA-ZÀ-ÿ0-9]', texto))
        texto_normalizado = unicodedata.normalize('NFKD', texto)
        return ''.join(c for c in texto_normalizado if not unicodedata.combining(c))

class ComparadorArquivos:
    def __init__(self):
        self.processador = ProcessadorColunas()

    def comparar(self, source: List[str], compare: List[str]) -> tuple:
        source_p = self.processador.padronizar_coluna(source)
        compare_p = self.processador.padronizar_coluna(compare)
        
        colunas_em_ambos = source_p & compare_p
        colunas_diferentes = source_p ^ compare_p
        
        check = len(colunas_diferentes) > 0 and len(colunas_em_ambos) > 0
        
        increase = colunas_em_ambos == source_p or colunas_em_ambos == compare_p
        
        percent = len(colunas_diferentes) / (len(colunas_em_ambos) + len(colunas_diferentes))
        
        return (check and not increase, len(colunas_em_ambos), len(colunas_diferentes), percent)
    
class ProcessadorZip:
    def __init__(self, diretorio: Path):
        self.diretorio = diretorio
        self.comparador = ComparadorArquivos()

    def processar_arquivo(self, zip_info: ArquivoZip, df_comparacao: pd.DataFrame) -> List[Match]:
        caminho = self.diretorio / zip_info.arquivo
        matchs = []

        try:
            with zipfile.ZipFile(caminho) as archive:
                csv_files = self._criar_indice_csv(archive)
                matchs.extend(self._processar_comparacoes(archive, csv_files, df_comparacao, zip_info.pais))
        except zipfile.BadZipFile as error:
            print('error:', error)
        except FileNotFoundError:
            print(f"Erro: Arquivo '{zip_info.arquivo}' não encontrado no diretório '{str(self.diretorio)}'.")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")

        return matchs

    def _criar_indice_csv(self, archive: zipfile.ZipFile) -> Dict[str, str]:
        return {Path(filename).stem + Path(filename).suffix: filename
                for filename in archive.namelist() if Path(filename).suffix == '.csv'}

    def _processar_comparacoes(self, archive: zipfile.ZipFile, csv_files: Dict[str, str], 
                             df_comparacao: pd.DataFrame, pais: str) -> List[Match]:
        matchs = []
        for _, row in df_comparacao[df_comparacao.country == pais].iterrows():
            source_cols = self._ler_colunas_csv(archive, csv_files, row['query_table'])
            compare_cols = self._ler_colunas_csv(archive, csv_files, row['candidate_table'])
            
            if source_cols and compare_cols:
                check, iguais, diferentes, percentual =  self.comparador.comparar(source_cols, compare_cols)
                if check:
                    matchs.append(Match(
                        source=row['query_table'],
                        compare=row['candidate_table'],
                        col_iguais = iguais,
                        col_diferentes = diferentes,
                        col_dificuldade = percentual
                    ))
        return matchs

    def _ler_colunas_csv(self, archive: zipfile.ZipFile, csv_files: Dict[str, str], 
                        nome_arquivo: str) -> Optional[List[str]]:
        if nome_arquivo not in csv_files:
            return None
        
        with archive.open(csv_files[nome_arquivo]) as f:
            df = pd.read_csv(f, nrows=0)
            return list(df.columns)

def carregar_dados(diretorio: Path) -> pd.DataFrame:
    df_union = pd.read_csv(diretorio / 'opendata_union_ground_truth.csv')
    df_union['country'] = df_union['query_table'].str.split('_', n=1).str[0]

    df_join = pd.read_csv(
        diretorio / 'opendata_join_ground_truth.csv',
        usecols=['query_table', 'candidate_table']
    )
    df_join['country'] = df_join['query_table'].str.split('_', n=1).str[0]

    return pd.concat([df_join, df_union], ignore_index=True).drop_duplicates()

def main():
    try:
        diretorio = Path('.')
        
        zips = [
            ArquivoZip('USA', 'datasets_USA.zip'),
            ArquivoZip('CAN', 'datasets_CAN.zip'),
            ArquivoZip('UK', 'datasets_UK.zip')
        ]

        print("Iniciando processamento...")
        df_comparacao = carregar_dados(diretorio)
        processador = ProcessadorZip(diretorio)
        
        matchs = []
        with ProcessPoolExecutor() as executor:
            futures = [
                executor.submit(processador.processar_arquivo, zip_info, df_comparacao)
                for zip_info in zips
            ]
            
            for future in futures:
                try:
                    result = future.result(timeout=300)
                    matchs.extend(result)
                except TimeoutError:
                    print("Timeout ao processar arquivo")
                    continue
                except Exception as e:
                    print(f"Erro ao processar arquivo: {e}")
                    continue

        print("Finalizando processamento...")
        
        if matchs:
            df_resultados = pd.DataFrame([vars(match) for match in matchs])
            df_resultados.to_csv(diretorio / 'matching_lakebench.csv', index=False)
            print(f"Processamento concluído. {len(matchs)} matches encontrados.")
        else:
            print("Nenhum match encontrado.")
            
    except Exception as e:
        print(f"Erro durante a execução: {e}")
    finally:
        print("Programa finalizado.")
        
if __name__ == '__main__':
    main()
    # Força o flush do buffer de saída
    
    sys.stdout.flush()