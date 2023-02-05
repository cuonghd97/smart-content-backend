import os

from dotenv import load_dotenv

load_dotenv()


MONGO_STRING_URI = os.environ.get("MONGO_STRING_URI")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME")
MONGO_DB_WEBSITE = os.environ.get("WEBSITE")
MLINK = os.environ.get("MLINK")
WEBSITE = os.environ.get("WEBSITE")
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
KEYWORDS = os.environ.get("KEYWORDS")
PORT = os.environ.get("PORT")
SECRET_KEY = os.environ.get("SECRET_KEY")

MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"

FIELD_REGEX = "\[(.*?)\]"
