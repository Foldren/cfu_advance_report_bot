from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from components.states import UploadAdvanceReportStates
from config import UPLOAD_AR_ONLY_BY_USER_LIST, USERS_NAMES


async def on_upload_ar(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user_id = callback.from_user.id
    if user_id in UPLOAD_AR_ONLY_BY_USER_LIST:
        await dialog_manager.start(state=UploadAdvanceReportStates.select_start_date,
                                   data={'report_person': USERS_NAMES[user_id]})
    else:
        await dialog_manager.start(state=UploadAdvanceReportStates.select_report_person)
