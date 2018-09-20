#!/bin/bash
#SBATCH --account=dri-911-ab
#SBATCH --nodes=64
#SBATCH --gres=gpu:2
#SBATCH --ntasks-per-node=32
#SBATCH --mem=12700
#SBATCH --time=0-00:20

module load gcc/4.8.5
module load cuda/7.5.18

cd /home/mfregeau/from_helios/

python fix_node_names.py test_rankfile

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/cvmfs/soft.computecanada.ca/easybuild/software/2017/avx2/Compiler/gcc4.8/cuda/7.5.18/lib64/:/cvmfs/soft.computecanada.ca/easybuild/software/2017/avx2/Compiler/gcc4.8/cuda/7.5.18/lib64/stubs/

/home/mfregeau/bin/mpirun -np 6 -rf test_rankfile_p -mca pml ob1 ./test_ib_path >> ib_16K_latency_test.txt
