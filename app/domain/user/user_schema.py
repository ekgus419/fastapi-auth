from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None  # Admin만 수정 가능

class UserQueryParams(BaseModel):
    page: int = 1
    size: int = 10

class UserListItem(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    role: str
    is_active: bool

class UserListResponse(BaseModel):
    total: int
    page: int
    size: int
    users: List[UserListItem]
