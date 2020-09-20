# -*- coding: utf-8 -*-
import os


def check_exp_dir():
    if not os.path.isdir("experiment_output"):
        os.mkdir("experiment_output")
