from datetime import datetime as dt
from operator import itemgetter

from aiogoogle import Aiogoogle

from app.core.config import settings

FORMAT = "%Y/%m/%d %H:%M:%S"
ROW_COUNT = 100
COLUMN_COUNT = 11
TABLE_HEADER = [
    ['Отчет от', ''],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание']
]

SPREADSHEET_BODY_TEMPLATE = {
    'properties': {
        'title': '',
        'locale': 'ru_RU',
    },
    'sheets': [
        {
            'properties': {
                'sheetType': 'GRID',
                'sheetId': 0,
                'title': 'Лист1',
                'gridProperties': {
                    'rowCount': ROW_COUNT,
                    'columnCount': COLUMN_COUNT,
                },
            },
        },
    ],
}
SPREADSHEET_SIZE_ERROR_MESSAGE = (
    "Недопустимый размер таблицы "
    f"Число строк должно быть меньше {ROW_COUNT} "
    f"Число столбцов должно быть меньше {COLUMN_COUNT}"
)


async def spreadsheets_create(wrapper_services: Aiogoogle,
                              spreadsheet_body=None
                              ) -> str:
    """Функция создания документа с таблицами."""
    now_date_time = dt.now().strftime(FORMAT)
    spreadsheet_body = SPREADSHEET_BODY_TEMPLATE.copy()
    spreadsheet_body['properties']['title'] = f'Отчет от {now_date_time}'
    service = await wrapper_services.discover('sheets', 'v4')
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response['spreadsheetId']
    spreadsheet_url = response['spreadsheetUrl']
    return spreadsheet_id, spreadsheet_url


async def set_user_permissions(spreadsheet_id: str,
                               wrapper_services: Aiogoogle) -> None:
    """Функция для предоставления прав доступа вашему личному аккаунту
    к созданному документу."""
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.email}
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields="id"))


async def spreadsheets_update_value(
        spreadsheet_id: str,
        projects: list,
        wrapper_services: Aiogoogle
) -> None:
    """Функция для записи данных, полученных из базы, в гугл-таблицу."""
    now_date_time = dt.now().strftime(FORMAT)
    header = TABLE_HEADER.copy()
    header[0][1] = f'{now_date_time}'
    service = await wrapper_services.discover('sheets', 'v4')
    sorted_projects = sorted((({
        'name': project.name,
        'time_collected': project.close_date - project.create_date,
        'description': project.description,
    }) for project in projects), key=itemgetter('time_collected'))
    table_values = header + [
        [project['name'], str(project['time_collected']), project['description']]
        for project in sorted_projects
    ]
    rows = len(table_values)
    columns = max(map(len, table_values))
    if rows > ROW_COUNT or columns > COLUMN_COUNT:
        raise ValueError(SPREADSHEET_SIZE_ERROR_MESSAGE)
    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }

    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'R1C1:R{rows}C{columns}',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
