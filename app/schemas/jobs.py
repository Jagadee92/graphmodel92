from pydantic import BaseModel, Field

class ApplyRequest(BaseModel):
    cover_note: str = Field(default="", max_length=2000)
