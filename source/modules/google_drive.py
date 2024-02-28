import json
from io import BytesIO
from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds
from config import SERVICE_ACC_CREDS_URL
from models import Document


class GoogleDrive:
    credentials: ServiceAccountCreds
    json_creds_path = SERVICE_ACC_CREDS_URL

    def __init__(self):
        service_account_key = json.load(open(self.json_creds_path))
        self.credentials = ServiceAccountCreds(
            scopes=[
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/drive.file"
            ],
            **service_account_key
        )

    async def upload_documents_to_dir(self, main_dir_url: str, dir_name: str, documents: list[Document]) -> None:
        async with Aiogoogle(service_account_creds=self.credentials) as aiog_session:
            index_start_folder_id = main_dir_url.rfind("/") + 1
            folder_id = main_dir_url[index_start_folder_id:]
            drive_v3 = await aiog_session.discover('drive', 'v3')

            # Создаем папку для файлов ---------------------------------------------------------------------------------
            meta_data = {
                'name': dir_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [folder_id]
            }

            request = drive_v3.files.create(fields="id", json=meta_data)
            response = await aiog_session.as_service_account(request)
            dir_id = response['id']

            # Загружаем файлы в папку ----------------------------------------------------------------------------------
            list_requests = []

            for d in documents:
                meta_data = {
                    'name': d.name,
                    'parents': [dir_id]
                }
                request = drive_v3.files.create(pipe_from=BytesIO(d.data), fields="id", json=meta_data)
                list_requests.append(request)

            await aiog_session.as_service_account(*list_requests)
