from __future__ import annotations

import csv
import logging
from datetime import datetime
from typing import Any
from urllib.parse import unquote

from aiohttp import ClientSession

from constants import DISCUSSION_URL
from convert import convert_to_slug
from get_comments import get_comments


async def get_threads(
    output_filename: str,
    session: ClientSession,
    threads: list[dict[str, Any]],
    start_date: datetime | None,
    end_date: datetime | None,
    likes: dict[int, int],
    profiles: dict[str, str] | None = None,
) -> bool:
    """
    Получает список тредов и записывает их и комментарии в CSV-файл.

    Аргументы:
        - `output_filename (str)`: Имя файла для записи результатов.
        - `session (aiohttp.ClientSession)`: Сессия aiohttp для выполнения HTTP-запросов.
        - `threads (list[dict[str, Any]])`: Список словарей, представляющих треды на форуме.
        - `start_date (datetime | None)`: Начальная дата для фильтрации по времени создания треда или его последнего
          комментария.
        - `end_date (datetime | None)`: Конечная дата для фильтрации по времени создания треда или его последнего
          комментария.
        - `likes (dict[int, int])`: Словарь, в котором ключ - это идентификатор треда, а значение - число лайков.
        - `profiles (dict[str, str] | None)`: Словарь, в котором ключ - это адрес кошелька, а значение - имя
          пользователя.
            Используется для замены адреса автора треда на его имя пользователя в CSV-файле.

    Возвращает:
        `None`"""
    written = False
    with open(output_filename, "a", encoding="utf-8", newline="") as output_file:
        csv_writer = csv.writer(output_file, quoting=csv.QUOTE_MINIMAL)
        for thread in threads:
            thread_author_name = profiles[thread["Address"]["address"]] if profiles else thread["Address"]["address"]
            thread_title = unquote(thread["title"])
            thread_text = thread.get("plaintext", "")
            if thread_text is not None:
                thread_text = thread_text.replace("\n", " ")
            thread_likes_count = likes.get(thread["id"], 0)
            thread_slug = convert_to_slug(thread["title"])
            thread_url = f"{DISCUSSION_URL}{thread['id']}-{thread_slug}"
            thread_created_date = datetime.strptime(thread["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")

            if thread.get("last_commented_on"):
                last_comment_date = datetime.strptime(thread["last_commented_on"], "%Y-%m-%dT%H:%M:%S.%fZ")
                if (start_date and last_comment_date < start_date) or (end_date and last_comment_date > end_date):
                    continue
                comments = await get_comments(session, thread["id"], start_date, end_date)
                for comment in comments:
                    csv_writer.writerow(
                        [
                            thread_created_date.strftime("%Y-%m-%d %H:%M:%S"),
                            thread_likes_count,
                            thread_author_name,
                            thread_title,
                            thread_text,
                            comment["text"],
                            comment["likes"],
                            comment["address"],
                            datetime.strptime(comment["date"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S"),
                            thread_url,
                        ]
                    )
                logging.info(f"Записан тред [{thread_title}] и {len(comments)} комментариев {thread_url}")
            else:
                if (start_date and thread_created_date < start_date) or (end_date and thread_created_date > end_date):
                    continue
                csv_writer.writerow(
                    [
                        thread_created_date.strftime("%Y-%m-%d %H:%M:%S"),
                        thread_likes_count,
                        thread_author_name,
                        thread_title,
                        thread_text,
                        "",
                        "",
                        "",
                        "",
                        thread_url,
                    ]
                )
                logging.info(f"Записан тред [{thread_title}] {thread_url}")
            written = True
    return written
