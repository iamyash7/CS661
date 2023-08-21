#import sys module and take argument from command line
import sys
phong=int(sys.argv[1])

# Import VTK library and Numpy
from vtk import *
import numpy as np

# Create a reader object to read the image data from file
reader = vtkXMLImageDataReader()
reader.SetFileName('Isabel_3D.vti')
reader.Update()

# Get the output data from the reader
data = reader.GetOutput()

# Get the point data and pressure array
pdata = data.GetPointData()

#Create a color transfer function object
colorFunc=vtkColorTransferFunction()

#Add color and corresponding data values to the transfer function
colorFunc.AddRGBPoint(-4931.54, 0, 1, 1)
colorFunc.AddRGBPoint(-2508.95, 0, 0, 1)
colorFunc.AddRGBPoint(-1873.9, 0, 0, 0.5)
colorFunc.AddRGBPoint(-298.031, 1, 0.4, 0)
colorFunc.AddRGBPoint(2594.97, 1, 1, 0)

#Create a piecewise function object for scalar opacity
opacity=vtkPiecewiseFunction()

#Add scalar opacity values at corresponding data point
opacity.AddPoint(-4931.54, 1.0)
opacity.AddPoint(101.815, 0.002)
opacity.AddPoint(2594.97, 0.0)

#Create a smart volume mapper object and set the input data
volumeMapper=vtkSmartVolumeMapper()
volumeMapper.SetInputData(data)

#Create a volume Property object and set the color transfer function and scalar opacity
volumeProperty=vtkVolumeProperty()
volumeProperty.SetColor(colorFunc)
volumeProperty.SetScalarOpacity(opacity)

if phong==1:
    #enable Phong shading and set the ambient, diffuse, and specular lighting components
    volumeProperty.ShadeOn();
    volumeProperty.SetAmbient(0.5)
    volumeProperty.SetDiffuse(0.5)
    volumeProperty.SetSpecular(0.5)    
    
#Create an outline filter object and set the input data
outlineFilter=vtkOutlineFilter()
outlineFilter.SetInputData(data)
outlineFilter.Update()

#Create a poly data mapper object and set its input connection to the outline filter output port
outlineMapper = vtkPolyDataMapper()
outlineMapper.SetInputConnection(outlineFilter.GetOutputPort())

#Create an actor object for the outline and set its mapper and color
outlineActor=vtkActor()
outlineActor.SetMapper(outlineMapper)
outlineActor.GetProperty().SetColor(0,0,0)

#Create a volume actor object and set its mapper and property
volumeActor=vtkVolume()
volumeActor.SetMapper(volumeMapper)
volumeActor.SetProperty(volumeProperty)

#Create a renderer object and add the outline and volume actors to it
renderer = vtkRenderer()
renderer.AddActor(outlineActor)
renderer.AddActor(volumeActor)

#Create a render window and set the renderer 
renderWindow = vtkRenderWindow()
renderWindow.AddRenderer(renderer)

#Create a render window interactor and set the render window
renderWindowInteractor = vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

#Set the background color and window size 
renderer.SetBackground(1,1,1)
renderWindow.SetSize(1000,1000)

#render the window and start the interactor
renderWindow.Render()
renderWindowInteractor.Start()