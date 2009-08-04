//
//  camera_mac.m
//
//  Created by Werner Laurensse on 2009-05-28.
//  Copyright (c) 2009 . All rights reserved.
//

// TODO: memory management in open, init and close

#import "camera.h"

/* 
 * return: an array of the available cameras ids.
 * num_cameras: number of cameras in array.
 */
char** mac_list_cameras(int* num_cameras) {
    char** cameras;
    char* camera;
    
    // The ComponentDescription allows you to search for Components that can be used to capture
    // images, and thus can be used as camera.
    ComponentDescription cameraDescription;
    memset(&cameraDescription, 0, sizeof(ComponentDescription));
    cameraDescription.componentType = SeqGrabComponentType;
    
    // Count the number of cameras on the system, and allocate an array for the cameras
    *num_cameras = (int) CountComponents(&cameraDescription);
    cameras = (char **) malloc(sizeof(char*) * *num_cameras);
    
    // Try to find a camera, and add the camera's 'number' as a string to the array of cameras 
    Component cameraComponent = FindNextComponent(0, &cameraDescription);
    short num = 0;
    while(cameraComponent != NULL) {
        camera = malloc(sizeof(char) * 50); //TODO: find a better way to do this...
        sprintf(camera, "%d", cameraComponent);
        cameras[num] = camera;
        cameraComponent = FindNextComponent(cameraComponent, &cameraDescription);
        num++;
    }
    return cameras;
}

/* Open a Camera component. */
int mac_open_device (PyCameraObject* self) {
    OSErr theErr;

    // Initialize movie toolbox
    theErr = EnterMovies();
    if (theErr != noErr) {
        PyErr_Format(PyExc_SystemError, "Cannot initializes the Movie Toolbox");
        return 0;
    }
    
    // Open camera component
    SeqGrabComponent component = OpenComponent((Component) atoi(self->device_name));
    if (component == NULL) {
        PyErr_Format(PyExc_SystemError, "Cannot open '%s'", self->device_name);
        return 0;
    }
    self->component = component;
    
    return 1;
}

