#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Version: v1.0
Date: 2023-02-09
Authors: Chen G.
"""

import ee


# ---------------------------------------------------------------------------//
# Cloud Mask
# ---------------------------------------------------------------------------//
def mask_clouds(img, MAX_CLOUD_PROBABILITY):
    """
    mask cloud >= MAX_CLOUD_PROBABILITY

    Parameters
    ----------
    img : ee.Image
        image to apply the cloud masking
    MAX_CLOUD_PROBABILITY : odd integer
        max cloud probability

    Returns
    -------
    ee.Image
        Masked image

    """
    clouds = ee.Image(img.get('cloud_mask')).select('probability')
    isNotCloud = clouds.lt(MAX_CLOUD_PROBABILITY)
    return img.updateMask(isNotCloud).copyProperties(img, ["system:time_start"])


def cloud_mask_filter(col, MAX_CLOUD_PROBABILITY):
    """
    A wrapper function for cloud mask filter

    Parameters
    ----------
    col : ee Image collection
        the image collection to be filtered
    MAX_CLOUD_PROBABILITY : odd integer
        max cloud probability

    Returns
    -------
    ee.ImageCollection
        An image collection where a cloud mask filter is applied to each
        image individually

    """

    def _filter(image):
        _filtered = mask_clouds(image, MAX_CLOUD_PROBABILITY)
        return _filtered

    return col.map(_filter)


# ---------------------------------------------------------------------------//
# The masks for the 10m bands sometimes do not exclude bad data at
# scene edges, so we apply masks from the 20m and 60m bands as well.
# ---------------------------------------------------------------------------//
def mask_edges(s2_img):
    """
    masks images from the 20m and 60m bands

    Parameters
    ----------
    s2_img : ee.Image
        image to apply the border noise masking

    Returns
    -------
    ee.Image
        Masked image

    """
    return s2_img.updateMask(s2_img.select('B8A').mask().updateMask(s2_img.select('B9').mask()))


# 影像scale转换函数
def scale_image(image):
    """
    scale images by 10000

    Parameters
    ----------
    image : ee.Image
        image to apply scale

    Returns
    -------
    ee.Image
        Scaled image

    """
    time_start = image.get("system:time_strat")
    image = image.multiply(0.0001)
    image = image.set("system:time_strat", time_start)
    return image
