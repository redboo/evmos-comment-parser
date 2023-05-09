import csv
from datetime import datetime

from constants import DOWNLOAD_DIR

CSV_HEADER = [
    "thread_date",
    "thread_likes",
    "thread_author",
    "title",
    "text",
    "comment_text",
    "comment_likes",
    "comment_author",
    "comment_date",
    "thread_link",
]


def create_csv_file(download_dir: str = DOWNLOAD_DIR, filename_suffix: str = "evmos") -> str:
    """
    Создает новый CSV-файл в указанном каталоге загрузки с именем, содержащим текущую дату и время, и заданным суффиксом.
    Записывает заголовки столбцов в файл. Возвращает имя созданного файла.

    Аргументы:
        - `download_dir (str, optional)`: Каталог загрузки для сохранения файла. По умолчанию используется глобальная константа `DOWNLOAD_DIR`.
        - `filename_suffix (str, optional)`: Суффикс имени файла. По умолчанию используется значение `"evmos"`.

    Возвращает:
        `str`: Имя созданного файла в формате `"YYYY-MM-DD_HH-MM-SS_suffix.csv"`.
    """
    filename = f"{download_dir}/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{filename_suffix}.csv"
    with open(filename, "a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADER)
    return filename
