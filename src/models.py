from typing import Optional, List
from pydantic import BaseModel, Field
from langchain.output_parsers.structured import ResponseSchema

class State(BaseModel):
    post: str = ""
    topic: str = ""
    position: str = ""
    info: str = ""
    previous_post: str = ""
    feedback: str = "" 
    next: str = ""

class TopicResponseSchema(ResponseSchema):
    topic: str = Field(
        ...,
        description=(
            "Subtopic of the post. It must be as specific and technical as possible, "
            "e.g., 'creación de react agents en LangChain con modelos OpenAI'."
        )
    )
    position: str = Field(
        ...,
        description="Position of the post in the series. Must be one of: Initial, Middle, Final, StandAlone."
    )

class ResearchResponseSchema(ResponseSchema):
    info: str = Field(
        ...,
        description=(
            "usefull information gathered through the research, must be structured to be later used for and LLM"
        )
    )

class EditorResponseSchema(BaseModel):
    approved: bool = Field(
        ...,
        description="True if the post is valid and approved; False if it needs revision."
    )
    feedback: str = Field(
        ...,
        description=(
            "Clear, constructive feedback. If 'approved' is False, explain exactly what needs to be improved "
            "or changed in the post. If 'approved' is True, briefly state why the post is acceptable."
        )
    )