from aiogram_dialog.widgets.kbd import Group, Start, Next, Button
from aiogram_dialog.widgets.text import Const
from config import USERS_NAMES
from events.advance_report.upload import on_report_person_selected
from components.states import CreateAdvanceReportStates
from events.menu.change import on_upload_ar


start_menu = Group(
    Start(
        text=Const("Авансовый отчет"),
        id="advance_report",
        state=CreateAdvanceReportStates.write_projects_params
    ),
    Button(
        text=Const("Выгрузка АО"),
        id="upload_advance_report",
        on_click=on_upload_ar,
    ),
    width=2
)

report_persons = Group(
    *[Next(text=Const(user_name), id=str(i),
           on_click=on_report_person_selected) for i, user_name in enumerate(USERS_NAMES.values())],
    width=2,
)
