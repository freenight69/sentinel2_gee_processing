#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Version: v1.0
Date: 2023-02-09
Authors: Chen G.
Description: A wrapper function to derive the Sentinel-2 MSI
"""

import ee
import geemap
import os
import helper
import cal_index as ci

# VPN port
geemap.set_proxy(port=5188)
try:
    ee.Initialize()
except:
    ee.Authenticate()
    ee.Initialize()


###########################################
# DO THE JOB
###########################################

def s2_preprocess(params):
    """
    Applies preprocessing to a collection of S2 images to return an analysis ready sentinel-2 data.

    Parameters
    ----------
    params : Dictionary
        These parameters determine the data selection and image processing parameters.

    Raises
    ------
    ValueError


    Returns
    -------
    ee.ImageCollection
        A processed Sentinel-2 image collection

    """

    START_DATE = params['START_DATE']
    END_DATE = params['END_DATE']
    BANDS = params['BANDS']
    ROI = params['ROI']
    MAX_CLOUD_PROBABILITY = params['MAX_CLOUD_PROBABILITY']
    CAL_NDVI = params['CAL_NDVI']
    CAL_NDMI = params['CAL_NDMI']
    CLIP_TO_ROI = params['CLIP_TO_ROI']
    SAVE_ASSET = params['SAVE_ASSET']
    ASSET_ID = params['ASSET_ID']
    SAVE_LOCAL = params['SAVE_LOCAL']
    VISUALIZATION = params['VISUALIZATION']
    LOCAL_DIR = params['LOCAL_DIR']

    ###########################################
    # 0. CHECK PARAMETERS
    ###########################################

    if MAX_CLOUD_PROBABILITY is None:
        MAX_CLOUD_PROBABILITY = 100
    if CAL_NDVI is None:
        CAL_NDVI = False
    if CAL_NDMI is None:
        CAL_NDMI = False
    if VISUALIZATION is None:
        VISUALIZATION = False

    bands_required = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']
    # if any(band in bands_required for band in BANDS):
    #     raise ValueError("ERROR!!! Parameter BANDS not correctly defined")

    if MAX_CLOUD_PROBABILITY < 0 or MAX_CLOUD_PROBABILITY > 100:
        raise ValueError("ERROR!!! Parameter MAX_CLOUD_PROBABILITY not correctly defined")

    ###########################################
    # 1. DATA SELECTION
    ###########################################

    # select S-2 image collection
    s2_sr = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterDate(START_DATE, END_DATE) \
        .filterBounds(ROI)

    ###########################################
    # 2. REMOVE CLOUD
    ###########################################

    if 0 <= MAX_CLOUD_PROBABILITY <= 100:
        # Sentinel-2 cloud probability ImageCollection
        s2Clouds = ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')
        # Filter input collections by desired data range and region.
        criteria = ee.Filter.And(ee.Filter.bounds(ROI), ee.Filter.date(START_DATE, END_DATE))
        s2Sr = s2_sr.filter(criteria).map(helper.mask_edges)
        s2Clouds = s2Clouds.filter(criteria)
        # Join S2 SR with cloud probability dataset to add cloud mask.
        s2SrWithCloudMask = ee.Join.saveFirst('cloud_mask').apply(**{
            'primary': s2Sr,
            'secondary': s2Clouds,
            'condition': ee.Filter.equals(**{
                "leftField": "system:index",
                "rightField": "system:index"})
        })
        s2_sr = helper.cloud_mask_filter(ee.ImageCollection(s2SrWithCloudMask), MAX_CLOUD_PROBABILITY)
        # scale images
        s2_sr = s2_sr.map(helper.scale_image)

    ###########################################
    # 3. CALCULATE VEGETATION INDEX
    ###########################################
    
    if CAL_NDVI:
        s2_sr = s2_sr.map(ci.cal_ndvi)
        BANDS.append('NDVI')
    if CAL_NDMI:
        s2_sr = s2_sr.map(ci.cal_ndmi)
        BANDS.append('NDMI')

    ###########################################
    # 4. OUTPUT
    ###########################################

    # select bands
    s2_sr = s2_sr.select(BANDS)

    # clip to roi
    if CLIP_TO_ROI:
        s2_sr = s2_sr.map(lambda image: image.clip(ROI))

    # save to asset
    if SAVE_ASSET:
        size = s2_sr.size().getInfo()
        imlist = s2_sr.toList(size)
        for idx in range(0, size):
            img = imlist.get(idx)
            img = ee.Image(img)
            name = str(img.id().getInfo())
            description = name
            assetId = ASSET_ID + '/' + name

            task = ee.batch.Export.image.toAsset(image=img,
                                                 assetId=assetId,
                                                 description=description,
                                                 region=s2_sr.geometry(),
                                                 scale=10,
                                                 maxPixels=1e13)
            task.start()
            print('Exporting {} to {}'.format(name, assetId))

    # save to local
    if SAVE_LOCAL:

        size = s2_sr.size().getInfo()
        imlist = s2_sr.toList(size)
        for idx in range(0, size):
            img = imlist.get(idx)
            img = ee.Image(img)
            name = str(img.id().getInfo())

            # save raw images to local
            if not os.path.exists(LOCAL_DIR):
                os.makedirs(LOCAL_DIR)
            filename_raw = os.path.join(LOCAL_DIR, name + '.tif')
            print('Downloading Raw Image: {} to {}'.format(name, filename_raw))
            geemap.download_ee_image(img, filename_raw, region=ROI, crs='EPSG:4326', scale=10)
            # geemap.ee_export_image(img, filename=filename_raw, scale=10, region=ROI)

            # save visualization images to local
            if VISUALIZATION:
                rgb_bands = ['B4', 'B3', 'B2']
                # if not any(i in rgb_bands for i in BANDS):
                #     raise ValueError("ERROR!!! Only can convert RGB bands image into an 32-int RGB image")
                img_rgb = img.select(rgb_bands)
                rgbImage = img_rgb.visualize(**{
                    'bands': rgb_bands,
                    'min': 0.0,
                    'max': 0.3
                })
                filename_rgb = os.path.join(LOCAL_DIR, name + '_VIS_RGB.tif')
                print('Downloading Visualization RGB Image to {}'.format(filename_rgb))
                # geemap.download_ee_image(rgbImage, filename_rgb, region=ROI, crs='EPSG:4326', scale=10, dtype='int32')
                geemap.ee_export_image(rgbImage, filename=filename_rgb, scale=10, region=ROI)

                if CAL_NDVI:
                    img_ndvi = img.select('NDVI')
                    ndviImage = img_ndvi.visualize(**{
                        'bands': ['NDVI'],
                        'min': 0.0,
                        'max': 1.0,
                        'palette': ['FFFFFF',  'CE7E45',  'DF923D',  'F1B555',  'FCD163',
                                    '99B718',  '74A901',  '66A000',  '529400',  '3E8601',
                                    '207401',  '056201',  '004C00',  '023B01',  '012E01',
                                    '011D01',  '011301']
                    })
                    filename_vis_ndvi = os.path.join(LOCAL_DIR, name + '_VIS_NDVI.tif')
                    print('Downloading Visualization NDVI Image to {}'.format(filename_vis_ndvi))
                    # geemap.download_ee_image(ndviImage, filename_vis_ndvi, region=ROI, crs='EPSG:4326', scale=10, dtype='int32')
                    geemap.ee_export_image(ndviImage, filename=filename_vis_ndvi, scale=10, region=ROI)

    return s2_sr
