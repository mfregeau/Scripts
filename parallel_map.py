import copy
import sys
import itertools
import os
from mpi4py import MPI
from operator import itemgetter
import numpy as np
import time
import math

MAX_SLOTS = 10
SLOT0 = [0, 1, 2, 3, 4, 5, 6, 7, 16, 17, 18, 19, 20, 21, 22, 23, 32, 33, 34, 35, 36, 37, 38, 39, 48, 49, 50, 51, 52, 53, 54, 55]
SLOT1 = [8, 9, 10, 11, 12, 13, 14, 15, 24, 25, 26, 27, 28, 29, 30, 31, 40, 41, 42, 43, 44, 45, 46, 47, 56, 57, 58, 59, 60, 61, 62, 63]

def build_rankfile_16(mapping, filename):
	size = len(mapping)
	f = open(filename, 'w')
	rank = 0
	for line in range(size):
		machine_number = mapping[line]/16
		to_write = "rank " + str(rank) + "=" + str(machine_number) + " slot=" + str(mapping[line]/8) + ":" + str(mapping[line]%8) + "\n"
		f.write(to_write)
		rank += 1

def build_rankfile_64(mapping, filename):
	size = len(mapping)
	f = open(filename, 'w')
	rank = 0
	for line in range(size):
		if(size == 16):
			machine_number=0
		else:
			machine_number = int(math.floor(int(mapping[line])/16))
		if(mapping[line] in SLOT0):
			slot = 0
		else:
			slot = 1
		
		to_write = "rank " + str(rank) + "=" + str(machine_number) + " slot=" + str(slot) + ":" + str(mapping[line]%8) + "\n"
		f.write(to_write)
		rank += 1  




def build_gpuidfile(mapping, filename):
	size = len(mapping)
	f = open(filename, 'w')

	for line in range(size):
		f.write(str(mapping[line]%16) + "\n")



def generate_matrix(patt_file):
	text_file = open(patt_file, 'r')
	patt_mat = []

	for line in text_file:
		line_comms = line.split()
		line_comms = [float(x) for x in line_comms]
		patt_mat.append(line_comms)

	return patt_mat

def read_rankfile(rankfile, size):
	f = open(rankfile, 'r')
	new_mapping = list(range(size))
	i = 0
	mult = 1
	machines = []
	for line in f:
		machine = int(line[-11])
		if machine not in machines:
			machines.append(machine)
		space = line.index(' ')
		end = line.index('=')
		rank = int(line[space+1:end])
		if(size==64):
			new_rank = (int(line[-4:-3])*8 + int(line[-2:-1]))+16*(machines.index(machine))
		elif(size == 16):
			new_rank = int(line[-4:-3])*8 + int(line[-2:-1])
		new_mapping[rank] = new_rank
		if(size==64):
			i+= 1
		if(i%15==0):
			mult += 1
			i=0
	return new_mapping

def read_gpuidfile(gpuidfile, cpu_mapping, size):
	f = open(gpuidfile, 'r')
	mapping = []
	for i in range(size):
		mapping.append(0)
	
	j = 0
	
	for line in f:
		cpu_loc = cpu_mapping[j]
		machine_num = cpu_loc/16
		mapping[cpu_loc]=int(line[:-1])+16*(machine_num)
		j+=1
		


	return mapping

def get_mapped_pat(mapping, comm_matt):

	new_patt=[]
	for i in range(len(mapping)):
		proc = []
		for j in range(len(mapping)):
			proc.append(0)

		new_patt.append(proc)


	i = 0
	for process in comm_matt:
		j = 0
		for message in process:
			new_patt[mapping.index(i)][mapping.index(j)] = message
			j+=1
		i+=1
		
	return new_patt

