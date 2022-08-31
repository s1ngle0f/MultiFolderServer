import os

def path_to_dict(path):
    d = {'name': os.path.basename(path)}
    if os.path.isdir(path):
        d['type'] = "directory"
        d['children'] = [path_to_dict(os.path.join(path,x)) for x in os.listdir(path)]
    else:
        d['type'] = "file"
    return d

def get_files_folder_and_time(path, base_dir = '', d = None):
    if d == None:
        d = {}
    if not os.path.isdir(path):
        if os.path.basename(path.replace('\\', '/').replace(base_dir, ''))[0:2] != '~$':
            d[path.replace('\\', '/').replace(base_dir, '')] = os.path.getmtime(path)
    else:
        if path.replace('\\', '/').replace(base_dir, '').find('/') != -1: #Чтобы убрать время папки, в которой все находится
            d[path.replace('\\', '/').replace(base_dir, '')] = os.path.getmtime(path)
        for x in os.listdir(path):
            get_files_folder_and_time(os.path.join(path,x), base_dir, d)
    return d

def get_files_folder_and_size(path, base_dir = '', d = None):
    if d == None:
        d = {}
    if not os.path.isdir(path):
        if os.path.basename(path.replace('\\', '/').replace(base_dir, ''))[0:2] != '~$':
            d[path.replace('\\', '/').replace(base_dir, '')] = os.path.getsize(path)
    else:
        for x in os.listdir(path):
            get_files_folder_and_size(os.path.join(path,x), base_dir, d)
    return d

def get_files_folder(path, base_dir = '', d = None):
    if d == None:
        d = []
    if base_dir == '':
        base_dir = path[:path.rfind('/') + 1]
        # dir = path.replace(base_dir, '')
    if not os.path.isdir(path):
        if os.path.basename(path.replace('\\', '/').replace(base_dir, ''))[0:2] != '~$':
            d.append(path.replace('\\', '/').replace(base_dir, ''))
    else:
        if path.replace('\\', '/').replace(base_dir, '').find('/') != -1: #Чтобы убрать время папки, в которой все находится
            d.append(path.replace('\\', '/').replace(base_dir, ''))
        for x in os.listdir(path):
            get_files_folder(os.path.join(path,x), base_dir, d)
    return d