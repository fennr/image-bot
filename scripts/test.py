from datetime import datetime
from scripts.config import read_config
from pprint import pprint
import posixpath
import os
import yadisk
import time
import sys
import yaml
import requests
import discord

def func():
    print(datetime.now())

def ya_test(ctx):
    path = "config.yaml"
    if not os.path.isfile(path):
        sys.exit("'config.yaml' not found! Please add it and try again.")
    else:
        with open(path) as file:
            config = yaml.load(file, Loader=yaml.FullLoader)
    token = config["yadisk"]
    y = yadisk.YaDisk(token=token)

    # Проверяет, валиден ли токен
    # Получает общую информацию о диске

    path = config["root"]
    trash = config["trash"]
    root = list(y.listdir(path))

    max = config["count"]
    count = 0
    for set in root:
        set_path = path + '/' + set.name
        trash_path = trash + '/' + set.name
        try:
            y.mkdir(trash_path)
            time.sleep(2)
        except:
            pass
        files = list(y.listdir(set_path))
        pprint(files)
        ret = []
        for file in files:
            if file.name == '!readme.txt':
                r = requests.get(file.file)
                r.encoding = 'utf-8'
                print(r.text)
                ret.append(r.text)
                #y.move(file_path, move_path, overwrite=True, retry_interval=2, n_retries=2)
            else:
                if count < max:
                    file_path = set_path + '/' + file.name
                    move_path = trash_path + '/' + file.name
                    y.move(file_path, move_path, overwrite=True, retry_interval=2, n_retries=2)
                    print(file.name, file.preview)
                    ret.append(file.name)
                    count += 1
                else:
                    return ret
        print()

if __name__ == '__main__':
    print("work")