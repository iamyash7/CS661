The first python script takes an isovalue as an input parameter and outputs the extracted contour as a *.vtp (VTKPolyData) file.


Dependencies required for this python script are vtk library and numpy library. Also sys module is imported to take arguments from command line.
Once the dependencies are installed, the script can be run using the following command:
	python Part_1.py <isovalue>
Here: in place of <isovalue> you have to give value.
Example command:
python Part_1.py 0 ==>This command will extract contour for isovalue 0.


The output of the script is a *.vtp (VTKPolyData) file that contains the extracted contour. The file can be opened in ParaView for visualization and analysis.
Note: The ambiguities are not handled.(As per assignment)

The second Python script takes an input input parameter as to whether the user wants to use Phong shading or not.

The script can be run using the following command:
	python Part_2.py <Phong Value>
Here: in place of Phong Value you have to give 1 to enable phong shading and 0 to disable phong Shading.
Example commands:
python Part_2.py 0 ==> This command will disable phong shading while rendering
python Part_2.py 1 ==> This command will enable phong shading while rendering

The output of this script will be rendered image.