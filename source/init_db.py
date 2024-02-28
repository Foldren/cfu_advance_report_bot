from tortoise import Tortoise
from config import SQL_URL, IS_THIS_LOCAL


async def init_db():
    # Инициализируем модели
    if IS_THIS_LOCAL:
        await Tortoise.init(
            {
                "connections": {
                    "default": {
                        "engine": "tortoise.backends.sqlite",
                        "credentials": {
                            "file_path": SQL_URL,
                            "foreign_keys": "ON",
                        },
                    }  # Если не локальная авторизуемся по ссылке
                },
                "apps": {"models": {"models": ["models"], "default_connection": "default"}}
            }
        )
    else:
        await Tortoise.init(db_url=SQL_URL, modules={"models": ["models"]})

    # Создаем новые таблицы
    await Tortoise.generate_schemas(safe=True)

