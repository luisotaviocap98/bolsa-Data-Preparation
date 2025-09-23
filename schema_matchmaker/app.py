import streamlit as st
import os
import pandas as pd
import numpy as np # Para calcular perfis numéricos


# --- Funções Auxiliares para a Página de Configuração (mantidas e aprimoradas) ---

def get_file_type(filename):
    if filename:
        ext = os.path.splitext(filename)[1].lower()
        if ext in ['.xls', '.xlsx', '.ods']:
            return 'excel_ods'
        elif ext in ['.csv', '.tsv']:
            return 'csv_tsv'
    return None

def display_file_config(file_info, dataset_name, file_path_saved, unique_key_prefix):
    if file_info is None:
        st.info(f"Nenhum arquivo carregado para {dataset_name}.")
        return None, None # Retorna None para o dataframe e as configs

    st.subheader(f"Configurações para {dataset_name} ({file_info.name})")

    file_type = get_file_type(file_info.name)
    configs = {}
    df = None # DataFrame resultante da leitura

    # Garante que os valores padrão para configs estejam no session_state para persistência
    if f"{unique_key_prefix}_configs" not in st.session_state:
        st.session_state[f"{unique_key_prefix}_configs"] = {}

    current_configs = st.session_state[f"{unique_key_prefix}_configs"]

    if file_type == 'excel_ods':
        st.write("Configurações para Excel ou Open Document Spreadsheet:")

        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        configs['encoding'] = st.selectbox(
            f"Encoding para {dataset_name}",
            encodings,
            index=encodings.index(current_configs.get('encoding', 'utf-8')) if current_configs.get('encoding') in encodings else 0,
            key=f"{unique_key_prefix}_encoding_{dataset_name}"
        )

        sheet_names = []
        try:
            if file_path_saved and os.path.exists(file_path_saved):
                excel_file = pd.ExcelFile(file_path_saved, engine='openpyxl' if file_info.name.endswith('.xlsx') or file_info.name.endswith('.xls') else 'odf')
                sheet_names = excel_file.sheet_names
            else:
                st.warning(f"Arquivo temporário para {dataset_name} não encontrado. Por favor, recarregue na página principal.")
        except Exception as e:
            st.error(f"Erro ao ler abas para {dataset_name}: {e}")

        if sheet_names:
            default_sheet_idx = 0
            if current_configs.get('sheet_name') in sheet_names:
                default_sheet_idx = sheet_names.index(current_configs['sheet_name'])

            configs['sheet_name'] = st.selectbox(
                f"Selecione a aba (sheet) para {dataset_name}",
                sheet_names,
                index=default_sheet_idx,
                key=f"{unique_key_prefix}_sheet_{dataset_name}"
            )
        else:
            configs['sheet_name'] = None
            st.warning("Nenhuma aba disponível para seleção.")

        configs['skiprows'] = st.number_input(
            f"Ignorar X primeiras linhas para {dataset_name}",
            min_value=0,
            value=current_configs.get('skiprows', 0),
            step=1,
            key=f"{unique_key_prefix}_skiprows_{dataset_name}"
        )

        if st.button(f"Pré-visualizar {dataset_name}", key=f"{unique_key_prefix}_preview_excel_{dataset_name}"):
            if file_path_saved and os.path.exists(file_path_saved) and configs['sheet_name'] is not None:
                try:
                    df = pd.read_excel(
                        file_path_saved,
                        sheet_name=configs['sheet_name'],
                        skiprows=configs['skiprows'],
                        engine='openpyxl' if file_info.name.endswith('.xlsx') or file_info.name.endswith('.xls') else 'odf'
                    )
                    st.success(f"Dataset {dataset_name} carregado com sucesso!")
                    st.dataframe(df.head())
                    st.session_state[f"df_{unique_key_prefix}"] = df
                    st.session_state[f"{unique_key_prefix}_configs"] = configs
                except Exception as e:
                    st.error(f"Erro ao carregar Excel/ODS para {dataset_name}: {e}")
            else:
                st.warning("Por favor, carregue o arquivo e selecione uma aba válida.")

    elif file_type == 'csv_tsv':
        st.write("Configurações para CSV ou TSV:")

        separators = [',', ';', '\t', '|', 'Outro']
        default_sep_idx = 0
        if current_configs.get('sep') in separators:
            default_sep_idx = separators.index(current_configs['sep'])
        elif current_configs.get('sep') not in separators and current_configs.get('sep') is not None:
             default_sep_idx = separators.index('Outro')

        selected_separator = st.selectbox(
            f"Selecione o separador para {dataset_name}",
            separators,
            index=default_sep_idx,
            key=f"{unique_key_prefix}_separator_{dataset_name}"
        )
        if selected_separator == 'Outro':
            configs['sep'] = st.text_input(f"Digite o separador personalizado para {dataset_name}",
                                         value=current_configs.get('sep', '') if current_configs.get('sep') not in separators else '',
                                         key=f"{unique_key_prefix}_custom_sep_{dataset_name}")
        else:
            configs['sep'] = selected_separator

        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'ascii']
        configs['encoding'] = st.selectbox(
            f"Encoding para {dataset_name}",
            encodings,
            index=encodings.index(current_configs.get('encoding', 'utf-8')) if current_configs.get('encoding') in encodings else 0,
            key=f"{unique_key_prefix}_encoding_{dataset_name}"
        )

        quotes = ['"', "'", 'Nenhum', 'Outro']
        default_quote_idx = 0
        if current_configs.get('quotechar') in quotes:
            default_quote_idx = quotes.index(current_configs['quotechar'])
        elif current_configs.get('quotechar') not in quotes and current_configs.get('quotechar') is not None:
            default_quote_idx = quotes.index('Outro')

        selected_quotechar = st.selectbox(
            f"Símbolo para aspas para {dataset_name}",
            quotes,
            index=default_quote_idx,
            key=f"{unique_key_prefix}_quotechar_{dataset_name}"
        )
        if selected_quotechar == 'Nenhum':
            configs['quotechar'] = None
        elif selected_quotechar == 'Outro':
            configs['quotechar'] = st.text_input(f"Digite o símbolo de aspas personalizado para {dataset_name}",
                                               value=current_configs.get('quotechar', '') if current_configs.get('quotechar') not in quotes else '',
                                               max_chars=1,
                                               key=f"{unique_key_prefix}_custom_quotechar_{dataset_name}")
        else:
            configs['quotechar'] = selected_quotechar

        configs['skiprows'] = st.number_input(
            f"Ignorar X primeiras linhas para {dataset_name}",
            min_value=0,
            value=current_configs.get('skiprows', 0),
            step=1,
            key=f"{unique_key_prefix}_skiprows_{dataset_name}"
        )

        if st.button(f"Pré-visualizar {dataset_name}", key=f"{unique_key_prefix}_preview_csv_{dataset_name}"):
            if file_path_saved and os.path.exists(file_path_saved):
                try:
                    df = pd.read_csv(
                        file_path_saved,
                        sep=configs['sep'],
                        encoding=configs['encoding'],
                        quotechar=configs['quotechar'],
                        skiprows=configs['skiprows']
                    )
                    st.success(f"Dataset {dataset_name} carregado com sucesso!")
                    st.dataframe(df.head())
                    st.session_state[f"df_{unique_key_prefix}"] = df
                    st.session_state[f"{unique_key_prefix}_configs"] = configs
                except Exception as e:
                    st.error(f"Erro ao carregar CSV/TSV para {dataset_name}: {e}")
            else:
                st.warning("Por favor, carregue o arquivo.")

    else:
        st.warning(f"Formato de arquivo não reconhecido ou arquivo não carregado para {dataset_name}.")
        return None, None

    st.markdown("---")
    return df, configs

