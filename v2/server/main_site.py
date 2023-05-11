from fastapi import FastAPI, Request, Depends, UploadFile, APIRouter
from fastapi.responses import FileResponse, StreamingResponse, Response, RedirectResponse
from models import User, Directory, LastTimeModification, File, Tokens, db
from authorization_system import generate_token
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

base_url = 'http://localhost:5000'
site_router = APIRouter()

templates = Jinja2Templates(directory="templates")
site_router.mount("/static", StaticFiles(directory="static"), name="static")

async def get_user_by_token(request: Request, response: Response) -> User:
    current_token = request.cookies.get("usertoken")
    print(f'Current token: {current_token}')
    if current_token is not None:
        token = Tokens.select().where(Tokens.token == current_token).first()
        if token is not None:
            user_id = token.user_id
            return User.select().where(User.id == user_id).first()
        else:
            None
    else:
        return None


@site_router.get('/home')
async def home_get(request: Request, response: Response, cur_user: User = Depends(get_user_by_token)):
    data = {
        "user": cur_user,
        "base_url": base_url
    }
    return templates.TemplateResponse("home.html", {"request": request, 'response': Response, "data": data})


# @site_router.get('/authorization')
# async def authorization_get(request: Request, cur_user: User = Depends(get_user_by_token)):
#     data = {
#         "page": "Home page"
#     }
#     return templates.TemplateResponse("authorization.html", {"request": request, "data": data})


@site_router.post('/authorization')
async def authorization_post(request: Request, response: Response):
    current_token = request.cookies.get("usertoken")
    if current_token is not None:
        Tokens.delete().where(Tokens.token == current_token).execute()
    new_token = generate_token()
    form_data = await request.form()
    login = form_data["login"]
    password = form_data["password"]
    user = User.select().where((User.login == login) & (User.password == password)).first()
    Tokens.create(token=new_token, user_id=user.id)
    # template_response = templates.TemplateResponse("authorization.html", {"request": request})
    template_response = RedirectResponse(url='/home', status_code=302)
    if user is not None:
        template_response.set_cookie(key='usertoken', value=new_token, max_age=60*60*24*30, domain=None, path='/')
    return template_response


@site_router.get('/logout')
async def logout_get(request: Request, response: Response):
    current_token = request.cookies.get("usertoken")
    if current_token is not None:
        Tokens.delete().where(Tokens.token == current_token).execute()
    template_response = RedirectResponse(url='/home', status_code=302)
    template_response.set_cookie(key='usertoken', value="", max_age=60*60*24*30, domain=None, path='/')
    return template_response


@site_router.get('/account')
async def account_get(request: Request, response: Response, cur_user: User = Depends(get_user_by_token)):
    data = {
        "user": cur_user,
        "base_url": base_url
    }
    return templates.TemplateResponse("account.html", {"request": request, 'response': Response, "data": data})


@site_router.get('/download')
async def download_get(request: Request, response: Response, cur_user: User = Depends(get_user_by_token)):
    data = {
        "user": cur_user,
        "base_url": base_url
    }
    return templates.TemplateResponse("download.html", {"request": request, 'response': Response, "data": data})