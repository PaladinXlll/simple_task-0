import requests
import os
import filetype
import sys
import shutil
from pathlib import Path
import time

link = input('Введите ссылку для запроса: \n')
links = ['https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ8GhNc-8suOjv6I67ImRtvqinZeiAKEeeCNFigg9TerA&s=10', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQwqPr0s777IkvoIEGLWLK3NI0m3beaTGZGQ_HwvAvmuwtoA-sU-NEUGPA&s=10', 'https://www.raycast.com/_next/image?url=https%3A%2F%2Fmisc-assets.raycast.com%2Fwallpapers%2Fglaze_1_preview.png&w=3840&q=70', 'https://images.rawpixel.com/image_800/cHJpdmF0ZS9sci9pbWFnZXMvd2Vic2l0ZS8yMDIzLTAzL3JtNjE5LTEzLWItZWxlbWVudGdyb3VwLXRlLTAwMWEtYi5qcGc.jpg', 'https://i.pinimg.com/736x/7b/6e/dc/7b6edcf9e93cb91586c2af01a3ddbcf1.jpg', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR69D8nXbOuJmw6LevNKFotrwe6J6ZcW_J4nbOwDygdq5qnTE2JyArwoCM&s=10', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSUc_Dx7VhUZNQ2IYhez1sLI81HKAoGhlM7R3NcA-cOn4Ux1tFbJj9FdXM&s=10', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ_ADksRiwUBpKhjHRBUje_Nh0aHX-R0Gog7d5FH2RYOXXzK-ro5QdepnOC&s=10', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRYb7sTpiUp9XuKPlYDEQoQwzrQVQvt5A37L-gz9pRNSBHJprBpFeLxUzPV&s=10', 'https://4kwallpapers.com/images/wallpapers/royal-enfield-7680x4320-27778.jpg']
# link = 'https://cdn.loc.gov/master/pnp/hec/27900/27920a.tif'
# link = links[8]
# link = 'https://data.source.coop/harvard-lil/smithsonian-open-access/media/nzp/NZP-1501-1JC.tif'
COUNT = 10

# Создание и очистка необходимых папок
for folder in ("tmp", "files"):
    folder_path = Path(folder)

    if folder_path.exists():
        shutil.rmtree(folder_path)

    folder_path.mkdir()

def get__file_type():
    try:
        content_type = response.headers['Content-Type']
        file_type = content_type.split("/")[-1]
        wrong_types = ['data', 'octet-stream']
        if file_type in wrong_types: file_type = get__os_file_type()
    except:
        file_type = get__os_file_type()
    return file_type

def get__os_file_type():
    file = filetype.guess('tmp/downloaded_file')
    return file.extension

def first_download():
    try:
        first_request_time = request()
        if response.status_code == 200:
            open(f'tmp/downloaded_file', 'wb').write(downloaded_content)

            global file_type
            file_type = get__file_type()

            return first_request_time

        else:
            print('response status code =', response.status_code)
            return None
    except Exception as error:
        print('unexpected error:', error)
        return None

def request():
    global response, downloaded_content

    time_start = time.perf_counter()
    response = requests.get(
        link,
        headers = {
            "User-Agent": "Mozilla/5.0"
        },
        stream=True # stream для подачи частями
        )
    chunks = [] 
    downloaded = 0 # кол-во полученных байт

    for chunk in response.iter_content(chunk_size=64 * 1024): # перебор частей по 64кб
        if not chunk:
            continue

        chunks.append(chunk)
        downloaded += len(chunk)

        # кол-во секунд с начала загрузки
        elapsed = time.perf_counter() - time_start
        if elapsed > 0:
            average_download_speed = downloaded / elapsed
            average_download_speed_mb = round(average_download_speed / 1_000_000, 3)
            print(
                f'\rСкорость скачивания: {average_download_speed_mb} Mb/s', # /r для печати в той же строке
                end='', # замена дефолтного \n на ''
                flush=True # показ актуального значения
            )

    request_time = time.perf_counter() - time_start
    downloaded_content = b''.join(chunks)
    print()

    return request_time

request_time = 0.0
all_downloaded_bytes = 0
downloaded_content = b''
average_download_speed = 0.0

for i in range(COUNT):

    if i == 0:
        first_request_time = first_download()
        if first_request_time is None:
            sys.exit(1) # завершение с ошибкой

        request_time += first_request_time
        all_downloaded_bytes += len(downloaded_content)
        os.rename("tmp/downloaded_file", f"files/downloaded_file.{file_type}")
        continue

    request_time += request()
    all_downloaded_bytes += len(downloaded_content)
    open(f'files/downloaded_file.{file_type}', 'wb').write(downloaded_content)

average_request_time = round((request_time / COUNT), 3)

print('Общий объём скачанных данных:')
size_b = all_downloaded_bytes
size_kb = round(size_b / 1_000, 2)
print(f'{size_kb} Kb')
print(f'{round(size_b / 1_000_000, 2)} Mb')

print('Среднее время запроса -', average_request_time, 's')
input('Нажмите Enter для выхода..')