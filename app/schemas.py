"""Request and response schemas."""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, description="Product name")
    sku: str = Field(min_length=1, max_length=50, description="Unique stock keeping unit")
    quantity: int = Field(ge=0, description="Available quantity")
    price: float = Field(ge=0, description="Price per unit")
    description: str = Field(default="", max_length=500)

    @field_validator("name", "sku")
    @classmethod
    def strip_required_strings(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field must not be blank")
        return value


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    sku: Optional[str] = Field(default=None, min_length=1, max_length=50)
    quantity: Optional[int] = Field(default=None, ge=0)
    price: Optional[float] = Field(default=None, ge=0)
    description: Optional[str] = Field(default=None, max_length=500)

    @field_validator("name", "sku")
    @classmethod
    def strip_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("This field must not be blank")
        return value


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sku: str
    quantity: int
    price: float
    description: str
    created_at: str
    updated_at: str
