import streamlit as st

# --- Dados de Exemplo ---
# Em uma aplicação real, isso viria de um diretório, banco de dados, etc.
FILES = [
    'relatorio_vendas_2024_Q1.pdf',
    'relatorio_vendas_2024_Q2.pdf',
    'dados_brutos_clientes.csv',
    'dados_tratados_clientes.csv',
    'imagem_produto_A.jpg',
    'imagem_produto_B.jpg',
    'contrato_final.docx',
    'rascunho_contrato.docx',
]

# --- Funções para Manipular os Pares ---
def add_pair():
    """Adiciona um novo dicionário de par à lista no session_state."""
    st.session_state.pairs.append({'file1': None, 'file2': None})

def remove_pair(index):
    """Remove um par da lista no session_state com base no seu índice."""
    if len(st.session_state.pairs) > 0:
        st.session_state.pairs.pop(index)

def show_page():
    # --- Título e Descrição ---
    # st.title("🔗 Ferramenta de Pareamento de Arquivos com Streamlit")
    st.header("Selecione arquivos da lista para formar pares e executar ações.")

    # --- Inicialização do Estado da Sessão ---
    # Usamos st.session_state para manter o controle dos pares criados pelo usuário.
    # Isso é crucial porque o Streamlit re-executa o script a cada interação.
    if 'pairs' not in st.session_state:
        # Começamos com um par vazio por padrão.
        # Cada par é um dicionário com as chaves 'file1' e 'file2'.
        st.session_state.pairs = [{'file1': None, 'file2': None}]


    st.divider()

    # --- Layout da Interface ---
    # Dividimos a tela em duas colunas, similar ao design original.
    col_files, col_pairing = st.columns([1, 2]) # A coluna de pareamento é 2x maior

    # --- Coluna da Esquerda: Lista de Arquivos ---
    with col_files:
        st.header("Lista de Arquivos")
        # st.info("Estes são os arquivos disponíveis para seleção.")
        
        # Exibe a lista de arquivos de forma organizada
        for file in FILES:
            st.markdown(f"- `{file}`")

    # --- Coluna da Direita: Área de Pareamento ---
    with col_pairing:
        # Botão para adicionar um novo par
        st.button("Adicionar Novo Par", on_click=add_pair, type="primary", use_container_width=True)
        # st.divider()

        if not st.session_state.pairs:
            st.warning("Nenhum par criado. Clique no botão acima para adicionar um.")

        # Itera sobre cada par no session_state para renderizá-lo na tela
        for i, pair in enumerate(st.session_state.pairs):
            # Usamos um container para agrupar visualmente cada par
            with st.container(border=True):
                
                # Título e botão de remoção para cada par
                header_cols = st.columns([3, 1])
                with header_cols[0]:
                    st.subheader(f"Par #{i + 1}")
                with header_cols[1]:
                    # O botão de remover chama a função remove_pair, passando o índice atual
                    st.button("Remover", key=f"remove_{i}", on_click=remove_pair, args=(i,), use_container_width=True)

                # Colunas para as caixas de seleção dos arquivos
                select_cols = st.columns(2)
                
                # Caixa de seleção para o primeiro arquivo
                with select_cols[0]:
                    # O valor selecionado é armazenado diretamente no session_state
                    # A chave (key) é única para cada widget, garantindo que o Streamlit mantenha seu estado
                    pair['file1'] = st.selectbox(
                        "Arquivo 1",
                        options=[None] + FILES, # Adiciona None para permitir um estado "vazio"
                        index=0 if not pair['file1'] else FILES.index(pair['file1']) + 1,
                        key=f"file1_{i}"
                    )

                # Caixa de seleção para o segundo arquivo
                with select_cols[1]:
                    # Para evitar selecionar o mesmo arquivo duas vezes, removemos a seleção do Arquivo 1 da lista de opções
                    options_file2 = [f for f in FILES if f != pair['file1']]
                    pair['file2'] = st.selectbox(
                        "Arquivo 2",
                        options=[None] + options_file2,
                        index=0 if not pair['file2'] else options_file2.index(pair['file2']) + 1,
                        key=f"file2_{i}"
                    )

                # --- Área de Ações ---
                # As ações só aparecem se ambos os arquivos do par forem selecionados
                if pair['file1'] and pair['file2']:
                    st.success(f"Par Válido: `{pair['file1']}` e `{pair['file2']}`")
                    
                