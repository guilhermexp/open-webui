import json
import time
import uuid
from typing import Optional

from open_webui.internal.db import Base, get_db
from open_webui.utils.access_control import has_access
from open_webui.models.users import Users, UserResponse


from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Boolean, Column, String, Text, JSON
from sqlalchemy import or_, func, select, and_, text
from sqlalchemy.sql import exists

####################
# Note DB Schema
####################


class Note(Base):
    __tablename__ = "note"

    id = Column(Text, primary_key=True)
    user_id = Column(Text)

    title = Column(Text)
    data = Column(JSON, nullable=True)
    meta = Column(JSON, nullable=True)

    access_control = Column(JSON, nullable=True)
    folder_id = Column(Text, nullable=True)

    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)


class NoteModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str

    title: str
    data: Optional[dict] = None
    meta: Optional[dict] = None

    access_control: Optional[dict] = None
    folder_id: Optional[str] = None

    created_at: int  # timestamp in epoch
    updated_at: int  # timestamp in epoch


####################
# Forms
####################


class NoteForm(BaseModel):
    title: str
    data: Optional[dict] = None
    meta: Optional[dict] = None
    access_control: Optional[dict] = None
    folder_id: Optional[str] = None


class NoteUpdateForm(BaseModel):
    title: Optional[str] = None
    data: Optional[dict] = None
    meta: Optional[dict] = None
    access_control: Optional[dict] = None
    folder_id: Optional[str] = None


class NoteUserResponse(NoteModel):
    user: Optional[UserResponse] = None


class NoteTable:
    def insert_new_note(
        self,
        form_data: NoteForm,
        user_id: str,
    ) -> Optional[NoteModel]:
        with get_db() as db:
            note = NoteModel(
                **{
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    **form_data.model_dump(),
                    "created_at": int(time.time_ns()),
                    "updated_at": int(time.time_ns()),
                }
            )

            new_note = Note(**note.model_dump())

            db.add(new_note)
            db.commit()
            return note

    def get_notes(self) -> list[NoteModel]:
        with get_db() as db:
            notes = db.query(Note).order_by(Note.updated_at.desc()).all()
            return [NoteModel.model_validate(note) for note in notes]

    def get_notes_by_user_id(
        self, user_id: str, permission: str = "write"
    ) -> list[NoteModel]:
        notes = self.get_notes()
        return [
            note
            for note in notes
            if note.user_id == user_id
            or has_access(user_id, permission, note.access_control)
        ]

    def get_note_by_id(self, id: str) -> Optional[NoteModel]:
        with get_db() as db:
            note = db.query(Note).filter(Note.id == id).first()
            return NoteModel.model_validate(note) if note else None

    def update_note_by_id(
        self, id: str, form_data: NoteUpdateForm
    ) -> Optional[NoteModel]:
        with get_db() as db:
            note = db.query(Note).filter(Note.id == id).first()
            if not note:
                return None

            form_data = form_data.model_dump(exclude_unset=True)

            if "title" in form_data:
                note.title = form_data["title"]
            if "data" in form_data:
                note.data = {**note.data, **form_data["data"]}
            if "meta" in form_data:
                note.meta = {**note.meta, **form_data["meta"]}

            if "access_control" in form_data:
                note.access_control = form_data["access_control"]
            
            if "folder_id" in form_data:
                note.folder_id = form_data["folder_id"]

            note.updated_at = int(time.time_ns())

            db.commit()
            return NoteModel.model_validate(note) if note else None

    def delete_note_by_id(self, id: str):
        with get_db() as db:
            db.query(Note).filter(Note.id == id).delete()
            db.commit()
            return True
    
    def get_notes_by_user_id_and_folder_id(
        self, user_id: str, folder_id: Optional[str], permission: str = "write"
    ) -> list[NoteModel]:
        notes = self.get_notes_by_user_id(user_id, permission)
        return [
            note
            for note in notes
            if note.folder_id == folder_id
        ]
    
    def delete_notes_by_user_id_and_folder_id(self, user_id: str, folder_id: str):
        with get_db() as db:
            db.query(Note).filter(
                Note.user_id == user_id,
                Note.folder_id == folder_id
            ).delete()
            db.commit()
            return True
    
    def update_note_folder_id_by_id(
        self, id: str, folder_id: Optional[str]
    ) -> Optional[NoteModel]:
        with get_db() as db:
            note = db.query(Note).filter(Note.id == id).first()
            if not note:
                return None
            
            note.folder_id = folder_id
            note.updated_at = int(time.time_ns())
            
            db.commit()
            return NoteModel.model_validate(note) if note else None


Notes = NoteTable()
