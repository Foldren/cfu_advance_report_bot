from os import environ, getcwd
from dotenv import load_dotenv


load_dotenv()

IS_THIS_LOCAL = "Pycharm" in getcwd()

TOKEN = environ["TOKEN"]

REDIS_URL = environ["REDIS_URL"]

SQL_URL = environ["SQL_URL"]

SERVICE_ACC_CREDS_URL = getcwd() + "/.service-account-credentials.json"

GOOGLE_DIR_URL = environ["GOOGLE_DIR_URL"]

EXCEL_TEMPLATE_PATH = getcwd() + "/.excel_template.xlsx"

IMAGE_EXTENSIONS = [".jpeg", ".png", ".jpg", ".bmp", ".webp", ".heif", ".jfif", ".svg",
                    ".heic", ".jfi", ".jpe", ".jif", ".svgz", ".tiff", ".tif"]

CURRENCIES = ["доллар", "евро", "дирхам", "найра", "лира", "рубль"]

UPLOAD_AR_ONLY_BY_USER_LIST = [int(environ["TELEGRAM_C_ID"])] if IS_THIS_LOCAL else [478808028]

OPTIONAL_AR_ATTACH_USER_LIST = [int(environ["IME_C_ID"])] if IS_THIS_LOCAL else [1533616655]

ROLES = {
    "approver": int(environ["TELEGRAM_C_ID"]),
    "treasurer": int(environ["TELEGRAM_C_ID"]),
    "informers": [int(environ["TELEGRAM_C_ID"])]
} if IS_THIS_LOCAL else {
    "approver": 1533616655,
    "treasurer": 5001671686,
    "informers": [104480643]
}

USERS_NAMES = {
    int(environ["IME_C_ID"]): "Тест 1",
    int(environ["TELEGRAM_C_ID"]): "Тест 2",
} if IS_THIS_LOCAL else {
    5001671686: "Ольга Чуприна",
    478808028: "Ольга Бабина",
    1533616655: "Наталия Чеботарева",
    104480643: "Евгений Чупанов",
}
