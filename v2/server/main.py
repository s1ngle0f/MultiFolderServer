import io
import json
import os.path
import subprocess
import time
import datetime
import zipfile
from help_functions import get_diff, get_id, prepare_zippath, InMemoryZip
from files_manipulation import ManipulationType, file_manipulate
from fastapi import FastAPI, Request, Depends, UploadFile
from fastapi.responses import FileResponse, StreamingResponse, Response
import uvicorn
from os import listdir
from os.path import isfile, join
from models import User, Directory, LastTimeModification, File, db


settings_app_path = os.getcwd() + os.path.normpath('/settings_app')
files_buffer = {}
# data_app_path = os.path.dirname(os.getcwd()) + os.path.normpath('/data')
data_app_path = os.getcwd() + os.path.normpath('/data')

async def basic(request: Request):
    result = dict(request.query_params)
    print(result)
    with db:
        user = User.select().where((User.login == result['login']) & (User.password == result['password'])).first()
        if user != None:
            result['status'] = True
            result['user_id'] = user.id
        else:
            result['status'] = False
    return result

app = FastAPI()

@app.get('/installer/download')
async def installer_download(request: Request):
    if os.path.exists(settings_app_path + '/installer/installer_updater.exe'):
        return FileResponse(path=settings_app_path + '/installer/installer_updater.exe', media_type='application/octet-stream', filename='installer_updater.exe')

@app.get('/get_working_file')
async def get_working_file(request: Request):
    params = dict(request.query_params)
    if os.path.exists(settings_app_path + f'/{params["file_name"]}'):
        return FileResponse(path=settings_app_path + f'/{params["file_name"]}', media_type='application/octet-stream', filename=params["file_name"])

@app.get('/get_list_working_files')
async def get_list_working_files(request: Request):
    print(settings_app_path)
    files = [f for f in listdir(settings_app_path) if isfile(join(settings_app_path, f))]
    print(files)
    return {'files': files}

@app.get('/ping')
async def ping_pong(request: Request, params: dict = Depends(basic)):
    if params['status']:
        return 'Pong'

@app.get('/is_exist_user')
async def is_exist_user(params: dict = Depends(basic)):
    if params['status']:
        return True
    return False

@app.get('/get_dirs')
async def get_dirs(request: Request, params: dict = Depends(basic)):
    if params['status']:
        directories = Directory.select().where(Directory.user_id == params['user_id'])
        if directories is not None:
            return [{'name': directory.name} for directory in directories]
        return []

@app.get('/add_dir')
async def add_dir(request: Request, params: dict = Depends(basic)):
    if params['status']:
        directory = Directory.select().where((Directory.name == params['dir_name']) & (Directory.user_id == params['user_id'])).first()
        if directory is None:
            Directory.create(name=params['dir_name'], user_id=params['user_id'])
        git_dir_path = f'/home/{params["login"]}/git/{params["dir_name"]}.git'
        if not os.path.exists(git_dir_path):
            subprocess.run(["su", params["login"], "-c", f"mkdir -p '{git_dir_path}'"])
            subprocess.run(["su", params["login"], "-c", f"git init --bare '{git_dir_path}'"])

@app.get('/add_ssh_key')
async def add_ssh_key(request: Request, params: dict = Depends(basic)):
    if params['status']:
        username = params['login']
        ssh_key = params['ssh_key']
        with open(f"/home/{username}/.ssh/authorized_keys", 'r') as file:
            lines = file.read()
        if ssh_key not in lines:
            with open(f"/home/{username}/.ssh/authorized_keys", 'a') as file:
                file.write(ssh_key + '\n')

@app.get('/delete_dir')
async def delete_dir(request: Request, params: dict = Depends(basic)):
    if params['status']:
        directory = Directory.select().where((Directory.name == params['dir_name']) & (Directory.user_id == params['user_id'])).first()
        if directory is not None:
            File.delete().where(File.directory_id == directory.id).execute()
            LastTimeModification.delete().where(LastTimeModification.directory_id == directory.id).execute()
            Directory.delete().where(Directory.name == params['dir_name']).execute()

@app.get('/registrate')
async def registrate(request: Request):
    params = dict(request.query_params)
    username = params['login']
    if User.select().where(User.login == username).first() is None:
        User.create(login=username, password=params['password'])
    isuser = subprocess.run(["id", username]).returncode
    if isuser != 0:
        subprocess.run(["sudo", "useradd", "-m", username])
        subprocess.run(["chown", "-R", username, f'/home/{username}'])
        subprocess.run(["su", username, "-c", "mkdir -p ~/.ssh"])
        subprocess.run(["su", username, "-c", "touch ~/.ssh/authorized_keys"])
        subprocess.run(["su", username, "-c", "chmod 600 ~/.ssh/authorized_keys"])
        subprocess.run(["su", username, "-c", "chmod 700 ~/.ssh"])

if __name__ == '__main__':
    with db:
        db.create_tables([User, Directory, File, LastTimeModification])
    uvicorn.run(app, host='0.0.0.0', port=5000, loop='asyncio')