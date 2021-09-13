# -*- coding: utf-8 -*-
# encoding=utf-8 vi:ts=4:sw=4:expandtab:ft=python
"""
test ppyolov2 model
"""

import os
import sys
import logging
import tarfile
import six
import wget
import pytest
import numpy as np

# pylint: disable=wrong-import-position
sys.path.append("..")
from test_case import InferenceTest

# pylint: enable=wrong-import-position


def check_model_exist():
    """
    check model exist
    """
    ppyolov2_url = "https://paddle-qa.bj.bcebos.com/inference_model/2.1.0/detection/ppyolov2.tgz"
    if not os.path.exists("./ppyolov2/model.pdiparams"):
        wget.download(ppyolov2_url, out="./")
        tar = tarfile.open("ppyolov2.tgz")
        tar.extractall()
        tar.close()


@pytest.mark.p0
@pytest.mark.config_init_combined_model
def test_config():
    """
    test combined model config
    """
    check_model_exist()
    test_suite = InferenceTest()
    test_suite.load_config(model_file="./ppyolov2/model.pdmodel", params_file="./ppyolov2/model.pdiparams")
    test_suite.config_test()


@pytest.mark.p0
@pytest.mark.config_disablegpu_memory
def test_disable_gpu():
    """
    test no gpu resources occupied after disable gpu
    """
    check_model_exist()
    test_suite = InferenceTest()
    test_suite.load_config(model_file="./ppyolov2/model.pdmodel", params_file="./ppyolov2/model.pdiparams")
    batch_size = 1
    im_size = 640
    im = np.random.randn(batch_size, 3, 640, 640).astype("float32")
    data = np.random.randn(batch_size, 3, 640, 640).astype("float32")
    scale_factor = (
        np.array([im_size * 1.0 / im.shape[0], im_size * 1.0 / im.shape[1]]).reshape((1, 2)).astype(np.float32)
    )
    im_shape = np.array([im_size, im_size]).reshape((1, 2)).astype(np.float32)
    input_data_dict = {"im_shape": im_shape, "image": data, "scale_factor": scale_factor}
    test_suite.disable_gpu_test(input_data_dict)


@pytest.mark.p1
@pytest.mark.mkldnn_more_bz_precision
def test_more_bz_mkldnn():
    """
    compared mkldnn ppyolov2 more batch size outputs with true val
    """
    check_model_exist()

    file_path = "./ppyolov2"
    images_size = 640
    batch_size_pool = [1, 5, 10]
    for batch_size in batch_size_pool:

        test_suite = InferenceTest()
        test_suite.load_config(model_file="./ppyolov2/model.pdmodel", params_file="./ppyolov2/model.pdiparams")
        images_list, images_origin_list, npy_list = test_suite.get_images_npy(
            file_path, images_size, center=False, model_type="det"
        )

        img = images_origin_list[0:batch_size]
        result = npy_list[0 : batch_size * 2]
        data = np.array(images_list[0:batch_size]).astype("float32")
        scale_factor_pool = []
        for batch in range(batch_size):
            scale_factor = (
                np.array([images_size * 1.0 / img[batch].shape[0], images_size * 1.0 / img[batch].shape[1]])
                .reshape((1, 2))
                .astype(np.float32)
            )
            scale_factor_pool.append(scale_factor)
        scale_factor_pool = np.array(scale_factor_pool).reshape((batch_size, 2))
        im_shape_pool = []
        for batch in range(batch_size):
            im_shape = np.array([images_size, images_size]).reshape((1, 2)).astype(np.float32)
            im_shape_pool.append(im_shape)
        im_shape_pool = np.array(im_shape_pool).reshape((batch_size, 2))
        input_data_dict = {"im_shape": im_shape_pool, "image": data, "scale_factor": scale_factor_pool}

        scale_0 = []
        for batch in range(0, batch_size * 2, 2):
            scale_0 = np.concatenate((scale_0, result[batch].flatten()), axis=0)
        scale_1 = []
        for batch in range(1, batch_size * 2, 2):
            scale_1 = np.concatenate((scale_1, result[batch].flatten()), axis=0)

        output_data_dict = {"save_infer_model/scale_0.tmp_1": scale_0, "save_infer_model/scale_1.tmp_1": scale_1}
        test_suite.load_config(model_file="./ppyolov2/model.pdmodel", params_file="./ppyolov2/model.pdiparams")
        test_suite.mkldnn_test(input_data_dict, output_data_dict, repeat=1, delta=1e-4)


@pytest.mark.p1
@pytest.mark.gpu_more_bz_precision
def test_gpu_more_bz():
    """
    compared gpu ppyolov2 more batch size outputs with true val
    """
    check_model_exist()

    file_path = "./ppyolov2"
    images_size = 640
    batch_size_pool = [1, 5]
    for batch_size in batch_size_pool:

        test_suite = InferenceTest()
        test_suite.load_config(model_file="./ppyolov2/model.pdmodel", params_file="./ppyolov2/model.pdiparams")
        images_list, images_origin_list, npy_list = test_suite.get_images_npy(
            file_path, images_size, center=False, model_type="det"
        )

        img = images_origin_list[0:batch_size]
        result = npy_list[0 : (batch_size) * 2]
        data = np.array(images_list[0:batch_size]).astype("float32")
        scale_factor_pool = []
        for batch in range(batch_size):
            scale_factor = (
                np.array([images_size * 1.0 / img[batch].shape[0], images_size * 1.0 / img[batch].shape[1]])
                .reshape((1, 2))
                .astype(np.float32)
            )
            scale_factor_pool.append(scale_factor)
        scale_factor_pool = np.array(scale_factor_pool).reshape((batch_size, 2))
        im_shape_pool = []
        for batch in range(batch_size):
            im_shape = np.array([images_size, images_size]).reshape((1, 2)).astype(np.float32)
            im_shape_pool.append(im_shape)
        im_shape_pool = np.array(im_shape_pool).reshape((batch_size, 2))
        input_data_dict = {"im_shape": im_shape_pool, "image": data, "scale_factor": scale_factor_pool}

        scale_0 = []
        for batch in range(0, batch_size * 2, 2):
            scale_0 = np.concatenate((scale_0, result[batch].flatten()), axis=0)
        scale_1 = []
        for batch in range(1, batch_size * 2, 2):
            scale_1 = np.concatenate((scale_1, result[batch].flatten()), axis=0)

        output_data_dict = {"save_infer_model/scale_0.tmp_1": scale_0, "save_infer_model/scale_1.tmp_1": scale_1}
        test_suite.load_config(model_file="./ppyolov2/model.pdmodel", params_file="./ppyolov2/model.pdiparams")
        test_suite.gpu_more_bz_test(input_data_dict, output_data_dict, repeat=1, delta=1e-4)