def get_delta(comm_mats, unmapped_ranks, mapped_ranks, target): #candidate for optimization
	size = len(comm_mats[0][0])
	delta = 0
	target = int(target)
	for rank in unmapped_ranks:
		rank = int(rank)
		delta -= comm_mats[0][target][rank]
		delta -= comm_mats[0][rank][target]
		delta -= comm_mats[1][target][rank]
		delta -= comm_mats[1][rank][target]

	for rank in mapped_ranks:
		rank = int(rank)
		delta += comm_mats[0][target][rank]
		delta += comm_mats[0][rank][target]
		delta += comm_mats[1][target][rank]
		delta += comm_mats[1][rank][target]

	return delta




def zero_comm_patt(comm_pat, remap): #candidate for optimization
	patt = [[0]*len(remap)]*len(remap)
	zero = [0]*len(remap)
	num = len(remap)
	count = 0

	for proc in remap:
		if proc is None:
			patt[count] = zero
			for row in patt:
				row[count] = 0
		else:
			patt[count] = [item for item in comm_pat[count]]
		count += 1

	
	return patt

def get_partial_dilation(dist_mat, comm_mat, temp_remapping): #candidate for optimization

	partial_comms_cpu = zero_comm_patt(comm_mat[0], temp_remapping)
	partial_comms_gpu = zero_comm_patt(comm_mat[1], temp_remapping)


	count = 0
	dilation = 0
	for process in temp_remapping:
		proc_dilation = 0
		if process is not None:
			dest_proc = 0
			for message_count_cpu, message_count_gpu in zip(partial_comms_cpu[count], partial_comms_gpu[count]):
				if temp_remapping[dest_proc] is not None:
					temp = (message_count_cpu * dist_mat[0][temp_remapping[count]][temp_remapping[dest_proc]]) + (message_count_gpu * dist_mat[1][temp_remapping[count]][temp_remapping[dest_proc]])
					proc_dilation+= temp 
				dest_proc += 1
		dilation += proc_dilation
		count +=1
	del partial_comms_cpu
	del partial_comms_gpu
	return dilation


		
def get_target_processes(comm_mats, unmapped_processes, mapped_processes):
	max_delta = -10000000000000
	equal_options = []
	for process in unmapped_processes:
		delta = get_delta(comm_mats, unmapped_processes, mapped_processes, process)
		unmapped_processes[process] = delta

	for process in unmapped_processes:
		if unmapped_processes[process] > max_delta:
			equal_options = [int(process)]
			max_delta = unmapped_processes[process]

		elif(unmapped_processes[process] == max_delta):
			equal_options.append(int(process))

	return equal_options


def map_next_process(mapping_data, target_process):
	potential_spots = []
	dilations  = []
	for pe in mapping_data["unnoccupied_pes"]:
		mapping_data["remapping"][target_process] = pe
		dilation = get_partial_dilation(mapping_data["dist_mat"], mapping_data["comm_mat"], mapping_data["remapping"])
		dilations.append((pe, dilation))

	best_dil = dilations[0][1]
	best_pe = dilations[0][0]
	for dilation in dilations:
		if dilation[1] < best_dil:
			best_pe = dilation[0]
			relevant_dil = dilation[1]
		
	mapping_data["remapping"][target_process] = best_pe

	del mapping_data["unmapped_processes"][str(target_process)]			
	mapping_data["unnoccupied_pes"].remove(best_pe)
	mapping_data["occupied_pes"].append(best_pe)
	mapping_data["mapped_processes"].append(target_process)
	return mapping_data, relevant_dil



def recursive_map(mapping_data, mappings, depth, starting_procs):
	if(depth == 0):
		my_equals = starting_procs
	else:
		equals = get_target_processes(mapping_data["comm_mat"], mapping_data["unmapped_processes"], mapping_data["mapped_processes"])
		my_equals = equals
	
	if depth >= MAX_DEPTH:
		my_equals = [my_equals[0]]

	
	for equal in my_equals:
		new_mapping_data, relevant_dil = map_next_process(copy.deepcopy(mapping_data), equal)

		if None not in new_mapping_data["remapping"]:
			mappings.append((new_mapping_data["remapping"], relevant_dil))
			return (new_mapping_data, mappings)
		else:
			recursive_map(new_mapping_data, mappings, depth+1, None)
	if(len(mappings)>0):
		sorted_maps = sorted(mappings, key=itemgetter(1))
		best_map = sorted_maps[0]
	
	else:
		best_map = ([], 1000000000000)
	best_maps = newcomm.gather(best_map, root=0)
		
	if(rank == 0):
		final_map = sorted(best_maps, key=itemgetter(1))
		return final_map[0]
	else:
		return None


	



