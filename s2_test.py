#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File: s2_test.py
Version: v1.0
Date: 2023-02-09
Authors: Chen G.
Description: This script creates downloading and processing Sentinel-2 images.
License: This code is distributed under the MIT License.

    sentinel2_download Parameter:
        USER_NAME: The account name to log in ESA Copernicus Open Access Hub (https://scihub.copernicus.eu/).
        PASSWORD: The account password to log in ESA Copernicus Open Access Hub.
        FOOTPRINT: The region to include imagery within.
        START_DATE: A time interval filter based on the Sensing Start Time of the products. Following formats:
            - yyyyMMdd
            - yyyy-MM-ddThh:mm:ss.SSSZ (ISO-8601)
            - yyyy-MM-ddThh:mm:ssZ
            - NOW
            - NOW-<n>DAY(S) (or HOUR(S), MONTH(S), etc.)
            - NOW+<n>DAY(S)
            - yyyy-MM-ddThh:mm:ssZ-<n>DAY(S)
            - NOW/DAY (or HOUR, MONTH etc.) - rounds the value to the given unit
        END_DATE: A time interval filter based on the Sensing Start Time of the products.
        PRODUCT_TYPE: Type of sentinel-2 product to apply (String):
            'S2MSI2A' - Sentinel-2 MSI L2A product
            'S2MSI1C' - Sentinel-2 MSI L1C product
            'S2MS2Ap' - Sentinel-2 MSI L2Ap product
        CLOUD_COVER_PERCENTAGE: (Optional) cloud cover percentage to apply s2 products filter.
        SAVE_DIR: Download the sentinel-2 images to local.


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
             'LOCAL_DIR': "G:/test"
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
