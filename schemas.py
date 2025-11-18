"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# ---------------------- Gym App Schemas ----------------------

class GymClass(BaseModel):
    """
    Gym classes offered by the studio
    Collection name: "gymclass"
    """
    title: str = Field(..., description="Class title, e.g., HIIT Blast")
    description: Optional[str] = Field(None, description="What to expect in the class")
    coach: str = Field(..., description="Coach/instructor name")
    duration_minutes: int = Field(..., ge=15, le=180, description="Length of class in minutes")
    capacity: int = Field(..., ge=1, le=100, description="Max attendees")
    tags: List[str] = Field(default_factory=list, description="Tags like strength, cardio, yoga")
    image_url: Optional[str] = Field(None, description="Cover image URL")
    schedule_iso: str = Field(..., description="Start time in ISO format (e.g., 2025-01-01T18:00:00Z)")

class Booking(BaseModel):
    """
    User booking for a gym class
    Collection name: "booking"
    """
    class_id: str = Field(..., description="ID of the GymClass document")
    name: str = Field(..., description="Attendee full name")
    email: EmailStr = Field(..., description="Attendee email")
    phone: Optional[str] = Field(None, description="Contact phone")
    notes: Optional[str] = Field(None, description="Optional notes")

class Plugin(BaseModel):
    """
    Simple plugin registry to enable/disable booking-related add-ons
    Collection name: "plugin"
    """
    key: str = Field(..., description="Unique plugin key, e.g., payments.stripe")
    name: str = Field(..., description="Human readable name")
    enabled: bool = Field(True, description="Whether plugin is enabled")
    config: dict = Field(default_factory=dict, description="Arbitrary plugin configuration")

# Example schemas kept for reference (not used by app but available to viewer)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