# --- Geração de Perfil de Colunas ---
def generate_column_profile(df, column_name):
    """Gera um perfil detalhado para uma coluna específica do DataFrame."""
    if df is None or column_name not in df.columns or column_name == '':
        return "Coluna não encontrada ou DataFrame vazio."

    series = df[column_name]
    profile = {}

    profile['Tipo de Dado'] = str(series.dtype)
    profile['Valores Únicos'] = series.nunique()
    profile['Valores Faltantes'] = series.isnull().sum()
    # profile['% Faltantes'] = f"{(series.isnull().sum() / len(series) * 100):.2f}%"
    profile['Valores Duplicados'] = series.duplicated().sum()

    # Perfil para tipos numéricos
    if pd.api.types.is_numeric_dtype(series):
        try:
            profile['Mínimo'] = series.min()
            profile['Máximo'] = series.max()
            profile['Média'] = series.mean()
        except TypeError: # Lida com casos onde pode haver não-numéricos disfarçados
            profile['Mínimo'] = 'N/A (Erro numérico)'
            profile['Máximo'] = 'N/A (Erro numérico)'
            profile['Média'] = 'N/A (Erro numérico)'

    # Perfil para tipos de string
    elif pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series):
        # Converte para string e lida com NaN para evitar erro de .str
        non_null_strings = series.astype(str).dropna()
        if not non_null_strings.empty:
            profile['Tamanho Mínimo (Str)'] = non_null_strings.str.len().min()
            profile['Tamanho Máximo (Str)'] = non_null_strings.str.len().max()
        else:
            profile['Tamanho Mínimo (Str)'] = 'N/A'
            profile['Tamanho Máximo (Str)'] = 'N/A'

    # Adicionar uma amostra de valores únicos (primeiros 5)
    # unique_sample = series.unique()
    # if len(unique_sample) > 5:
    #     profile['Amostra de Únicos'] = str(unique_sample[:5].tolist()) + '...'
    # else:
    #     profile['Amostra de Únicos'] = str(unique_sample.tolist())

    profile_str = ""
    for k, v in profile.items():
        profile_str += f"**{k}**: {v}\n\n"
    return profile_str

