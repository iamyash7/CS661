import itk 
from vtk import *
CST_PATH_IN_VOLUME = "./BRATS_HG0015_T1C.mha"
CST_PATH_OUT_MASK = "./_mask.mha"

seg_max,seg_min=0,0
MORPHO_FILTERS = [
        ("NumberOfPixels", 10, False),
        ("Flatness", 5, True),
        ("NumberOfPixels", 3, False),
    ]
volume = vtkVolume()    
mapper = vtkFixedPointVolumeRayCastMapper()
volume.SetMapper(mapper)
volume_mapper = volume.GetMapper()

iren = vtkRenderWindowInteractor()
renWin = vtkRenderWindow()
ren = vtkRenderer()
fct_color_default = vtkColorTransferFunction()
fct_opacity_mask = vtkPiecewiseFunction()
fct_color_mask = vtkColorTransferFunction()
fct_opacity_default = vtkPiecewiseFunction()

def morpho_filters(image, filters):
    """
    Apply multiple filters on connected components
    """
    history = [image]
    for (attr, n, reverse) in filters:
        history.append(itk.LabelShapeKeepNObjectsImageFilter.New(
            Input=history[-1],
            BackgroundValue=0,
            NumberOfObjects=n,
            Attribute=attr,
            ReverseOrdering=reverse
        ))
    return history
    
def generate_mask(image, path_out=None):
    
    mask = itk.NotImageFilter(Input=image)
    mask = itk.NotImageFilter(Input=mask)

    converted = itk.CastImageFilter[itk.Image[itk.SS,3], itk.Image[itk.UC,3]].New(Input=mask)

    result_im = itk.RescaleIntensityImageFilter.New(
        Input=converted,
        OutputMinimum=0,
        OutputMaximum=1,
    )
    
    if path_out:
        writer = itk.ImageFileWriter.New(Input=result_im, FileName=path_out)
        writer.Update()
    else:
        result_im.Update()
    
    return result_im
    
def _check_valid_arg(val, name, available):
    if val not in available:
        raise f"{name}='{val}' is not a valid arg. Valid values are: {available}"
        
def load_volume(reader, color=(1.,1.,1.), render_with="gl", interpolation="linear"):
    global volume
    _check_valid_arg(render_with, "render_with", {'gl', 'gpu', 'cpu'})
    _check_valid_arg(interpolation, "interpolation", {'linear', 'nearest'})
    
    reader.Update()

    if render_with == "gl":
        mapper = vtkOpenGLGPUVolumeRayCastMapper()
    elif render_with == 'gpu':
        mapper = vtkGPUVolumeRayCastMapper() 
    elif render_with == 'cpu':
        mapper = vtkFixedPointVolumeRayCastMapper()
    else:
        raise "unexpected"
        
    mapper.SetInputConnection(reader.GetOutputPort())
    mapper.SetAutoAdjustSampleDistances(0)
    mapper.SetSampleDistance(0.5)
    mapper.SetMaskTypeToLabelMap()
    mapper.SetMaskBlendFactor(0.7)
    mapper.SetBlendModeToComposite()
    
    props = vtkVolumeProperty()
    props.SetIndependentComponents(True) 
    props.ShadeOff()

    if interpolation == "linear":
        props.SetInterpolationTypeToLinear()
    elif interpolation == 'nearest':
        props.SetInterpolationTypeToNearest()
    else:
        raise "unexpected"

    volume = vtkVolume()
    volume.SetMapper(mapper)
    volume.SetProperty(props)
    
    return volume
    
def AddSlider(interactor, value_range, x, y, length=0.25, title="", default_value=None, callback=lambda x: _, integer_steps=False):
    assert 0 <= x <= 1 and 0 <= y <= 1

    def _cb(s, *args):
        slider_representation = s.GetSliderRepresentation()
        value = slider_representation.GetValue()
        if integer_steps: 
            value = round(value)
            slider_representation.SetValue(value)
        callback(value)

    # Set slider properties
    slider = vtkSliderRepresentation2D()
    slider.SetMinimumValue(value_range[0])
    slider.SetMaximumValue(value_range[-1])
    slider.SetValue(value_range[0] if default_value is None else default_value)
    slider.SetTitleText(title)
    slider.ShowSliderLabelOn()
    slider.SetSliderWidth(0.03)
    slider.SetSliderLength(0.0001)
    slider.SetEndCapWidth(0)
    slider.SetTitleHeight(0.02)
    slider.SetTubeWidth(0.005)
    
    # Set the slider position
    slider.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay();
    slider.GetPoint1Coordinate().SetValue(x, y);
    slider.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay();
    slider.GetPoint2Coordinate().SetValue(x + length, y);

    # Add the slider to the UI
    sliderWidget = vtkSliderWidget()
    sliderWidget.SetInteractor(interactor);
    sliderWidget.SetRepresentation(slider);
    sliderWidget.EnabledOn();
    
    # Add callback
    sliderWidget.AddObserver("InteractionEvent", _cb)
    
    return sliderWidget