/* Make the Camera object ready for capturing images. */
int mac_init_device(PyCameraObject* self) {
    OSErr theErr;

    if (self->color_out == YUV_OUT)
        self->pixelformat = kYUVSPixelFormat;
    else if (self->color_out == HSV_OUT)
        self->pixelformat = k24RGBPixelFormat; 
    else
        self->pixelformat = k24RGBPixelFormat;
    
    int rowlength = self->boundsRect.right * self->bytes;
	
	theErr = SGInitialize(self->component);
    if (theErr != noErr) {
        PyErr_Format(PyExc_SystemError,
        "Cannot initialize sequence grabber component");
        return 0;
    }
    
	
    theErr = SGSetDataRef(self->component, 0, 0, seqGrabDontMakeMovie);
    if (theErr != noErr) {
        PyErr_Format(PyExc_SystemError,
        "Cannot set the sequence grabber destination data reference for a record operation");
        return 0;
    }
        
    theErr = SGNewChannel(self->component, VideoMediaType, &self->channel);
    if (theErr != noErr) {
        PyErr_Format(PyExc_SystemError,
        "Cannot creates a sequence grabber channel and assigns a channel component to the channel");
        return 0;
    }
    
    //theErr = SGSettingsDialog (self->component, self->channel, 0, NULL, 0, NULL, 0);
    
    theErr = SGSetChannelBounds(self->channel, &self->boundsRect);
    if (theErr != noErr) {
        PyErr_Format(PyExc_SystemError,
        "Cannot specifie a channel's display boundary rectangle");
        return 0;
    }
	
	/*
	theErr = SGSetFrameRate (vc, fps);
    if(theErr != noErr){
        PyErr_Format(PyExc_SystemError,
        "Cannot set the frame rate of the sequence grabber");
        return 0;
    }
    */
      
    theErr = SGSetChannelUsage(self->channel, seqGrabPreview);
    if (theErr != noErr) {
        PyErr_Format(PyExc_SystemError,
        "Cannot specifie how a channel is to be used by the sequence grabber componen");
        return 0;
    }
    
	theErr = SGSetChannelPlayFlags(self->channel, channelPlayAllData);
	if (theErr != noErr) {
        PyErr_Format(PyExc_SystemError,
        "Cannot adjust the speed and quality with which the sequence grabber displays data from a channel");
        return 0;
	}
	
	/*
    MatrixRecord matrix;
    short i, j;
    Fixed minusOne = Long2Fix(-1L);
    Fixed PlusOne = Long2Fix(1L);
    Fixed zero = Long2Fix(0L);

    ImageDescriptionHandle imageDesc = (ImageDescriptionHandle)NewHandle(0);
    
    // retrieve a channelÕs current sample description, the channel returns a sample description that is
    // appropriate to the type of data being captured
    //theErr = SGGetChannelSampleDescription(self->channel, (Handle)imageDesc);
    if (theErr != noErr) {
        PyErr_Format(PyExc_SystemError,
        "SG sample description");
        return 0;
	}
    
    Rect dstRect;
    dstRect.top = 0;
    dstRect.left = 0;
    dstRect.bottom = 200;
    dstRect.right = 200;
    
	RectMatrix(&matrix, &self->boundsRect, &dstRect);
	theErr = SGSetChannelMatrix(self->channel, &matrix);
    if (theErr != noErr) {
        PyErr_Format(PyExc_SystemError,
        "set matrix fail");
        return 0;
	}
	*/
    
    /*
    if (true) {
        printf("View = flip\n");
        // err = SGGetChannelMatrix(videoChannel, &mat);
        // keyPrint("return from get matrix = %d\n", err);
        if (!(matrix = malloc(sizeof(MatrixRecord)))) {
            printf(" malloc failed for MatrixRecord.\n");
            return;
        }
        matrix->matrix[0][0] = zero;
        matrix->matrix[0][1] = zero;
        matrix->matrix[0][2] = zero;

        matrix->matrix[1][0] = zero;
        matrix->matrix[1][1] = zero;
        matrix->matrix[1][2] = zero;

        matrix->matrix[2][0] = (Fract) 0x00000000L;
        matrix->matrix[2][1] = (Fract) 0x00000000L;
        matrix->matrix[2][2] = (Fract) 0x00000000L;
        
        theErr = SGGetChannelMatrix(self->channel, matrix);
        
        for (i=0; i<3; ++i)
            for (j=0; j<3; ++j)
                printf("matrix->matrix[%d][%d] = %d\n", i, j, matrix->matrix[i][j]);
        printf("return from get matrix = %d\n", theErr);
        
        ScaleMatrix(matrix, fixed1, minusOne, 0, 0);
        TranslateMatrix(matrix, Long2Fix(self->boundsRect.right), 0);
        
        
        theErr = SGSetChannelMatrix(self->channel, matrix);
        printf("return from set matrix = %d\n", theErr);
        
        
        matrix->matrix[0][0] = PlusOne;
        matrix->matrix[0][1] = zero;
        matrix->matrix[0][2] = zero;

        matrix->matrix[1][0] = zero;
        matrix->matrix[1][1] = PlusOne;
        matrix->matrix[1][2] = zero;

        matrix->matrix[2][0] = (Fract) 0x00000000L;
        matrix->matrix[2][1] = (Fract) 0x00000000L;
        matrix->matrix[2][2] = fract1;
        

        for (i=0; i<3; ++i)
            for (j=0; j<3; ++j)
                printf("matrix->matrix[%d][%d] = %d\n", i, j, matrix->matrix[i][j]);
        
        theErr = SGSetChannelMatrix(self->channel, matrix);
        printf("return from set matrix = %d\n", theErr);
        SGVideoDigitizerChanged(self->channel);
    } else {
        printf("View = normal\n");
    }
	*/
	
	
    self->pixels.length = self->boundsRect.right * self->boundsRect.bottom * self->bytes;
	self->pixels.start = (unsigned char*) malloc(self->pixels.length);
	
	theErr = QTNewGWorldFromPtr(&self->gworld,
								self->pixelformat,
                                &self->boundsRect, 
                                NULL, 
                                NULL, 
                                0, 
                                self->pixels.start, 
                                rowlength);
        
	if (theErr != noErr) {
	    PyErr_Format(PyExc_SystemError,
	    "Cannot wrap a graphics world and pixel map structure around an existing block of memory containing an image, "
	    "failed to run QTNewGWorldFromPtr");
		free(self->pixels.start);
		self->pixels.start = NULL;
        self->pixels.length = 0;
		return 0;
	}  
	
    if (self->gworld == NULL) {
		PyErr_Format(PyExc_SystemError,
		"Cannot wrap a graphics world and pixel map structure around an existing block of memory containing an image, "
		"gworld is NULL");
		free(self->pixels.start);
		self->pixels.start = NULL;
        self->pixels.length = 0;
		return 0;
	}
	
    theErr = SGSetGWorld(self->component, (CGrafPtr)self->gworld, NULL);
	if (theErr != noErr) {
		PyErr_Format(PyExc_SystemError,
		"Cannot establishe the graphics port and device for a sequence grabber component");
        free(self->pixels.start);
		self->pixels.start = NULL;
        self->pixels.length = 0;
		return 0;
	}
	    
    return 1;
}

