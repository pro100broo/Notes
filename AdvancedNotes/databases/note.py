from pydantic import BaseModel
from datetime import datetime


class Note(BaseModel):
    note_id: str
    creation_date: datetime
    last_change_date: datetime
    title: str
    text: str