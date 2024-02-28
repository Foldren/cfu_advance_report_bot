from aiogram_dialog import Window
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
from aiogram_dialog.widgets.text import Multi, Const, Format
from components.keyboards import start_menu
from components.states import MenuStates


main = Window(
    Multi(
        Format("👋 Вы в главном меню, <b>{event.from_user.username}</b>"),
        Const(f"<u>Рабочие кнопки персонального бота ЦФУ ⚙️</u>\n"
              f"<b>🔹 Авансовый отчет</b> - сформировать АО с прикреплением файлов "
              f"<i>(с этапом согласования и оплаты)</i>\n"
              f"<b>🔹 Выгрузка АО</b> - выгрузить АО по подотчетном лицу в формате Excel файла за определенный "
              f"интервал."),
        sep="\n\n"
    ),
    start_menu,
    state=MenuStates.main,
    markup_factory=ReplyKeyboardFactory(resize_keyboard=True, input_field_placeholder=Const("Главное меню"))
)
