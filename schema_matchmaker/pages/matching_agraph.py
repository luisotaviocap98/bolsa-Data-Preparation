import streamlit as st
import streamlit.components.v1 as components

# Listas de itens
items_left = ["Item A1", "Item A2", "Item A3"]
items_right = ["Item B1", "Item B2", "Item B3"]

# Estado
if "connections" not in st.session_state:
    st.session_state.connections = []

if "selected_left" not in st.session_state:
    st.session_state.selected_left = None

if "selected_right" not in st.session_state:
    st.session_state.selected_right = None

st.title("Conectar Itens com Canvas (Visual)")

# Colunas para seleção
col1, col2 = st.columns(2)

with col1:
    st.subheader("Esquerda")
    for item in items_left:
        if st.button(f"Selecionar {item}", key=f"left_{item}"):
            st.session_state.selected_left = item

with col2:
    st.subheader("Direita")
    for item in items_right:
        if st.button(f"Selecionar {item}", key=f"right_{item}"):
            st.session_state.selected_right = item

# Criar conexão
if st.session_state.selected_left and st.session_state.selected_right:
    new_conn = (st.session_state.selected_left, st.session_state.selected_right)
    if new_conn not in st.session_state.connections:
        st.session_state.connections.append(new_conn)
    st.session_state.selected_left = None
    st.session_state.selected_right = None

# HTML + CSS + JS para visual
html = """
<style>
.container {
    display: flex;
    justify-content: space-between;
    position: relative;
    width: 600px;
    height: 300px;
    margin-top: 30px;
}
.list {
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: 10px;
}
.item {
    background-color: #e3e3e3;
    padding: 8px;
    border-radius: 5px;
    text-align: center;
    position: relative;
}
#line-canvas {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 0;
}
.overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}
</style>
<div class="container">
  <canvas id="line-canvas" width="600" height="300"></canvas>
  <div class="list" id="left">
"""
for i, item in enumerate(items_left):
    html += f'<div class="item" id="left_{i}">{item}</div>'
html += """
  </div>
  <div class="list" id="right">
"""
for i, item in enumerate(items_right):
    html += f'<div class="item" id="right_{i}">{item}</div>'
html += """
  </div>
</div>
<script>
const canvas = document.getElementById('line-canvas');
const ctx = canvas.getContext('2d');
ctx.clearRect(0, 0, canvas.width, canvas.height);

function getMidPoint(el) {
  const rect = el.getBoundingClientRect();
  const container = document.querySelector(".container").getBoundingClientRect();
  return {
    x: rect.left + rect.width / 2 - container.left,
    y: rect.top + rect.height / 2 - container.top
  };
}

const connections = [
"""
for left, right in st.session_state.connections:
    left_index = items_left.index(left)
    right_index = items_right.index(right)
    html += f'  ["left_{left_index}", "right_{right_index}"],\n'
html += """];

connections.forEach(([lid, rid]) => {
  const l = document.getElementById(lid);
  const r = document.getElementById(rid);
  if (l && r) {
    const p1 = getMidPoint(l);
    const p2 = getMidPoint(r);
    ctx.beginPath();
    ctx.moveTo(p1.x, p1.y);
    ctx.lineTo(p2.x, p2.y);
    ctx.strokeStyle = "#007bff";
    ctx.lineWidth = 2;
    ctx.stroke();
  }
});
</script>
"""
components.html(html, height=350, width=620)
