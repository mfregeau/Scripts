#!/bin/bash
#PBS -A dri-911-ab
#PBS -l walltime=02:00:00
#PBS -l nodes=4:gpus=16
#PBS -l feature=k80


module load compilers/gcc/4.8
module load cuda/7.5.18
module load mpi/openmpi/1.10.0
cd /home/mfregeau/MPI_Acc_bench_scripts/tacmga_dilation/results_aug/64/lat



 
python ~/MPI_Acc_bench_scripts/tacmga_dilation/fix_node_names.py ~/MPI_Acc_bench_scripts/tacmga_dilation/new_output_files/64/lat_pats/rankfile_2D_2D_nw.txt


export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/software-gpu/cuda/6.0.37/lib64/
export IMI_ENV_CYCLE=0
export IMI_GPUID_FILE=~/MPI_Acc_bench_scripts/tacmga_dilation/new_output_files/64/lat_pats/gpuidfile_2D_2D_nw.txt

echo "2D-2D Non Weighted Cluster Results">2D_2D_64_nw_results.txt

for i in 256 1024 4096 16384 65536 262144 1048576 4194304
do
    echo ">>>>>> Results, $i B <<<<<<" >> 2D_2D_64_nw_results.txt
    for q in 1 2 3
    do
	mpirun -np 64 -rf ~/MPI_Acc_bench_scripts/tacmga_dilation/new_output_files/64/lat_pats/rankfile_2D_2D_nw.txt_p ~/MPI_Acc_bench_scripts/23_MICROBENCHMARKS_PARCO/RUN/MICRO_BENCHMARK 64 1000 100 2DSTENCIL cpu $i 1 8 8 2DSTENCIL gpu $i 1 8 8 >> 2D_2D_64_nw_results.txt
    done
done




