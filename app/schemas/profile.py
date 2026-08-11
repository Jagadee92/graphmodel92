from pydantic import BaseModel, Field

class ProfileUpdateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    location: str = Field(min_length=2, max_length=100)
    bio: str = Field(default="", max_length=1000)
    skills: list[str] = Field(default_factory=list)
