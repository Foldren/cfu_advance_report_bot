from datetime import datetime, date
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Cancel, Calendar, CalendarConfig, Back, Row
from aiogram_dialog.widgets.text import Multi, Const
from components.keyboards import report_persons
from events.advance_report.upload import on_date_end_selected, on_date_start_selected
from components.states import UploadAdvanceReportStates
from modules.text import Text


select_report_person = Window(
    Multi(
        Const(Text.title("Выгрузка АО", 1)),
        Const(f"👨‍💼 Выберите подотчетное лицо:"),
        sep="\n\n"
    ),
    report_persons,
    Cancel(text=Const("⛔️ Отмена")),
    state=UploadAdvanceReportStates.select_report_person
)

select_start_date = Window(
    Multi(
        Const(Text.title("Выгрузка АО", 2)),
        Const(f"📆 Выберите начальную дату отгрузки:"),
        sep="\n\n"
    ),
    Calendar(id='upload_ar_calendar',
             on_click=on_date_start_selected,
             config=CalendarConfig(
                 min_date=date(year=1991, month=1, day=1),
                 max_date=datetime.now().date()
             )
             ),
    Row(
        Back(text=Const("◀️ Назад")),
        Cancel(text=Const("⛔️ Отмена")),
    ),
    state=UploadAdvanceReportStates.select_start_date
)

select_end_date = Window(
    Multi(
        Const(Text.title("Выгрузка АО", 3)),
        Const(f"📆 Выберите итоговую дату отгрузки:"),
        sep="\n\n"
    ),
    Calendar(id='upload_ar_calendar',
             on_click=on_date_end_selected,
             config=CalendarConfig(
                 min_date=date(year=1991, month=1, day=1),
                 max_date=datetime.now().date()
             )
             ),
    Row(
        Back(text=Const("◀️ Назад")),
        Cancel(text=Const("⛔️ Отмена")),
    ),
    state=UploadAdvanceReportStates.select_end_date
)

get_xslx_file = Window(
    Multi(
        Const("<b>Выгрузка АО</b>"),
        Const(f"✅ Результат сформирован в итоговом файле Microsoft Excel.\n <i>(нажмите, чтобы скачать)</i>"),
        sep="\n\n"
    ),
    state=UploadAdvanceReportStates.get_xslx_file
)
