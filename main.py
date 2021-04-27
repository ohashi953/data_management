import sys
import json
import git_cmd
import networkx as nx
import plotly.graph_objects as go
import plotly
import os

args = sys.argv

"""
Make json file
"""
if __name__ == '__main__':
    print(os.getcwd() + '/' + args[1].split('/')[4][:-4]) #cloneしたディレクトリ名
    repo = "/Users/yukinaohashi/sample_project" #手動
    print(repo)

    # git_cmd.git_clone()

    """
    git_cmd.py
    """
    print("start")
    file_name = git_cmd.get_filename(repo)
    hash_list = git_cmd.get_all_hash(repo)
    ddd = {}
    metrics_value = None

    with open(os.getcwd() + '/commit_log.json', 'w') as f:
        f.write('')

    keys = ['File_name', 'author_name', 'author_date', 'committer_name', 'committer_date', 'command',
            'parameter', 'parameter_change', 'original_file', 'metrics', 'metrics_value']

    for commit_hash in hash_list:
        dd = {}
        temp = git_cmd.get_commit_message(commit_hash, repo).split()

        for file_num in file_name:
            param = None
            change = None
            file = None
            metrics = None
            metrics_value = None

            index_num = [n for n, v in enumerate(temp) if v == 'change']
            for j in index_num:
                if len(temp[j:]) >= 10:
                    if temp[j + 1] == 'param' and (temp[j + 7] == file_num or temp[j + 9] == file_num):
                        param = temp[j + 2]
                        if temp[j + 4] == "to":
                            change = ' '.join(temp[j+3:j+6])
                        if temp[j + 6] != 'from': break
                        file = temp[j + 7]
                        break

            index_num = [n for n, v in enumerate(temp) if v == 'metrics']
            for j in index_num:
                if len(temp[j:]) >= 5:
                    if temp[j + 4] == file_num:
                        metrics = temp[j + 1]
                        metrics_value = temp[j + 2]
                        break

            if metrics_value is None:
                continue
            else:
                values = [file_num, git_cmd.git_log(commit_hash, '--format=%an', repo), str(
                    git_cmd.datetime.datetime.strptime(git_cmd.git_log(commit_hash, '--format=%ad', repo), '%a %b %d %H:%M:%S %Y %z')),
                          git_cmd.git_log(commit_hash, '--format=%cn', repo), str(
                        git_cmd.datetime.datetime.strptime(git_cmd.git_log(commit_hash, '--format=%cd', repo), '%a %b %d %H:%M:%S %Y %z')),
                          git_cmd.get_commit_message(commit_hash, repo), param, change, file, metrics, metrics_value]
            d = {file_num: dict(zip(keys, values))}
            dd.update(d)

        ddd[commit_hash] = dd

    with open(os.getcwd() + '/commit_log.json', 'a') as f:
        json.dump(ddd, f, indent=2, ensure_ascii=False)

    """
    visualization.py
    """

    f = open(os.getcwd() + '/commit_log.json', 'r')
    json_dict = json.load(f)

    G = nx.Graph()
    x = 1
    pre_h = None
    metrics = ""

    for keys in json_dict.keys():
        hash_dict = json_dict[keys]
        if not bool(hash_dict): continue
        for i in hash_dict.keys():
            if not hash_dict.get(i): continue
            metrics = hash_dict[i]['metrics'] + "[" + hash_dict[i]['metrics_value'][-1:] + "]"
            node_name = keys + '_' + i
            G.add_node(node_name)  # Add node
            G.nodes[node_name]["pos"] = (hash_dict[i]['author_date'], int(hash_dict[i]['metrics_value'][:-1]))  # Add node position
            if pre_h:  # Add edge
                pre_f = hash_dict[i]['original_file']
                if pre_f:
                    pre_node_name = pre_h + '_' + pre_f
                    if pre_node_name in G.nodes(): G.add_edge(node_name, pre_node_name)
            G.nodes[node_name]["node_info"] = hash_dict[i] # Add node_info for customdata
        x = x + 1
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
    fig.update_xaxes(title="commit_date")  # X軸タイトルを指定
    fig.update_yaxes(title="metrics_" + metrics)  # Y軸タイトルを指定

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
    with open("index.html", "w") as f:
        f.write(html_str)
