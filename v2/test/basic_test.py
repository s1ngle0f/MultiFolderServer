import os.path
from os import listdir
from os.path import isfile, join

# print({'1': 1} | {'2': 2})
# print(os.path.basename('\\asdasd.txt'))

# code = b"\xff\xd8\xff\xdb\x00C"
# print(type(code))
# str_code = str(code)
# print(bytes(str_code, 'utf-8'))
#
# print(os.getcwd())

settings_app_path = os.path.dirname(os.getcwd()) + '\\settings_app'
onlyfiles = [f for f in listdir(settings_app_path) if isfile(join(settings_app_path, f))]
print(onlyfiles)