# --- Lógica de Match de Colunas ---
def determine_match_type(col_a_name, col_b_name, cols_a_list, cols_b_list):
    """Determina o tipo de match entre duas colunas."""
    # Garante que os nomes das colunas são strings e não vazios
    if col_a_name == '' and col_b_name == '':
        return "Inexistente"
    if col_a_name == col_b_name and col_a_name != '':
        return "Igual"
    if col_a_name in cols_b_list and col_b_name == '':
        return "Possivel" # Coluna A existe em B, mas B não foi selecionada
    if col_b_name in cols_a_list and col_a_name == '':
        return "Possivel" # Coluna B existe em A, mas A não foi selecionada
    return "Parcial" # Default ou outra lógica


# --- Conteúdo da Página Inicial ---
def home_page_content():
    st.title("Bem-vindo ao Schema Matchmaker 🔀!")

    st.write(
        """
        Este é um site local desenvolvido para realizar schema matching entre duas fontes de dados.
        """
    )
    st.markdown("---")

    # armazenameto temporarios dos arquivos de fontes de dados
    if not os.path.exists("uploaded_files"):
        os.makedirs("uploaded_files")

    st.header("Carregamento de Datasets")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Dataset A")
        st.markdown("Esta é a sua referência ou dataset base.")

        # with st.container(border=True):
        st.subheader("Dataset A")

        uploaded_file_a = st.file_uploader(
            "Arraste e solte ou clique para fazer upload",
            type=["xls", "xlsx", "csv", "tsv", "ods"],
            key="file_uploader_A",
            label_visibility="collapsed"
        )
        if uploaded_file_a is not st.session_state.uploaded_file_a_info:
                st.session_state.uploaded_file_a_info = uploaded_file_a
        st.markdown("<p style='text-align: center; font-size: 0.9em; color: gray;'>Excel, CSV, TSV ou ODS files</p>", unsafe_allow_html=True)

        if st.button("Clear", key="clear_data_A"):
            st.session_state.uploaded_file_a_info = None
            st.session_state.file_uploader_A = None
            st.session_state.file_path_a_saved = None
            st.session_state.df_A = None
            st.session_state.column_match_rows = [] # Limpa as linhas da tabela
            st.rerun()

    with col2:
        st.markdown("### Dataset B")
        st.markdown("Este é o dataset que você deseja comparar com a origem.")

        # with st.container(border=True):
        st.subheader("Dataset B")

        uploaded_file_b = st.file_uploader(
            "Arraste e solte ou clique para fazer upload",
            type=["xls", "xlsx", "csv", "tsv", "ods"],
            key="file_uploader_B",
            label_visibility="collapsed"
        )
        if uploaded_file_b is not st.session_state.uploaded_file_b_info:
            st.session_state.uploaded_file_b_info = uploaded_file_b
        st.markdown("<p style='text-align: center; font-size: 0.9em; color: gray;'>Excel, CSV, TSV ou ODS files</p>", unsafe_allow_html=True)

        if st.button("Clear", key="clear_data_B"):
            st.session_state.uploaded_file_b_info = None
            st.session_state.file_uploader_B = None
            st.session_state.file_path_b_saved = None
            st.session_state.df_B = None
            st.session_state.column_match_rows = [] # Limpa as linhas da tabela
            st.rerun()
            
    st.markdown("---")

    st.header("Nomes dos Datasets")

    col_name1, col_name2 = st.columns(2)

    with col_name1:
        st.text_input(
            "Source Dataset Name",
            # value=st.session_state.source_dataset_name,
            key="source_dataset_name"
        )

    with col_name2:
        st.text_input(
            "Target Dataset Name",
            # value=st.session_state.target_dataset_name,
            key="target_dataset_name"
        )

    st.markdown("---")

    # --- Salvamento dos Arquivos ---
    if st.session_state.uploaded_file_a_info is not None:
        base_name_a, ext_a = os.path.splitext(st.session_state.uploaded_file_a_info.name)
        safe_file_name_a = f"{st.session_state.source_dataset_name.replace(' ', '_').replace('/', '_')}_{base_name_a}{ext_a}"
        file_path_a = os.path.join("uploaded_files", safe_file_name_a)
        try:
            with open(file_path_a, "wb") as f:
                f.write(st.session_state.uploaded_file_a_info.getbuffer())
            st.session_state.file_path_a_saved = file_path_a
        except Exception as e:
            st.error(f"Erro ao salvar arquivo A: {e}")
    else:
        st.session_state.file_path_a_saved = None

    if st.session_state.uploaded_file_b_info is not None:
        base_name_b, ext_b = os.path.splitext(st.session_state.uploaded_file_b_info.name)
        safe_file_name_b = f"{st.session_state.target_dataset_name.replace(' ', '_').replace('/', '_')}_{base_name_b}{ext_b}"
        file_path_b = os.path.join("uploaded_files", safe_file_name_b)
        try:
            with open(file_path_b, "wb") as f:
                f.write(st.session_state.uploaded_file_b_info.getbuffer())
            st.session_state.file_path_b_saved = file_path_b
        except Exception as e:
            st.error(f"Erro ao salvar arquivo B: {e}")
    else:
        st.session_state.file_path_b_saved = None


    # --- Botão de Navegação no Rodapé ---
    st.markdown("---")
    if st.session_state.uploaded_file_a_info is not None or st.session_state.uploaded_file_b_info is not None:
        if st.button("Ir para Configurações de Arquivo", help="Clique para ajustar como seus dados serão lidos."):
            st.session_state.current_page = "config"
            st.rerun()
    else:
        st.warning("Carregue pelo menos um arquivo para configurar.")


