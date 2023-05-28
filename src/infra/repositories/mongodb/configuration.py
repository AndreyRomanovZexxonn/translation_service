from pydantic import BaseModel, Field


class MongodbConfiguration(BaseModel):
    url: str
    username: str
    password: str
    db: str
    collection: str
