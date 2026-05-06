"""Pydantic schemas for API payloads."""

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=120)
    full_name: str = Field(..., min_length=3, max_length=150)
    role: str = Field(default="viewer", min_length=3, max_length=50)


class CategoryCreate(BaseModel):
    slug: str = Field(..., min_length=2, max_length=50)
    title: str = Field(..., min_length=2, max_length=120)


class ServerCreate(BaseModel):
    hostname: str = Field(..., min_length=2, max_length=100)
    ip_address: str = Field(..., min_length=7, max_length=45)
    status: str = Field(default="active", min_length=3, max_length=30)
    category_id: int
    owner_id: int
