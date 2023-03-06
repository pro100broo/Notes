"""
Custom data classes
"""


from pydantic import BaseModel
from datetime import datetime


class Note(BaseModel):
    note_id: int
    creation_date: datetime
    last_change_date: datetime
    title: str
    text: str


class Group(BaseModel):
    name: str
    notes_list: list[Note]


class Groups(BaseModel):
    groups_list: list[Group]
