import os.path

# print({'1': 1} | {'2': 2})
# print(os.path.basename('\\asdasd.txt'))

code = b"\xff\xd8\xff\xdb\x00C"
print(type(code))
str_code = str(code)
print(bytes(str_code, 'utf-8'))

print(os.getcwd())