/* Start Capturing */
int mac_start_capturing(PyCameraObject* self) {
    OSErr theErr;
    
    theErr = SGPrepare(self->component, true, false);
    if (theErr != noErr) {
        PyErr_Format(PyExc_SystemError,
        "Cannot istruct a sequence grabber to get ready to begin a preview or record operation");
        free(self->pixels.start);
		self->pixels.start = NULL;
        self->pixels.length = 0;
        return 0;
	}
	
	theErr = SGStartPreview(self->component);
    if (theErr != noErr) {
        PyErr_Format(PyExc_SystemError,
        "Cannot instruct the sequence grabber to begin processing data from its channels");
        free(self->pixels.start);
		self->pixels.start = NULL;
        self->pixels.length = 0;
        return 0;
	}
	
    return 1;
}

/* Close the camera component, and stop the image capturing if necessary. */
int mac_close_device (PyCameraObject* self) {
    ComponentResult theErr;
    
    // Stop recording
   	if (self->component)
   		SGStop(self->component);

    // Close sequence grabber component
   	if (self->component) {
   		theErr = CloseComponent(self->component);
   		if (theErr != noErr) {
   			PyErr_Format(PyExc_SystemError,
   			"Cannot close sequence grabber component");
            return 0;
   		}
   		self->component = NULL;
   	}
    
    // Dispose of GWorld
   	if (self->gworld) {
   		DisposeGWorld(self->gworld);
   		self->gworld = NULL;
   	}
   	// Dispose of pixels buffer
    free(self->pixels.start);
    self->pixels.start = NULL;
    self->pixels.length = 0;
    return 1;
}

/* Stop capturing. */
int mac_stop_capturing (PyCameraObject* self) {
    OSErr theErr = SGStop(self->component);
    if (theErr != noErr) {
        PyErr_Format(PyExc_SystemError, "Could not stop the sequence grabber with previewing");
        return 0;
    }
    return 1;
}

/* Read a frame, and put the raw data into a python string. */
PyObject *mac_read_raw(PyCameraObject *self) {
    if (self->gworld == NULL) {
        PyErr_Format(PyExc_SystemError, "Cannot set convert gworld to surface because gworls is 0");
        return 0;
    }
    
    if (mac_camera_idle(self) == 0) {
        return 0;
    }
    
    PyObject *raw;
    PixMapHandle pixmap_handle = GetGWorldPixMap(self->gworld);
    LockPixels(pixmap_handle);
    raw = PyString_FromStringAndSize(self->pixels.start, self->pixels.length);
    UnlockPixels(pixmap_handle);
    return raw;
}

/* Read a frame from the camera and copy it to a surface. */
int mac_read_frame(PyCameraObject* self, SDL_Surface* surf) {
    if (mac_camera_idle(self) != 0) {
        //return mac_copy_gworld_to_surface(self, surf);
        return mac_process_image(self, self->pixels.start, self->pixels.length, surf);
    } else {
        return 0;
    }
}

