import streamlit as st
import os



# --- Conteúdo da Página Inicial ---
def show_page():
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

    col1, col2 = st.columns(2, border=True)

    with col1:
        st.markdown("### Carregar Projeto", unsafe_allow_html=True)
        st.markdown("Retome um projeto existente")
        st.button("Selecionar Projeto", key="select_project_button", help="Clique para selecionar um projeto existente.")

    with col2:
        st.markdown("### Novo Projeto")

        uploaded_file = st.file_uploader(
            label="Selecione arquivos para um novo projeto",
            type=["xls", "xlsx", "csv", "tsv", "ods"],
            key=st.session_state.file_uploader_key,
            accept_multiple_files=True
        )
        if uploaded_file is not st.session_state.uploaded_file_info:
            st.session_state.uploaded_file_info = uploaded_file

        if st.button("Clear", key="clear_files"):
            key_count = int(st.session_state.file_uploader_key.split("_")[-1]) + 1
            st.session_state.file_uploader_key = f"file_uploader_{key_count}"
            st.session_state.uploaded_file_info = None
            st.rerun()
            
