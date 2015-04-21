#!/usr/bin/python3
import os
import itertools

class ProblemList:
    def __init__(self, path):
        self.path = path

    def __iter__(self):
        for f in os.listdir(self.path):
            if os.path.isdir(os.path.join(self.path, f)):
                yield os.path.join(self.path, f)

class SolutionList:
    def __init__(self, path):
        self.path = path

    def __iter__(self):
        for f in os.listdir(self.path):
            if os.path.isfile(os.path.join(self.path, f)):
                yield Solution(os.path.join(self.path, f))

class Solution:
    def __init__(self, filename):
        self.filename = filename
        lines = open(filename,encoding="latin-1").readlines()
        self.author = lines[0].strip()
        self.code = " ".join(lines[1:])
        self.tokens = self.code.split()

    def __str__(self):
        return self.author + ": " + str(self.tokens)

def compare(sol1, sol2):
    ans = {}
    s1 = sol1.code
    s2 = sol2.code
    print(sol1.filename+ " " + sol2.filename, len(s1), len(s2))
    for i in range(len(s1)+1):
        ans[i] = {}
        ans[i][0] = 0
    for j in range(len(s2)+1):
        ans[0][j] = 0
    for i in range(1, len(s1)+1):
        for j in range(1, len(s2)+1):
            if s1[i-1] == s2[j-1]:
                ans[i][j] = ans[i-1][j-1] + 1
            else:
                ans[i][j] = max(ans[i-1][j], ans[i][j-1])
    finalAns = ans[len(s1)][len(s2)]
    length = max(len(s1), len(s2))
    eps = max(length // 100, 2)
    return finalAns >= length - eps

def add_to_graph(gr, a, b, prob):
    if not a in gr.keys():
        gr[a] = {}
    if not b in gr[a].keys():
        gr[a][b] = [0, []]
    if prob in gr[a][b][1]:
        return
    gr[a][b][0] += 1
    gr[a][b][1].append(prob)

def process_problem(problem, graph):
    sols = list(SolutionList(problem))
    for sol1, sol2 in itertools.combinations(sols, 2):
        if (sol1.author != sol2.author) and compare(sol1, sol2):
            add_to_graph(graph, sol1.author, sol2.author, problem)
            add_to_graph(graph, sol2.author, sol1.author, problem)
            
def generate_output(gr):
    nodes = set()
    for v in gr.keys():
        nodes.add(v)
        for u in gr[v].keys():
            nodes.add(u)
    num = 0
    nodesNum = {}
    for v in nodes:
        nodesNum[v] = num
        num += 1
    print("nodedef>name VARCHAR,label VARCHAR")
    for v in nodesNum.keys():
        print("v%d, %s" % (nodesNum[v], v))
    print("edgedef>node1 VARCHAR,node2 VARCHAR, weight DOUBLE")
    for v in gr.keys():
        for u in gr[v].keys():
            print("v%d,v%d,%d" % (nodesNum[v], nodesNum[u], gr[v][u][0]))

#--------------------

graph = {}
processedNum = 0
problems = list(ProblemList('data'))
for f in problems:
    print(">",f,processedNum,"/", len(problems))
    processedNum += 1
    try:
        process_problem(f, graph)
    except KeyboardInterrupt:
        break

generate_output(graph)