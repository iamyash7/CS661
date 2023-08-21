Dependencies required for this python script are vtk library, numpy library, scipy library, random and time. Also argparse module is imported to take arguments from command line.
I have also included requirements.txt file inside, you can install dependencies from it.

Once the dependencies are installed, the script can be run using the following command:

	python yash_A4.py --percentage <percentage> --method <method>
	
	
Here: in place of <percentage> you have to enter sampling percentage. 
and in place of <method> you have enter reconstruction method. Valid inputs are {linear,nearest}

Example command:

python yash_A4.py --percentage 1 --method linear ==>This command will perform sampling for 1% data and will use linear method to do reconstruction from sample data.

The output of the script is a sample.vtp (VTKPolyData) file and reconstructed_data.vti(VTKImageData) file.
sample.vtp file contains sampled points and reconstructed_data.vti file contains reconstructed data. Both these files can be viewed in Paraview.

Note: If you will run this script without arguments then by default the sampling percentage will be 1% and method will be nearest.
Reconstruction time and  SNR is mentioned in PDF. The time and snr varies from system to system. Variance is not much but it does varies.
