import random
import string
import os
import zipfile
import io
import hashlib


def hash_password(password):
    sha256Hash = hashlib.sha256()
    sha256Hash.update(password.encode('utf-8'))
    hashedPassword = sha256Hash.hexdigest()
    return hashedPassword

def calculate_file_hash(file_path, hash_algorithm='sha256'):
    # Открываем файл в бинарном режиме
    with open(file_path, 'rb') as file:
        # Создаем объект хэша с выбранным алгоритмом
        hash_obj = hashlib.new(hash_algorithm)
        # Читаем файл блоками и обновляем хэш
        while chunk := file.read(4096):
            hash_obj.update(chunk)
    # Возвращаем строку с шестнадцатеричным представлением хэша
    return hash_obj.hexdigest()

def get_diff(last_files_info, current_files_info):
    add = []
    change = []
    remove = []

    for last_info in last_files_info:
        filter_files_info_data = list(filter(lambda x: x['path'] == last_info['path'], current_files_info))
        if len(filter_files_info_data) > 0:
            if last_info['time_modification'] < filter_files_info_data[0]['time_modification']:
                change.append(filter_files_info_data[0])
        else:
            remove.append(last_info)
    for current_info in current_files_info:
        filter_files_info_data = list(filter(lambda x: x['path'] == current_info['path'], last_files_info))
        if len(filter_files_info_data) == 0:
            add.append(current_info)

    return {
        'add': add,
        'change': change,
        'remove': remove
    }

def get_id(length: int=8):
    res = ''
    chars = '0123456789' + string.ascii_letters
    for _ in range(length):
        res += random.choice(chars)
    return res
# print(get_id())

def add_file_bytes(bytes_parts: dict):
    res = None
    bytes_parts = dict(sorted(bytes_parts.items()))
    for part_num, bytes_part in bytes_parts.items():
        if res == None:
            res = bytes_part
        else:
            res += bytes_part
    return res

def prepare_zippath(s):
    s = s.replace(chr(92), '/')
    char = '/'
    while char * 2 in s:
        s = s.replace(char * 2, char)
    s = os.path.relpath(s, '/').replace(chr(92), '/')
    while s[0] == '/' or s[0] == chr(92) or s[0] == '.':
        s = s[1:]
    return s

from typing import Generator
class InMemoryZip(object):
    def __init__(self, dir_path):
        # Create the in-memory file-like object
        self.in_memory_zip = io.BytesIO()
        self.dir_path = dir_path

    def append(self, files):
        '''Appends a file with name filename_in_zip and contents of
        file_contents to the in-memory zip.'''
        # Get a handle to the in-memory zip in append mode
        zf = zipfile.ZipFile(self.in_memory_zip, "a", zipfile.ZIP_DEFLATED, False)

        # Write the file to the in-memory zip
        for file in files:
            with open(self.dir_path + file['path'], 'rb') as f:
                data = f.read()
            zf.writestr(prepare_zippath(file['path']), data)

        # Mark the files as having been created on Windows so that
        # Unix permissions are not inferred as 0000
        for zfile in zf.filelist:
            zfile.create_system = 0

        # zf.close()
        return self

    def read(self):
        '''Returns a string with the contents of the in-memory zip.'''
        self.in_memory_zip.seek(0)
        return self.in_memory_zip.read()

    def read_generator(self) -> Generator:
        '''Returns a string with the contents of the in-memory zip.'''
        self.in_memory_zip.seek(0)
        yield self.in_memory_zip.read()

    def writetofile(self, filename):
        '''Writes the in-memory zip to a file.'''
        with open(filename, 'wb') as f:
            f.write(self.read())