from fastapi import FastAPI, Request, Depends, UploadFile, APIRouter
from fastapi.responses import FileResponse, StreamingResponse, Response
from main import app
from authorization_system import generate_token, get_user_by_token

site_router = APIRouter()

@site_router.get('/authorization')
async def authorization(request: Request, response: Response):
    current_token = request.cookies.get("usertoken")
    return None