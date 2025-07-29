from typing import Optional, List
from pydantic import BaseModel

class State(BaseModel):
    post: str = ""
    topic: str = ""
    position: str = ""
    info: str = ""
    previous_post: str = ""
    feedback: str = "" 
    next: str = ""