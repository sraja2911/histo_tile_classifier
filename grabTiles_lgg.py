# Imports Girder Client, HistomicsTK utils, Python os, sys functions
import matplotlib
matplotlib.use('Agg')
import os, sys, json, glob
import numpy as np
import girder_client
import histomicstk.utils as htk_utils
from cStringIO import StringIO
import io, random
import logging
from os.path import join as opj
import matplotlib.pyplot as plt
from PIL import Image

cohort = "lgg"

logging.getLogger("requests").setLevel(logging.WARNING)
#gc = girder_client.GirderClient(apiUrl="http://candygram.neurology.emory.edu:8080/api/v1")
gc = girder_client.GirderClient(apiUrl="http://digitalslidearchive.emory.edu:8080/api/v1")

## Connect to girder and get the cohort ID's for all the TCGA collections
tcgaCohorts = gc.get('/tcga/cohort')  ## This gets me the folderID for all the TCGA cohorts
cohortInfo = dict([(x['name'],x['_id']) for x in tcgaCohorts['data']])

slidesInCohort = gc.get('/tcga/cohort/%s/images?limit=%d' % (cohortInfo[cohort],2000))
## PROBABLY should write a generator to grab all the slides instead of just specifying some giant number

### For now I am going to filter out any non DX Cases
dxSlides = [x for x in slidesInCohort['data'] if '-DX' in x['name']]
print(len(dxSlides),"for the %s Cohort"%cohort)

for idx,sl in enumerate(dxSlides):
    lowResMag = 0.625
    lowResImg = gc.get('/item/%s/tiles/region?magnification=%s' % (sl['_id'], lowResMag),jsonResp=False)    
    lowResPILimage = Image.open(io.BytesIO(lowResImg.content))
    break
    
class LinePrinter():
    """
    Print things to stdout on one line dynamically
    """
    def __init__(self,data):
        sys.stdout.write("\r\x1b[K"+data.__str__())
        sys.stdout.flush()

def grabTilesFromImage(imageData, outputDir, lowResMag=0.625, outputRes=20, tilesToOutput=200,debug=False):
    ### This receives a list of images from Girder and will generate tiles and place them in 
    ### Train and Test Directories-- it will split based on train_test_split and also
    ## Will run a low res segmentation step prior to trying to randomly grab tiles from the input stream
    ## outputDir should be something like /data/train/gbm or similar; I'll have the function calling this make sure those
    ## Dirs already exist

    ## Pull the image from girder and then use PIL to turn the raw bytes in an image object
    if debug:
        print("Analyzing %s; pulling base image at %s and outputing tiles at %s" % (imageData['name'],lowResMag,outputRes))
    lowResImg = gc.get('/item/%s/tiles/region?magnification=%s' % ( imageData['_id'], lowResMag),jsonResp=False)    
    lowResPILimage = Image.open(io.BytesIO(lowResImg.content))

    # Using HistomicsTK utils's simple mask function to mask out tissue areas from background in brightfield H&E images
    im_fgnd_mask_lres = htk_utils.simple_mask(np.asarray(lowResPILimage))

    # To extract masked coordinates from numpy array
    (YmaskPts,XmaskPts)  = np.nonzero(im_fgnd_mask_lres)
    maskCoords = zip(XmaskPts,YmaskPts) # To change into (x, y) form

    # To Create a bounding box of masked image
    scaleFactor = 32 # this is the high magnification (20x) / low res (0.625)
    left   = int(min(XmaskPts) * scaleFactor)
    top    = int(min(YmaskPts) * scaleFactor)
    right  = int(max(XmaskPts) * scaleFactor)
    bottom = int(max(YmaskPts) * scaleFactor)
    left, right, top, bottom

    # To generate tile corners from the bounding box
    corners = []
    for x in range(left, right, 256):
        for y in range(top, bottom, 256):
            corners.append([x,y])
        
    np.random.shuffle(corners)

    slideBaseName =  sl['name'].split(".")[0]

    regionWidth = regionHeight = 256
    outputRes = 20
    count = 0

    for c in corners:
        x_low = c[0] / scaleFactor
        y_low = c[1] / scaleFactor
        top = c[1]
        left = c[0]
        
        # Extracts tile for the specified corner region 
        curTile = gc.get('/item/%s/tiles/region?magnification=%s&top=%d&left=%d&regionWidth=%d&regionHeight=%d' 
            % ( imageData['_id'], outputRes, top, left,regionWidth,regionHeight),jsonResp=False)
        
        img = np.asarray(Image.open(io.BytesIO(curTile.content))) # Converts binary image to numpy array
        label = im_fgnd_mask_lres[y_low, x_low]
        
        if label:
            count += 1
            plt.imshow(img)
            #plt.show()
            tilename = outputDir + "/"+ slideBaseName + '_%dx_%d_%d_%dx%d.jpg' % (outputRes, top, left,regionWidth,regionHeight) 
            plt.savefig(tilename)
            
            if count > tilesToOutput:
                break  

# To generate Training and Test Tiles for CNN
train  = 0.8
totalSlides = len(dxSlides)
## Output Testing & Training Images for Cohort

for idx,sl in enumerate(dxSlides):
## I am assuming 80% i.e. 16/20 = 0.8...
    if( (idx % 20)  <  16 ):
        opd = "/data/train/%s" % cohort
    else:
        opd = "/data/test/%s" % cohort

    if not os.path.isdir(opd):
        os.makedirs(opd)
        print("Outputing test set now!!")

    slideBaseName = sl['name'].split(".")[0]
    tilesFound = glob.glob(opd+"/%s*png" %  (slideBaseName))
    
    tilesWanted = 22
    tilesToGenerate = tilesWanted - len(tilesFound)
    
    if (tilesToGenerate) > 0:
        grabTilesFromImage( sl, opd, lowResMag=0.625, outputRes=20, tilesToOutput=tilesWanted,debug=True)
        #grabTilesFromImage( sl, opd, lowResMag=0.625, outputRes=20, tilesToOutput=tilesToGenerate,debug=True)
    else:
        stats = "Processed %d images" % idx
        LinePrinter(stats)