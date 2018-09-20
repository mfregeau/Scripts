#!/bin/bash
#PBS -A dri-911-ab
#PBS -l walltime=01:00:00
#PBS -l nodes=4:gpus=16
#PBS -l feature=k80


module load apps/python/3.5
source ~/MPI_Acc_bench_scripts/tacmga_dilation/test_par/timingEnv/bin/activate

cd /home/mfregeau/MPI_Acc_bench_scripts/tacmga_dilation/hoomd_tests/
module load compilers/gcc/4.8.5
module load cuda/7.5.18
module load mpi/openmpi/1.10.0 

 
python ~/MPI_Acc_bench_scripts/tacmga_dilation/fix_node_names.py ~/MPI_Acc_bench_scripts/tacmga_dilation/hoomd_tests/mapping/rankfile_hoomd_64_2M_0.txt


export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/software-gpu/cuda/6.0.37/lib64/
export PYTHONPATH=$PYTHONPATH:/home/mfregeau/hoomd/lib/python
export GPUID_FILE = ~/MPI_Acc_bench_scripts/tacmga_dilation/hoomd_tests/gpuidfile_hoomd_64_2M_0.txt
#for i in 0 2 4 8 12 14 16 20 24 30 36 
#do
mpirun -np 64 -rf ~/MPI_Acc_bench_scripts/tacmga_dilation/hoomd_tests/mappings/rankfile_hoomd_64_2M_0.txt_p python lj_2M_opt.py --mode=gpu > 2M_opt.txt
#done




