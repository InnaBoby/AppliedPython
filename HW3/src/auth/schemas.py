import uuid

from fastapi_users import schemas

class UserRead(schemas.BaseUser[uuid.UUID]):
    id: uuid.UUID
    email: str
    name: str


class UserCreate(schemas.BaseUserCreate):
    id: uuid.UUID
    email: str
    name: str
    password: str
