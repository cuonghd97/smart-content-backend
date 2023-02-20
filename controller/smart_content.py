import base64
import re
import uuid
from datetime import timedelta
from http import HTTPStatus
import uuid

import openai
import requests
from bson import ObjectId
from fastapi import File, Form, HTTPException, UploadFile

from config.minio import minio_client
from database.database import MongoConnection
from models.smart_content import (
    ArticleRequestModel,
    CreateTemplateRequestModel,
    Message,
)

import random


LIST_OPENAI_API_KEY = [
    "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",
    "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",
    "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",
]


class SmartContentService:
    def __init__(self) -> None:
        self.template = MongoConnection().get_collection("template")
        self.keyword_campaign = MongoConnection().get_collection("keyword_campaign")
        self.article = MongoConnection().get_collection("article")
        self.website = MongoConnection().get_collection("website")

    def create_template(
        self,
        displayName: str,
        prompt: str,
        description: str,
        maxTokens: int,
        presencePenalty: int,
        frequencyPenalty: int,
        temperature: float,
        topP: int,
        templateImage: UploadFile = None,
    ):
        fileName = self.template_image_process(templateImage)

        list_field_value = list(dict.fromkeys(re.findall(r"\[(.*?)\]", prompt)))
        template = {
            "displayName": displayName,
            "prompt": prompt,
            "description": description,
            "listFieldValue": list_field_value,
            "maxTokens": maxTokens,
            "presencePenalty": presencePenalty,
            "frequencyPenalty": frequencyPenalty,
            "temperature": temperature,
            "topP": topP,
            "filename": fileName,
        }

        try:
            self.template.insert_one(template)
            return {"message": "Create template success"}
        except Exception as e:
            print(e)
            return False

    def generate_presigned_url_image_template(self):
        file_id = str(uuid.uuid4())
        url = minio_client.presigned_put_object(
            "template-image",
            f"{file_id}.jpg",
            expires=timedelta(hours=1),
        )
        print(url)

        return {"url": url, "fileId": file_id}

    def update_template(
        self,
        templateId,
        displayName: str,
        prompt: str,
        description: str,
        maxTokens: int,
        presencePenalty: int,
        frequencyPenalty: int,
        temperature: float,
        topP: int,
        templateImage: UploadFile = None,
    ):
        fileName = fileName = self.template_image_process(templateImage)
        list_field_value = list(dict.fromkeys(re.findall(r"\[(.*?)\]", prompt)))

        template = {
            "displayName": displayName,
            "prompt": prompt,
            "description": description,
            "listFieldValue": list_field_value,
            "maxTokens": maxTokens,
            "presencePenalty": presencePenalty,
            "frequencyPenalty": frequencyPenalty,
            "temperature": temperature,
            "topP": topP,
        }
        if fileName != "":
            template["filename"] = fileName

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
            return HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e)
            )

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
            template_response = {
                "id": str(template["_id"]),
                "displayName": template["displayName"],
                "descriptions": template["description"],
                "url": "",
            }

            if "filename" in template and template["filename"] != "":
                template_response["url"] = f"{template['filename']}"
            list_template_response.append(template_response)
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
        print(template)
        list_field_template = template["listFieldValue"]
        for field in article_data.listField:
            prompt = prompt.replace(f"[{field['key']}]", field["value"])

        print(prompt)
        if not article_data.style:
            prompt += f" theo phong cách {article_data.style}"

        openai.api_key = random.choice(LIST_OPENAI_API_KEY)
        results = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt + "",
            temperature=template["temperature"],
            max_tokens=3158,
            top_p=0.01,
            frequency_penalty=0.2,
            presence_penalty=0,
            stream=True,
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
        query = {"userId": user_id, "templateId": template_id}

        total_article = self.article.count_documents(query)
        if total_article == 0:
            article = {
                "templateId": template_id,
                "userId": user_id,
                "contentHistory": [],
            }
            self.article.insert_one(article)

        article_model = self.article.find_one(query)
        template = self.template.find_one({"_id": ObjectId(template_id)})

        article_response = {
            "id": str(article_model["_id"]),
            "templateId": article_model["templateId"],
            "displayName": template["displayName"],
            "listField": template["listFieldValue"],
            "description": template["description"],
            "prompt": template["prompt"],
            "maxTokens": template["maxTokens"],
            "userId": article_model["userId"],
            "contentHistory": article_model["contentHistory"],
            "openaiToken": random.choice(LIST_OPENAI_API_KEY),
        }

        return article_response

    def template_image_process(self, templateImage: UploadFile):
        fileName = ""
        if templateImage and templateImage.filename != "":
            print(templateImage)
            fileName = (
                f"assets/images/template/{str(uuid.uuid4())}_{templateImage.filename}"
            )
            with open(fileName, "wb+") as templateImageObject:
                templateImageObject.write(templateImage.file.read())
            templateImageObject.close()

        return fileName
    