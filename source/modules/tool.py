from dataclasses import dataclass, fields, asdict
from datetime import datetime
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import State
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, ShowMode, StartMode
from components.responses import ProjectResponse
from config import USERS_NAMES
from models import AdvanceReport, Project, Document


class Tool:
    @staticmethod
    async def create_advance_report(callback: CallbackQuery, current_date: datetime,
                                    projects: list[ProjectResponse], files: list[dict]) -> AdvanceReport:
        advance_report = await AdvanceReport.create(
            datetime=current_date,
            accountable_person=USERS_NAMES[callback.from_user.id],
            sender_chat_id=callback.from_user.id,
        )

        bd_projects = []
        for p in projects:
            bd_projects.append(Project(
                advance_report=advance_report,
                project_name=p.name,
                comment=p.comment,
                amount=p.amount,
                currency=p.currency.lower(),
                expense=p.expense)
            )

        bd_files = []
        for f in files:
            io_file = await callback.bot.download(file=f['id'])
            bd_files.append(Document(advance_report=advance_report, name=f['name'], data=io_file.read()))

        await Project.bulk_create(bd_projects, ignore_conflicts=True)
        await Document.bulk_create(bd_files, ignore_conflicts=True)

        return advance_report

    @staticmethod
    async def check_last_media_file(message: Message) -> bool:
        last_message_flag = False
        try:
            await message.bot.edit_message_text(
                text="  ",
                chat_id=message.from_user.id,
                message_id=message.message_id + 1
            )
        except TelegramBadRequest as exc:
            if (exc.message == "Bad Request: message must be non-empty" or
                    exc.message == "Bad Request: message to edit not found"):
                last_message_flag = True
        return last_message_flag

    @staticmethod
    async def send_notify(chat_id: int, state: State, dialog_manager: DialogManager, start_data: dict = None):
        user_dm = dialog_manager.bg(user_id=chat_id, chat_id=chat_id)
        await user_dm.start(state=state, show_mode=ShowMode.DELETE_AND_SEND, mode=StartMode.NORMAL, data=start_data)

    @staticmethod
    async def next_and_done(dialog_manager: DialogManager):
        await dialog_manager.next()
        await dialog_manager.show(show_mode=ShowMode.DELETE_AND_SEND)
        await dialog_manager.done()

    @staticmethod
    async def message_to_dataclass(message: Message, dataclass_obj: dataclass,
                                   is_list: bool = False, to_dict: bool = False):
        msg_list_data = message.text.split("\n")

        if is_list:
            dataclass_list_obj = []

            msg_element_list_data = []
            element_number = 1
            for param in msg_list_data:
                if (param == "") or (element_number == len(msg_list_data)):
                    if element_number == len(msg_list_data):
                        msg_element_list_data.append(param)
                    element_d_obj = dataclass_obj(*msg_element_list_data)
                    if to_dict:
                        dataclass_list_obj.append(asdict(element_d_obj))
                    else:
                        dataclass_list_obj.append(element_d_obj)
                    msg_element_list_data = []
                elif param != "":
                    msg_element_list_data.append(param)
                element_number += 1
            return dataclass_list_obj

        else:
            if to_dict:
                result_one_obj = asdict(dataclass_obj(*msg_list_data))
            else:
                result_one_obj = dataclass_obj(*msg_list_data)
            return result_one_obj

    @staticmethod
    async def callback_to_dataclass(callback: CallbackQuery, dataclass_obj: dataclass) -> dataclass:
        list_data = callback.data.split("&")

        # Убираем первый элемент
        list_data.pop(0)
        cls_fields = fields(dataclass_obj)

        # Первый элемент пропускаем
        i = 1
        for field in cls_fields:
            if field.name != "data":
                setattr(dataclass_obj, field.name, list_data[i])
                i += 1

        return dataclass_obj

    @staticmethod
    async def get_callback_data(callback: CallbackQuery):
        return callback.data.split("&")[1]
