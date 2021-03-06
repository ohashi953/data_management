import subprocess
import sys
import re
import json
import git_cmd
import networkx as nx
import plotly.graph_objects as go
import plotly
import os

args = sys.argv

if __name__ == '__main__':

    f = open(os.getcwd() + '/commit_log.json', 'r')
    json_dict = json.load(f)

    p_list = []  # パラメータのリスト
    for x in json_dict.values():
        for y in x.values():
            for i in y['parameter']:
                p_list.append(i)
    p_list = [x for x in set(p_list) if x is not None]
    print(p_list)

    m_list = []  # 評価値のリスト
    for x in json_dict.values():
        for y in x.values():
            for i in y['metrics']:
                m_list.append(i)
    m_list = [x for x in set(m_list) if x is not None]
    print(m_list)

    # 評価値と評価値のグラフ
    G = nx.Graph()
    pre_node_name = None
    mx = m_list[1]   # 好きな評価値を二つ選んでね！(ブラウザで選択してもらう)
    my = m_list[0]
    mx_num = None
    my_num = None

    for keys in json_dict.keys():
        hash_dict = json_dict[keys]
        if not bool(hash_dict): continue
        for i in hash_dict.keys():
            if not hash_dict.get(i): continue  # ファイルが空だったら次へ
            if mx not in hash_dict[i]['metrics']: continue  # jsonのメトリクスリストにmxがなかった場合
            if my not in hash_dict[i]['metrics']: continue  # jsonのメトリクスリストにmyがなかった場合
            mx_num = hash_dict[i]['metrics'].index(mx)  # mxの位置
            my_num = hash_dict[i]['metrics'].index(my)  # myの位置
            print(keys + '_' + i)
            node_name = keys + '_' + i
            G.add_node(node_name)  # Add node
            G.nodes[node_name]["pos"] = (int(hash_dict[i]['metrics_value'][mx_num][:-1]),
                                         int(hash_dict[i]['metrics_value'][my_num][:-1]))  # Add node position
            if pre_node_name in G.nodes(): G.add_edge(node_name, pre_node_name)
            pre_node_name = node_name
            G.nodes[node_name]["node_info"] = hash_dict[i] # Add node_info for customdata
        pre_h = keys

    # Create a node trace
    node_x = []
    node_y = []
    node_info = []
    text = []
    for n in G.nodes():
        x, y = G.nodes[n]["pos"]
        node_x.append(x)
        node_y.append(y)
        node_info.append(G.nodes[n]["node_info"])
        text.append(n)
    print(node_x)
    print(node_y)
    nodes = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        marker=dict(size=20, line=dict(width=2)),
        name="commit_file",
        customdata=node_info,
        text=text,  # pass the text
        hovertemplate="Node: %{text}<extra></extra>",
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
    edges = go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(width=2), name="from_original_file")
    # Create a figure from nodes and edges
    fig = go.Figure(
        data=[edges, nodes],
        layout=go.Layout(
            showlegend=True,
            xaxis=dict(tickmode='array', tickvals=node_x),
            yaxis=dict(showgrid=True, zeroline=True, showticklabels=True),
            clickmode="select+event",
        ),
    )
    fig.update_xaxes(title=mx)  # X軸タイトルを指定
    fig.update_yaxes(title=my)  # Y軸タイトルを指定

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
        <link rel="stylesheet" type="text/css" href="style.css"/>
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
    with open("m_m.html", "w") as f:
        f.write(html_str)