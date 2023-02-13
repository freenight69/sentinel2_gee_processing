#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File: s2_test.py
Version: v1.0
Date: 2023-02-09
Authors: Chen G.
Description: This script creates downloading and processing Sentinel-2 images based on Google Earth Engine.
License: This code is distributed under the MIT License.

    Parameter:
        START_DATE: The earliest date to include images for (inclusive).
        END_DATE: The latest date to include images for (exclusive).
        BANDS: The Sentinel-2 image bands to select for processing.
        ROI: The boundry to select for processing.
        MAX_CLOUD_PROBABILITY: (Optional) cloud cover percentage to apply s2 image collection filter.
        CAL_NDVI: (Optional) calculate the Normalized Difference Vegetation Index (NDVI) from multiband s2 images.
        CAL_NDMI: (Optional) calculate the Normalized Difference Moisture Index (NDMI) from multiband s2 images.
        CLIP_TO_ROI: (Optional) clip the processed image to the region of interest.
        SAVE_ASSETS : (Optional) exports the processed collection to an asset.
        ASSET_ID : (Optional) the user id path to save the assets
        SAVE_LOCAL : (Optional) download the processed images to local.
        VISUALIZATION : (Optional) convert raw image to RGB image and download the processed images to local.
        LOCAL_DIR : (Optional) where to save downloaded images.
        
    Returns:
        An ee.ImageCollection with an analysis ready Sentinel 2 imagery with the cloud masked images and vegetation index band.


    """

import ee
import datetime
import wrapper as wp

# /***************************/
# // MAIN
# /***************************/
# Parameters
roi = ee.Geometry.Polygon(
    [
        [
            [121.93826854879164, 30.970113616024253],
            [121.92722368998854, 30.969653807534907],
            [121.92926211306607, 30.964191528157762],
            [121.9295732493118, 30.963142738459393],
            [121.92982001254117, 30.96126592814542],
            [121.92984147021329, 30.95840464144593],
            [121.94244755425436, 30.958885338234488],
            [121.95453596983721, 30.962624820837277],
            [121.94630590848263, 30.981625659888707],
            [121.93452564648922, 30.981202542714716]
        ]
    ]
)
parameter = {'START_DATE': '2023-01-20',
             'END_DATE': '2023-01-31',
             'BANDS': ['B2', 'B3', 'B4', 'B8', 'B11'],
             # 'ROI': ee.Geometry.Rectangle([-47.1634, -3.00071, -45.92746, -5.43836]),
             'ROI': roi,
             'MAX_CLOUD_PROBABILITY': 65,
             'CAL_NDVI': True,
             'CAL_NDMI': False,
             'CLIP_TO_ROI': True,
             'SAVE_ASSET': False,
             'ASSET_ID': "users/gongchen9369",
             'SAVE_LOCAL': True,
             'VISUALIZATION': True,
             'LOCAL_DIR': "G:/test/wgs84"
             }

# /***************************/
# // MAIN
# /***************************/
if __name__ == "__main__":
    start_time = datetime.datetime.now()

    # processed s1 collection
    s2_processed = wp.s2_preprocess(parameter)

    end_time = datetime.datetime.now()
    print("Elapsed Time:", end_time - start_time)  # 输出程序运行所需时间
