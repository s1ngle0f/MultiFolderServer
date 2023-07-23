import io
import json
import os.path
import subprocess
import time
import datetime
import zipfile
from help_functions import get_diff, get_id, prepare_zippath, InMemoryZip, hash_password
from files_manipulation import ManipulationType, file_manipulate
from fastapi import FastAPI, Request, Depends, UploadFile
from fastapi.responses import FileResponse, StreamingResponse, Response
from authorization_system import generate_token
import uvicorn
from os import listdir
from os.path import isfile, join
from models import User, Directory, LastTimeModification, File, Tokens, db
from main_site import site_router
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


settings_app_path = os.getcwd() + os.path.normpath('/settings_app')
files_buffer = {}
# data_app_path = os.path.dirname(os.getcwd()) + os.path.normpath('/data')
data_app_path = os.getcwd() + os.path.normpath('/data')

async def basic(request: Request):
    result = dict(request.query_params)
    print(result)
    with db:
        user = await get_user_by_token(result['usertoken'])
        if user != None:
            result['status'] = True
            result['user_id'] = user.id
        else:
            result['status'] = False
    return result

async def get_user_by_token(usertoken) -> User:
    current_token = usertoken
    # print(f'Current token: {current_token}')
    if current_token is not None:
        token = Tokens.select().where(Tokens.token == current_token).first()
        if token is not None:
            user_id = token.user_id
            return User.select().where(User.id == user_id).first()
        else:
            None
    else:
        return None

app = FastAPI()
app.include_router(site_router)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get('/installer/download')
async def installer_download(request: Request):
    if os.path.exists(settings_app_path + '/installer/Setup.msi'):
        return FileResponse(path=settings_app_path + '/installer/Setup.msi', media_type='application/octet-stream', filename='Setup.msi')

@app.get('/get_working_file')
async def get_working_file(request: Request):
    params = dict(request.query_params)
    if os.path.exists(settings_app_path + f'/{params["file_name"]}'):
        return FileResponse(path=settings_app_path + f'/{params["file_name"]}', media_type='application/octet-stream', filename=params["file_name"])

@app.get('/get_list_working_files')
async def get_list_working_files(request: Request):
    def split_path_into_list(path):
        path_parts = []
        while True:
            path, folder = os.path.split(path)
            if folder:
                path_parts.insert(0, folder)
            else:
                if path:
                    path_parts.insert(0, path)
                break
        return path_parts

    print(settings_app_path)
    file_paths = []
    for root, dirs, files in os.walk(settings_app_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(file_path)

    base_path = os.path.abspath(settings_app_path)
    relative_files = [os.path.relpath(file_path, base_path) for file_path in file_paths if split_path_into_list(os.path.relpath(file_path, base_path))[0] != "installer"]
    print(relative_files)
    return {'files': relative_files}

@app.get('/ping')
async def ping_pong(request: Request, params: dict = Depends(basic)):
    if params['status']:
        return 'Pong'

@app.get('/is_exist_user')
async def is_exist_user(params: dict = Depends(basic)):
    if params.get('password') is None:
        if params['status']:
            return True
    else:
        user = User.select().where((User.login == result['login']) & (User.password == hash_password(result['password']))).first()
        if user != None:
            return True
    return False

@app.get('/is_exist_user_by_password')
async def is_exist_user_by_password(request: Request):
    params = dict(request.query_params)
    user = User.select().where((User.login == params['login']) & (User.password == hash_password(params['password']))).first()
    if user != None:
        return True
    return False

@app.get('/get_dirs')
async def get_dirs(request: Request, params: dict = Depends(basic)):
    if params['status']:
        directories = Directory.select().where(Directory.user_id == params['user_id'])
        if directories is not None:
            return [directory.name for directory in directories]
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
            subprocess.run(["su", params["login"], "-c", f"git config --system --add safe.directory '*'"])

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
        User.create(login=username, password=hash_password(params['password']))
    isuser = subprocess.run(["id", username]).returncode
    if isuser != 0:
        subprocess.run(["sudo", "useradd", "-m", username])
        subprocess.run(["chown", "-R", username, f'/home/{username}'])
        subprocess.run(["su", username, "-c", "mkdir -p ~/.ssh"])
        subprocess.run(["su", username, "-c", "touch ~/.ssh/authorized_keys"])
        subprocess.run(["su", username, "-c", "chmod 600 ~/.ssh/authorized_keys"])
        subprocess.run(["su", username, "-c", "chmod 700 ~/.ssh"])

@app.get('/authorization_desktop')
async def authorization_desktop_get(request: Request, response: Response):
    params = dict(request.query_params)
    current_token = params.get("usertoken")
    if current_token is not None:
        Tokens.delete().where(Tokens.token == current_token).execute()
    new_token = generate_token()
    login = params["login"]
    password = hash_password(params["password"])
    user = User.select().where((User.login == login) & (User.password == password)).first()
    if user is not None:
        Tokens.create(token=new_token, user_id=user.id)
        return new_token
    return None

if __name__ == '__main__':
    with db:
        db.create_tables([User, Directory, File, LastTimeModification, Tokens])
    Tokens.delete().execute()
    # uvicorn.run(app, host='0.0.0.0', port=5000, loop='asyncio')
    uvicorn.run('main:app', host='0.0.0.0', port=5000, loop='asyncio', reload=True)