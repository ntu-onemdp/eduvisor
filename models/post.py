# Models a post object from OneMDP
from pydantic import BaseModel


class Post(BaseModel):
    """Models a simplified post object from OneMDP."""

    title: str
    content: str
    author: str
