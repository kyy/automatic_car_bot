from bs4 import BeautifulSoup
from pathlib import Path
import requests
import urllib.request
import shutil
import numpy as np


def parse(urls):
    r = requests.get(urls)
    r = r.content
    soup = BeautifulSoup(r, 'html.parser')
    return soup

url = 'https://gdz-shok.ru' # 0-вая страница сайта

def base(): # база книг со сслыками
    all_links = parse(url+'/gdz/')
    all_links = all_links.find_all('a') # все ссылки с 0-вой страницы (нужные + мусор)
    base = {} # получаем полезный словарь -  {название книги: ссылка на страницы}
    for link in all_links:
        text = link.text
        link = url+link.get('href')
        if 'ГДЗ,' in text: # отсеиваем полезную информацию
            base.update({
            text: link
            })
    np.save('my_file.npy', base) # сохраняем все в файл
    links = np.load('my_file.npy', allow_pickle=True).item() # сохраняем все в файл
    return links

def run():
    with open("test.txt", "r") as file:
        done_base = file.read()
        try:
            for key in base():
                if base()[key] not in done_base:
                    pages = parse(base()[key])
                    pages = pages.select('.content ul a')
                    links = []      # получаем страницы книги
                    split = base()[key].split('/')      # разрезаем ссылку для имен папок каталога
                    file = Path(f'd:/books/{split[4]}/{split[5]}/{key}')    # созаем имена для каталога из нарезки ссылки
                    file.mkdir(exist_ok=True, parents=True)     # создаем папки для картинки
                    for link in pages:
                        link = link.get('href').replace('/', '')
                        links.append(link)
                    for i in links:
                        img = parse(base()[key]+i)
                        img = img.select('.ex img')
                        for link in img:
                            src = url+link.get('src')       # ссылка на картинку
                            try:
                                img = urllib.request.urlopen(src).read()
                            except Exception as e:
                                print(f"Файл не существует {src}")
                                continue
                            target_folder = Path.cwd() / file   # каталог для картинок
                            source_folder = Path.cwd() / f'{i}.jpg'     # путь к картинке скачаной
                            target_folder_file = target_folder / f'{i}.jpg'     # путь к картинке финиш
                            if Path.exists(target_folder_file):
                                print(f'OK -- {src}')       # если картинка скачна выводим ее
                            else:
                                try:
                                    with open(f'{i}.jpg', "wb") as f_obj:
                                        f_obj.write(img)     # скачиваем картинку
                                        f_obj.close()
                                        print(f'скачан -- {src}')
                                    shutil.move(source_folder, target_folder)   # перемещаем скачанныую картинку
                                    print(f'перемещен')
                                except Exception:
                                    print(f'ОШИБКА -- {target_folder_file}\n{src}')
                                    continue
                    with open("test.txt", "a") as file:
                        file.write(f"\n{base()[key]}")      # записываем пройденные книги в файл(могут быть пустыми)
                else:
                    print(f'OK -- {base()[key]}')    # если книгу прошли выводим ее
        except:
            run()

if __name__ == "__main__":
    run()
