def OnClose(interactor, event):
    # Callback to correctly close the UI
    interactor.GetRenderWindow().Finalize()
    interactor.TerminateApp()
    
def cb_opacity_brain(x):
    # Callback to update brain volume opacity
    global fct_opacity_default,seg_min,seg_max
    fct_opacity_default.AddSegment(seg_min, 0., seg_max, x)
    
def cb_opacity_mask(x):
    global volume_mapper
    # Callback to update mask opacity
    volume_mapper.SetMaskBlendFactor(x)
    
def cb_morpho_filters(idx,cc):
    # Genreate callbacks to update the morpho filters
    def cb(x):
        global MORPHO_FILTERS, CST_PATH_OUT_MASK
        attr, _, negate = MORPHO_FILTERS[idx]
        MORPHO_FILTERS[idx] = (attr, x, negate)
        
        cc_filters = morpho_filters(cc, filters=MORPHO_FILTERS)

        result_im = generate_mask(cc_filters[-1], CST_PATH_OUT_MASK)
        reader_mask = vtkMetaImageReader()
        reader_mask.SetFileName(CST_PATH_OUT_MASK)
        reader_mask.Update()
        volume_mapper.SetMaskInput(reader_mask.GetOutput())
    return cb    
    
def render():
    global CST_PATH_IN_VOLUME,CST_PATH_OUT_MASK
    global seg_max,seg_min
    global MORPHO_FILTERS
    global fct_color_default, fct_opacity_mask, fct_color_mask, fct_opacity_default 
    global iren, renWin, ren 
    global volume,volume_mapper
    base_image = itk.ImageFileReader(FileName=CST_PATH_IN_VOLUME)

    rescaled = itk.RescaleIntensityImageFilter.New(
        Input=base_image,
        OutputMinimum=0,
        OutputMaximum=255
    )

    binary_im = itk.ThresholdImageFilter.New(
        Input=rescaled,
        Lower=102,
    )

    cc = itk.ConnectedComponentImageFilter.New(
        Input=binary_im,
    )

    

    cc_filters = morpho_filters(cc, filters=MORPHO_FILTERS)
    mask = generate_mask(cc_filters[-1], path_out=CST_PATH_OUT_MASK)
    
    reader_brain = vtkMetaImageReader()
    reader_brain.SetFileName(CST_PATH_IN_VOLUME)
    reader_mask = vtkMetaImageReader()
    reader_mask.SetFileName(CST_PATH_OUT_MASK)
    reader_mask.Update()

    volume = load_volume(reader_brain)
    volume_property = volume.GetProperty()
    volume_mapper = volume.GetMapper()
    
#  Set brain rendering properties (color, opacity)

    data_min, data_max = reader_brain.GetOutput().GetScalarRange()

    seg_min, seg_max = 0, 0.6 * data_max
    
    fct_color_default.AddRGBSegment(seg_min, *(0,0,0),
                                    seg_max, *(1,1,1))

    
    fct_color_mask.AddRGBSegment(seg_min, *(0,0,0),
                                 seg_max, *(0,0,1))   
    
    fct_opacity_default.AddSegment(seg_min, 0.,
                                   seg_max, 0.1)
    fct_opacity_mask.AddSegment(seg_min, 0.,
                                seg_max, 1.)

    volume_property.SetColor(fct_color_default)
    volume_property.SetScalarOpacity(fct_opacity_default)
    volume_property.SetLabelColor(1, fct_color_mask)
    volume_property.SetLabelScalarOpacity(1, fct_opacity_mask)

    # Apply generated mask
    volume_mapper.SetMaskInput(reader_mask.GetOutput())
    
    ren.AddVolume(volume)
    renWin.AddRenderer(ren)
    iren.SetRenderWindow(renWin)

    iren.AddObserver('ExitEvent', OnClose)

    # Add all UI sliders
    sl_0 = AddSlider(interactor=iren, value_range=(0, 1), x=0.7, y=0.15, title="Brain Opacity", 
                     default_value=0.1, callback=cb_opacity_brain)
    sl_1 = AddSlider(interactor=iren, value_range=(0, 1), x=0.7, y=0.30, title="Tumor Highlight", 
                     default_value=0.7, callback=cb_opacity_mask)

    sl_2 = AddSlider(interactor=iren, value_range=(0, 20), x=0.7, y=0.55, title="2. NB Final Components", 
                     default_value=3, callback=cb_morpho_filters(2,cc), integer_steps=True)
    sl_3 = AddSlider(interactor=iren, value_range=(1, 20), x=0.7, y=0.70, title="1. NB Bumpiest", 
                     default_value=5, callback=cb_morpho_filters(1,cc), integer_steps=True)
    sl_4 = AddSlider(interactor=iren, value_range=(1, 20), x=0.7, y=0.85, title="0. NB Biggest Components", 
                     default_value=10, callback=cb_morpho_filters(0,cc), integer_steps=True)
                     
    iren.Initialize()
    renWin.Render()
    iren.Start()