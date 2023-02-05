from datetime import timedelta
import re
from models.smart_content import (
    CreateTemplateRequestModel,
    Message,
    ArticleRequestModel,
)
from config.minio import minio_client
from database.database import MongoConnection
from bson import ObjectId
from fastapi import HTTPException
from http import HTTPStatus
import base64
import requests
import openai
import uuid


class SmartContentService:
    def __init__(self) -> None:
        self.template = MongoConnection().get_collection("template")
        self.keyword_campaign = MongoConnection().get_collection("keyword_campaign")
        self.article = MongoConnection().get_collection("article")
        self.website = MongoConnection().get_collection("website")

    def create_template(self, template_request: CreateTemplateRequestModel):
        template = {
            "displayName": template_request.displayName,
            "prompt": template_request.prompt,
            "description": template_request.descriptions,
            "listFieldValue": re.findall(r"\[(.*?)\]", template_request.prompt),
            "maxTokens": template_request.maxTokens,
            "presencePenalty": template_request.presencePenalty,
            "frequencyPenalty": template_request.frequencyPenalty,
            "temperature": template_request.temperature,
            "topP": template_request.topP,
        }

        try:
            self.template.insert_one(template)
            return {"message": "Create template success"}
        except Exception as e:
            print(e)
            return False

    def generate_presigned_url_image_template(self):
        url = minio_client.presigned_put_object(
            "template-image",
            f"{uuid.uuid4()}.jpg",
            expires=timedelta(hours=1),
        )
        print(url)
        return {"url": url}

    def update_template(self, templateId, template_request: CreateTemplateRequestModel):
        template = {
            "displayName": template_request.displayName,
            "prompt": template_request.prompt,
            "description": template_request.descriptions,
            "listFieldValue": template_request.listFieldValue,
            "maxTokens": template_request.maxTokens,
            "presencePenalty": template_request.presencePenalty,
            "frequencyPenalty": template_request.frequencyPenalty,
            "temperature": template_request.temperature,
            "topP": template_request.topP,
        }

        try:
            self.template.update_one({"_id": ObjectId(templateId)}, {"$set": template})
            return {"message": "Update template success"}
        except Exception as e:
            print(e)
            return False

    def delete_template(self, template_id):
        query = {"_id": ObjectId(template_id)}
        try:
            self.template.delete_one(query)
            return {"message": "Delete template success"}
        except Exception as e:
            print(e)
            return False

    def get_template_detail(self, template_id):
        query = {"_id": ObjectId(template_id)}
        try:
            template = self.template.find_one(query)
            template_response = {
                "id": str(template["_id"]),
                "displayName": template["displayName"],
                "prompt": template["prompt"],
                "description": template["description"],
                "listFieldValue": template["listFieldValue"],
                "maxTokens": template["maxTokens"],
                "presencePenalty": template["presencePenalty"],
                "frequencyPenalty": template["frequencyPenalty"],
                "temperature": template["temperature"],
                "topP": template["topP"],
            }
            return {"data": template_response}
        except Exception as e:
            print(e)
            return False

    def get_list_template(self):
        list_template_model = self.template.find({})

        list_template_response = []
        for template in list_template_model:
            list_template_response.append(
                {
                    "id": str(template["_id"]),
                    "displayName": template["displayName"],
                    "descriptions": template["description"],
                }
            )
        return {"data": list_template_response}

    def create_keyword_campaign(self, keyword_campaign_data: dict):
        try:
            result = self.keyword_campaign.insert_one(keyword_campaign_data)
            return {"id": str(result.inserted_id)}
        except ValueError as err:
            print(err)
            return HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(err))

    def update_keyword_campaign(
        self, keyword_campaign_id: str, keyword_campaign_data: dict
    ):
        result = self.keyword_campaign.update_one(
            {"_id": ObjectId(keyword_campaign_id)}, {"$set": keyword_campaign_data}
        )
        if not result.modified_count:
            return HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=Message.KEYWORD_CAMPAIGN_NOTFOUND,
            )

        return {"message": "Ok"}

    def delete_keyword_campaign(self, keyword_campaign_id: str):
        result = self.keyword_campaign.delete_one(
            {"_id": ObjectId(keyword_campaign_id)}
        )
        if not result.deleted_count:
            return HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=Message.KEYWORD_CAMPAIGN_NOTFOUND,
            )

        return {"message": "Ok"}

    def save_article(self, content, user_id, template_id, prompt, website_id):
        result = self.article.insert_one(
            {
                "templateId": template_id,
                "userId": 1,
                "contentHistory": {
                    "content": content,
                    "prompt": prompt,
                    "websiteId": website_id,
                },
            }
        )
        if not result.inserted_id:
            return HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail=Message.GENERAL_ERROR
            )
        return {"message": "Save article success"}

    def post_article(self, user_id, article_id, website_id):
        website_detail = self.website.find_one(
            {"UserId": 1, "_id": ObjectId(website_id)}
        )
        article_detail = self.article.find_one(
            {"userId": 1, "_id": ObjectId(article_id)}
        )

        list_content_history = list(article_detail["contentHistory"])
        content_history = list_content_history[-1]

        user = website_detail["UserWP"]
        password = website_detail["PasswordWP"]
        credentials = user + ":" + password
        token = base64.b64encode(credentials.encode())
        header = {
            "Authorization": "Basic " + token.decode("utf-8"),
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        }
        post = {
            "status": "publish",
            "title": content_history["prompt"],
            "content": content_history["content"],
            "categories": [
                1
            ],  # The terms assigned to the object in the category taxonomy. Context: [0] -> view, [1] -> edit
        }

        response = requests.post(
            website_detail["WebsitePost"], headers=header, json=post
        )
        print(response.status_code)
        if response.status_code == HTTPStatus.CREATED:
            return {"message": "Success"}
        else:
            return {"message": response.json(), "d": website_detail["WebsitePost"]}

    def generate_article(self, article_data: ArticleRequestModel):
        template = self.template.find_one({"_id": ObjectId(article_data.templateId)})

        prompt = template["prompt"]
        print(article_data.listField)
        for field in article_data.listField:
            prompt = prompt.replace("[]", field)

        print(prompt)

        openai.api_key = "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"
        results = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt + "",
            temperature=0.7,
            max_tokens=3158,
            top_p=0.01,
            frequency_penalty=0.2,
            presence_penalty=0,
        )
        response = dict(results)
        openai_response = response["choices"]

        print(article_data)

        article = self.article.find_one({"_id": ObjectId(article_data.articleId)})

        content_history = article["contentHistory"]
        content_history.append(
            {
                "content": openai_response[-1]["text"].strip(),
                "prompt": prompt,
                "websiteId": "",
            }
        )

        self.article.update_one(
            {"_id": ObjectId(article_data.articleId)},
            {"$set": {"contentHistory": content_history}},
        )

        return {"content": openai_response[-1]["text"].strip()}

    def get_list_article(self, user_id):
        article_data = self.article.find({"userId": user_id})
        result = []
        for record in article_data:
            record["id"] = str(record["_id"])
            del record["_id"]
            result.append(record)
        return {"data": result}

    def get_article(self, user_id, template_id):
        query = {"userId": 1, "templateId": template_id}

        total_article = self.article.count_documents(query)
        if total_article == 0:
            article = {"templateId": template_id, "userId": 1, "contentHistory": []}
            self.article.insert_one(article)

        article_model = self.article.find_one(query)
        template = self.template.find_one({"_id": ObjectId(template_id)})

        article_response = {
            "id": str(article_model["_id"]),
            "templateId": article_model["templateId"],
            "displayName": template["displayName"],
            "listField": template["listFieldValue"],
            "description": template["description"],
            "userId": article_model["userId"],
            "contentHistory": article_model["contentHistory"],
        }

        return article_response
