import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState    
from streamlit_flow.layouts import ManualLayout

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
    "backgroundColor": "#5a5a5a6a",
    'overflowY': 'scroll'
}

nome = 'Node Teste'


def show_page():
    col_1, col_2, col_3 = st.columns([1, 2, 1])
    
    with col_1:
        st.subheader('Teste de Streamlit Flow')
        container = st.container(height=200)

        # Aplica estilo para criar o "scroll visual"
        st.markdown("""
            <style>
            .scroll-container {
                overflow-y: auto;
                padding: 10px;
                background-color: #5a5a5a6a;
                border-radius: 8px;
            }
            </style>
        """, unsafe_allow_html=True)

        # Use st.markdown para criar o div scrollável
        with container:
            st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
            for i in range(1, 31):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"Texto número {i}")
                with col2:
                    if st.button(f"Botão {i}", key=f"botao_{i}"):
                        st.success(f"Você clicou no botão {i}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            
    
    with col_2:
        with st.container():
            st.subheader('Teste de Streamlit Flow')
            st.text("Clique e arraste para conectar os itens. Selecione uma aresta e pressione 'Backspace' para removê-la.")
            
            # source = [StreamlitFlowNode(id='1', pos=(100, 100), data={"content": f'{nome}'}, node_type='output', target_position='right',  draggable=False , style= style_node_top),
            #         StreamlitFlowNode(id='2', pos=(100, 160), data={"content": 'Node 2'}, node_type='output', target_position='right',  draggable=False , style= style_node_middle),
            #         StreamlitFlowNode(id='3', pos=(100, 220), data={"content": 'Node 3'}, node_type='output', target_position='right',  draggable=False , style= style_node_middle),
            #         StreamlitFlowNode(id='4', pos=(100, 280), data={"content": 'Node 4'}, node_type='output', target_position='right',  draggable=False , style= style_node_middle),
            #         StreamlitFlowNode(id='5', pos=(100, 340), data={"content": 'Node 5'}, node_type='output', target_position='right',  draggable=False , style= style_node_middle),
            #         StreamlitFlowNode(id='6', pos=(100, 400), data={"content": 'Node 6'}, node_type='output', target_position='right',  draggable=False , style= style_node_middle),
            #         StreamlitFlowNode(id='7', pos=(100, 460), data={"content": 'Node 7'}, node_type='output', target_position='right',  draggable=False , style= style_node_middle),
            #         StreamlitFlowNode(id='8', pos=(100, 520), data={'content': 'Node 8'}, node_type='output', target_position='right',  draggable=False, style= style_node_bottom)]
            
            source = [
                StreamlitFlowNode(id='1', pos=(100, 100), data={"content": f'{nome}'}, node_type='output', target_position='right', draggable=False, style=style_node_top),
            ]

            for i in range(2, 31):
                y = 100 + (i - 1) * 60
                style = style_node_middle
                content = f'Node {i}'
                source.append(StreamlitFlowNode(id=str(i), pos=(100, y), data={'content': content}, node_type='output', target_position='right', draggable=False, style=style))

            # Ajusta o último nó como "bottom"
            source[-1].style = style_node_bottom
            
            target = [StreamlitFlowNode(id='a', pos=(450, 100), data={'content': 'Node 5'}, node_type='input', source_position='left',  draggable=False, style= style_node_top, connectable=True),
                    StreamlitFlowNode(id='b', pos=(450, 160), data={'content': 'Node 6'}, node_type='input', source_position='left',  draggable=False, style= style_node_bottom, connectable=False)]

            nodes = source + target

            source_dict = {node.id: node for node in source}
            target_dict = {node.id: node for node in target}

            edges = []
            
            
            if 'click_interact_state' not in st.session_state:
                st.session_state.click_interact_state = StreamlitFlowState(nodes, edges)


            previous_edges_ids = {edge.id for edge in st.session_state.click_interact_state.edges}

            # backspace apaga a conexão
            update_state = streamlit_flow('ret_val_flow',
                            st.session_state.click_interact_state,
                            # layout=TreeLayout(direction='right'), 
                            enable_node_menu=True,
                            fit_view=True,
                            show_controls=True,
                            allow_new_edges=True,
                            animate_new_edges=False,
                            get_node_on_click=True,
                            get_edge_on_click=True,
                            hide_watermark=True,
                            allow_zoom=True,
                            enable_edge_menu=True,
                            pan_on_drag=True,
                            min_zoom=0,
                            style=custom_style)
            
            st.write(f"Clicked on: {update_state.selected_id}")
            
            current_edges_ids = {edge.id for edge in update_state.edges}
            newly_added_edge_ids = current_edges_ids - previous_edges_ids

            # updated_edges = []
            # for edge in update_state.edges:
            #     if edge.id in newly_added_edge_ids:
            #         # Esta é uma nova aresta, adicione o marcador a ela
            #         # Importante: Crie uma *nova* instância para garantir que o React Flow detecte a mudança
            #         new_edge_with_marker = StreamlitFlowEdge(
            #             id=edge.id,
            #             source=edge.source,
            #             target=edge.target,
            #             animated=edge.animated, # Mantenha as propriedades existentes
            #             label=edge.label,
            #             # Adicione o marcador de início ou fim
            #             marker_end={'type':'arrow'} # ou marker_start, dependendo da sua preferência
            #         )
            #         updated_edges.append(new_edge_with_marker)
            #     else:
            #         # Aresta existente ou não é uma nova aresta que precisa de correção
            #         updated_edges.append(edge)
                    
            # if update_state.selected_id and not update_state.selected_id in newly_added_edge_ids:
            #     selected_edge_from_update = next((e for e in update_state.edges if e.id == update_state.selected_id), None)
            #     if selected_edge_from_update and hasattr(selected_edge_from_update, 'source') and hasattr(selected_edge_from_update, 'target'):
            #         # Encontre a aresta na lista updated_edges e a substitua
            #         for i, edge in enumerate(updated_edges):
            #             if edge.id == update_state.selected_id:
            #                 updated_edges[i] = StreamlitFlowEdge(
            #                     id=edge.id,
            #                     source=edge.source,
            #                     target=edge.target,
            #                     animated=edge.animated,
            #                     label=edge.label,
            #                     marker_end={'type':'arrow'} # Garante a seta se for clicada
            #                 )
            #                 break
                        
            # # Atribua a lista de arestas atualizada ao estado
            # update_state.edges = updated_edges

            st.session_state.click_interact_state = update_state
            
            # if len(newly_added_edge_ids):
            #     # print('Nova aresta adicionada')
            #     new_edge = next((edge for edge in update_state.edges if edge.id == update_state.selected_id), None)
            #     new_node = next((node for node in update_state.nodes if node.id == update_state.selected_id), None)
            #     # print(new_edge , new_node, update_state.edges.index(new_edge) if new_edge else None)
            #     # print(new_edge, update_state.edges, '---')
            #     posicao_edge = update_state.edges.index(new_edge) if new_edge else None
            #     if posicao_edge is not None:
            #         update_state.edges.pop(posicao_edge)
            #         corrigir_edge = StreamlitFlowEdge(id=update_state.selected_id, source=new_edge.source, target=new_edge.target, animated=False, marker_start= {'type':'arrow'}, deletable=True)
            #         # print('corrigir_edge', corrigir_edge)
            #         update_state.edges.insert(posicao_edge,corrigir_edge)
            #         st.session_state.click_interact_state = update_state
            #         # print('Atualizou o estado com a nova aresta')
            #         st.rerun()  
            #     # print('--',update_state.edges[posicao_edge].marker_start, st.session_state.click_interact_state,'\n')
            # else:
            #     # print('else')
            #     st.session_state.click_interact_state = update_state
            # st.rerun()
            # print('atualizou', st.session_state.click_interact_state,'\n\n')
            
        
    with col_3:
        st.subheader('Teste de Streamlit Flow')
        with st.container(border=True):
            st.write('Tipo')
            st.write('Valores unicos')
            st.write('Valores faltantes')
            st.write('Valores duplicados')
            st.write('Min')
            st.write('Max')
            st.write('Media')
            st.write('Length Min')
            st.write('Length Max')