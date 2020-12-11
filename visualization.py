import subprocess
import sys
import re
import json
from graphviz import Digraph
from graphviz import Graph
import git_cmd

args = sys.argv


if __name__ == '__main__':
    g = Digraph(format="png")

    g.attr("node", shape="box", width="2", color="orange")

    json_open = open(args[1] + '/test.json', 'r')
    json_load = json.load(json_open)

    date = []
    for x in git_cmd.get_all_hash():
        date.append(json_load[x]['command'])
        g.node(date[-1])
    for x in range(len(date) - 1):
        print(date[x])
        print(date[x + 1])
        g.edge(date[x + 1], date[x])

    g.render("order_state1")