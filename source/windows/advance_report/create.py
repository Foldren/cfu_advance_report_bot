from aiogram import F
from aiogram.enums import ContentType
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Back, Group, Button
from aiogram_dialog.widgets.text import Multi, Const
from components.jinja_templates import jinja_check_report
from components.states import CreateAdvanceReportStates
from events.advance_report.create import on_write_projects_params, on_attach_documents, \
    send_for_approval, on_pass_attach_documents
from modules.text import Text


select_currency = Window(
    Multi(
        Const(Text.title("Авансовый отчет", 1)),
        Const(f"<u>Введите параметры отчета:</u>\n"
              f"<b>Название проекта</b> - наименование проекта\n"
              f"<b>Статья затрат</b> - на что были произведены расходы\n"
              f"<b>Комментарий</b> - ваш комментарий\n"
              f"<b>Сумма</b> - общая сумма затрат\n"
              f"<b>Валюта</b> - валюта затрат<i> (нажмите на валюту чтобы скопировать:"
              f" <code>доллар</code>, <code>евро</code>, <code>лира</code>, "
              f"<code>дирхам</code>, <code>найра</code>, <code>рубль</code>)</i>"),
        Const(f"<i>🗂 Если нужно отправить несколько отчетов, используйте пустую строку как в примере.</i>"),
        Const(f"<i>ℹ️ Каждый параметр вводите с новой строки, как в примере ниже</i>"),
        Const(Text.example("УСН Чечня", "бензин", "комментарий", "35673", "доллар", "",
                           "УСН Чечня2", "воздух", "комментарий", "0", "лира")),
        sep="\n\n"
    ),
    Cancel(text=Const("⛔️ Отмена")),
    MessageInput(func=on_write_projects_params, content_types=[ContentType.TEXT]),
    state=CreateAdvanceReportStates.write_projects_params
)

attach_documents = Window(
    Multi(
        Const(Text.title("Авансовый отчет", 2)),
        Const(f"📥 Отправьте документы для отчета."),
        sep="\n\n"
    ),
    MessageInput(func=on_attach_documents, content_types=[ContentType.DOCUMENT, ContentType.PHOTO]),
    Group(
        Back(text=Const("◀️ Назад")),
        Cancel(text=Const("⛔️ Отмена")),
        Button(text=Const("⏩ Пропустить"), when=F['dialog_data']['is_optional_attach'],
               on_click=on_pass_attach_documents, id="pass_doc_attach"),
        width=2
    ),
    state=CreateAdvanceReportStates.attach_documents
)

check_report = Window(
    Multi(
        Const(Text.title("Авансовый отчет", 3)),
        jinja_check_report
    ),
    Group(
        Back(text=Const("◀️ Назад")),
        Cancel(text=Const("⛔️ Отмена")),
        Button(text=Const("✅ Отправить на согласование"), id="send_for_approval", on_click=send_for_approval,
               when=~F['dialog_data']['is_approver']),
        Button(text=Const("✅ Отправить на оплату"), id="send_for_treasure", on_click=send_for_approval,
               when=F['dialog_data']['is_approver']),
        width=2
    ),
    state=CreateAdvanceReportStates.check_report
)
