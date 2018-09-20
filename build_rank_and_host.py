
num_nodes = int(sys.argv[1])
def_ranks=sys.argv[2]
nodefile = os.environ.get("PBS_NODEFILE")
nodes = []


with open(nodefile) as f:
    i = 0
    a = f.readline()[:-1]
    nodes.append(a)
    while(i<num_nodes-1):
        a = f.readline()[:-1]
        if a != nodes[i]:
            nodes.append(a)
            i+=1
    f.close()
h = open("hostfile.txt", "w+")
for node in nodes:
    h.write(node+'\n')
h.close()

w = open("new_rankfile.txt", "w+")
with open(def_ranks) as f:

    #line will say rank 1=node0 slot0:00, i need to replace all instances of node0 with nodes[0], node1 with nodes[1], etc.     
    for line in f:
        a=line.find('=')
        b=line.find(' ', a)
        c = int(line[a+5:b])
        new_line = line[:a+1] + nodes[c] + line[b:]
        w.write(new_line)

