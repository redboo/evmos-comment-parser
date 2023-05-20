import asyncio
import logging
import os
import time
from datetime import datetime

import aiohttp

from arg_parser import parse_args
from constants import API_BULK_URL, DOWNLOAD_DIR
from create_csv_file import create_csv_file
from get_profiles import get_profiles
from get_threads import get_threads
from logging_utils import setup_logging
from reactions_count import get_reactions_count


async def main(profiles: dict | None = None) -> None:
    args = parse_args()
    setup_logging(args.log)

    start_date = datetime.strptime(args.start, "%Y%m%d") if args.start else None
    end_date = datetime.strptime(args.end, "%Y%m%d") if args.end else None

    if start_date and end_date and end_date <= start_date:
        error_message = "Дата окончания должна быть больше даты начала. Программа прервана."
        logging.error(error_message)
        raise ValueError(error_message)

    while True:
        start_time = time.monotonic()
        logging.info("Парсер запущен.")

        written = False

        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

        async with aiohttp.ClientSession() as session:
            async with session.get(API_BULK_URL) as response:
                response.raise_for_status()
                json_data = await response.json()
                threads = json_data["result"]["threads"]
                logging.info(f"Получено {len(threads)} тредов")
                thread_ids = [thread["id"] for thread in threads]
                if profiles:
                    profile_addresses = {thread["Address"]["address"] for thread in threads}
                    profiles = get_profiles(list(profile_addresses))
                likes = get_reactions_count(thread_ids)
                filename = create_csv_file()
                written = await get_threads(filename, session, threads, start_date, end_date, likes, profiles)

        if not args.interval:
            break

        elapsed_time = max(time.monotonic() - start_time, 0)
        await asyncio.sleep(max(args.interval - elapsed_time, 0))

    if written:
        logging.info(f"Программа завершена. Результаты сохранены в {filename}")
    else:
        logging.info("Программа завершена. Результатов не найдено.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.warning("\nПрограмма остановлена пользователем.")
