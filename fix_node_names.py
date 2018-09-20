import sys, os
import fileinput

rankfile = sys.argv[1]

pbs = os.getenv("PBS_NODEFILE")

f = open(pbs, 'r')
r = open(rankfile, "r")
proper = rankfile+"_p"
p = open(proper, "w+")

nodes = []

for line in f:
	if line[0:-1] not in nodes:
		nodes.append(line[0:-1])


for line in r:
	a = line.find('=')
	b = line.find(' ', a)
	c = int(line[a+1:b])
	new_line = line[:a+1] + nodes[c] + line[b:]
	p.write(new_line)
