from aiogram.enums import ContentType
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.text import Multi, Const
from components.states import FailureAdvanceReportStates
from events.advance_report.failure import on_failure_enter_comment
from modules.text import Text


enter_comment = Window(
    Multi(
        Const(Text.title("Отказ от АО", 1)),
        Const("✒️ Напишите комментарий."),
        sep="\n\n",
    ),
    MessageInput(func=on_failure_enter_comment, content_types=[ContentType.TEXT]),
    state=FailureAdvanceReportStates.enter_comment
)

info_message_failure = Window(
    Const("📩 Отправитель проинформирован об отказе."),
    state=FailureAdvanceReportStates.info_send_for_failure
)
