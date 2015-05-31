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
        filenameParts = filename.split("-")
        self.author = filenameParts[2]
        #print(self.author)
        lines = open(filename,encoding="latin-1").readlines()
        self.code = " ".join(lines)
        self.tokens = self.code.split()

    def __str__(self):
        return self.author + ": " + str(self.tokens)

class Comparator:
    cache = {}
    
    def __init__(self, cacheFile):
        self.loadCache(cacheFile)
        self.cacheFile = open(cacheFile, "w")
        
    def loadCache(self, cacheFile):
        self.cache = {}
        if not os.path.isfile(cacheFile):
            return
        lines = open(cacheFile).readlines()
        for line in lines:
            (sol1, sol2, res) = line.split()
            res = (res == str(True))
            self.cache[sol1 + ":" + sol2] = res
            print("Restored from cache: ", sol1, sol2, res, res)
            
    def writeToCache(self, sol1, sol2, res):
        self.cacheFile.write(sol1.filename + " " + sol2.filename + " " + str(res)+"\n")
        self.cacheFile.flush()
        
        
    def compare(self, sol1, sol2):
        key = sol1.filename + ":" + sol2.filename
        #print("check key: " + key)
        if key in self.cache.keys():
            res = self.cache[key]
            self.writeToCache(sol1, sol2, res)
            print("Cache match: ", sol1.filename, sol2.filename, res)
            return res
        ans = {}
        s1 = sol1.code
        s2 = sol2.code
        #print(sol1.filename+ " " + sol2.filename, len(s1), len(s2))
        for i in range(len(s1)+1):
            ans[i] = {}
            ans[i][0] = 0
        for j in range(len(s2)+1):
            ans[0][j] = 0
        length = max(len(s1), len(s2))
        eps = max(length // 30, 3)
        earlyFail = False
        if (length < 120) or (length > 5000):
            if (length > 5000) and (length < 20000):
                print("Intermediate length!", sol1.filename, sol2.filename)
            earlyFail = True
        else:
            for i in range(1, len(s1)+1):
                for j in range(1, len(s2)+1):
                    if s1[i-1] == s2[j-1]:
                        ans[i][j] = ans[i-1][j-1] + 1
                    else:
                        ans[i][j] = max(ans[i-1][j], ans[i][j-1])
                j = i
                if j > len(s2):
                    j = len(s2)
                if ans[i][j] < i - 3 * eps:
                    earlyFail = True
                    break
        if not earlyFail:
            finalAns = ans[len(s1)][len(s2)]
        else:
            finalAns = -eps*2
        res = (not earlyFail) and (finalAns >= length - eps)
        if res:
            print("Match: ", sol1.filename, sol2.filename, ans[len(s1)][len(s2)], length)
        self.cache[key] = res
        self.writeToCache(sol1, sol2, res)
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

def process_problem(problem, graph, comparator):
    sols = list(SolutionList(problem))
    res = []
    allPairs = list(itertools.combinations(sols, 2))
    total = 0
    for sol1, sol2 in allPairs:
        total += 1
        if (total % 1023 == 0):
            print(problem, total, "/", len(allPairs))
        if (sol1.author != sol2.author) and comparator.compare(sol1, sol2):
            add_to_graph(graph, sol1.author, sol2.author, problem)
            add_to_graph(graph, sol2.author, sol1.author, problem)
            res.append((sol1.filename, sol2.filename))
    with open("list.txt","a") as f:
        f.write(problem + "\n")
        for r in res:
            f.write(str(r) + "\n")
            
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
    with open("res.gdf","w",encoding="latin-1") as f:
        f.write("nodedef>name VARCHAR,label VARCHAR\n")
        for v in nodesNum.keys():
            f.write("v%d, %s\n" % (nodesNum[v], v))
        f.write("edgedef>node1 VARCHAR,node2 VARCHAR, weight DOUBLE\n")
        for v in gr.keys():
            for u in gr[v].keys():
                if gr[v][u][0]>2:
                    f.write("v%d,v%d,%d\n" % (nodesNum[v], nodesNum[u], gr[v][u][0]))

#--------------------

graph = {}
processedNum = 0
problems = list(ProblemList('data'))
comparator = Comparator("cache.txt")
for f in problems:
    print(">",f,processedNum,"/", len(problems))
    processedNum += 1
    process_problem(f, graph, comparator)
    generate_output(graph)
