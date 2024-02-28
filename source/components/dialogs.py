from aiogram_dialog import Dialog, LaunchMode
from windows.advance_report.create import select_currency, attach_documents, check_report
from windows.advance_report.failure import enter_comment
from windows.advance_report.upload import select_end_date, select_start_date, select_report_person, get_xslx_file
from windows.menu import main

# menu -----------------------------------------------------------------------------------------------------------------
menu = Dialog(main,
              launch_mode=LaunchMode.ROOT)

# dialogs --------------------------------------------------------------------------------------------------------------
create_advance_report = Dialog(select_currency, attach_documents, check_report,
                               launch_mode=LaunchMode.SINGLE_TOP)

failure_advance_report = Dialog(enter_comment, launch_mode=LaunchMode.SINGLE_TOP)

upload_advance_report = Dialog(select_report_person, select_start_date, select_end_date, get_xslx_file,
                               launch_mode=LaunchMode.SINGLE_TOP)
