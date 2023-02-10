import io
import json
import os.path
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
data_app_path = os.path.dirname(os.getcwd()) + os.path.normpath('/data')

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
            file_manipulate(
                os.path.join(data_app_path, params['login'], directory.name) + os.path.normpath(params['local_path']),
                ManipulationType.DELETE)
            return 'Deleted'

@app.post('/upload_file')
async def upload_file(request: Request, file: UploadFile, params: dict = Depends(basic)):
    if params['status']:
        directory = Directory.select().where((Directory.name == params['dir_name']) & (Directory.user_id == params['user_id'])).first()
        if directory is not None:
            existing_file = File.select().where((File.path == params['local_path']) & (File.directory_id == directory.id)).first()
            file_data = b''
            while chunk := await file.read(1024*1024*4):
                file_data += chunk
            if existing_file is None:
                File.create(directory_id=directory.id, name=os.path.basename(file.filename), path=params['local_path'],
                            timestamp=float(params['timestamp']), size=len(file_data)) #ПОФИКСИТЬ ЗАГРУЗКУ БИТОВ
            else:
                File.update(timestamp=float(params['timestamp']), size=len(file_data)).where(
                    (File.path == params['local_path']) & (File.directory_id == directory.id)
                ).execute()
            file_manipulate(os.path.join(data_app_path, params['login'], directory.name) + os.path.normpath(params['local_path']), ManipulationType.UPLOAD, file_data)
            save_file_last_time_modification(directory.id, float(params['dir_timestamp']))
            return 'Uploaded'

@app.post('/upload_zipfile')
async def upload_zipfile(request: Request, file: UploadFile, json_file: UploadFile, params: dict = Depends(basic)):
    if params['status']:
        directory = Directory.select().where((Directory.name == params['dir_name']) & (Directory.user_id == params['user_id'])).first()
        if directory is not None:

            files_info = b''
            while chunk := await json_file.read(1024 * 1024 * 4):
                files_info += chunk
            files_info = json.loads(str(files_info, 'utf-8'))
            print(files_info)

            zipfile_data = b''
            while chunk := await file.read(1024*1024*4):
                zipfile_data += chunk
            zip = zipfile.ZipFile(io.BytesIO(zipfile_data), 'r', zipfile.ZIP_DEFLATED, False)
            for file_info in files_info:
                try:
                    local_path = prepare_zippath(file_info['path'])
                    info = zip.getinfo(local_path)
                    # print(info.filename, file_info['path'], file_info['time_modification'], info.file_size, zip.open(local_path, 'r').read()[:10])

                    existing_file = File.select().where((File.path == file_info['path']) & (File.directory_id == directory.id)).first()
                    if existing_file is None:
                        File.create(directory_id=directory.id, name=os.path.basename(info.filename), path=file_info['path'],
                                    timestamp=float(file_info['time_modification']), size=info.file_size)
                    else:
                        File.update(timestamp=float(file_info['time_modification']), size=info.file_size).where(
                            (File.path == file_info['path']) & (File.directory_id == directory.id)
                        ).execute()
                    file_manipulate(os.path.join(data_app_path, params['login'], directory.name) + os.path.normpath(file_info['path']), ManipulationType.UPLOAD, zip.open(local_path, 'r').read())
                    save_file_last_time_modification(directory.id, float(params['dir_timestamp']))
                except Exception as e:
                    print(file_info)
                    print(prepare_zippath(file_info['path']))
                    print(e)
            return 'Uploaded'

@app.post('/test_stream_upload_file')
async def test_stream_upload_file(request: Request, file: UploadFile, params: dict = Depends(basic)):
    global files_buffer
    # file_data = await file.read()
    # print(file_data)
    # print(file.filename)
    if params['status']:
        content = b''
        while file_data := await file.read(1024*1024*4):
            print(file_data[:25], len(file_data))
            content += file_data
        print(len(content))
        return str(content)[2:-1]
        # body = b''
        # async for chunk in request.stream():
        #     body += chunk
        #     print(f'Chunk: {len(chunk)} {chunk[:25]}')
        # print(body[:50])

        # # print(params['id'])
        # files_buffer[params['id']]['data'][params['part']] = await file.read()
        # files_buffer[params['id']]['data'][params['part']] = params['file']

        # files_buffer[params['id']]['data'][params['part']] = bytes(json.loads(await request.json())['file'], 'utf-8').decode('unicode_escape').encode("raw_unicode_escape")
        # if len(files_buffer[params['id']]['data']) == int(files_buffer[params['id']]['parts']):
        #     data = add_file_bytes(files_buffer[params['id']]['data'])
        #     print(data)
        #     del files_buffer[params['id']]
        #     print('Loaded!')
        #     return str(data)

@app.get('/get_unique_id')
async def get_unique_id(request: Request, params: dict = Depends(basic)):
    global files_buffer
    if params['status']:
        id = get_id()
        while files_buffer.get(id) != None:
            id = get_id()
        files_buffer[id] = {'data': {}, 'parts': params['parts']}
        return id

@app.get('/get_file_info')
async def get_file_info(request: Request, params: dict = Depends(basic)):
    if params['status']:
        directory = Directory.select().where((Directory.name == params['dir_name']) & (Directory.user_id == params['user_id'])).first()
        if directory != None:
            file = File.select().where((File.directory_id == directory.id) & (File.path == params['local_path'])).first()
            if file != None:
                time_modification = time.mktime(datetime.datetime.strptime(str(file.timestamp), "%Y-%m-%d %H:%M:%S").timetuple())
                return {'name': file.name, 'path': file.path, 'time_modification': time_modification, 'size': file.size}

