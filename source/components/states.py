from aiogram.fsm.state import StatesGroup, State


class MenuStates(StatesGroup):
    main = State()


class CreateAdvanceReportStates(StatesGroup):
    write_projects_params = State()
    attach_documents = State()
    check_report = State()


class AcceptAdvanceReportStates(StatesGroup):
    info_send_for_accept = State()


class FailureAdvanceReportStates(StatesGroup):
    enter_comment = State()
    info_send_for_failure = State()


class UploadAdvanceReportStates(StatesGroup):
    select_report_person = State()
    select_start_date = State()
    select_end_date = State()
    get_xslx_file = State()


