import random
import string
import os
import zipfile
import io


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
    s = s.replace(os.sep, '/')
    char = '/'
    while char * 2 in s:
        s = s.replace(char * 2, char)
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
            zf.writestr(os.path.relpath(file['path'], '\\'), data)

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