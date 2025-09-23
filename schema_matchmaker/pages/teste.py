import streamlit as st
import streamlit.components.v1 as components

# --- Configuração da Página e Título ---
st.set_page_config(layout="wide")
st.title("🔗 Conectar Itens (Versão Corrigida)")
st.write("Clique em um item da esquerda e depois em um da direita para criar uma conexão.")

# --- Listas de Itens ---
items_left = ["Item A1", "Item A2", "Item A3", "Item A4"]
items_right = ["Item B1", "Item B2", "Item B3", "Item B4"]

# --- Gerenciamento de Estado ---
if "connections" not in st.session_state:
    st.session_state.connections = []
if "selected_left" not in st.session_state:
    st.session_state.selected_left = None
if "selected_right" not in st.session_state:
    st.session_state.selected_right = None

# --- Componente HTML Interativo Unificado ---

# Construção do HTML, CSS e JavaScript
# Toda a interatividade e visualização acontecem aqui dentro
html_content = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    /* Estilo geral e tema escuro para combinar com o Streamlit */
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        margin: 0;
        padding: 0;
        color: white; /* Cor do texto padrão */
    }}
    .container {{
        display: flex;
        justify-content: space-between;
        position: relative;
        width: 100%;
        height: 300px;
        padding: 10px;
        box-sizing: border-box;
    }}
    #line-canvas {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none; /* Permite cliques "através" do canvas */
        z-index: 1;
    }}
    .list {{
        display: flex;
        flex-direction: column;
        gap: 20px; /* Espaçamento entre os itens */
        z-index: 10; /* Garante que os itens fiquem na frente do canvas */
    }}
    /* Estilo dos itens, agora menores e mais parecidos com botões/tags */
    .item {{
        background-color: #444; /* Fundo cinza escuro */
        padding: 8px 16px;
        border: 1px solid #777;
        border-radius: 6px;
        cursor: pointer;
        text-align: center;
        min-width: 80px;
        transition: background-color 0.2s, border-color 0.2s;
    }}
    .item:hover {{
        background-color: #555;
        border-color: #999;
    }}
    /* Estilo para o item quando selecionado */
    .item.selected {{
        background-color: #0d47a1; /* Azul escuro para seleção */
        border-color: #2196f3; /* Borda azul clara */
        color: white;
    }}
</style>
</head>
<body>
    <div class="container" id="main-container">
        <canvas id="line-canvas"></canvas>

        <div class="list" id="left-list">
            {''.join([f'<div class="item" id="left_{i}" data-name="{item}">{item}</div>' for i, item in enumerate(items_left)])}
        </div>

        <div class="list" id="right-list">
            {''.join([f'<div class="item" id="right_{i}" data-name="{item}">{item}</div>' for i, item in enumerate(items_right)])}
        </div>
    </div>
    
    <!-- Campo oculto para comunicação com Streamlit -->
    <input type="hidden" id="connections-data" value="{st.session_state.connections}" />