# --- Conteúdo da Página de Configuração ---
def config_page_content():
    st.title("⚙️ Configurações de Arquivo")
    st.markdown("---")

    st.write("Ajuste as configurações para cada dataset carregado.")

    df_A_loaded, _ = display_file_config(
        st.session_state.uploaded_file_a_info,
        st.session_state.source_dataset_name,
        st.session_state.file_path_a_saved,
        "A"
    )

    df_B_loaded, _ = display_file_config(
        st.session_state.uploaded_file_b_info,
        st.session_state.target_dataset_name,
        st.session_state.file_path_b_saved,
        "B"
    )

    st.markdown("---")
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("Voltar para Página Inicial"):
            st.session_state.current_page = "home"
            st.rerun()
    with col_nav2:
        if st.session_state.get('df_A') is not None or st.session_state.get('df_B') is not None:
            if st.button("Ir para Análise de Colunas"):
                st.session_state.current_page = "column_analysis"
                st.rerun()
        else:
            st.warning("Pré-visualize pelo menos um dataset para prosseguir com a análise de colunas.")


# --- Conteúdo da Página de Análise de Colunas ---
def column_analysis_page_content():
    st.title("📊 Análise e Match de Colunas")
    st.markdown("---")

    st.write("Compare as colunas dos seus datasets e adicione observações.")

    df_a = st.session_state.get('df_A')
    df_b = st.session_state.get('df_B')

    cols_a = [''] + (list(df_a.columns) if df_a is not None else [])
    cols_b = [''] + (list(df_b.columns) if df_b is not None else [])
    
    # Opções para o selectbox de match_type
    match_options = ["Igual", "Parcial", "Possivel", "Inexistente"]

    # Modificação para pré-preencher a tabela com colunas do Dataset A
    if 'column_match_rows' not in st.session_state or len(st.session_state.column_match_rows) == 0:
        if df_a is not None:
            st.session_state.column_match_rows = []
            for col in df_a.columns:
                profile_a_str = generate_column_profile(df_a, col)
                st.session_state.column_match_rows.append({
                    'col_a': col,
                    'profile_a': profile_a_str,
                    'col_b': '',
                    'profile_b': '',
                    'match_type':  match_options[0],
                    'observations': ''
                })
                # st.session_state.column_match_rows.append({
                #     'col_a': col,
                #     'profile_a': profile_a_str,
                #     'col_b': '',
                #     'profile_b': '',
                #     'match_type': determine_match_type(col, '', cols_a, cols_b),
                #     'observations': ''
                # })
        else:
            st.session_state.column_match_rows = []
            st.session_state.column_match_rows.append({
                'col_a': '',
                'profile_a': '',
                'col_b': '',
                'profile_b': '',
                'match_type':  match_options[0],
                'observations': ''
            })

    st.subheader("Tabela de Match de Colunas")

    # Layout das colunas para a tabela (cabeçalhos)
    header_cols_widths = [2, 2, 2, 2, 2, 3] # Defina as larguras uma vez
    header_cols = st.columns(header_cols_widths)
    # Criar cabeçalhos dentro de containers com borda para consistência visual
    header_cols[0].markdown("Perfil Coluna Dataset A")
    header_cols[1].markdown("Nome Coluna Dataset A")
    header_cols[2].markdown("Perfil Coluna Dataset B")
    header_cols[3].markdown("Nome Coluna Dataset B")
    header_cols[4].markdown("Tipo de Match")
    header_cols[5].markdown("Observações")

    # Renderiza cada linha da tabela
    for i, row in enumerate(st.session_state.column_match_rows):
        # A coluna de observações e o botão remover precisam de mais espaço,
        # então ajustamos o último slot do layout.
        row_cols = st.columns(header_cols_widths)
        
        row_cols[0].markdown(row['profile_a'])

        # with row_cols[1].container(border=True):
        selected_col_a = row_cols[1].selectbox(
            "",
            cols_a,
            index=cols_a.index(row['col_a']) if row['col_a'] in cols_a else 0,
            key=f"col_a_select_{i}",
            label_visibility="collapsed",
            on_change=lambda idx=i: update_row_profiles(idx, 'col_a', df_a, df_b, cols_a, cols_b)
        )
        
        if selected_col_a != row['col_a']:
            st.session_state.column_match_rows[i]['col_a'] = selected_col_a

        # with row_cols[2].container(border=True):
        row_cols[2].markdown(row['profile_b'])

        # with row_cols[3].container(border=True):
        selected_col_b = row_cols[3].selectbox(
            "",
            cols_b,
            index=cols_b.index(row['col_b']) if row['col_b'] in cols_b else 0,
            key=f"col_b_select_{i}",
            label_visibility="collapsed",
            on_change=lambda idx=i: update_row_profiles(idx, 'col_b', df_a, df_b, cols_a, cols_b)
        )
        if selected_col_b != row['col_b']:
            st.session_state.column_match_rows[i]['col_b'] = selected_col_b

        # with row_cols[4].container(border=True):
        current_match_type_index = match_options.index(row['match_type']) if row['match_type'] in match_options else 0
        selected_match_type = row_cols[4].selectbox(
            "",
            match_options,
            index=current_match_type_index,
            key=f"match_type_select_{i}",
            label_visibility="collapsed",
            on_change=lambda idx=i: update_match_type_in_state(idx, match_options) # Adiciona um callback para o selectbox
        )
        # Atualiza o estado da sessão se o valor do selectbox mudar
        if selected_match_type != row['match_type']:
            st.session_state.column_match_rows[i]['match_type'] = selected_match_type

        # Para a última coluna (Observações + Botão Remover),
        # você pode colocar o text_input e o botão dentro de um único container,
        # ou se quiser bordas separadas, mais colunas internas.
        # Por simplicidade e visual, vamos colocar ambos dentro de um container com borda.
        # with row_cols[5].container(border=True):
        # Usar sub-colunas aqui dentro para alinhar o input e o botão
        obs_col_inner, remove_btn_col_inner = row_cols[5].columns([4,1])

        st.session_state.column_match_rows[i]['observations'] = obs_col_inner.text_input(
            "",
            value=row['observations'],
            key=f"obs_input_{i}",
            label_visibility="collapsed"
        )
        
        if i > 0:
            if remove_btn_col_inner.button("X", key=f"remove_row_{i}", help="Remover esta linha"):
                st.session_state.column_match_rows.pop(i)
                st.rerun()


    # Botão para adicionar mais uma linha
    if st.button("Adicionar Nova Linha"):
        st.session_state.column_match_rows.append({
            'col_a': '',
            'profile_a': '',
            'col_b': '',
            'profile_b': '',
            'match_type': match_options[0],
            'observations': ''
        })
        st.rerun() # Recarrega para mostrar a nova linha

    st.markdown("---")
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("Voltar para Configurações de Arquivo", key="back_to_config_btn"):
            st.session_state.current_page = "config"
            st.rerun()
    with col_nav2:
        # Botão para gerar CSV do mapeamento
        # Filtra linhas onde pelo menos uma coluna A ou B foi selecionada
        mapping_data = []
        for row in st.session_state.column_match_rows:
            if row['col_a'] or row['col_b']: # Apenas linhas com alguma seleção
                mapping_data.append({
                    'Coluna Dataset A': row['col_a'],
                    # 'Perfil Dataset A': row['profile_a'].replace('\n', ' | '), # Ajusta perfil para CSV
                    'Coluna Dataset B': row['col_b'],
                    # 'Perfil Dataset B': row['profile_b'].replace('\n', ' | '),
                    'Tipo de Match': row['match_type'],
                    'Observações': row['observations']
                })
        
        if mapping_data:
            mapping_df = pd.DataFrame(mapping_data)
            csv_output = mapping_df.to_csv(index=False, encoding='utf-8') # utf-8-sig para compatibilidade com Excel
            
            st.download_button(
                label="Gerar CSV do Mapeamento",
                data=csv_output,
                file_name="mapeamento_datasets.csv",
                mime="text/csv",
                key="download_mapping_csv"
            )
        else:
            st.info("Adicione e preencha algumas linhas para gerar o CSV de mapeamento.")