from typing import Generator
def get_data_from_file(file_path: str) -> Generator:
    with open(file=file_path, mode="rb") as file_like:
        yield file_like.read()

@app.get('/get_file')
async def get_file(request: Request, params: dict = Depends(basic)):
    if params['status']:
        directory = Directory.select().where((Directory.name == params['dir_name']) & (Directory.user_id == params['user_id'])).first()
        if directory != None:
            file = File.select().where((File.directory_id == directory.id) & (File.path == params['local_path'])).first()
            if file != None:
                # data = file_manipulate(
                #     os.path.join(data_app_path, params['login'], directory.name) + os.path.normpath(
                #         params['local_path']),
                #     ManipulationType.GET)
                data = get_data_from_file(os.path.join(data_app_path, params['login'], directory.name) + os.path.normpath(params['local_path']))
                return StreamingResponse(content=data, media_type='application/octet-stream')

@app.get('/get_zipfile')
async def get_zipfile(request: Request, params: dict = Depends(basic)):
    if params['status']:
        directory = Directory.select().where((Directory.name == params['dir_name']) & (Directory.user_id == params['user_id'])).first()
        files_info = json.loads(await request.json())
        if directory != None:
            imz = InMemoryZip(os.path.join(data_app_path, params['login'], params['dir_name']))
            imz.append(files_info)
            data = imz.read_generator()
            # return StreamingResponse(content=data, media_type='application/octet-stream')
            return Response(content=data, media_type='application/octet-stream')

@app.get('/get_zipfile_info')
async def get_zipfile_info(request: Request, params: dict = Depends(basic)):
    if params['status']:
        directory = Directory.select().where((Directory.name == params['dir_name']) & (Directory.user_id == params['user_id'])).first()
        files_info = json.loads(await request.json())
        if directory != None:
            res = []
            for file_info in files_info:
                file = File.select().where((File.directory_id == directory.id) & (File.path == file_info['path'])).first()
                if file != None:
                    time_modification = time.mktime(
                        datetime.datetime.strptime(str(file.timestamp), "%Y-%m-%d %H:%M:%S").timetuple())
                    res.append({'name': file.name, 'path': file.path, 'time_modification': time_modification, 'size': file.size})
            return res

@app.get('/get_dir_last_time_modification')
async def get_dir_last_time_modification(request: Request, params: dict = Depends(basic)):
    if params['status']:
        directory = Directory.select().where((Directory.name == params['dir_name']) & (Directory.user_id == params['user_id'])).first()
        if directory is not None:
            dir_ltm = LastTimeModification.select().where((LastTimeModification.directory_id == directory.id)).first()
            ltm = dir_ltm.timestamp if dir_ltm is not None else 0
            return time.mktime(datetime.datetime.strptime(str(ltm), "%Y-%m-%d %H:%M:%S").timetuple()) if isinstance(ltm, datetime.datetime) else 0

@app.get('/get_dirs')
async def get_dirs(request: Request, params: dict = Depends(basic)):
    if params['status']:
        directories = Directory.select().where(Directory.user_id == params['user_id'])
        if directories is not None:
            return [{'name': directory.name} for directory in directories]
        return []

@app.get('/get_dir')
async def get_dir(request: Request, params: dict = Depends(basic)):
    if params['status']:
        directory = Directory.select().where((Directory.name == params['dir_name']) & (Directory.user_id == params['user_id'])).first()
        if directory is not None:
            return [{'name': file.name, 'path': file.path, 'time_modification': file.timestamp, 'size': file.size} for file in File.select().where(File.directory_id == directory.id)]

@app.get('/add_dir')
async def add_dir(request: Request, params: dict = Depends(basic)):
    if params['status']:
        directory = Directory.select().where((Directory.name == params['dir_name']) & (Directory.user_id == params['user_id'])).first()
        if directory is None:
            Directory.create(name=params['dir_name'], user_id=params['user_id'])
            return 'Directory was created'

@app.get('/delete_dir')
async def delete_dir(request: Request, params: dict = Depends(basic)):
    if params['status']:
        directory = Directory.select().where((Directory.name == params['dir_name']) & (Directory.user_id == params['user_id'])).first()
        if directory is not None:
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
        if directory is not None:
            server_data = [{'path': file.path, 'size': file.size, 'time_modification': time.mktime(datetime.datetime.strptime(str(file.timestamp), "%Y-%m-%d %H:%M:%S").timetuple())}
                           for file in File.select().where(File.directory_id == directory.id)]
            dir_ltm = LastTimeModification.select().where((LastTimeModification.directory_id == directory.id)).first()
            ltm = dir_ltm.timestamp if dir_ltm is not None else 0
            ltm = time.mktime(datetime.datetime.strptime(str(ltm), "%Y-%m-%d %H:%M:%S").timetuple()) if isinstance(ltm, datetime.datetime) else 0
            return get_diff(data, server_data) | {'last_time_modification': ltm}

@app.get('/registrate')
async def registrate(request: Request):
    params = dict(request.query_params)
    if User.select().where(User.login == params['login']).first() is None:
        User.create(login=params['login'], password=params['password'])

if __name__ == '__main__':
    with db:
        db.create_tables([User, Directory, File, LastTimeModification])
    uvicorn.run(app, host='0.0.0.0', port=5000, loop='asyncio')