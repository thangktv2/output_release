import cv2 as cv
from matplotlib.pyplot import contour
import numpy as np

def imagePreprocess(iP_frame):
    iP_morphologyKernel = np.array(
                           [[0, 0, 1, 0, 0],
                            [0, 1, 1, 1, 0],
                            [1, 1, 1, 1, 1],
                            [0, 1, 1, 1, 0],
                            [0, 0, 1, 0, 0]],
                            dtype=np.uint8)

    iP_HSV = cv.cvtColor(iP_frame, cv.COLOR_BGR2HSV)

    iP_lowerColorBoundary = np.array([90, 0, 0])
    iP_upperColorBoundary = np.array([130, 255, 255])
    iP_rawItemExtract = cv.inRange(iP_HSV,
                                   iP_lowerColorBoundary,
                                   iP_upperColorBoundary)
    # Remove Noise from raw image
    iP_output = cv.morphologyEx(iP_rawItemExtract,
                                          cv.MORPH_OPEN,
                                          iP_morphologyKernel)
    return iP_output

def getItemCoordinate(gIC_frame):
    gIC_output = [0, 0, 0, 0, 0]
    gIC_minAreaThreshold = cV_gICsetMinThreshold
    gIC_maxAreaThreshold = cV_gICsetMaxThreshold                                       
    gIC_contours, gIC_hierarchy = cv.findContours(gIC_frame,
                                                 cv.RETR_TREE, 
                                                 cv.CHAIN_APPROX_SIMPLE)
    # Get the actual inner list of hierarchy descriptions
    if gIC_hierarchy is None:
        pass
    else:
        gIC_hierarchy = gIC_hierarchy[0]

        # For each contour, draw contour and calculate area of 10 frames to get average value
        for gIC_component in zip(gIC_contours, gIC_hierarchy):
            gIC_currentContour = gIC_component[0]
            gIC_currentHierarchy = gIC_component[1]

            gIC_contourArea = cv.contourArea(gIC_currentContour) # Calculate the contour area
            if (gIC_currentHierarchy[3] < 0) and (gIC_minAreaThreshold < gIC_contourArea < gIC_maxAreaThreshold): # The outermost parent components
                gIC_x, gIC_y, gIC_w, gIC_h = cv.boundingRect(gIC_currentContour)
                gIC_output = [1, gIC_x, gIC_y, gIC_w, gIC_h]
            else:
                pass
    return gIC_output

def capture(c_source, c_frameWidth, c_frameHeight):
    global hT_frameWidth
    hT_frameWidth = c_frameWidth
    c_cap = cv.VideoCapture(c_source, apiPreference=cv.CAP_ANY, params=[cv.CAP_PROP_FRAME_WIDTH, c_frameWidth,
                                                                        cv.CAP_PROP_FRAME_HEIGHT, c_frameHeight])
    c_result = c_cap.isOpened()
    if c_result is False:
        print("Can't find external camera")
        exit()
    else:
        return c_cap

def setGlobalValue(sGV_cap,sGV_error1,sGV_error2):
    global pi
    pi = np.pi
    sGV_sumInnerArea = 0
    sGV_sumOuterArea = 0
    

    # Declare config value for getItemCoordinate() function
    global cV_gICsetMinThreshold
    global cV_gICsetMaxThreshold
    
    # Declare config value for houghTransform() function
    global hT_minInnerRadiusThreshold
    global hT_maxInnerRadiusThreshold

    global hT_minOuterRadiusThreshold
    global hT_maxOuterRadiusThreshold

    for frames in range (0,10):
        sGV_ret, sGV_frame = sGV_cap.read() # Read a frame from video/camera
        if sGV_ret == True:
            # Pre-process input image
            iP_output = imagePreprocess(sGV_frame)
            
            # Contours process
            returnArea = contoursProcess(iP_output,None,1)
            sGV_sumInnerArea = sGV_sumInnerArea + returnArea[0] # Sum area of inner circle
            sGV_sumOuterArea = sGV_sumOuterArea + returnArea[1] # Sum area of outer circle

    sGV_averageInnerArea = sGV_sumInnerArea/10 # Average area of inner circle
    sGV_averageOuterArea = sGV_sumOuterArea/10 # Average area of outer circle

    if sGV_averageInnerArea != 0 and sGV_averageOuterArea != 0:

        inner_dia = 2*np.sqrt(sGV_averageInnerArea/pi)
        hT_minInnerRadiusThreshold = (inner_dia/2)*float(1-sGV_error2)
        hT_maxInnerRadiusThreshold = (inner_dia/2)*float(1+sGV_error2)

        outer_dia = 2*np.sqrt(sGV_averageOuterArea/pi)
        hT_minOuterRadiusThreshold = (outer_dia/2)*float(1-sGV_error2)
        hT_maxOuterRadiusThreshold = (outer_dia/2)*float(1+sGV_error2)
        
        # Set output value for getItemCoordinate() function
        cV_gICsetMinThreshold = sGV_averageOuterArea*float(1-sGV_error1)
        cV_gICsetMaxThreshold = sGV_averageOuterArea*float(1+sGV_error1)

        return True
    else:
        return False

