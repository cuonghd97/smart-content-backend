from typing import Optional

from pydantic import BaseModel


class Message:
    KEYWORD_CAMPAIGN_NOTFOUND = "keyword not found"
    GENERAL_ERROR = "Error"
    TEMPLATE_NOT_FOUND = "Could not found template content"


class KeywordCampaignModel(BaseModel):
    organization: str
    product_type: str
    content_type: Optional[str]


class CreateTemplateRequestModel(BaseModel):
    displayName: Optional[str]
    prompt: Optional[str]
    descriptions: Optional[str]
    listFieldValue: Optional[list]
    maxTokens: Optional[int]
    presencePenalty: Optional[int]
    temperature: Optional[float]
    frequencyPenalty: Optional[int]
    presencePenalty: Optional[int]
    topP: Optional[int]
    filename: Optional[str]


class ArticleRequestModel(BaseModel):
    template: Optional[str]
    content: Optional[str]
    userId: Optional[str]
    templateId: Optional[str]
    prompt: Optional[str]
    style: Optional["str"]
    websiteId: Optional[str]
    articleId: Optional[str]
    templateId: Optional[str]
    listField: Optional[list]


class LoginRequestModel(BaseModel):
    username: str
    password: str
