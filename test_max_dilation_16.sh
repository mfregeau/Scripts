#!/bin/bash
#PBS -A dri-911-ab
#PBS -l walltime=00:05:00
#PBS -l nodes=1:gpus=16
#PBS -l feature=k80


module load compilers/gcc/4.8
module load cuda/7.5.18
module load mpi/openmpi/1.10.0
cd /home/mfregeau/MPI_Acc_bench_scripts/tacmga_dilation


. exports.sh
python ~/MPI_Acc_bench_scripts/tacmga_dilation/run_script.py -p 16 -n 1 --phase1-patt=2 --phase2-patt=2
 

cat ${PBS_NODEFILE} > nodes_16.txt
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/software-gpu/cuda/6.0.37/lib64/

export IMI_GPUID_FILE=~/MPI_Acc_bench_scripts/tacmga_dilation/new_output_files/16/gpuidfile_2D_2D.txt
echo "2D-2D results, 256B" > 2D_16_opt_results.txt 
mpirun -np 16 -rf ~/MPI_Acc_bench_scripts/tacmga_dilation/new_output_files/16/rankfile_2D_2D.txt ~/MPI_Acc_bench_scripts/23_MICROBENCHMARKS_PARCO/RUN/MICRO_BENCHMARK 16 1000 100 2DSTENCIL cpu 256 1 4 4 2DSTENCIL gpu 256 1 4 4 >> 2D_16_opt_results.txt 



