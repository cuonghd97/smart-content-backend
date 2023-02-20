"""
Xây dựng hệ thống smart content
"""
from http import HTTPStatus
import jwt
import uvicorn
from fastapi import FastAPI, Form, HTTPException, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from config import constant
from controller.account import AccountService
from controller.smart_content import SmartContentService
from models.smart_content import (
    KeywordCampaignModel,
    ArticleRequestModel,
    LoginRequestModel
)
from models.admin_model import RegisClientUserModel, ResetPasswordModel
from controller.admin import AdminService
from fastapi.staticfiles import StaticFiles

app = FastAPI()

smart_content_module = FastAPI()
authentication_module = FastAPI()
admin_module = FastAPI()

smart_content_service = SmartContentService()
account_service = AccountService()
admin_service = AdminService()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/assets", StaticFiles(directory="assets"), name="assets")


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print(e)
        return {"message": "Internal server error", "status": 500}


smart_content_module.middleware("http")(catch_exceptions_middleware)
admin_module.middleware("http")(catch_exceptions_middleware)


@smart_content_module.middleware("http")
async def check_user_header(request: Request, call_next):
    response = Response(status_code=401, content="Unauthorized")
    if request["path"] == "/docs" or request["path"] == "/openapi.json":
        next = await call_next(request)
    else:
        try:
            user = jwt.decode(
                request.headers["Authorization"],
                constant.SECRET_KEY,
                algorithms=["HS256"],
            )
            request.state.user_id = user["id"]
        except:
            print("error")
            return response
        next = await call_next(request)
    return next


@admin_module.middleware("http")
async def check_user_header(request: Request, call_next):
    response = Response(status_code=401, content="Unauthorized")
    if request["path"] == "/docs" or request["path"] == "/openapi.json":
        next = await call_next(request)
    else:
        try:
            user = jwt.decode(
                request.headers["Authorization"],
                constant.SECRET_KEY,
                algorithms=["HS256"],
            )
            request.state.user_id = user["id"]
        except:
            print("error")
            return response
        next = await call_next(request)
    return next


@smart_content_module.post("/template")
def CreateTemplate(
        displayName: str = Form(...),
        prompt: str = Form(...),
        description: str = Form(...),
        maxTokens: int = Form(...),
        presencePenalty: int = Form(...),
        frequencyPenalty: int = Form(...),
        temperature: float = Form(...),
        topP: int = Form(...),
        templateImage: UploadFile = None,
):
    try:
        return smart_content_service.create_template(
            displayName,
            prompt,
            description,
            maxTokens,
            presencePenalty,
            frequencyPenalty,
            temperature,
            topP,
            templateImage,
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e)
        )


@smart_content_module.get("/template/presigned-image-upload")
def GeneratePresignedURLUpload():
    return smart_content_service.generate_presigned_url_image_template()


@smart_content_module.get("/template/{templateId}")
async def GetTemplateDetail(request: Request, templateId: str):
    return smart_content_service.get_template_detail(templateId)


@smart_content_module.put("/template/{templateId}")
def UpdateTemplate(
        request: Request,
        templateId: str,
        displayName: str = Form(...),
        prompt: str = Form(...),
        description: str = Form(...),
        maxTokens: int = Form(...),
        presencePenalty: int = Form(...),
        frequencyPenalty: int = Form(...),
        temperature: float = Form(...),
        topP: int = Form(...),
        templateImage: UploadFile = None,
):
    try:
        return smart_content_service.update_template(
            templateId,
            displayName,
            prompt,
            description,
            maxTokens,
            presencePenalty,
            frequencyPenalty,
            temperature,
            topP,
            templateImage,
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e)
        )


@smart_content_module.get("/article-template/{templateId}")
async def GetArticleByTemplate(request: Request, templateId: str):
    user_id = request.state.user_id

    return smart_content_service.get_article(user_id, template_id=templateId)


@smart_content_module.delete("/template/{template_id}")
def DeleteTemplate(template_id: str):
    print(template_id)
    return smart_content_service.delete_template(template_id)


@smart_content_module.get("/list-template")
def GetListTemplate():
    return smart_content_service.get_list_template()


@smart_content_module.post("/create-keyword-campaign")
async def create_keyword_campaign(keyword_campaign: KeywordCampaignModel):
    keyword_campaign = {
        "organization": keyword_campaign.organization,
        "product_type": keyword_campaign.product_type,
        "content_type": keyword_campaign.content_type,
    }
    return smart_content_service.create_keyword_campaign(
        keyword_campaign_data=keyword_campaign
    )


@smart_content_module.put("/update-keyword-campaign/{keyword_campaign_id}")
async def update_keyword_campaign(
        keyword_campaign_id, keyword_campaign: KeywordCampaignModel
):
    keyword_campaign = {
        "organization": keyword_campaign.organization,
        "product_type": keyword_campaign.product_type,
    }
    return smart_content_service.update_keyword_campaign(
        keyword_campaign_id, keyword_campaign_data=keyword_campaign
    )


@smart_content_module.delete("/delete-keyword-campaign/{keyword_campaign_id}")
async def delete_keyword_campaign(keyword_campaign_id):
    return smart_content_service.delete_keyword_campaign(keyword_campaign_id)


@smart_content_module.post("/save-article")
async def save_article(article_data: ArticleRequestModel):
    return smart_content_service.save_article(
        article_data.content,
        article_data.userId,
        article_data.templateId,
        article_data.prompt,
        article_data.websiteId,
    )


@smart_content_module.get("/list-article/{userId}")
async def get_list_article(userId):
    return smart_content_service.get_list_article(userId)


@smart_content_module.post("/post-article")
async def post_article(request: Request, article_data: ArticleRequestModel):
    user_id = request.state.user_id
    return smart_content_service.post_article(
        user_id, article_data.articleId, article_data.websiteId
    )


@smart_content_module.post("/generate-article")
def generate_article(article_data: ArticleRequestModel):
    return smart_content_service.generate_article(article_data)


@authentication_module.post("/login")
async def login(login_request: LoginRequestModel):
    return account_service.login(login_request)


@admin_module.post('/regis')
async def regis(client_user: RegisClientUserModel):
    return admin_service.regis_client_user(client_user.username, client_user.password, client_user.fullname)


@admin_module.put('/active/{userId}')
async def active_user(userId):
    return admin_service.active_client_user(user_id=userId)


@admin_module.put('/deactivate/{userId}')
async def deactivate_user(userId):
    return admin_service.deactivate_client_user(user_id=userId)


@admin_module.post('/reset/{userId}')
async def reset_password(userId, reset_request: ResetPasswordModel):
    return admin_service.reset_client_user_password(user_id=userId, password=reset_request.password)


app.mount("/smart-content", smart_content_module)
app.mount("/admin", admin_module)
app.mount("/auth", authentication_module)

if __name__ == "__main__":
    uvicorn.run(
        "app:app", host="0.0.0.0", port=8091, reload=True, forwarded_allow_ips="*"
    )
