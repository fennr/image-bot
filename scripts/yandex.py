import os
import time
import yadisk
import requests
from datetime import datetime
from scripts.config import read_config
from discord import File
from pprint import pprint

config = read_config()
y = yadisk.YaDisk(token=config["yadisk"])


def is_good_time(time: list):
    """
    Возвращает совпадает ли текущее время с временем для публикации

    :param time: list с временем публикаций
    :return: bool
    """
    now = datetime.now().strftime('%H:%M')
    if now in time:
        return True
    else:
        return False


def create_trash(trash, name):
    """
    Создание папок с аналогичными названиями в корзине

    :param trash: str, основная папка Корзины
    :param name: str, имя обрабатываемой папки
    :return: None
    """
    path = f"{trash}/{name}"
    try:
        y.mkdir(path)
        time.sleep(2)
    except:
        pass


def is_readme(file):
    """
    Проверка является ли файл текстовым

    :param file: yadisk.file, файл считанный с ЯД
    :return: bool
    """
    if file.media_type == 'document':
        return True
    else:
        return False

def read_set_name(file):
    """
    Считывание названия сета

    :param file: yadisk.file, файл считанный с ЯД
    :return: str, имя папки, в которой лежит изображение
    """
    directory, file_name = file.path.replace(f"disk:{config['root']}", "")[1:].split('/', maxsplit=1)
    return directory


def read_file(file):
    """
    Считывание текста из текстового файла

    :param file: yadisk.file, файл считанный с ЯД
    :return: str, весь текст из файла
    """
    r = requests.get(file.file)
    r.encoding = 'utf-8'
    return r.text


def read_image(file):
    """
    Считывание изображения из яндекса в discord.File

    :param file: yadisk.file
    :return: discord.File
    """
    directory, file_name = file.path.replace(f"disk:{config['root']}", "")[1:].split('/', maxsplit=1)
    directory = 'img/' + directory
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = directory + '/' + file.name
    with open(file_path, 'wb') as image:
        r = requests.get(file.file)
        image.write(r.content)
    with open(file_path, 'rb') as image:
        picture = File(image, filename=file.name)
        return picture


def move_to_trash(file):
    """
    Перемещение файла в корзину

    :param file: yadisk.file, файл считанный с ЯД
    :return: None
    """
    trash_path = file.path.replace(config["root"], config["trash"])
    y.move(file.path, trash_path, overwrite=True, retry_interval=2, n_retries=2)


def get_all_files(path, trash):
    """
    Считывание всех файлов внутри каждой папки (не рекурсивно)

    :param path: str, корневая папка
    :param trash: str, папка для корзины
    :return: list of yadisk.file
    """
    root = list(y.listdir(path))
    all_files = []
    for set in root:
        set_path = path + '/' + set.name
        create_trash(trash, set.name)
        set_files = list(y.listdir(set_path))
        all_files = [*all_files, *set_files]
    return all_files

def get_files(path, trash, max):
    """
    Аналогичное считывание, но с оптимизацией по количеству считываемых файлов
    Выходит из цикла, если в папке уже больше файлов чем нужно

    :param path: str, корневая папка
    :param trash: str, папка для корзины
    :param max: int, количество нужных файлов
    :return: list of yadisk.file
    """
    root = list(y.listdir(path))
    all_files = []
    for set in root:
        set_path = path + '/' + set.name
        create_trash(trash, set.name)
        set_files = list(y.listdir(set_path))
        if config['upload'] == 'set' and len(set_files) > 0:
            return set_files
        all_files = [*all_files, *set_files]
        if len(all_files) > max and config['upload'] != 'set':
            return all_files
    return all_files


if __name__ == '__main__':
    files = get_files(config["root"], config["trash"], 2)
    for file in files:
        print(file.file)
        print(read_image(file))



