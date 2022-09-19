import time

import jsondiff
from flask import Flask, request, jsonify, send_file
import sqlite3
import os
from os import listdir
from os.path import isfile, join
import directory_tree

data_path = __file__[:str(__file__).rfind('\\')+1].replace('\\', '/') + 'DATA/' #'C:/Users/zubko/Desktop/DATA/'
settings_app_path = __file__[:str(__file__).rfind('\\')+1].replace('\\', '/') + 'SettingsApp/' #'C:/Users/zubko/Desktop/SettingsApp'

if not os.path.exists(data_path[:-1]):
    os.makedirs(data_path[:-1])
if not os.path.exists(settings_app_path[:-1]):
    os.makedirs(settings_app_path[:-1])

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        params = request.values
        print(params.to_dict(), params.get('login'))
        main_path = data_path + params.get('login') + '/' + params.get('path').replace('/'+request.files.get('document').filename, '') + '/'
        print(main_path)
        if not os.path.isdir(main_path):
            os.makedirs(main_path)
        filename = main_path + str(request.files.get('document').filename)
        request.files.get('document').save(filename)
        print(type(request.files.get('document')), request.files.get('document').filename)
        return jsonify('Created!')

@app.route('/createFolders', methods=['POST'])
def createFolders():
    if request.method == 'POST':
        params = request.values
        print(params.to_dict(), params.get('login'))
        main_path = data_path + params.get('login') + '/' + params.get('path')
        print(main_path)
        if not os.path.isdir(main_path):
            os.makedirs(main_path)
        return jsonify('Created folders!')

@app.route('/equalTree', methods=['POST'])
def equalTree():
    if request.method == 'POST':
        params = request.values
        json = request.json
        print(json, type(json))
        print(params.to_dict(), params.get('login'))
        main_path = data_path + params.get('login') + '/' + json['name']
        print(main_path)
        print(directory_tree.path_to_dict(main_path))
        if directory_tree.path_to_dict(main_path) == json:
            return {'isEquals': True}
        else:
            return {'isEquals': False}

@app.route('/getTree', methods=['GET'])
def getTree():
    if request.method == 'GET':
        params = request.values
        print(params.to_dict(), params.get('login'))
        main_path = data_path + params.get('login') + '/' + params.get('folder_name')
        print(main_path)
        response = directory_tree.path_to_dict(main_path)
        # print(response)
        return jsonify(response if response.get('type') != 'file' else 'This directory dont exist')

@app.route('/isExistFolder', methods=['GET'])
def isExistFolder():
    if request.method == 'GET':
        params = request.values
        print(params.to_dict(), params.get('login'))
        main_path = data_path + params.get('login') + '/' + params.get('folder_name')
        if not os.path.exists(main_path):
            os.makedirs(main_path)
            return jsonify(False)
        else:
            return jsonify(True)

@app.route('/getLastTimeModification', methods=['GET'])
def getLastTimeModification():
    if request.method == 'GET':
        params = request.values
        base_dir = data_path + params.get('login') + '/'
        main_path = base_dir + params.get('folder_name')
        response = directory_tree.get_files_folder_and_time(main_path, base_dir=base_dir)
        return jsonify(sorted(response.values())[-1])

@app.route('/getFilesSize', methods=['GET'])
def getFilesSize():
    if request.method == 'GET':
        params = request.values
        base_dir = data_path + params.get('login') + '/'
        main_path = base_dir + params.get('folder_name')
        response = directory_tree.get_files_folder_and_size(main_path, base_dir=base_dir)
        return jsonify(response)

@app.route('/getDirs', methods=['GET'])
def getDirs():
    if request.method == 'GET':
        params = request.values
        base_dir = data_path + params.get('login')
        return jsonify([os.path.basename(x) for x in os.listdir(base_dir)])

@app.route('/deleteNonExistentFoldersOrFiles', methods=['POST'])
def deleteNonExistentFoldersOrFiles():
    if request.method == 'POST':
        params = request.values
        json = request.json
        main_path = data_path + params.get('login') + '/' + params.get('folder_name')
        tree = directory_tree.path_to_dict(main_path)
        client_arr = getPathsOfTree(json, '')
        server_arr = getPathsOfTree(tree, '')
        deleteArr = findDifferentForDelete(client_arr, server_arr)
        for i in deleteArr:
            try:
                if os.path.isdir(main_path + i):
                    os.removedirs(main_path + i)
                else:
                    os.remove(main_path + i)
            except:
                print(main_path + i)
                print('Error')
        # print(getPathsOfTree(tree, main_path))
        return jsonify('Deleted!')

@app.route('/delete', methods=['GET'])
def delete():
    if request.method == 'GET':
        params = request.values
        main_path = data_path + params.get('login') + '/' + params.get('path')
        if os.path.isdir(main_path):
            os.removedirs(main_path)
        else:
            os.remove(main_path)
    return jsonify('Deleted!')

def findDifferentForDelete(client_tree, server_tree):
    recieve = []
    for i in server_tree:
        if i not in client_tree:
            recieve.append(i)
    return recieve

