import json
import os.path
import time
import datetime
from help_functions import get_diff
from fastapi import FastAPI, Request, Depends, UploadFile
from fastapi.responses import FileResponse
import uvicorn
from os import listdir
from os.path import isfile, join
from models import User, Directory, LastTimeModification, File, db


settings_app_path = os.getcwd() + '/settings_app'

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

def save_file_last_time_modification(directory_id, timestamp):
    # print(f'{directory_id} {timestamp}')
    dir_ltm = LastTimeModification.select().where(LastTimeModification.directory_id == directory_id).first()
    if dir_ltm == None:
        LastTimeModification.create(directory_id=directory_id, timestamp=timestamp)
    else:
        dir_ltm_timestamp = time.mktime(datetime.datetime.strptime(str(dir_ltm.timestamp), "%Y-%m-%d %H:%M:%S").timetuple())
        if timestamp > dir_ltm_timestamp:
            LastTimeModification.update(timestamp=timestamp).where(LastTimeModification.directory_id == directory_id).execute()

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

@app.get('/delete_file')
async def delete_file(request: Request, params: dict = Depends(basic)):
    if params['status']:
        directory = Directory.select().where((Directory.name == params['dir_name']) & (Directory.user_id == params['user_id'])).first()
        if directory != None:
            File.delete().where((File.directory_id == directory.id) & (File.path == params['local_path'])).execute()
            save_file_last_time_modification(directory.id, float(params['timestamp']))
            return 'Deleted'

@app.post('/upload_file')
async def upload_file(request: Request, file: UploadFile, params: dict = Depends(basic)):
    if params['status']:
        directory = Directory.select().where((Directory.name == params['dir_name']) & (Directory.user_id == params['user_id'])).first()
        if directory != None:
            existing_file = File.select().where((File.path == params['local_path']) & (File.directory_id == directory.id)).first()
            file_data = await file.read()
            if existing_file == None:
                File.create(directory_id=directory.id, name=os.path.basename(file.filename), path=params['local_path'],
                            timestamp=float(params['timestamp']), size=len(file_data), data=file_data) #ПОФИКСИТЬ ЗАГРУЗКУ БИТОВ
            else:
                File.update(timestamp=float(params['timestamp']), size=len(file_data), data=file_data).where(
                    (File.path == params['local_path']) & (File.directory_id == directory.id)
                ).execute()
            save_file_last_time_modification(directory.id, float(params['dir_timestamp']))
            return 'Uploaded'

@app.get('/get_file')
async def get_file(request: Request, params: dict = Depends(basic)):
    if params['status']:
        directory = Directory.select().where((Directory.name == params['dir_name']) & (Directory.user_id == params['user_id'])).first()
        if directory != None:
            file = File.select().where((File.directory_id == directory.id) & (File.path == params['local_path'])).first()
            if file != None:
                # print(bytes(file.data)[:100])
                time_modification = time.mktime(datetime.datetime.strptime(str(file.timestamp), "%Y-%m-%d %H:%M:%S").timetuple())
                return {'name': file.name, 'path': file.path, 'time_modification': time_modification, 'size': file.size, 'data': str(bytes(file.data))[2:-1]}

@app.get('/get_dir_last_time_modification')
async def get_dir_last_time_modification(request: Request, params: dict = Depends(basic)):
    if params['status']:
        directory = Directory.select().where((Directory.name == params['dir_name']) & (Directory.user_id == params['user_id'])).first()
        if directory != None:
            dir_ltm = LastTimeModification.select().where((LastTimeModification.directory_id == directory.id)).first()
            ltm = dir_ltm.timestamp if dir_ltm != None else 0
            return time.mktime(datetime.datetime.strptime(str(ltm), "%Y-%m-%d %H:%M:%S").timetuple()) if isinstance(ltm, datetime.datetime) else 0

@app.get('/get_dirs')
async def get_dirs(request: Request, params: dict = Depends(basic)):
    if params['status']:
        directories = Directory.select().where(Directory.user_id == params['user_id'])
        if directories != None:
            return [{'name': directory.name} for directory in directories]
        return []

@app.get('/get_dir')
async def get_dir(request: Request, params: dict = Depends(basic)):
    if params['status']:
        directory = Directory.select().where((Directory.name == params['dir_name']) & (Directory.user_id == params['user_id'])).first()
        if directory != None:
            return [{'name': file.name, 'path': file.path, 'time_modification': file.timestamp, 'size': file.size} for file in File.select().where(File.directory_id == directory.id)]

@app.get('/add_dir')
async def add_dir(request: Request, params: dict = Depends(basic)):
    if params['status']:
        directory = Directory.select().where((Directory.name == params['dir_name']) & (Directory.user_id == params['user_id'])).first()
        if directory == None:
            Directory.create(name=params['dir_name'], user_id=params['user_id'])
            return 'Directory was created'

@app.get('/delete_dir')
async def delete_dir(request: Request, params: dict = Depends(basic)):
    if params['status']:
        directory = Directory.select().where((Directory.name == params['dir_name']) & (Directory.user_id == params['user_id'])).first()
        if directory != None:
            File.delete().where(File.directory_id == directory.id).execute()
            LastTimeModification.delete().where(LastTimeModification.directory_id == directory.id).execute()
            Directory.delete().where(Directory.name == params['dir_name']).execute()
            return 'Directory was deleted'

@app.get('/get_differents')
async def get_differents(request: Request, params: dict = Depends(basic)):
    if params['status']:
        client_files_info = json.loads(await request.json())
        # print(client_files_info)
        dir_name = client_files_info['server_dir_name']
        data = client_files_info['data']
        directory = Directory.select().where((Directory.name == dir_name) & (Directory.user_id == params['user_id'])).first()
        if directory != None:
            server_data = [{'path': file.path, 'size': file.size, 'time_modification': time.mktime(datetime.datetime.strptime(str(file.timestamp), "%Y-%m-%d %H:%M:%S").timetuple())}
                           for file in File.select().where(File.directory_id == directory.id)]
            dir_ltm = LastTimeModification.select().where((LastTimeModification.directory_id == directory.id)).first()
            ltm = dir_ltm.timestamp if dir_ltm != None else 0
            ltm = time.mktime(datetime.datetime.strptime(str(ltm), "%Y-%m-%d %H:%M:%S").timetuple()) if isinstance(ltm, datetime.datetime) else 0
            return get_diff(data, server_data) | {'last_time_modification': ltm}

@app.get('/registrate')
async def registrate(request: Request):
    params = dict(request.query_params)
    if User.select().where(User.login == params['login']).first() == None:
        User.create(login=params['login'], password=params['password'])

if __name__ == '__main__':
    with db:
        db.create_tables([User, Directory, File, LastTimeModification])
    uvicorn.run(app, host='0.0.0.0', port=5000, loop='asyncio')