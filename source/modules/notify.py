from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message, InputMediaDocument, \
    InputMediaPhoto
from components.responses import ProjectResponse
from config import IMAGE_EXTENSIONS, ROLES, GOOGLE_DIR_URL
from models import AdvanceReport, Project


class Notify:
    @staticmethod
    async def __send_to_informers(event: CallbackQuery | Message, msg_text: str,
                                  media_group: list[InputMediaPhoto | InputMediaDocument] = None):
        for chat_id in ROLES["informers"]:
            await event.bot.send_message(chat_id=chat_id, text=msg_text)
            if media_group:
                await event.bot.send_media_group(chat_id=chat_id, media=media_group)

    @staticmethod
    async def __get_projects_msg_txt(projects: list[ProjectResponse | Project]):
        msg_text = ""
        for p in projects:
            msg_text += f"\n\n🔹 <u>{p.name if type(p) is not Project else p.project_name}</u>\n" \
                        f"Статья затрат: <b>{p.expense}</b>\n" \
                        f"Комментарий: <b>{p.comment}</b>\n" \
                        f"Сумма: <b>{p.amount}</b>\n" \
                        f"Валюта: <b>{p.currency if type(p) is not Project else p.currency.value}</b>"
        return msg_text

    async def send_about_approve_for_informers(self, callback: CallbackQuery, projects: list[ProjectResponse],
                                               advance_report: AdvanceReport,
                                               media_group: list[InputMediaPhoto | InputMediaDocument] = None):
        current_fstr_date = advance_report.datetime.strftime('%d.%m.%Y-%H.%M')
        msg_text = (f"<b>🟢 Новый запрос на согласование АО от {advance_report.accountable_person}: "
                    f"(От {current_fstr_date})</b>") + await self.__get_projects_msg_txt(projects)

        await self.__send_to_informers(event=callback, msg_text=msg_text, media_group=media_group)
        await callback.message.answer(f"✅ Запрос отправлен финансовому менеджеру.\n" +
                                      (f"<i>🔗<a href='{GOOGLE_DIR_URL}'>Нажмите сюда, чтобы посмотреть файлы</a></i>"
                                       if media_group is not None else ""))

    async def send_for_approval_ar(self, callback: CallbackQuery, projects: list[ProjectResponse],
                                   advance_report: AdvanceReport, files: list[dict]):
        current_fstr_date = advance_report.datetime.strftime('%d.%m.%Y-%H.%M')
        msg_text = (f"<b>🟢 Новый запрос на согласование АО от {advance_report.accountable_person}: "
                    f"(От {current_fstr_date})</b>") + await self.__get_projects_msg_txt(projects)
        reply_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_ar&{advance_report.id}"),
                InlineKeyboardButton(text="⛔️ Отказать", callback_data=f"failure_ar&{advance_report.id}")
            ]
        ])

        await callback.bot.send_message(
            chat_id=ROLES["approver"],
            text=msg_text,
            reply_markup=reply_keyboard
        )

        # Отправляем документы -----------------------------------------------------------------------------------------
        media_group = []
        for f in files:
            if any(ext in f['name'].lower() for ext in IMAGE_EXTENSIONS):
                media_group.append(InputMediaPhoto(media=f['id']))
            else:
                media_group.append(InputMediaDocument(media=f['id']))
        if files:
            await callback.bot.send_media_group(chat_id=ROLES["approver"], media=media_group)

        # Отправляем информаторам
        await self.__send_to_informers(event=callback, msg_text=msg_text, media_group=media_group if files else None)

        await callback.message.answer("✅ Отчеты отправлены на согласование")

    async def send_on_failure_ar(self, message: Message, advance_report_id: int):
        advance_report = await AdvanceReport.get(id=advance_report_id)
        date_ar = advance_report.datetime.strftime('%d.%m.%Y-%H.%M')
        msg_text = (f"🔴 Ваш запрос по АО <i>(От: {date_ar})</i> не прошел этап согласования.\n"
                    f"<i>(Комментарий: {message.text})</i>")
        msg_text_for_informers = (f"🔴 Запрос от {advance_report.accountable_person} по АО "
                                  f"<i>(От: {date_ar})</i> не прошел этап согласования.\n"
                                  f"<i>(Комментарий: {message.text})</i>")

        await message.bot.send_message(chat_id=advance_report.sender_chat_id, text=msg_text)

        # Отправляем информаторам
        await self.__send_to_informers(event=message, msg_text=msg_text_for_informers, media_group=None)

    async def send_on_accept_ar(self, message: Message, advance_report_id: int):
        advance_report = await AdvanceReport.get(id=advance_report_id)
        sender_chat_id = advance_report.sender_chat_id
        date_ar = advance_report.datetime.strftime('%d.%m.%Y-%H.%M')
        msg_text = f"🔵 Ваш запрос по АО <i>(От: {date_ar})</i> прошел этап согласования."
        msg_text_for_informers = (f"🔵 Запрос от {advance_report.accountable_person} по АО "
                                  f"<i>(От: {date_ar})</i> прошел этап согласования.")

        await message.bot.send_message(chat_id=sender_chat_id, text=msg_text)

        # Отправляем информаторам
        await self.__send_to_informers(event=message, msg_text=msg_text_for_informers, media_group=None)

    async def send_request_on_pay_ar(self, callback: CallbackQuery, advance_report_id: int):
        advance_report = await AdvanceReport.get(id=advance_report_id)
        projects = await advance_report.projects
        date_ar = advance_report.datetime.strftime('%d.%m.%Y-%H.%M')
        msg_text = (f"<b>🟢 Новый запрос на оплату АО от {advance_report.accountable_person}: "
                    f"(От {date_ar})</b>") + await self.__get_projects_msg_txt(projects)
        reply_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Оплачено", callback_data=f"paid_ar&{advance_report.id}")]
        ])

        await callback.bot.send_message(
            chat_id=ROLES["treasurer"],
            text=msg_text,
            reply_markup=reply_keyboard
        )

    async def send_on_paid_ar(self, message: Message, advance_report_id: int):
        advance_report = await AdvanceReport.get(id=advance_report_id)
        date_ar = advance_report.datetime.strftime('%d.%m.%Y-%H.%M')
        msg_text = f"🟢 Произведена оплата по запросу АО <i>(От: {date_ar})</i>"
        msg_text_for_informers = (f"🟢 Произведена оплата по запросу АО от {advance_report.accountable_person}"
                                  f" <i>(От: {date_ar})</i>")

        await message.bot.send_message(chat_id=advance_report.sender_chat_id, text=msg_text)
        await message.answer("✅ Отправитель проинформирован об оплате.")

        # Отправляем информаторам
        await self.__send_to_informers(event=message, msg_text=msg_text_for_informers, media_group=None)