# --- Função para atualizar perfil e match_type em uma linha específica ---
def update_row_profiles(row_index, changed_col_source, df_a, df_b, cols_a, cols_b):
    """
    Função callback para on_change de selectbox.
    Atualiza o perfil e o tipo de match da linha especificada.
    """
    row = st.session_state.column_match_rows[row_index]

    current_col_a = st.session_state[f"col_a_select_{row_index}"]
    current_col_b = st.session_state[f"col_b_select_{row_index}"]

    # Sempre recalcula o perfil da coluna que foi alterada no dropdown
    if changed_col_source == 'col_a':
        row['profile_a'] = generate_column_profile(df_a, current_col_a) if current_col_a else ''
    elif changed_col_source == 'col_b':
        row['profile_b'] = generate_column_profile(df_b, current_col_b) if current_col_b else ''
    
    # Recalcula o tipo de match sempre que um dropdown muda
    # row['match_type'] = determine_match_type(current_col_a, current_col_b, cols_a, cols_b)
    
    st.session_state.column_match_rows[row_index] = row


def update_match_type_in_state(row_index, match_options):
    """
    Atualiza o valor de 'match_type' na session_state quando o selectbox é alterado.
    """
    # O valor do selectbox é automaticamente atualizado em st.session_state[key]
    st.session_state.column_match_rows[row_index]['match_type'] = st.session_state[f"match_type_select_{row_index}"]
    st.rerun() 

