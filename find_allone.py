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
        print(filename)
        self.filename = filename
        lines = open(filename,encoding="latin-1").readlines()
        self.author = lines[0].strip()
        self.code = " ".join(lines[2:])
        self.tokens = self.splitCode(self.code)
        self.tokens = [x for x in self.tokens if x!='']
        self.conv = {}
        i = 0
        self.tokens_conv = []
        for t in self.tokens:
            if not t in self.conv:
                self.conv[t] = str(i)
                i = i + 1
            self.tokens_conv.append(self.conv[t])

    def __str__(self):
        return self.author + ": " + str(self.tokens)
    
    def splitCode(self, code):
        res = []
        curs = ''
        for ch in code:
            if ch.isalnum():
                curs += ch
            else:
                res.append(curs)
                curs = ''
                if not ch.isspace():
                    res.append(ch)
        res.append(curs)
        return res

def add_to_graph(gr, a, b, prob):
    if not a in gr.keys():
        gr[a] = {}
    if not b in gr[a].keys():
        gr[a][b] = [0, []]
    if prob in gr[a][b][1]:
        return
    gr[a][b][0] += 1
    gr[a][b][1].append(prob)
    
class Cacher:
    def __init__(self, graph):
        self.strs = {}
        self.maxlen = 50
        self.graph = graph
        self.found = {}
        
    def addStr(self, str, problem):
        #print(str)
        if not str in self.strs:
            self.strs[str] = []
        for (author, filename) in self.strs[str]:
            if author!=problem.author:
                key = author + ":" + problem.author + ":" + problem.filename
                if key in self.found:
                    continue
                self.found[key] = 1
                print("Found match ",author, problem.author, filename, problem.filename, "'"+str+"'")
                add_to_graph(self.graph, author, problem.author, filename + ":" + problem.filename)
        self.strs[str].append((problem.author, problem.filename))
    
    def processSolution(self,problem):
        #print(problem.filename)
        #print(problem.tokens_conv)
        #print(problem.tokens)
        if len(problem.tokens_conv)>10000:
            return
        for tokens in (problem.tokens, problem.tokens_conv):
            ts = []
            for t in tokens:
                if len(ts) >= self.maxlen:
                    str = ' '.join(ts)
                    self.addStr(str, problem)
                    ts = ts[1:]
                ts.append(t)
            if len(ts) >= self.maxlen // 2:
                str = ' '.join(ts)
                self.addStr(str, problem)
    
def process_problem(problem, graph, comparator, Comparator2):
    sols = list(SolutionList(problem))
    res = []
    for sol1, sol2 in itertools.combinations(sols, 2):
        if (sol1.author != sol2.author) and (
            comparator.compare(sol1, sol2) or
            comparator2.compare(sol1, sol2)):
            add_to_graph(graph, sol1.author, sol2.author, problem)
            add_to_graph(graph, sol2.author, sol1.author, problem)
            res.append((sol1.filename, sol2.filename))
    with open("list.txt","a") as f:
        f.write(problem + "\n")
        for r in res:
            f.write(str(r) + "\n")

def process_problem_cache(problem, graph):
    cacher = Cacher(graph)
    for sol in SolutionList(problem):
        cacher.processSolution(sol)
            
def generate_output(gr):
    mind = 5
    nodes = set()
    for v in gr.keys():
        for u in gr[v].keys():
            if gr[v][u][0]>mind:
                nodes.add(v)
                nodes.add(u)
    num = 0
    nodesNum = {}
    for v in nodes:
        nodesNum[v] = num
        num += 1
    with open("res.gdf","w",encoding="latin-1") as f:
        f.write("nodedef>name VARCHAR,label VARCHAR\n")
        for v in nodesNum.keys():
            f.write("v%d, %s\n" % (nodesNum[v], v))
        f.write("edgedef>node1 VARCHAR,node2 VARCHAR, weight DOUBLE\n")
        for v in gr.keys():
            for u in gr[v].keys():
                if gr[v][u][0]>mind:
                    f.write("v%d,v%d,%d\n" % (nodesNum[v], nodesNum[u], gr[v][u][0]))

#--------------------

graph = {}
processedNum = 0
#problems = list(ProblemList('data'))
#comparator = Comparator2("cache.txt")
#comparator2 = Comparator("cache2.txt")
#for f in problems:
#    print(">",f,processedNum,"/", len(problems))
#    processedNum += 1
#    process_problem(f, graph, comparator, comparator2)
process_problem_cache('data', graph)
generate_output(graph)