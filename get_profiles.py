import logging

import requests

from constants import API_PROFILES_URL


def get_profiles(profile_addresses: list[str]) -> dict[str, str]:
    """
    Получает информацию о пользователях по их адресам кошельков.

    Аргументы:
        - `profile_addresses (list[str])`: Список адресов кошельков пользователей.

    Возвращает:
        `dict[str, str]`: Словарь, в котором ключ - это адрес кошелька пользователя, а значение - его имя (если есть).
    """

    logging.info("Получение информации о профилях пользователей...")
    chains = ["osmosis" if address.startswith("osmo10njy") else "evmos" for address in profile_addresses]
    data = {"address[]": list(profile_addresses), "chain[]": chains}
    response = requests.post(API_PROFILES_URL, data=data)
    response.raise_for_status()
    result = response.json().get("result", [])
    logging.info(f"Получено {len(result)} профилей пользователей")
    return {item["address"]: item.get("name", "") for item in result}
