import random
import string
import os


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