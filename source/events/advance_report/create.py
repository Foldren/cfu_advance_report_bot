from datetime import datetime
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaDocument
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from components.responses import ProjectResponse
from config import CURRENCIES, ROLES, GOOGLE_DIR_URL, IMAGE_EXTENSIONS, OPTIONAL_AR_ATTACH_USER_LIST
from modules.google_drive import GoogleDrive
from modules.notify import Notify
from modules.tool import Tool


async def on_write_projects_params(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    try:
        message_r_list: list[dict] = await Tool.message_to_dataclass(message, ProjectResponse,
                                                                     is_list=True, to_dict=True)
    except TypeError:
        await message.answer("⛔️ Данные введены неверно")
        return

    for message_r in message_r_list:
        if message_r['currency'].lower() not in CURRENCIES:
            await message.answer("⛔️ Валюта задана неверно. Обратите внимание на доступные варианты валют.")
            return
        if not message_r['amount'].isdigit():
            await message.answer("⛔️ Сумма задана неверно, нужно указать число.")
            return

    dialog_manager.dialog_data['projects'] = message_r_list

    dialog_manager.dialog_data['is_optional_attach'] = True if (message.from_user.id in OPTIONAL_AR_ATTACH_USER_LIST) \
        else False
    dialog_manager.dialog_data['is_approver'] = True if message.from_user.id == ROLES['approver'] else False

    await dialog_manager.next()


async def on_attach_documents(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    current_time = datetime.now().strftime('%Y.%m.%d-%H:%M')

    if message.content_type == 'document':
        file_id = message.document.file_id
        file_name = current_time + "." + message.document.file_name.split(".").pop()
    else:
        file_id = message.photo[-1].file_id
        file_name = current_time + ".png"

    # Записываем id, названия файлов в список (число выполнений функций = числу файлов в группе)
    file = {"id": file_id, "name": file_name}

    # Если файлы уже были загружены, обнуляем списки
    if 'is_files_uploaded' in dialog_manager.dialog_data:
        dialog_manager.dialog_data["files"] = []
        dialog_manager.dialog_data["files_names"] = []
        dialog_manager.dialog_data.pop('is_files_uploaded')

    # Создаем если нужно данные для файлов, добавляем загружаемый файл в список
    dialog_manager.dialog_data.setdefault("files", []).append(file)
    dialog_manager.dialog_data.setdefault("files_names", []).append(file_name)

    # Проверяем последнее ли сообщение, если да, то продолжаем диалог
    is_last_media_file = await Tool.check_last_media_file(message)

    if is_last_media_file:
        dialog_manager.dialog_data['is_files_uploaded'] = True
        await dialog_manager.next()


async def on_pass_attach_documents(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['attach_is_passed'] = True
    await dialog_manager.next()


async def send_for_approval(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    projects = []
    dm_projects = dialog_manager.dialog_data['projects']
    files = dialog_manager.dialog_data['files'] if 'attach_is_passed' not in dialog_manager.dialog_data else []
    current_date = datetime.now()
    media_group = None

    for p in dm_projects:
        projects.append(ProjectResponse.from_dict(p))

    # Создаем записи в бд со статусом 0 и текущей датой
    advance_report = await Tool.create_advance_report(callback, current_date, projects, files)

    if dialog_manager.dialog_data['is_approver']:
        advance_report.status = 1
        await advance_report.save()

        # Уведомление о запросе на оплату ФМ ---------------------------------------------------------------------------
        try:
            await Notify().send_request_on_pay_ar(callback, advance_report.id)
        except:
            await advance_report.delete()
            await callback.message.answer("⛔️ Казначей не начал чат с ботом.")
            await dialog_manager.done()
            return

        if 'attach_is_passed' not in dialog_manager.dialog_data:
            # Отправляем документы в созданную папку в google_drive ----------------------------------------------------
            documents = await advance_report.documents
            bd_projects = await advance_report.projects

            amount_sum = 0
            for p in bd_projects:
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

            # Документы для Чупанова -----------------------------------------------------------------------------------
            media_group = []
            for f in files:
                if any(ext in f['name'].lower() for ext in IMAGE_EXTENSIONS):
                    media_group.append(InputMediaPhoto(media=f['id']))
                else:
                    media_group.append(InputMediaDocument(media=f['id']))

        # Отправляем информаторам --------------------------------------------------------------------------------------
        media_group = media_group if 'attach_is_passed' not in dialog_manager.dialog_data else None

        await Notify().send_about_approve_for_informers(callback, projects, advance_report, media_group)
        await dialog_manager.done()

    else:
        # Отправляем уведомление согласующему --------------------------------------------------------------------------
        try:
            await Notify().send_for_approval_ar(callback, projects, advance_report, files)
            await dialog_manager.done()
        except:
            await advance_report.delete()
            await callback.message.answer("⛔️ Согласующий не начал чат с ботом.")