<script>
    // Injeta os dados do Python no JavaScript
    const connections = {st.session_state.connections};
    const items_left = {items_left};
    const items_right = {items_right};
    
    // Estado da seleção no navegador
    let selectedLeft = null;
    let selectedRight = null;

    // Função para atualizar o estilo visual dos itens selecionados
    function updateVisualSelection() {{
        document.querySelectorAll('.item').forEach(el => {{
            el.classList.remove('selected');
        }});
        if (selectedLeft) document.getElementById(selectedLeft.id)?.classList.add('selected');
        if (selectedRight) document.getElementById(selectedRight.id)?.classList.add('selected');
    }}

    // Função para criar conexão localmente
    function createConnection(left, right) {{
        console.log('Creating connection:', left, right);
        // Adiciona a conexão localmente
        connections.push([left, right]);
        // Redesenha as linhas
        drawLines();
        // Envia para o Streamlit
        sendToStreamlit(connections);
    }}
    
    // Função para enviar dados para o Streamlit
    function sendToStreamlit(data) {{
        window.parent.postMessage({{
            type: 'streamlit:setComponentValue',
            value: data
        }}, '*');
    }}

    // Adiciona listener de clique a todos os itens
    document.querySelectorAll('.item').forEach(item => {{
        item.addEventListener('click', (event) => {{
            const clickedId = event.currentTarget.id;
            const clickedName = event.currentTarget.dataset.name;
            const selection = {{ id: clickedId, name: clickedName }};

            if (clickedId.startsWith('left_')) {{
                selectedLeft = selection;
            }} else if (clickedId.startsWith('right_')) {{
                selectedRight = selection;
            }}
            
            updateVisualSelection();

            // Se ambos os lados foram selecionados, cria a conexão
            if (selectedLeft && selectedRight) {{
                const newConn = [selectedLeft.name, selectedRight.name];
                // Verifica se a conexão já existe
                const exists = connections.some(([l, r]) => l === newConn[0] && r === newConn[1]);
                if (!exists) {{
                    createConnection(selectedLeft.name, selectedRight.name);
                }}
                
                // Limpa a seleção local para a próxima conexão
                selectedLeft = null;
                selectedRight = null;
                updateVisualSelection();
            }}
        }});
    }});

    // --- LÓGICA PARA DESENHAR A LINHA (CORRIGIDA) ---
    const canvas = document.getElementById('line-canvas');
    const container = document.getElementById('main-container');
    const ctx = canvas.getContext('2d');

    function resizeCanvas() {{
        canvas.width = container.offsetWidth;
        canvas.height = container.offsetHeight;
    }}

    function getMidPoint(element) {{
        if (!element) return null;
        const containerRect = container.getBoundingClientRect();
        const elemRect = element.getBoundingClientRect();
        const x = element.id.startsWith('left')
                  ? elemRect.right - containerRect.left
                  : elemRect.left - containerRect.left;
        const y = elemRect.top - containerRect.top + elemRect.height / 2;
        return {{ x, y }};
    }}
    
    function drawLines() {{
        ctx.clearRect(0, 0, canvas.width, canvas.height); // Limpa o canvas antes de redesenhar
        connections.forEach(([leftName, rightName]) => {{
            const leftIndex = items_left.indexOf(leftName);
            const rightIndex = items_right.indexOf(rightName);

            if(leftIndex !== -1 && rightIndex !== -1) {{
                const leftEl = document.getElementById(`left_${{leftIndex}}`);
                const rightEl = document.getElementById(`right_${{rightIndex}}`);
                
                const p1 = getMidPoint(leftEl);
                const p2 = getMidPoint(rightEl);
                
                if (p1 && p2) {{
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.bezierCurveTo(p1.x + 60, p1.y, p2.x - 60, p2.y, p2.x, p2.y);
                    ctx.strokeStyle = "#2196f3"; // Cor da linha azul
                    ctx.lineWidth = 2;
                    ctx.stroke();
                }}
            }}
        }});
    }}

    // Garante que o canvas seja desenhado depois que a página carregar
    window.addEventListener('load', () => {{
        resizeCanvas();
        drawLines();
    }});
    window.addEventListener('resize', () => {{
        resizeCanvas();
        drawLines();
    }});

</script>
</body>
</html>
"""

# Renderiza o componente e captura conexões
event = components.html(html_content, height=320)

# Processa novas conexões recebidas do JavaScript
if event and isinstance(event, list):
    st.session_state.connections = event
    st.rerun()

# --- Interface Adicional (Fora do Componente) ---
col1, col2 = st.columns([1, 4])

with col1:
    if st.button("🗑️ Limpar Conexões"):
        st.session_state.connections = []
        st.rerun()

with col2:
    st.write("#### Conexões Atuais:")
    if st.session_state.connections:
        st.write(st.session_state.connections)
    else:
        st.info("Nenhuma conexão foi feita ainda.")