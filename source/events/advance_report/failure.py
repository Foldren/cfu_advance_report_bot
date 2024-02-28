from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from models import AdvanceReport
from modules.notify import Notify


async def on_failure_enter_comment(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    ar_id = dialog_manager.start_data['advance_report_id']
    advance_report = await AdvanceReport.get(id=ar_id)

    # Отправляем уведомление об отказе ---------------------------------------------------------------------------------
    await Notify().send_on_failure_ar(message, advance_report.id)

    # Удаляем запись о авансовом отчете вместе с документами и проектами
    await advance_report.delete()

    await message.answer("📩 Отправитель проинформирован об отказе.")
    await dialog_manager.done(show_mode=ShowMode.NO_UPDATE)
