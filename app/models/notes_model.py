from pydantic import BaseModel, field_validator


class YoutubeLink(BaseModel):
    link: str

    @field_validator("link")
    def trim_and_validate(cls, value: str) -> str:
        value = value.strip()
        return value
