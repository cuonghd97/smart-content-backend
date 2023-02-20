from fastapi import HTTPException
from http import HTTPStatus
from config import constant
from models.smart_content import LoginRequestModel
import jwt
import hashlib


class AccountService:
    def login(self, login_request: LoginRequestModel):
        if login_request.username == "admin" or login_request.username == "user":
            encoded_password = hashlib.sha256(
                login_request.password.encode("utf-8")
            ).hexdigest()
            base_password = (
                "db635b9ff63a5c7efe644b76ce61a75dfdfd30be21a8ea3703336ac416dc7b0b"
            )
            if str(encoded_password) == base_password:
                user = {
                    "id": login_request.username,
                    "username": login_request.username,
                    "firstName": login_request.username,
                    "lastName": "",
                    "role": login_request.username,
                }
                
                encoded_jwt = jwt.encode(user, constant.SECRET_KEY, algorithm="HS256")

                user["accessToken"] = str(encoded_jwt)
                return user
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=f"Wrong username or password",
        )
