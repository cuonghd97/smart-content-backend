from fastapi import HTTPException
from http import HTTPStatus
from config import constant
from database.database import MongoConnection
from models.smart_content import LoginRequestModel
import jwt
import hashlib


class AccountService:
    def __init__(self) -> None:
        self.user = MongoConnection().get_collection("user")

    def login(self, login_request: LoginRequestModel):
        encoded_password = hashlib.sha256(
            login_request.password.encode("utf-8")
        ).hexdigest()
        result = self.user.find_one({
            "username": login_request.username,
            "password": encoded_password,
        })
        if not result:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail=f"Wrong username or password",
            )
        if not result.get("active"):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail=f"User does not active, please contact further support for active an user",
            )
        user = {
            "id": str(result.get("_id")),
            "username": login_request.username,
            "fullname": result.get("fullname"),
            "role": result.get("role"),
        }
        encoded_jwt = jwt.encode(user, constant.SECRET_KEY, algorithm="HS256")

        user["accessToken"] = str(encoded_jwt)
        return user
