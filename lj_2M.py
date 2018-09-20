import hoomd
import hoomd.md
import os

rank = int(os.getenv("OMPI_COMM_WORLD_RANK"))
gpu = rank%16
options = "--gpu={}".format(gpu)

hoomd.context.initialize(options);

hoomd.init.create_lattice(unitcell=hoomd.lattice.sc(a=2.0), n=[128, 128, 128]);

nl = hoomd.md.nlist.cell();
lj = hoomd.md.pair.lj(r_cut=2.5, nlist=nl);

lj.pair_coeff.set('A', 'A', epsilon=1.0, sigma=1.0);

hoomd.md.integrate.mode_standard(dt=0.005);

all = hoomd.group.all();
hoomd.md.integrate.langevin(group=all, kT=0.2, seed=42);

hoomd.analyze.log(filename="log-output.log",
	    quantities=['potential_energy', 'temperature'],
	    period=100,
	    overwrite=True);

hoomd.run(1e6);