def getPathsOfTree(tree, path):
    arr = []
    if tree['type'] == 'directory':
        for i, child in enumerate(tree['children']):
            arr.append((path + '/' + child['name']).replace(data_path, ''))
            # print(path + '/' + child['name'])
            if child['type'] == 'directory':
                _getPathsOfTree(child, path + '/' + child['name'], arr)
    return arr

def _getPathsOfTree(tree, path, arr):
    if tree['type'] == 'directory':
        for i, child in enumerate(tree['children']):
            arr.append((path + '/' + child['name']).replace(data_path, ''))
            # print(path + '/' + child['name'])
            if child['type'] == 'directory':
                _getPathsOfTree(child, path + '/' + child['name'], arr)

@app.route('/getListOfMissingObjects', methods=['POST'])
def getListOfMissingObjects():
    params = request.values
    json = request.json
    main_path = data_path + params.get('login') + '/' + params.get('folder_name')
    tree = directory_tree.path_to_dict(main_path)
    client_arr = getPathsOfTree(json, '')
    server_arr = getPathsOfTree(tree, '')
    # print(client_arr)
    # print(server_arr)
    recieve = findDifferentForDelete(client_arr, server_arr)
    print(recieve)
    return jsonify(recieve)

@app.route('/getFile', methods=['GET'])
def getFile():
    params = request.values
    main_path = data_path + params.get('login') + '/' + params.get('folder_name') + params.get('path')
    print(main_path)
    tree = directory_tree.path_to_dict(main_path)
    # return jsonify()
    return send_file(main_path)

@app.route('/getFilesArray', methods=['GET'])
def getFilesArray():
    params = request.values
    main_path = data_path + params.get('login') + '/' + params.get('folder_name')

    return jsonify(directory_tree.get_files_folder(main_path))

@app.route('/getListSettingsApp', methods=['GET'])
def getListSettingsApp():
    return jsonify([f for f in listdir(settings_app_path) if isfile(join(settings_app_path, f))])

@app.route('/getSettingsApp', methods=['GET'])
def getSettingsApp():
    params = request.values
    return send_file(settings_app_path + '/' + params.get('app_name'))

@app.route('/download', methods=['GET'])
def download():
    return send_file(settings_app_path + '/MAIN_APP/main_app.exe')

# def deleteJdiff(tree, jdiff, path):
#     print(jdiff)
#     print()
#     for k, v in jdiff.items():
#         if str(k) == '$delete':
#             for i in v:
#                 pass
#         # else:
#         #     deleteJdiff(tree.get(k), v, path + '/')
#
#
#     # if json['name'] == tree['name'] and json['type'] == tree['type']:
#     #     if tree['type'] == 'directory':
#     #         for i, child in enumerate(tree['children']):
#     #             print(path + '/' + child['name'])
#     #             try:
#     #                 delete(json['children'][i], child, path + '/' + child['name'])
#     #             except:
#     #                 os.removedirs(path + '/' + child['name'])#Удалить папку
#     #                 print('ERRROR')
#     #                 return False
#     # else:
#     #     return False
#     return True
#
# def deleteDirs(json, tree, path):
#     print(json)
#     print(tree)
#     if json['name'] == tree['name'] and json['type'] == tree['type']:
#         if tree['type'] == 'directory':
#             for i, child in enumerate(tree['children']):
#                 print(path + '/' + child['name'])
#                 try:
#                     deleteDirs(json['children'][i], child, path + '/' + child['name'])
#                 except:
#                     try:
#                         os.removedirs(path + '/' + child['name'])  # Удалить папку
#                     except:
#                         os.remove(path + '/' + child['name'])
#                     print('ERRROR')
#                     return False
#     else:
#         try:
#             os.removedirs(path + '/' + tree['name'])
#         except:
#             os.remove(path + '/' + tree['name'])
#         return False
#     return True
#
# def deleteFiles(json, tree, path):
#     print(json)
#     print(tree)
#     if json['name'] == tree['name'] and json['type'] == tree['type']:
#         if tree['type'] == 'directory':
#             for i, child in enumerate(tree['children']):
#                 print(path + '/' + child['name'])
#                 try:
#                     deleteFiles(json['children'][i], child, path + '/' + child['name'])
#                 except:
#                     if os.path.isdir(path + '/' + child['name']):
#                         os.removedirs(path + '/' + child['name'])#Удалить папку
#                     else:
#                         os.remove(path + '/' + child['name'])
#                     print('ERRROR')
#                     return False
#     else:
#         if os.path.isdir(path + '/' + tree['name']):
#             os.removedirs(path + '/' + tree['name'])  # Удалить папку
#         else:
#             os.remove(path + '/' + tree['name'])
#         return False
#     return True
#
# def getDifferentPathAndFiles(json, tree, path):
#     paths = []
#     if json['name'] == tree['name'] and json['type'] == tree['type']:
#         if tree['type'] == 'directory':
#             pass
#             # for i, child in enumerate(tree['children']):
#             #     print(path + '/' + child['name'])
#             #     try:
#             #         getDifferentPathAndFiles(json['children'][i], child, path + '/' + child['name'])
#             #     except:
#             #         try:
#             #             os.removedirs(path + '/' + child['name'])  # Удалить папку
#             #         except:
#             #             os.remove(path + '/' + child['name'])
#             #         print('ERRROR')
#             #         return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000 ,debug=False)
