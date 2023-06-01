from __future__ import annotations

import logging

import requests

from constants import API_REACTIONS_URL


def get_reactions_count(ids: list[int]) -> dict[int, int]:
    """
    Получает количество реакций (лайков) для заданных идентификаторов тредов
    и комментариев.

    Аргументы:
        - `ids (List[int])`: Список идентификаторов тредов и комментариев.

    Возвращает:
        `Dict[int, int]`: Словарь, в котором ключ - это идентификатор треда
        или комментария, а значение - количество лайков.
    """
    logging.info("Получение информации о лайках...")
    response = requests.post(API_REACTIONS_URL, json={"thread_ids": ids})
    response.raise_for_status()
    result = response.json().get("result", [])
    return {item.get("comment_id") or item.get("thread_id"): item.get("like", 0) for item in result}
