import json
import logging
from typing import Optional


from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from pydantic import BaseModel

from open_webui.socket.main import sio


from open_webui.models.users import Users, UserResponse
from open_webui.models.note_folders import NoteFolders, NoteFolderModel, NoteFolderForm
from open_webui.models.notes import Notes

from open_webui.config import ENABLE_ADMIN_CHAT_ACCESS, ENABLE_ADMIN_EXPORT
from open_webui.constants import ERROR_MESSAGES
from open_webui.env import SRC_LOG_LEVELS


from open_webui.utils.auth import get_admin_user, get_verified_user
from open_webui.utils.access_control import has_access, has_permission

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

router = APIRouter()

############################
# GetNoteFolders
############################


@router.get("/", response_model=list[NoteFolderModel])
async def get_note_folders(request: Request, user=Depends(get_verified_user)):

    if user.role != "admin" and not has_permission(
        user.id, "features.notes", request.app.state.config.USER_PERMISSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )

    folders = NoteFolders.get_folders_by_user_id(user.id)
    return folders


############################
# CreateNewNoteFolder
############################


@router.post("/", response_model=Optional[NoteFolderModel])
async def create_new_note_folder(
    request: Request, form_data: NoteFolderForm, user=Depends(get_verified_user)
):

    if user.role != "admin" and not has_permission(
        user.id, "features.notes", request.app.state.config.USER_PERMISSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )

    try:
        folder = NoteFolders.insert_new_folder(user.id, form_data)
        return folder
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.DEFAULT()
        )


############################
# GetNoteFolderById
############################


@router.get("/{id}", response_model=Optional[NoteFolderModel])
async def get_note_folder_by_id(request: Request, id: str, user=Depends(get_verified_user)):
    if user.role != "admin" and not has_permission(
        user.id, "features.notes", request.app.state.config.USER_PERMISSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )

    folder = NoteFolders.get_folder_by_id_and_user_id(id, user.id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )

    return folder


############################
# UpdateNoteFolderById
############################


@router.post("/{id}/update", response_model=Optional[NoteFolderModel])
async def update_note_folder_by_id(
    request: Request, id: str, form_data: NoteFolderForm, user=Depends(get_verified_user)
):
    if user.role != "admin" and not has_permission(
        user.id, "features.notes", request.app.state.config.USER_PERMISSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )

    folder = NoteFolders.get_folder_by_id_and_user_id(id, user.id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )

    try:
        folder = NoteFolders.update_folder_by_id_and_user_id(id, user.id, form_data)
        return folder
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.DEFAULT()
        )


############################
# UpdateNoteFolderIsExpandedById
############################


@router.post("/{id}/update/expanded", response_model=Optional[NoteFolderModel])
async def update_note_folder_is_expanded_by_id(
    request: Request, id: str, is_expanded: dict, user=Depends(get_verified_user)
):
    if user.role != "admin" and not has_permission(
        user.id, "features.notes", request.app.state.config.USER_PERMISSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )

    folder = NoteFolders.get_folder_by_id_and_user_id(id, user.id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )

    try:
        folder = NoteFolders.update_folder_is_expanded_by_id_and_user_id(
            id, user.id, is_expanded.get("is_expanded", False)
        )
        return folder
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.DEFAULT()
        )


############################
# UpdateNoteFolderParentIdById
############################


@router.post("/{id}/update/parent", response_model=Optional[NoteFolderModel])
async def update_note_folder_parent_id_by_id(
    request: Request, id: str, parent_id: dict, user=Depends(get_verified_user)
):
    if user.role != "admin" and not has_permission(
        user.id, "features.notes", request.app.state.config.USER_PERMISSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )

    folder = NoteFolders.get_folder_by_id_and_user_id(id, user.id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )

    try:
        folder = NoteFolders.update_folder_parent_id_by_id_and_user_id(
            id, user.id, parent_id.get("parent_id", None)
        )
        return folder
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.DEFAULT()
        )


############################
# DeleteNoteFolderById
############################


@router.delete("/{id}", response_model=bool)
async def delete_note_folder_by_id(request: Request, id: str, user=Depends(get_verified_user)):
    if user.role != "admin" and not has_permission(
        user.id, "features.notes", request.app.state.config.USER_PERMISSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )

    folder = NoteFolders.get_folder_by_id_and_user_id(id, user.id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )

    try:
        result = NoteFolders.delete_folder_by_id_and_user_id(id, user.id)
        return result
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.DEFAULT()
        )