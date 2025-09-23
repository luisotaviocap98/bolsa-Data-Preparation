from pyvis.network import Network
import networkx as nx
import webbrowser

# Cria um grafo do NetworkX
G = nx.Graph()

# Listas de itens
lista_1 = [f"A{i}" for i in range(5)]
lista_2 = [f"B{i}" for i in range(5)]

# Adiciona os nós das duas listas com posições fixas
for i, item in enumerate(lista_1):
    G.add_node(item, label=item, x=-200, y=i * 100)

for i, item in enumerate(lista_2):
    G.add_node(item, label=item, x=200, y=i * 100)

# Cria a visualização com Pyvis
net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white", notebook=False, directed=False)
net.from_nx(G)
net.toggle_physics(False)
net.show_buttons(filter_=['nodes'])

# Salva e abre o HTML
output_path = "grafo_interativo.html"
net.write_html(output_path)
webbrowser.open(output_path)
