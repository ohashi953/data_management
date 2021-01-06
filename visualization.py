import subprocess
import sys
import re
import json
import git_cmd
import networkx as nx
import plotly.graph_objects as go
import plotly

args = sys.argv

if __name__ == '__main__':
    f = open(args[1] + '/test.json', 'r')
    json_dict = json.load(f)

    G = nx.Graph()
    x = 1
    pre_h = None

    for keys in json_dict.keys():
        hash_dict = json_dict[keys]
        for i in hash_dict.keys():
            node_name = keys + '_' + i
            G.add_node(node_name)  # Add node
            G.nodes[node_name]["pos"] = (x, hash_dict[i]['metrics_value'])  # Add node position
            if pre_h:  # Add edge
                pre_f = hash_dict[i]['original_file']
                pre_node_name = pre_h + '_' + pre_f
                G.add_edge(node_name, pre_node_name)
            G.nodes[node_name]["node_info"] = hash_dict[i]  # Add node_info for customdata
        x = x + 1
        pre_h = keys

    # Create a node trace
    node_x = []
    node_y = []
    node_info = []
    for n in G.nodes():
        x, y = G.nodes[n]["pos"]
        node_x.append(x)
        node_y.append(y)
        node_info.append(G.nodes[n]["node_info"])
    nodes = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        marker=dict(size=20, line=dict(width=2)),
        customdata=node_info,
        hovertemplate="x: %{x}, y: %{y}<extra></extra>",
    )
    # Create a edge trace
    edge_x = []
    edge_y = []
    for e in G.edges():
        x0, y0 = G.nodes[e[0]]["pos"]
        x1, y1 = G.nodes[e[1]]["pos"]
        edge_x.append(x0)
        edge_y.append(y0)
        edge_x.append(x1)
        edge_y.append(y1)
        edge_x.append(None)
        edge_y.append(None)
    edges = go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(width=2))
    # Create a figure from nodes and edges
    fig = go.Figure(
        data=[edges, nodes],
        layout=go.Layout(
            showlegend=False,
            clickmode="select+event",
        ),
    )
    # Load JavaScript
    with open("plotly_click.js") as f:
        plotly_click_js = f.read()
    # Create <div> element
    plot_div = plotly.io.to_html(
        fig,
        include_plotlyjs=True,
        post_script=plotly_click_js,
        full_html=False,
    )
    # Build HTML
    html_str = """
    <html>
    <head>
    </head>
    <body>
    <div id="plotly-node-info">
    <p>**Node Information**</p>
    </div>
    {plot_div}
    </body>
    </html>
    """.format(
        plot_div=plot_div
    )
    # Write out HTML file
    with open("index.html", "w") as f:
        f.write(html_str)
