#!/bin/env python3
# -*- coding: utf-8 -*-
# @author Zeref996
# encoding=utf-8 vi:ts=4:sw=4:expandtab:ft=python
"""
测试执行器
"""
import os
import platform
from datetime import datetime
import layertest
from db.layer_db import LayerBenchmarkDB
from tools.case_select import CaseSelect
from tools.logger import Logger
from tools.yaml_loader import YamlLoader
from tools.res_save import xlsx_save
from tools.upload_bos import UploadBos


class Run(object):
    """
    最终执行接口
    """

    def __init__(self):
        """
        init
        """
        # 获取所有layer.yml文件路径
        # self.layer_dir = os.path.join("layercase", os.environ.get("CASE_DIR"))
        self.layer_dir = [os.path.join("layercase", item) for item in os.environ.get("CASE_DIR").split(",")]

        # 获取需要忽略的case
        # self.ignore_list = YamlLoader(yml=os.path.join("yaml", "ignore_case.yml")).yml.get(os.environ.get("CASE_DIR"))
        self.ignore_list = YamlLoader(yml=os.path.join("yaml", "ignore_case.yml")).yml.get(os.environ.get("TESTING"))

        # 获取测试集
        # self.py_list = CaseSelect(self.layer_dir, self.ignore_list).get_py_list(base_path=self.layer_dir)
        py_list = []
        for layer_dir in self.layer_dir:
            py_list = py_list + CaseSelect(layer_dir, self.ignore_list).get_py_list(base_path=layer_dir)

        # 测试集去重
        self.py_list = []
        for item in py_list:
            if not item in self.py_list:
                self.py_list.append(item)

        self.testing = os.environ.get("TESTING")
        self.py_cmd = os.environ.get("python_ver")
        self.report_dir = os.path.join(os.getcwd(), "report")

        self.logger = Logger("PaddleLTRun")
        self.AGILE_PIPELINE_BUILD_ID = os.environ.get("AGILE_PIPELINE_BUILD_ID", 0)
        self.now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _test_run(self):
        """run some test"""
        error_list = []
        error_count = 0
        for py_file in self.py_list:
            title = py_file.replace(".py", "").replace("/", "^").replace(".", "^")
            exit_code = os.system(
                "cp -r PaddleLT.py {}.py && "
                "{} -m pytest {}.py --title={} --layerfile={} --testing={} --alluredir={}".format(
                    title, self.py_cmd, title, title, py_file, self.testing, self.report_dir
                )
            )
            if exit_code != 0:
                error_list.append(py_file)
                error_count += 1
        if error_count != 0:
            # print("测试失败，报错子图为: {}".format(error_list))
            self.logger.get_log().warn("测试失败，报错子图为: {}".format(error_list))
            os.system("echo 7 > exit_code.txt")
        else:
            # print("测试通过，无报错子图-。-")
            self.logger.get_log().info("测试通过，无报错子图-。-")
            os.system("echo 0 > exit_code.txt")

    def _perf_test_run(self):
        """run some test"""
        sublayer_dict = {}
        error_count = 0
        error_list = []
        for py_file in self.py_list:
            title = py_file.replace(".py", "").replace("/", "^").replace(".", "^")
            single_test = layertest.LayerTest(title=title, layerfile=py_file, testing=self.testing)
            perf_dict, exit_code = single_test._perf_case_run()

            # 报错的子图+engine将不会收录进sublayer_dict
            if exit_code != 0:
                error_list.append(py_file)
                error_count += 1
                continue

            sublayer_dict[title] = perf_dict

        if error_count != 0:
            # print("测试失败，报错子图为: {}".format(error_list))
            self.logger.get_log().warn("测试失败，报错子图为: {}".format(error_list))
            os.system("echo 7 > exit_code.txt")
        else:
            # print("测试通过，无报错子图-。-")
            self.logger.get_log().info("测试通过，无报错子图-。-")
            os.system("echo 0 > exit_code.txt")

        # 数据库交互
        if os.environ.get("PLT_BM_DB") == "insert":  # 存入数据, 作为基线或对比
            layer_db = LayerBenchmarkDB(storage="apibm_config.yml")
            if os.environ.get("PLT_BM_MODE") == "baseline":
                layer_db.baseline_insert(data_dict=sublayer_dict, error_list=error_list)
            elif os.environ.get("PLT_BM_MODE") == "latest":
                layer_db.latest_insert(data_dict=sublayer_dict, error_list=error_list)
            else:
                raise Exception("unknown benchmark mode, PaddleLT benchmark only support baseline mode or latest mode")
        elif os.environ.get("PLT_BM_DB") == "select":  # 不存数据, 仅对比并生成表格
            layer_db = LayerBenchmarkDB(storage="apibm_config.yml")
            layer_db.compare_with_baseline(data_dict=sublayer_dict, error_list=error_list)
        elif os.environ.get("PLT_BM_DB") == "non-db":  # 不加载数据库，仅生成表格
            xlsx_save(
                sublayer_dict=sublayer_dict,
                excel_file=os.environ.get("TESTING").replace("yaml/", "").replace(".yml", "") + ".xlsx",
            )
        else:
            Exception("unknown benchmark datebase mode, only support insert, select or nonuse")

        # 产物上传
        bos_path = "PaddleLT/PaddleLTBenchmark/{}/build_{}".format(
            os.environ.get("PLT_BM_DB"), self.AGILE_PIPELINE_BUILD_ID
        )
        excel_file = os.environ.get("TESTING").replace("yaml/", "").replace(".yml", "") + ".xlsx"
        if os.path.exists(excel_file):
            UploadBos().upload_to_bos(bos_path="paddle-qa/{}".format(bos_path), file_path=excel_file)
            self.logger.get_log().info("表格下载链接: https://paddle-qa.bj.bcebos.com/{}/{}".format(bos_path, excel_file))
        os.system("tar -czf plot.tar *.png")
        UploadBos().upload_to_bos(bos_path="paddle-qa/{}".format(bos_path), file_path="plot.tar")
        self.logger.get_log().info("plot下载链接: https://paddle-qa.bj.bcebos.com/{}/{}".format(bos_path, "plot.tar"))
        os.system("tar -czf pickle.tar *.pickle")
        UploadBos().upload_to_bos(bos_path="paddle-qa/{}".format(bos_path), file_path="pickle.tar")
        self.logger.get_log().info("pickle下载链接: https://paddle-qa.bj.bcebos.com/{}/{}".format(bos_path, "pickle.tar"))


if __name__ == "__main__":
    tes = Run()
    if os.environ.get("TESTING_MODE") == "precision":
        tes._test_run()
    elif os.environ.get("TESTING_MODE") == "performance":
        tes._perf_test_run()
    else:
        raise Exception("unknown testing mode, PaddleLayerTest only support test precision or performance")