// TODO sometimes it is posible to directly grab the image in the desired pixel format,
// but this format needs to be known at the beginning of the initiation of the camera.
int mac_process_image(PyCameraObject* self, const void *image, unsigned int buffer_size, SDL_Surface* surf) {
    if (!surf)
        return 0;
    
    SDL_LockSurface (surf);
    
    switch (self->pixelformat) {
        case k24RGBPixelFormat:
            if (buffer_size >= self->size * 3) {
                switch (self->color_out) {
                    case RGB_OUT:
                        rgb24_to_rgb(image, surf->pixels, self->size, surf->format);
                        break;
                    case HSV_OUT:
                        rgb_to_hsv(image, surf->pixels, self->size, V4L2_PIX_FMT_RGB24, surf->format);
                        break;
                    case YUV_OUT:
                        rgb_to_yuv(image, surf->pixels, self->size, V4L2_PIX_FMT_RGB24, surf->format);
                        break;
                }
            } else {
                SDL_UnlockSurface(surf);
                return 0;
            }
            break;
        
        //this isn't really necessary
        case k16BE555PixelFormat:
            if (buffer_size >= self->size * 2) {
                switch (self->color_out) {
                    case RGB_OUT:
                        rgb444_to_rgb(image, surf->pixels, self->size, surf->format);
                        break;
                    case HSV_OUT:
                        rgb_to_hsv(image, surf->pixels, self->size, V4L2_PIX_FMT_RGB444, surf->format);
                        break;
                    case YUV_OUT:
                        rgb_to_yuv(image, surf->pixels, self->size, V4L2_PIX_FMT_RGB444, surf->format);
                        break;
                }
            } else {
                SDL_UnlockSurface (surf);
                return 0;
            }
            break;
        
        case kYUVSPixelFormat:
            if (buffer_size >= self->size * 2) {
                switch (self->color_out) {
                    case YUV_OUT:
                        yuyv_to_yuv(image, surf->pixels, self->size, surf->format);
                        break;
                    case RGB_OUT:
                        yuyv_to_rgb(image, surf->pixels, self->size, surf->format);
                        break;
                    case HSV_OUT:
                        yuyv_to_rgb(image, surf->pixels, self->size, surf->format);
                        rgb_to_hsv(surf->pixels, surf->pixels, self->size, V4L2_PIX_FMT_YUYV, surf->format);
                        break;
                }
            } else {
                SDL_UnlockSurface (surf);
                return 0;
            }
            break;
        /* I don't use thse
        case V4L2_PIX_FMT_SBGGR8:
            if (buffer_size >= self->size) {
                switch (self->color_out) {
                    case RGB_OUT:
                        sbggr8_to_rgb(image, surf->pixels, self->width, self->height, surf->format);
                        break;
                    case HSV_OUT:
                        sbggr8_to_rgb(image, surf->pixels, self->width, self->height, surf->format);
                        rgb_to_hsv(surf->pixels, surf->pixels, self->size, V4L2_PIX_FMT_SBGGR8, surf->format);
                        break;
                    case YUV_OUT:
                        sbggr8_to_rgb(image, surf->pixels, self->width, self->height, surf->format);
                        rgb_to_yuv(surf->pixels, surf->pixels, self->size, V4L2_PIX_FMT_SBGGR8, surf->format);
                        break;
                }
            } else {
                SDL_UnlockSurface (surf);
                return 0;
            }
            break;
        
        case V4L2_PIX_FMT_YUV420:
            if (buffer_size >= (self->size * 3) / 2) {
                switch (self->color_out) {
                    case YUV_OUT:
                        yuv420_to_yuv(image, surf->pixels, self->width, self->height, surf->format);
                        break;
                    case RGB_OUT:
                        yuv420_to_rgb(image, surf->pixels, self->width, self->height, surf->format);
                        break;
                    case HSV_OUT:
                        yuv420_to_rgb(image, surf->pixels, self->width, self->height, surf->format);
                        rgb_to_hsv(surf->pixels, surf->pixels, self->size, V4L2_PIX_FMT_YUV420, surf->format);
                        break;
                }
            } else {
                SDL_UnlockSurface (surf);
                return 0;
            }
            break;
        */
        
    }
    SDL_UnlockSurface (surf);
    return 1;
}

/* Put the camera in idle mode. */
int mac_camera_idle(PyCameraObject* self) {
    OSErr theErr = SGIdle(self->component);
    if (theErr != noErr) {
        PyErr_Format(PyExc_SystemError, "SGIdle failed");
        return 0;
    }
    
    return 1;
}

/* Copy the data from a gworld into an SDL_Surface.
 * If nesesary it addjust the masks of the surface to fit the rgb layout of the gworld. */
int mac_copy_gworld_to_surface(PyCameraObject* self, SDL_Surface* surf) {
    SDL_LockSurface(surf);
	
	memcpy(surf->pixels, self->pixels.start, self->pixels.length);
	
    SDL_UnlockSurface(surf);
    
    return 1;
}