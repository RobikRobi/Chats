from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.models.UserModel import User
from src.auth.auth_shema import RegUser, UserShema
from src.db import get_session
from src.auth.auth_utilits import create_access_token, dencode_password, check_password
from src.get_current_user import get_current_user
 
app = APIRouter(prefix="/users", tags=["Users"])


@app.post("/reg")
async def auth_user(data: RegUser, session: AsyncSession = Depends(get_session)):
    stmt = select(User).where(User.username == data.username)
    isUserEx = await session.scalar(stmt)
    
    if isUserEx:
        raise HTTPException(status_code=411, detail={
        "status":411,
        "data":"user is exists"
        })
        
    data_dict = data.model_dump()
        
    data_dict["password"] = await dencode_password(password=data.password)
    
    user = User(**data_dict)
    session.add(user) 
    await session.flush()

    user_id = user.id
        
    await session.commit()
        
    user_token = await create_access_token(user_id=user_id)
    data_dict["token"] = user_token  
        
    return data_dict

@app.post("/login")
async def login_user(username: str, password: str, session: AsyncSession = Depends(get_session)):
    user = await session.scalar(select(User).where(User.username == username))

    if user:
        if await check_password(password=password, old_password=user.password):
            user_token = await create_access_token(user_id=user.id)
            return {"token": user_token}

    raise HTTPException(
        status_code=401,
        detail={
            "details": "user does not exist or password incorrect",
            "status": 401
        }
    )


@app.get("/all_users", response_model=list[UserShema])
async def get_users(session:AsyncSession=Depends(get_session)):
    stmt = select(User)
    users = await session.execute(stmt)
    return users.scalars().all()
    