def contoursProcess(cP_input,
                    cP_drawFrame,cP_mode): # 1: Draw contours

    cP_noiseThreshold = 1500 # Threshold to remove noise contours
    cP_output = [0,0] # Inner, outer

    cP_contours,cP_hierarchy = cv.findContours(cP_input,
                                               cv.RETR_TREE,
                                               cv.CHAIN_APPROX_SIMPLE)
    if cP_hierarchy is not None:
        # Get the actual inner list of hierarchy descriptions
        cP_hierarchy = cP_hierarchy[0]

        # For each contour, draw contour and calculate area
        for cP_component in zip(cP_contours, cP_hierarchy):
            cP_currentContour = cP_component[0]
            cP_currentHierarchy = cP_component[1]

            cP_contourArea = cv.contourArea(cP_currentContour) # Calculate the contour area
            if cP_contourArea > cP_noiseThreshold: # Remove noise contour
                if cP_currentHierarchy[2] < 0: # The innermost child components
                    if cP_mode == 0:
                        cv.drawContours(cP_drawFrame, [cP_currentContour], 0, (0,255,0), 2)
                        cP_output[0] = cP_contourArea # Area of inner circle
                    elif cP_mode == 1:
                        (x,y),radius = cv.minEnclosingCircle(cP_currentContour)
                        center = (int(x),int(y))
                        radius = int(radius)
                        cv.circle(cP_drawFrame,center,radius,(255,0,0),3)
                        cP_output[0] = pi*radius**2 # Area of inner circle
                    else:
                        pass

                elif cP_currentHierarchy[3] < 0: # The outermost parent components
                    if cP_mode == 0:
                        cv.drawContours(cP_drawFrame, [cP_currentContour], 0, (0,255,0), 2)
                        cP_output[1] = cP_contourArea # Area of outer circle
                    elif cP_mode == 1:
                        (x,y),radius = cv.minEnclosingCircle(cP_currentContour)
                        center = (int(x),int(y))
                        radius = int(radius)
                        cv.circle(cP_drawFrame,center,radius,(255,0,0),3)
                        cP_output[1] = pi*radius**2 # Area of outer circle
                    else:
                        pass
                else:
                    pass
            else:
                pass
    else:
        pass
    return cP_output

def cropImage(cAS_input,
              cAS_size):
    try:
        cAS_inputWidth = cAS_input.shape[1]
        cAS_inputHeight = cAS_input.shape[0]

        if cAS_inputWidth < cAS_inputHeight:
            cAS_sideValue = cAS_inputWidth
        else:
            cAS_sideValue = cAS_inputHeight

        cAS_inputCenterX = int(cAS_inputWidth/2)
        cAS_inputCenterY = int(cAS_inputHeight/2)

        cAS_hsideValue = int(cAS_sideValue/2)

        cAS_cropped = cAS_input[(cAS_inputCenterY - cAS_hsideValue):(cAS_inputCenterY + cAS_hsideValue), (cAS_inputCenterX - cAS_hsideValue):(cAS_inputCenterX + cAS_hsideValue)]
        cAS_output = cv.resize(cAS_cropped, (cAS_size,cAS_size), interpolation = cv.INTER_AREA)
        return cAS_output
    except:
        pass