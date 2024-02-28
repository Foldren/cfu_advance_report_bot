from aiogram import Router, F
from aiogram.types import Message, BotCommandScopeAllPrivateChats, CallbackQuery
from aiogram_dialog import DialogManager, StartMode, ShowMode
from components.commands import commands
from config import GOOGLE_DIR_URL
from models import AdvanceReport
from modules.google_drive import GoogleDrive
from components.states import MenuStates
from components.states import FailureAdvanceReportStates
from modules.notify import Notify
from modules.tool import Tool

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")


@router.message(F.text == "/start")
async def start(message: Message, dialog_manager: DialogManager):
    await message.bot.set_my_commands(commands=commands, scope=BotCommandScopeAllPrivateChats())
    await dialog_manager.start(state=MenuStates.main,
                               mode=StartMode.RESET_STACK,
                               show_mode=ShowMode.DELETE_AND_SEND)


@router.callback_query(F.data.startswith("failure_ar"))
async def failure_advance_report(callback: CallbackQuery, dialog_manager: DialogManager):
    advance_report_id = await Tool.get_callback_data(callback)
    await dialog_manager.start(state=FailureAdvanceReportStates.enter_comment,
                               show_mode=ShowMode.DELETE_AND_SEND,
                               data={"advance_report_id": advance_report_id})


@router.callback_query(F.data.startswith("accept_ar"))
async def accept_advance_report(callback: CallbackQuery, dialog_manager: DialogManager):
    advance_report_id = await Tool.get_callback_data(callback)
    advance_report = await AdvanceReport.get(id=advance_report_id)
    advance_report.status = 1

    await advance_report.save()

    # Уведомление о положительном решении сендеру ----------------------------------------------------------------------
    await Notify().send_on_accept_ar(callback.message, advance_report_id)

    # Уведомление о запросе на оплату ФМ -------------------------------------------------------------------------------
    try:
        await Notify().send_request_on_pay_ar(callback, advance_report_id)
    except:
        await advance_report.delete()
        await callback.message.answer("⛔️ Казначей не начал чат с ботом.")
        return

    # Отправляем документы в созданную папку в google_drive ------------------------------------------------------------
    documents = await advance_report.documents
    projects = await advance_report.projects

    amount_sum = 0
    for p in projects:
        amount_sum += int(p.amount)

    child_dir_name = (advance_report.datetime.strftime('%d.%m.%Y-%H.%M') + " " +
                      advance_report.accountable_person + " " + str(amount_sum) + "руб.")

    await GoogleDrive().upload_documents_to_dir(
        main_dir_url=GOOGLE_DIR_URL,
        dir_name=child_dir_name,
        documents=documents,
    )

    # Удаляем файлы авансового отчета, теперь они в гугл папке
    await advance_report.documents.all().delete()
    await callback.message.answer(f"✅ Отправитель проинформирован о положительном результате согласования.\n" +
                                  (f"<i>🔗<a href='{GOOGLE_DIR_URL}'>Нажмите сюда, чтобы посмотреть файлы</a></i>"
                                   if documents else ""))
    await callback.message.delete()


@router.callback_query(F.data.startswith("paid_ar"))
async def paid_advance_report(callback: CallbackQuery, dialog_manager: DialogManager):
    advance_report_id = await Tool.get_callback_data(callback)

    await Notify().send_on_paid_ar(callback.message, advance_report_id)
    await callback.message.delete()
