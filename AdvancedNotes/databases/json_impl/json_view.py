"""
Custom data classes
"""


from pydantic import BaseModel
from datetime import datetime


class Note(BaseModel):
    note_id: str
    creation_date: datetime
    last_change_date: datetime
    title: str
    text: str


class Group(BaseModel):
    title: str
    notes_list: list[Note]


class Groups(BaseModel):
    groups_list: list[Group]