# --- Configuração Principal do App ---
st.set_page_config(
    page_title="Schema Matchmaker",
    page_icon="🔀",
    layout="wide"
)

# --- Inicialização Global do Session State ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"
if 'uploaded_file_a_info' not in st.session_state:
    st.session_state.uploaded_file_a_info = None
if 'uploaded_file_b_info' not in st.session_state:
    st.session_state.uploaded_file_b_info = None
if 'source_dataset_name' not in st.session_state:
    st.session_state.source_dataset_name = "Dataset A"
if 'target_dataset_name' not in st.session_state:
    st.session_state.target_dataset_name = "Dataset B"
if 'file_path_a_saved' not in st.session_state:
    st.session_state.file_path_a_saved = None
if 'file_path_b_saved' not in st.session_state:
    st.session_state.file_path_b_saved = None
if 'df_A' not in st.session_state:
    st.session_state.df_A = None
if 'df_B' not in st.session_state:
    st.session_state.df_B = None
if 'A_configs' not in st.session_state:
    st.session_state.A_configs = {}
if 'B_configs' not in st.session_state:
    st.session_state.B_configs = {}
if 'column_match_rows' not in st.session_state:
    st.session_state.column_match_rows = []


# --- Renderiza o conteúdo da página com base no valor de st.session_state.current_page ---
if st.session_state.current_page == "home":
    home_page_content()
elif st.session_state.current_page == "config":
    config_page_content()
elif st.session_state.current_page == "column_analysis":
    column_analysis_page_content()