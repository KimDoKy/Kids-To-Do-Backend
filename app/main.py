from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from ormar.exceptions import NoMatch
from starlette.middleware.cors import CORSMiddleware

from app.db import database, User, Mission, Board
from app.auth import *

from copy import deepcopy
import datetime

app = FastAPI(title="FastAPI, Docker")

origins = [
    "http://localhost",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

RequestUser = User.get_pydantic(exclude={
    "id":..., "active":..., "missions":..., "boards":...})
ResponseUser = User.get_pydantic(exclude={
    "id":..., "missions":..., "boards":..., "password":...
})
RequestMission = Mission.get_pydantic(exclude={
    "id":..., "owner":...})
ResponseMission = Mission.get_pydantic(exclude={"owner":...})
RequestBoard = Board.get_pydantic(exclude={
    "id":..., "writer":..., "created_at":... ,"updated_at":...})
ResponseBoard = Board.get_pydantic(exclude={"writer":...})

@app.get("/")
async def read_root():
    return await User.objects.all()

@app.on_event("startup")
async def startup():
    if not database.is_connected:
        await database.connect()
    await User.objects.get_or_create(email="test100@test.com", password="test123")

@app.on_event("shutdown")
async def shutdown():
    if database.is_connected:
        await database.disconnect()

@app.post("/login/")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    status_code = 400
    try:
        email = form_data.username
        user = await authenticate_user(email, form_data.password)
        if not user:
            raise
        token = create_token(user.email, user.id, token_type="access")
        refresh_token = create_token(user.email, user.id, token_type="refresh")
        status_code = 200
        content = {
            "access_token": token,
            "refresh_token": refresh_token
            }
    except Exception as e:
        print('e: ', e)
        content = dict(message="no match user")
    return JSONResponse(status_code=status_code, content=content)

@app.post("/refresh-token")
async def refresh_jwt(token: str = Depends(oauth2_bearer)):
    try:
        user = await get_current_user(token, token_type="refresh")
        if not user:
            raise
        token = create_token(user.email, user.id, token_type="access")
        refresh_token = create_token(user.email, user.id, token_type="refresh")
        status_code = 200
        content = {
            "access_token": token,
            "refresh_token": refresh_token
            }
    except Exception as e:
        print('e: ', e)
        content = dict(message="no match user")
        status_code = 400
    return JSONResponse(status_code=status_code, content=content)

@app.post("/register/", response_model=ResponseUser)
async def register(user: RequestUser):
    try:
        input_password = user.dict()["password"]
        hashed_password = get_password_hash(input_password)
        data = deepcopy(user.dict())
        data["password"] = hashed_password
        user = await User(**data).save()
    except Exception as e:
        content = {'message': e.message}
        return JSONResponse(status_code=400, content=content)
    return user

@app.get("/missions/", response_model=list[ResponseMission])
async def get_mission_list(token: str = Depends(oauth2_bearer)):
    try:
        user = await get_current_user(token)
        missions = await Mission.objects.filter(owner=user).all()
        if len(missions) == 0:
            return []
        return missions
    except Exception as e:
        content = {'message': e.detail}
        return JSONResponse(status_code=400, content=content)

@app.post("/missions/", response_model=ResponseMission)
async def create_mission(mission: RequestMission, token: str = Depends(oauth2_bearer)):
    user = await get_current_user(token)
    data = mission.dict()
    data["owner"] = user
    mission = await Mission(**data).save()
    return mission

@app.get("/missions/{mission_id}/", response_model=ResponseMission)
async def get_mission(mission_id: int, token: str = Depends(oauth2_bearer)):
    try:
        user = await get_current_user(token)
        mission = await Mission.objects.filter(owner=user).filter(pk=mission_id).first()
    except NoMatch:
        content = {'message': 'No Match'}
        return JSONResponse(status_code=400, content=content)
    return mission

@app.put("/missions/{mission_id}/", response_model=ResponseMission)
async def update_mission(mission_id: int, mission: RequestMission, token: str = Depends(oauth2_bearer)):
    status_code = 400
    try:
        user = await get_current_user(token)
        target_mission = await Mission.objects.filter(owner=user).filter(pk=mission_id).first()
        return await target_mission.update(**mission.dict())
    except NoMatch as e:
        content = {'message': 'No Match'}
    except HTTPException as e:
        content = {'message': e.detail}
    except Exception as e:
        content = {'message': e.detail}
    return JSONResponse(status_code=status_code, content=content)

@app.delete("/missions/{mission_id}/")
async def delete_mission(mission_id: int, token: str = Depends(oauth2_bearer)):
    status_code = 400
    try:
        user = await get_current_user(token)
        target_mission = await Mission.objects.filter(owner=user).filter(pk=mission_id).first()
        await target_mission.delete()
        status_code = 200
        content = {"deleted_mission": True}
    except NoMatch as e:
        content = {'message': 'No Match'}
    except Exception as e:
        content = {'message': e.detail}
    return JSONResponse(status_code=status_code, content=content)

@app.get("/board/", response_model=list[ResponseBoard])
async def get_board_list():
    boards = await Board.objects.all()
    return boards

@app.post("/board/", response_model=ResponseBoard)
async def create_board(board: RequestBoard, token: str = Depends(oauth2_bearer)):
    user = await get_current_user(token)
    data = board.dict()
    data["writer"] = user
    board = await Board(**data).save()
    return board

@app.get("/board/{board_id}/", response_model=ResponseBoard)
async def get_board_detail(board_id: int, token: str = Depends(oauth2_bearer)):
    try:
        board = await Board.objects.filter(pk=board_id).first()
        return board
    except NoMatch as e:
        content = {'message': 'No Match'}
    except Exception as e:
        content = e.detail
    return JSONResponse(status_code=400, content=content)

@app.put("/board/{board_id}/", response_model=ResponseBoard)
async def update_board(board_id: int, board: RequestBoard, token: str = Depends(oauth2_bearer)):
    board_obj = await Board.objects.get(pk=board_id)
    board_obj.updated_at = datetime.datetime.now()
    return await board_obj.update(**board.dict())

@app.delete("/board/{board_id}/")
async def delete_board(board_id: int, token: str = Depends(oauth2_bearer)):
    status_code = 400
    try:
        user = await get_current_user(token)
        target_board = await Board.objects.filter(writer=user).filter(pk=board_id).first()
        await target_board.delete()
        status_code = 200
        content = {"deleted_mission": True}
    except NoMatch as e:
        content = {'message': 'No Match'}
    except Exception as e:
        content = {'message': e.detail}
    return JSONResponse(status_code=status_code, content=content)
