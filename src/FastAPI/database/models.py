from pydantic import BaseModel, Field
from typing import List, Dict, ClassVar
from bson import ObjectId
from enum import Enum
from typing import Optional
from datetime import date


class userModel(BaseModel):
    userName: str = Field(default="")
    email: str = Field(default="")
    password: str = Field(default="")
    all_posts: List[str] = Field(default=[], description="List of post IDs")
    token: str = Field(default="", description="User token")
    user_platforms: List[str] = Field(default=[], description="List of user platforms")
    platform_info: Dict[str, Dict[str, float]] = Field(
        default={}, description="Dictionary of time spent on each platform"
    )


class StatusEnum(str, Enum):
    done = "done"
    inProgress = "in_progress"
    pending = "pending"
    inCreation = "in_creation"
    broken: "broken_url"


class nutritionModel(BaseModel):
    owner_id: Optional[str] = Field(default=None, description="Owner ID")
    url: Optional[str] = Field(default=None, description="URL")
    labels: Dict[str, float] = Field(
        default={
            "Lifestyle & Entertainment": 0.0,
            "News & Politics": 0.0,
            "Travel & Exploration": 0.0,
            "Health & Wellness": 0.0,
            "Technology & Science": 0.0,
            "Food & Cuisine": 0.0,
            "Pet & Animal Content": 0.0,
            "Nature & Photography": 0.0,
            "Sports & Fitness": 0.0,
            "Cultural & Social Issues": 0.0,
        }
    )

    Mood: Dict[str, float] = Field(
        default={
            "Joyful": 0.0,
            "Sad/Depressive": 0.0,
            "Peaceful": 0.0,
            "Energetic/Excited": 0.0,
            "Mysterious/Romantic": 0.0,
            "Nostalgic/Hopeful": 0.0,
            "Frightening/Creepy": 0.0,
            "Inspiring": 0.0,
            "Playful": 0.0,
            "Thoughtful/Contemplative": 0.0,
        }
    )

    Purpose: Dict[str, float] = Field(
        default={
            "Educate": 0.0,
            "Inspire": 0.0,
            "Entertain": 0.0,
            "Promotion": 0.0,
        }
    )

    status: StatusEnum = Field(
        default=StatusEnum.inCreation, description="Status of the post classification"
    )

    time_spent_on_post: Optional[float] = Field(
        default=0, description="Time spent on the post"
    )

    post_creation_time: date = Field(default=None, description="Time spent on the post")
    cosine_similarity_classification: Dict[str, float] = Field(
        default={},
        description="used to store the result form the cosine similarity classification",
    )
