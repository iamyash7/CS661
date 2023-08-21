#import sys module
import sys
isovalue = float(sys.argv[1])

# Import VTK library and Numpy 
from vtk import *
import numpy as np

# Create a reader object to read the image data from file
reader = vtkXMLImageDataReader()
reader.SetFileName('Isabel_2D.vti')
reader.Update()

# Get the output data from the reader
data = reader.GetOutput()

# Get the point data and pressure array
pdata = data.GetPointData()
pressureArr = pdata.GetArray('Pressure')

# Ask the user to input the isovalue
#isovalue=float(input('Enter Isovalue:'))


# Get the number of cells in the image data
n=data.GetNumberOfCells()

# Create a list of indices to access vertices in counter-clockwise order
count=[0,1,3,2]

# Create a cell array to hold the line segments
cellArray=vtkCellArray()

# Create a vtkPoints object to hold the points
points=vtkPoints()

# Create a vtkPolyData object to hold the generated points and lines
polydata = vtkPolyData()

# Loop through all the cells in the image data
for i in range (n):
    # Get the ID of the current cell
    cellId = i
    
    # Get the current cell 
    cell = data.GetCell(cellId)
    
    # Get the PointIds for the current cell
    pointIds = cell.GetPointIds()
    
    # Loop through all the edges of the current cell
    for j in range(4):
    
        # Get the pressure values for the vertices of the current edge
        pvalue1=pressureArr.GetTuple1(pointIds.GetId(count[j]))
        pvalue2=pressureArr.GetTuple1(pointIds.GetId(count[(j+1)%4]))
        
        if(pvalue1>isovalue and pvalue2<isovalue):
            # Calculate the interpolation factor
            tmp=(pvalue1-isovalue)/(pvalue1-pvalue2)
            
            # Get the coordinates of the two vertices of the current edge
            p2=data.GetPoint(cell.GetPointId(count[(j+1)%4]))
            p1=data.GetPoint(cell.GetPointId(count[j]))
            
            # Convert the coordinates to numpy arrays                
            p1=np.array(p1)
            p2=np.array(p2)
            
            # Calculate the coordinates of the intersection point            
            iso_point=(tmp*(p2-p1))+p1
            
            # Add the intersection point to the vtkPoints object            
            points.InsertNextPoint(iso_point)
            
        elif(pvalue1<isovalue and pvalue2>isovalue):
            # Calculate the interpolation factor            
            tmp=(pvalue2-isovalue)/(pvalue2-pvalue1)
            
            # Get the coordinates of the two vertices of the current edge
            p1=data.GetPoint(cell.GetPointId(count[(j+1)%4]))
            p2=data.GetPoint(cell.GetPointId(count[j]))
            
            # Convert the coordinates to numpy arrays
            p1=np.array(p1)
            p2=np.array(p2)
            
            # Calculate the coordinates of the intersection point
            iso_point=(tmp*(p2-p1))+p1
            
            # Add the intersection point to the vtkPoints object 
            points.InsertNextPoint(iso_point)
            
# Get the number of points from points object
n=points.GetNumberOfPoints()

# Create line segments connecting pairs of adjacent points in the list of isosurface intersection points
for i in range(0,n,2):

    # Create a new VTK poly line object and Set the point IDs to 2(to create line segments)
    polyLine = vtkPolyLine()
    polyLine.GetPointIds().SetNumberOfIds(2)
    
    #Set both points of Polyline
    polyLine.GetPointIds().SetId(0,i)
    polyLine.GetPointIds().SetId(1,i+1)
    
    # Add the poly line object to a VTK cell array
    cellArray.InsertNextCell(polyLine)
 
# Set the points and cells of the output polydata object
polydata.SetPoints(points)
polydata.SetLines(cellArray)

#Store the polydata into a vtkpolydata file with extension .vtp
writer = vtkXMLPolyDataWriter()
writer.SetInputData(polydata)
writer.SetFileName('output.vtp')
writer.Write()
