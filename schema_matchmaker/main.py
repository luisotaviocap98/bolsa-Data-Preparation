import streamlit as st
from pages import home, pair_selector, file_config, matching

# --- Configuração da Página e CSS para Ocultar a Barra Lateral ---
st.set_page_config(
    page_title="Schema Matchmaker",
    page_icon="🔀",
    layout="wide"
)

# background do site todo
st.markdown(
    """
    <style>
    [data-testid="stApp"] {
        background: #242529;
        opacity: 0.95;
    }
    </style>
    """,
    unsafe_allow_html=True
)

#Variaveis
if 'uploaded_file_a_info' not in st.session_state:
    st.session_state.uploaded_file_a_info = None
if 'uploaded_file_info' not in st.session_state:
    st.session_state.uploaded_file_info = None
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
if 'file_uploader_key' not in st.session_state:
    st.session_state.file_uploader_key = 'file_uploader_0'


# --- Lógica de Navegação ---

# Inicializa o estado da sessão se ainda não estiver definido
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0

# Define a lista de funções de página que importamos
# A ordem aqui define a sequência de navegação
PAGES = [
    home.show_page, 
    pair_selector.show_page,
    matching.show_page
]
NUM_PAGES = len(PAGES)

# --- Renderização da Interface ---

# Renderiza a página atual chamando a função correspondente
current_page_function = PAGES[st.session_state.page_number]
current_page_function()

st.divider()

# --- Botões de Navegação ---
col1, col2, col3 = st.columns([0.1, 0.8, 0.1])

with col1:
    # Botão "Anterior"
    # Fica desabilitado (não aparece) se estivermos na primeira página
    if st.session_state.page_number > 0:
        if st.button("⬅️ Anterior"):
            st.session_state.page_number -= 1
            st.rerun()

with col2:
    # Indicador de progresso ou texto central
    # st.write(f"Página {st.session_state.page_number + 1} de {NUM_PAGES}")
    st.markdown(
        f"<div style='text-align: center; font-size: 18px;'>Página {st.session_state.page_number + 1} de {NUM_PAGES}</div>",
        unsafe_allow_html=True
    )

with col3:
    # Botão "Próximo"
    # Fica desabilitado (não aparece) se estivermos na última página
    if st.session_state.page_number < NUM_PAGES - 1:
        if st.button("Próximo ➡️"):
            st.session_state.page_number += 1
            st.rerun()