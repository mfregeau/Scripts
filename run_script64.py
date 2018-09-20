import sys, getopt, os

def usage():
    print "-p NUM_OF_PROCESSES"
    print "-n NUM_OF_NODES"
    print "--phase1-patt=0 or 1 or 2 (CPU, GPU, CPUGPU)"
    print "--phase2-patt=0 or 1 or 2 (CPU, GPU, CPUGPU)"
    print "Actual host names should be in hostnames.txt"

def build_hostnames(path):
    if "PBS_NODEFILE" in os.environ:
        os.system("sort $PBS_NODEFILE | uniq > " + path + "hostnames.txt")
    else:
        print "PBS_NODEFILE not defined. Skipping hostnames.txt build"

def build_def_host(np, nn, path):
    ranks_per_node = np / nn
    with open(path + "hostnames.txt", "r") as fh:
        with open(path + "def_hostfile.txt", "w") as f:
            hostnames = fh.read().splitlines()
            for host in hostnames:
                for i in range(ranks_per_node):
                    f.write(host + "\n")

def build_def_rank(np, nn, ns, path):
    ranks_per_node = np / nn
    ranks_per_socket = ranks_per_node / ns
    r = 0
    with open(path + "hostnames.txt", "r") as fh:
        with open(path + "def_rankfile.txt", "w") as f:
            hostnames = fh.read().splitlines()
            for host in hostnames:
                for s in range(ns):
                    for c in range(ranks_per_socket):
                        f.write("rank " + str(r) + "=" + host + \
                                " slot="+str(s)+":"+str(c) + "\n")
                        r = r + 1

def build_def_gpuid(np, nn, path):
    ranks_per_node = np / nn
    with open(path + "def_gpuidfile.txt", "w") as f:
        for node in range(nn):
            for r in range(ranks_per_node):
                f.write(str(r) + "\n")


def build_def_files(np, nn, ns, path):
    build_def_host(np, nn, path)
    build_def_rank(np, nn, ns, path)
    build_def_gpuid(np, nn, path)


prefix = "./"
np = ""
nn = ""
ns = 2
print "Assuming 2 sockets on each node"
phase1_patt = ""
phase2_patt = ""
exec_file = prefix + "tacmga2"

try:
    options, arguments = getopt.getopt(sys.argv[1:], "hp:n:", ["phase1-patt=", "phase2-patt="])
except getopt.GetoptError:
    print "Eroor in input options or arguments"
    sys.exit(2)

for opt, val in options:
    if opt == "-h":
        usage()
        sys.exit()
    if opt == "-p":
        np = val
    elif opt == "-n":
        nn = val
    elif opt == "--phase1-patt":
        phase1_patt = val
    elif opt == "--phase2-patt":
        phase2_patt = val
try:
    int(np)
    int(nn)
except:
    print "Invalid number of processes or nodes!"
    usage()
    sys.exit()


######## Start #########
patt_dir = "/home/mfregeau/MPI_Acc_bench_scripts/23_MICROBENCHMARKS_PARCO/RUN/mac_patts/"+np+"/"
out_dir = prefix + "new_output_files/live_run/"+np+"/"

#building hostnames.txt file
build_hostnames(out_dir)

#building the default hostfile, rankfile, and gpuid files
build_def_files(int(np), int(nn), int(ns), out_dir)

#bench_list = ["chain", "eam", "eim", "phosphate", "lj"]
bench_list = ["2D_2D_nw", "2D_2D_w", "2D_2D_nwc", "2D_2D_wc", "3D_3D_nw",  "3D_3D_w", "3D_3D_nwc", "3D_3D_wc", "2D_3D_nw", "2D_3D_w", "2D_3D_nwc", "2D_3D_wc"]
#bench_list=["COL_COL_nw"]
#size_list = [("2", "2", "2"), ("4", "4", "4")]
size_list = [("4", "4", "4")]

#for bench in bench_list:
    #for x, y, z, in size_list:
    
#    bench_str = bench
   # bench_str = bench + "_" + x + "x" + y + "x" + z
#    env_list = ""
#    env_list = env_list + " SHM_CPU_VOL_FILE=" + patt_dir + bench_str + "_64_cpu_cnt_out.txt"
#    env_list = env_list + " SHM_GPU_VOL_FILE=" + patt_dir + bench_str + "_64_gpu_cnt_out.txt"
    #env_list = env_list + " SHM_GLOB_CPU_PHY_FILE=" + patt_dir + "cpu_glob_dist.txt"
    #env_list = env_list + " SHM_GLOB_GPU_PHY_FILE=" + patt_dir + "gpu_glob_dist.txt"
#    env_list = env_list + " SHM_GPU_PHY_FILE=" + patt_dir + "gpu_phy.txt"
#    env_list = env_list + " SHM_CPU_PHY_FILE=" + patt_dir + "cpu_phy.txt"
#    env_list = env_list + " SHM_PHASE_1_USE_PATTERN=" + phase1_patt
#    env_list = env_list + " SHM_PHASE_2_USE_PATTERN=" + phase2_patt
    #env_list = env_list + " IMI_NORM_MAX="
    
#    env_list = env_list + " SHM_RANK_FILE=" + out_dir + "rankfile_" + bench_str + ".txt"
#    env_list = env_list + " SHM_HOST_FILE=" + out_dir + "hostfile_" + bench_str + ".txt"
#    env_list = env_list + " IMI_GPUID_FILE=" + out_dir + "gpuidfile_" + bench_str + ".txt"
#    env_list = env_list + " SHM_HOST_NAMES_FILE=" + out_dir + "hostnames.txt"
#    env_list = env_list + " IMI_NORM_MAX=0"
    #print env_list
#    bash_cmd = "export " + env_list
#    run_cmd = exec_file + " " + np + " " + nn
#    print run_cmd
#    bash_cmd = bash_cmd + " && " + run_cmd
#    os.system(bash_cmd)

