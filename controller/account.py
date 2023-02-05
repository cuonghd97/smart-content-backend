from fastapi import HTTPException
from http import HTTPStatus
from config import constant
from models.smart_content import LoginRequestModel
import jwt
import hashlib


class AccountService:
    def login(self, login_request: LoginRequestModel):
        encoded_password = hashlib.sha256(
            login_request.password.encode("utf-8")
        ).hexdigest()
        base_password = (
            "c2f24513cb858481e624ed0118f2a3ae7f7152efb941f2a07e8134272c1b9a93"
        )
        print("asd: ", constant.SECRET_KEY)
        if str(encoded_password) == base_password:
            user = {
                "id": 1,
                "username": "admin",
                "firstName": "Admin",
                "lastName": "",
                "role": "admin",
            }
            
            encoded_jwt = jwt.encode(user, constant.SECRET_KEY, algorithm="HS256")

            user["accessToken"] = str(encoded_jwt)
            return user
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=f"Wrong username or password",
        )
