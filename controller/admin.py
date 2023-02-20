from bson import ObjectId
from http import HTTPStatus
from database.database import MongoConnection
import hashlib
from fastapi import HTTPException


class AdminService:
    def __init__(self) -> None:
        self.user = MongoConnection().get_collection("user")

    def active_client_user(self, user_id):
        try:
            self.user.update_one({"_id": ObjectId(user_id)}, {"$set": {"active": True}})
            return {"message": "Active user success"}
        except Exception as err:
            print("err active user: ", str(err))
            return HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="Active user fail"
            )

    def deactivate_client_user(self, user_id):
        try:
            self.user.update_one({"_id": ObjectId(user_id)}, {"$set": {"active": False}})
            return {"message": "Deactivate user success"}
        except Exception as err:
            print("err deactivate user: ", str(err))
            return HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="Deactivate user fail"
            )

    def regis_client_user(self, username, password, fullname):
        try:
            hashed_password = hashlib.sha256(
                password.encode("utf-8")
            ).hexdigest()
            self.user.insert_one({"username": username, "password": hashed_password,
                                  "fullname": fullname, "token": 0,
                                  "active": False, "role": "user"
                                  })
            return {"message": "Regis user success"}
        except Exception as err:
            print("err regis user: ", str(err))
            return HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Regis user fail"
            )

    def reset_client_user_password(self, user_id, password):
        try:
            hashed_password = hashlib.sha256(
                password.encode('utf-8')
            ).hexdigest()
            self.user.update_one({"_id": ObjectId(user_id)}, {"$set": {"password": hashed_password}})
            return {"message": "Reset password user success"}
        except Exception as err:
            print("err reset password user: ", str(err))
            return HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="Reset password user fail"
            )

    def increase_token(self, user_id, token):
        try:
            self.user.update_one({"_id": ObjectId(user_id)}, {"$inc": {"token": int(token)}})
            return {"message": "Increase token user success"}
        except Exception as err:
            print("err increase token user: ", str(err))
            return HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="Increase token user fail"
            )

    def decrease_token(self, user_id, token):
        try:
            self.user.update_one({"_id": ObjectId(user_id)}, {"$inc": {"token": -int(token)}})
            return {"message": "Decrease user token success"}
        except Exception as err:
            print("err decrease user user: ", str(err))
            return HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="Decrease user token fail"
            )
