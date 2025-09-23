import streamlit as st
from streamlit_elements import mui, elements

# Duas listas de itens
items_left = [
    "Item A1", "Item A2", "Item A3", "Item A4", "Item A5"
]

items_right = [
    "Item B1", "Item B2", "Item B3", "Item B4", "Item B5"
]

# Estado
if "clicked_items_left" not in st.session_state:
    st.session_state.clicked_items_left = []

if "clicked_items_right" not in st.session_state:
    st.session_state.clicked_items_right = []

if "click_flags_left" not in st.session_state:
    st.session_state.click_flags_left = {item: False for item in items_left}

if "click_flags_right" not in st.session_state:
    st.session_state.click_flags_right = {item: False for item in items_right}

st.title("Duas Listas com Scroll e Botões")

# Renderiza listas lado a lado
with elements("dual-list-scroll"):
    with mui.Box(sx={
        "display": "flex",
        "gap": 2
    }):

        # Lista da esquerda
        with mui.Box(sx={
            "width": 300,
            "height": 300,
            "overflowY": "auto",
            "border": "1px solid #ccc",
            "borderRadius": "8px",
            "padding": 1
        }):
            for i, item in enumerate(items_left):
                with mui.Box(sx={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                    "marginBottom": "8px",
                    "padding": "8px",
                    "backgroundColor": "#333333",
                    "borderRadius": "4px"
                }):
                    mui.Typography(item)
                    mui.IconButton(
                        mui.icon.AddCircleOutline,
                        key=f"icon_left_{i}",
                        color="primary",
                        size="small"
                    )

        # Lista da direita
        with mui.Box(sx={
            "width": 300,
            "height": 300,
            "overflowY": "auto",
            "border": "1px solid #ccc",
            "borderRadius": "8px",
            "padding": 1
        }):
            for i, item in enumerate(items_right):
                with mui.Box(sx={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                    "marginBottom": "8px",
                    "padding": "8px",
                    "backgroundColor": "#333333",
                    "borderRadius": "4px"
                }):
                    mui.Typography(item)
                    mui.IconButton(
                        mui.icon.AddCircleOutline,
                        key=f"icon_right_{i}",
                        color="secondary",
                        size="small"
                    )

# Botões invisíveis para clique
for i, item in enumerate(items_left):
    if st.button(f"Selecionar {item}", key=f"btn_left_{i}"):
        if not st.session_state.click_flags_left[item]:
            st.session_state.clicked_items_left.append(item)
            st.session_state.click_flags_left[item] = True

for i, item in enumerate(items_right):
    if st.button(f"Selecionar {item}", key=f"btn_right_{i}"):
        if not st.session_state.click_flags_right[item]:
            st.session_state.clicked_items_right.append(item)
            st.session_state.click_flags_right[item] = True

# Exibe seleção
if st.session_state.clicked_items_left:
    st.markdown("### Itens clicados da esquerda:")
    for item in st.session_state.clicked_items_left:
        st.write("-", item)

if st.session_state.clicked_items_right:
    st.markdown("### Itens clicados da direita:")
    for item in st.session_state.clicked_items_right:
        st.write("-", item)
