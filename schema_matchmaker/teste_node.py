import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState    


# --- Configuração Principal do App ---
st.set_page_config(
    page_title="Schema Matchmaker",
    page_icon="🔀",
    layout="wide"
)

style_node_top = {"width": 80, 
              "height": 60, 
              "background": "#F7F7F7", 
              "color": "#000", 
              "borderTopLeftRadius": "5%",
              "borderTopRightRadius": "5%",
              "borderBottomLeftRadius": "0%",
              "borderBottomRightRadius": "0%",
              'borderWidth': "0px"}

style_node_middle = {"width": 80, 
              "height": 60, 
              "background": "#F7F7F7", 
              "color": "#000", 
              "borderRadius": "0%",
              'borderWidth': "0px"}

style_node_bottom = {"width": 80, 
              "height": 60, 
              "background": "#F7F7F7", 
              "color": "#000", 
              "borderTopLeftRadius": "0%",
              "borderTopRightRadius": "0%",
              "borderBottomLeftRadius": "5%",
              "borderBottomRightRadius": "5%",
              'borderWidth': "0px"}


custom_style = {
    "backgroundColor": "#ffffff"
}

nome = 'Node Teste'

def show_popover_A():
    st.session_state.popover_node_A_visible = True
    st.session_state.popover_node_B_visible = False # Garante que apenas um popover esteja ativo
    st.rerun()

def hide_all_popovers():
    st.session_state.popover_node_A_visible = False
    st.session_state.popover_node_B_visible = False
    st.rerun()

def pagina():
    st.subheader('Teste de Streamlit Flow')
    source = [StreamlitFlowNode(id='1', pos=(100, 100), data={"content": f'{nome}'}, node_type='output', target_position='right',  draggable=False , style= style_node_top),
              StreamlitFlowNode(id='2', pos=(100, 160), data={'content': 'Node 2'}, node_type='output', target_position='right',  draggable=False, style= style_node_bottom)]
    
    target = [StreamlitFlowNode(id='3', pos=(450, 100), data={'content': 'Node 3'}, node_type='input', source_position='left',  draggable=False, style= style_node_top),
              StreamlitFlowNode(id='4', pos=(450, 160), data={'content': 'Node 4'}, node_type='input', source_position='left',  draggable=False, style= style_node_bottom)]
    # nodes = [StreamlitFlowNode(id='1', pos=(100, 100), data={'content': 'Node 1'}, node_type='input', source_position='right',  draggable=False),
    #         StreamlitFlowNode('2', (350, 50), {'content': 'Node 2'}, node_type='default', source_position='right', target_position = 'left', draggable=False),
    #         StreamlitFlowNode('3', (350, 150), {'content': 'Node 3'}, 'default', 'right', 'left', draggable=False),
    #         StreamlitFlowNode('4', (600, 100), {'content': 'Node 4'}, 'output', target_position='left', draggable=False)]

    # edges = [StreamlitFlowEdge('1-2', '1', '2', animated=True),
            # StreamlitFlowEdge('1-3', '1', '3', animated=True),
            # StreamlitFlowEdge('2-4', '2', '4', animated=True),
            # StreamlitFlowEdge('3-4', '3', '4', animated=True)]

    nodes = source + target

    edges = []
    
    if 'click_interact_state' not in st.session_state:
        st.session_state.click_interact_state = StreamlitFlowState(nodes, edges)
        


    # backspace apaga a conexão
    st.session_state.click_interact_state = streamlit_flow('ret_val_flow',
                    st.session_state.click_interact_state,
                    fit_view=True,
                    show_controls=False,
                    allow_new_edges=True,
                    animate_new_edges=False,
                    get_node_on_click=True,
                    get_edge_on_click=True,
                    hide_watermark=True,
                    allow_zoom=False,
                    pan_on_drag=False,
                    style=custom_style)
    
    st.write(f"Clicked on: {st.session_state.click_interact_state.selected_id}")

    # if st.session_state.click_interact_state.selected_id:
    #     if st.session_state.click_interact_state.selected_id == '1':
    #         st.info("Você clicou no Nó A. Mostrando popover...")
    #         show_popover_A()
    #     else:
    #         # Se outro nó for clicado, feche os popovers existentes
    #         hide_all_popovers()
    # elif st.session_state.popover_node_A_visible or st.session_state.popover_node_B_visible:
    #     # Se nenhum nó está selecionado, mas um popover está visível (ex: após reruns por outras interações)
    #     # Você pode optar por manter o popover ou fechá-lo
    #     pass # Manter o popover visível até que outro nó seja clicado ou ele seja fechado manualmente.


    # if st.session_state.popover_node_A_visible:
    #     st.subheader("Detalhes do Nó A")
    #     with st.popover("Clique para esconder", help="Clique no botão para esconder este popover"):
    #         st.write("Aqui estão as informações detalhadas sobre o **Nó A**.")
    #         st.text_area("Descrição", "Este nó representa o ponto inicial do fluxo.")
            # st.button("Fechar Popover", on_click=hide_all_popovers, key="close_A_popover") # Botão dentro do popover para fechar


pg = st.Page(pagina, title='Home', icon='📊')

nv = st.navigation({"H":[pg]})

nv.run()
