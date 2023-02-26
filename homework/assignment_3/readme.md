# Homework 3

Hi all,

For the next week, I would like you to work on the following assignments:

1) Create a simulation with a layered model. For instance, try with three layers. You can keep the rest of the parameters as in the example. Remember that you'll need to change the interfaces.dat, the material definition in the Par_file, and the definition of the regions in the Par_file for the internal mesher. For the material, use the following properties:

1 1 2200.d0 2200.d0 1343.375d0 0 0 9999 9999 0 0 0 0 0 0

2 1 2200.d0 2500.d0 1443.375d0 0 0 9999 9999 0 0 0 0 0 0

3 1 2700.d0 3000.d0 1800.0d0 0 0 9999 9999 0 0 0 0 0 0

Analyze the results of the mesh (histogram of points per wavelength). You can try to optimize it. Optimizing the internal mesher of specfem2d is only possible in the vertical direction, so you have to be careful with the aspect ratio of the elements (~0.8). (We can discuss your results/questions about this assignment on tuesday). Also, if you didn't work on the assignment for today, I recommend working on it and analyzing the results you got in terms of the mesh and the seismograms, so you have a good understanding of the effect your mesh can have in the resolution of your simulations.

2) Look at the jupyter notebook for computing the kernel. Try computing your own kernel; you can play with the material properties and boundary conditions (for instance, you can consider a free surface). And you can also try different misfit functions for computing the kernel. You can read the following articles to understand better the adjoint method and different misfit functions you can use.

https://academic.oup.com/gji/article/160/1/195/712020 Links to an external site.  (Tromp et al. 2005)

https://onlinelibrary.wiley.com/doi/full/10.1111/j.1365-246X.2011.04970.x Links to an external site.  (Bozdağ et al. 2011)

Next week we'll start working with seisflows to run a full waveform inversion case.

See you next thursday,

AR
