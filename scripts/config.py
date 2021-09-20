import yaml
import os
import sys


def read_config():
    path = "config.yaml"
    if not os.path.isfile(path):
        sys.exit("'config.yaml' not found! Please add it and try again.")
    else:
        with open(path, encoding='utf-8') as file:
            config = yaml.load(file, Loader=yaml.FullLoader)
    return config