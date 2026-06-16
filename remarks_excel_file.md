General remarks: Recheck in slides of lecture 5 how the coordinate system of the probing traverse works. The x axis starts at the beginning of the tunnel (upwind side). X/Y/Z = 0/0/0 is the home position of the traversing system. Home position is at hub height, in a down wind distance (x) of 0.5D (1D = 1100 mm) directly behind the rotor center.

Requested windspeed has to be in steps of 0.5 m/s starting at lowest possibe wind speed (check with constraints) since it is not possible to set the wind speed that finely. In task 1 that might lead to less measurement points, but is fine as 30 is the maximum number of points.

The test matricies should be ordered by wind speeds, since that will be the hardest paramter to set in the wind tunnel. 

For task 2: We are actually allowed to also perform measurements in z- direction. Decision: We stick with the calculated x (downwind distance) and want to also perform measurements in the z direction to span a plane in x-z. This plane needs to cover reasonable points (e.g. a circle in this plane and other valid points in the plane) to properly graph and model the wake. 

In task 2 we should have a requested wind speed of 5,4 m/s. In current implementation we wrongly set the 5,4 m/s for the equivalent free air speed. 

For task 2 we need to generate a tab seperated .txt file containaing the X / Y / Z positions of the traversing system which the measurement probes are attached to. Check slide 21 in lecture 3 for this.




Points from simone after calibration lab
1. Use the same blockage correction for all yaw situations! Use the blockage from the 0° yaw situation

2. For positioning the y/z plane in the wake measurements. If you want to place another turbine in the 4D plane maybe consier measuring there as well. 

3. We will have 4 data files

4. speed traverse: y/z (4cm per second) , x (1/4 of this) is super slow. 


