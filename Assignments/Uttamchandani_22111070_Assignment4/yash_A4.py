#Importing required libraries.
from vtk import *
import random
import numpy as np
from scipy.interpolate import griddata
import time
import argparse

# Add two optional arguments to the parser: --percentage and --method
parser = argparse.ArgumentParser()
parser.add_argument('--percentage', type=float, help='percentage of data points to sample from the original data')
parser.add_argument('--method', help='interpolation method to use for reconstruction')
args = parser.parse_args()
#default values , if someone runs script without arguments
percentage=1
method='nearest'

if(args.percentage!=None and args.method!=None):
    percentage = args.percentage # percentage of data points to sample from the original data
    method = args.method # interpolation method to use for reconstruction


def load_data(dataset):
    # Load dataset 
    reader = vtkXMLImageDataReader()
    reader.SetFileName(dataset)
    reader.Update()
    data = reader.GetOutput()
    return data
    

    
    
data=load_data('Isabel_3D.vti')#call function to load dataset

numOfPoints=data.GetNumberOfPoints() # get number of points in the dataset
pressureArr=data.GetPointData().GetArray('Pressure') # get pressure array 

print('Initiating Data Sampling....')

x,y,z=data.GetDimensions() # get dimensions of the dataset
arr_values=[] # empty list to store pressure values of sampled points

# Function to randomly sample a percentage of points from the original dataset
def random_sample(percentage):
    sample_data=set() # empty set to store coordinates of sampled points
    global x,y,z
    sample=int(numOfPoints*percentage/100)
    corner = np.array([(0, 0, 0), (x-1, 0, 0), (0, y-1, 0), (x-1, y-1, 0), 
                              (0, 0, z-1), (x-1, 0, z-1), (0, y-1, z-1), (x-1, y-1, z-1)])
    for i in corner:
        sample_data.add(tuple(i))
    while(len(sample_data)!=sample):
        num=random.randint(0,numOfPoints-1)
        sample_data.add(data.GetPoint(num))
    for i in sample_data:
        arr_values.append(pressureArr.GetValue(data.FindPoint(i)))
        
    return sample_data
    
sample_data=random_sample(percentage) #calls function to randomly sample points

print('Data Sampling Done for {}% data!!'.format(percentage))

# create a VTK data array and insert values from the arr_values list and set it as the pressure array 
dataArray = vtkFloatArray()
dataArray.SetName('Pressure')
for value in arr_values:
    dataArray.InsertNextValue(value)

# create a VTK points object from the sample_data list and set it as the points for a VTK polydata object
points=vtkPoints()
polyData=vtkPolyData()
for i in (sample_data):
    points.InsertNextPoint(i)
polyData.SetPoints(points)
polyData.GetPointData().SetScalars(dataArray)

# write the data to file
writer = vtkXMLPolyDataWriter()
writer.SetInputData(polyData)
writer.SetFileName('sample.vtp')
writer.Write()
    
# create original_points array 
orig_points=[]
for i in range(numOfPoints):
    orig_points.append(np.array(data.GetPoint(i)))
orig_points=np.array(orig_points)

# Define a function to perform nearest interpolation
def nearest(sample_data):
    reconstructed_data=[] # empty list to store reconstructed data
    # Record the time taken to perform the reconstruction
    t1 = time.time()
    # Perform the nearest interpolation using the sample data and its values
    sample_data=list(sample_data)
    reconstructed_data = griddata(sample_data, arr_values, orig_points, method='nearest')
    t2 = time.time()
    reconstructed_data=reconstructed_data.reshape((x,y,z))
    print('Reconstruction time using nearest method:', t2 - t1, 'seconds')
    
    return reconstructed_data

# Define a function to perform linear interpolation
def linear(sample_data):
    
    reconstructed_data=[] # empty list to store reconstructed data
    # Record the time taken to perform the reconstruction
    t1 = time.time()
    # Perform the linear interpolation using the sample data and its values
    sample_data=list(sample_data)
    reconstructed_data = griddata(sample_data, arr_values, orig_points, method='linear')
    reconstructed_data=reconstructed_data.reshape((x,y,z))
    #Handles nan values if any
    if(np.isnan(reconstructed_data).sum()>0):
        # Perform nearest interpolation on the NaN values
        nearest_arr=griddata(sample_data, arr_values, orig_points,method='nearest')
        nearest_arr=nearest_arr.reshape((x,y,z))
        # Replace NaN values with the interpolated values
        reconstructed_data = np.where(np.isnan(reconstructed_data),nearest_arr,reconstructed_data)
    t2 = time.time()    
    print('Reconstruction time using linear method:', t2 - t1, 'seconds')
    
    return reconstructed_data
    
    

# Check which interpolation method to use
if(method=='linear'):
    # If linear interpolation is to be used, call the linear function
    reconstructed_data=linear(sample_data)
else:
    # Otherwise, call the nearest function
    reconstructed_data=nearest(sample_data)
    
# Create a vtkImageData object and Set its Dimensionsz spacing, Origin.
imageData = vtkImageData()
imageData.SetDimensions(x, y, z)
imageData.SetSpacing(1, 1, 1)
imageData.SetOrigin(0, 0, 0)

# Create a vtkFloatArray object to store the reconstructed data values
data_array = vtkFloatArray()
data_array.SetNumberOfValues(x * y * z)
data_array.SetName('Pressure')

# Iterate over each point in the 3D grid
for i in range(x):
    for j in range(y):
        for k in range(z):
            # Calculate the index of the point in the vtkFloatArray object
            index = i * y * z + j * z + k
            # Set the value of the point in the vtkFloatArray object to the corresponding value in the reconstructed data
            data_array.SetValue(index, reconstructed_data[i][j][k])
            
# Add the pressure array to the point data of imageData

imageData.GetPointData().SetScalars(data_array)

# write the data to file
writer = vtkXMLImageDataWriter()
writer.SetInputData(imageData)
writer.SetFileName('reconstructed_data.vti')    
writer.Write()

#Defining a function to compute signal-to-noise ratio (SNR)
def compute_SNR(arrgt,arr_recon) :
    arrgt=np.array(arrgt)
    arr_recon=np.array(arr_recon)
    diff = arrgt - arr_recon
    sqd_max_diff = (np.max(arrgt)-np.min(arrgt))**2
    snr = 10*np.log10(sqd_max_diff/np.mean(diff**2))
    return snr

data=load_data('reconstructed_data.vti') #loads Reconstructed Data
#Gets Pressure Array from Reconstructed data
pressureNew=data.GetPointData().GetArray('Pressure')
#Computing the SNR between the original pressure array and the reconstructed pressure array
snr=compute_SNR(pressureArr,pressureNew)
print('SNR is:',snr)
