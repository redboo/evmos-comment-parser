import logging
from datetime import datetime
from typing import Any

from aiohttp import ClientSession

from constants import API_COMMENTS_URL


async def get_comments(
    session: ClientSession,
    thread_id: str,
    start_date: datetime | None,
    end_date: datetime | None,
) -> list[Any]:
    """
    Получает список комментариев к треду с заданным идентификатором, и фильтрует их по дате.

    Аргументы:
        - `session (aiohttp.ClientSession)`: Сессия aiohttp для выполнения HTTP-запросов.
        - `thread_id (str)`: Идентификатор треда для получения комментариев.
        - `start_date (datetime | None)`: Начальная дата для фильтрации по времени создания комментария.
            Если не указана, то комментарии не фильтруются по дате начала.
        - `end_date (datetime | None)`: Конечная дата для фильтрации по времени создания комментария.
            Если не указана, то комментарии не фильтруются по дате окончания.

    Возвращает:
        Список словарей с информацией о комментариях, отфильтрованных по дате:
        - `text (str)`: Текст комментария, без переносов строк.
        - `date (str)`: Дата и время последнего обновления комментария, в формате `"%Y-%m-%dT%H:%M:%S.%fZ"`.
        - `address (str)`: Адрес кошелька автора комментария.
        - `likes (int)`: Количество лайков у комментария.
    """

    comments_link = f"{API_COMMENTS_URL}{thread_id}"
    logging.info(f"Парсинг комментариев по ссылке {comments_link}")

    comments = []
    async with session.get(comments_link) as response:
        if response.status != 200:
            logging.warning(
                f"❌ ОШИБКА: комментарии по ссылке {comments_link} недоступны, код состояния: {response.status}"
            )
        else:
            comments_data = await response.json()
            for comment in comments_data["result"]:
                comment_date = datetime.strptime(comment["updated_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
                if (not start_date or start_date <= comment_date) and (not end_date or comment_date <= end_date):
                    comments.append(
                        {
                            "text": comment["plaintext"].replace("\n", " "),
                            "date": comment["updated_at"],
                            "address": comment["Address"]["address"],
                            "likes": len(comment["reactions"]),
                        }
                    )

    return comments