if (len(sys.argv) != 8):
	print("Incorrect Usage: Program requires 7 inputs, a distance file(cpu and gpu), a communication pattern (cpu and gpu), a gpuidfile, a rankfile, and an output file name")
	pass

distances_cpu = sys.argv[1]
distances_gpu = sys.argv[2]
comm_patt_cpu = sys.argv[3]
comm_patt_gpu = sys.argv[4]

#outputs
gpuidfile = sys.argv[5]
rankfile = sys.argv[6]
MAX_DEPTH=int(sys.argv[7])


dist_mat_cpu = generate_matrix(distances_cpu)
dist_mat_gpu = generate_matrix(distances_gpu)
comm_mat_cpu = generate_matrix(comm_patt_cpu)
comm_mat_gpu = generate_matrix(comm_patt_gpu)
size = len(comm_mat_cpu[0])


temp_unmapped_processes = list(range(size))
unmapped_processes = {}
for proc in temp_unmapped_processes:
	unmapped_processes[str(proc)] = 0

unnoccupied_pes  = list(range(size))
mapped_processes = []
occupied_pes = []
remappings = []
remapping = [None]*size
mapping = {}
my_comm_mat_cpu = copy.deepcopy(comm_mat_cpu)
my_comm_mat_gpu = copy.deepcopy(comm_mat_gpu)
depth = 0
done = False

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
comm_size = comm.Get_size()

mapping_data = {"remapping":copy.deepcopy(remapping), "mapped_processes":copy.deepcopy(mapped_processes), "unnoccupied_pes":copy.deepcopy(unnoccupied_pes),
				 "unmapped_processes":copy.deepcopy(unmapped_processes), "comm_mat":[copy.deepcopy(my_comm_mat_cpu), copy.deepcopy(my_comm_mat_gpu)], "dist_mat":[dist_mat_cpu, dist_mat_gpu], "occupied_pes": copy.deepcopy(occupied_pes)}

equals = get_target_processes(mapping_data["comm_mat"], mapping_data["unmapped_processes"], mapping_data["mapped_processes"])
equals = np.array_split(equals, comm_size)
new_equals = []
for equal in equals:
	if(len(equal)>0):
		new_equals.append(list(equal))

my_equals = []
for i in range(len(new_equals)):
	if rank == i:
		my_equals = new_equals[i]


newcomm = MPI.COMM_WORLD.Split(rank<len(new_equals), rank)


if(rank == 0):
	start = time.perf_counter()
if(len(my_equals)>0):
	maps = recursive_map(mapping_data, [], 0, my_equals)
if(rank == 0):
	end = time.perf_counter()
	elapsed = end-start
	print("elapsed time = {:.12f} seconds, depth {}".format(elapsed, MAX_DEPTH))




if(rank == 0):
	best_mapping = maps[0]
	default = get_partial_dilation([dist_mat_cpu, dist_mat_gpu], [comm_mat_cpu, comm_mat_gpu], list(range(size)))
	opt = get_partial_dilation([dist_mat_cpu, dist_mat_gpu], [comm_mat_cpu, comm_mat_gpu], best_mapping)
	print("DEFAULT: ",default)
	print("CHOSEN MAPPING: ",best_mapping)
	print("MAPPED: ", opt)
	print(str((float(default-opt)/float(default))*100))
	build_rankfile_64(best_mapping, rankfile)
	build_gpuidfile(best_mapping, gpuidfile)





