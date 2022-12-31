from fastapi import FastAPI, Request, Depends, UploadFile
import uvicorn
from models import *


async def basic(request: Request):
    result = dict(request.query_params)
    with db:
        user = User.select().where(User.login == result['login'] and User.password == result['password']).first()
        if user != None:
            result['status'] = 'Ok'
        else:
            result['status'] = 'Fail'
    return result

app = FastAPI()

@app.get('/ping')
async def ping_pong(request: Request, params: dict = Depends(basic)):
    print(f'Params: {params}')
    if params['status'] == 'Ok':
        return 'Pong'
    return 'Fail'

@app.get('/delete_file')
async def delete_file(request: Request, params: dict = Depends(basic)):
    pass

@app.post('/upload_file')
async def upload_file(request: Request, file: UploadFile, params: dict = Depends(basic)):
    print(f'Params: {params}')
    print(f'Files: {file.filename}, {file.content_type}, {file.file} -> type: {type(file.file)}')
    return 'Uploaded'

@app.get('/get_file')
async def get_file(request: Request, params: dict = Depends(basic)):
    pass

@app.get('/get_dir_last_time_modification')
async def get_dir_last_time_modification(request: Request, params: dict = Depends(basic)):
    pass

@app.get('/get_dirs')
async def get_dirs(request: Request, params: dict = Depends(basic)):
    pass

@app.get('/get_dir_files_info')
async def get_dir_files_info(request: Request, params: dict = Depends(basic)):
    pass

@app.get('/get_dir_newer_files_info')
async def get_dir_newer_files_info(request: Request, params: dict = Depends(basic)):
    pass

@app.get('/registrate')
async def registrate(request: Request, params: dict = Depends(basic)):
    pass

if __name__ == '__main__':
    with db:
        db.create_tables([User, Directory, File])
    uvicorn.run(app, host='0.0.0.0', port=5000, loop='asyncio')