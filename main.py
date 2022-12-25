from bs4 import BeautifulSoup
from pathlib import Path
import requests
import urllib.request
import shutil


def parse(urls):
    r = requests.get(urls)
    r = r.content
    soup = BeautifulSoup(r, 'html.parser')
    return soup

url = 'https://gdz-shok.ru' # 0-вая страница сайта

all_links = parse(url+'/gdz/') 
all_links = all_links.find_all('a') # все ссылки с 0-вой страницы (нужные + мусор)

base ={} # получаем полезный словарь -  {название книги: ссылка на страницы}

for link in all_links:
    text = link.text
    link = url+link.get('href')
    if 'ГДЗ,' in  text: # отсеиваем полезную информацию
        base.update({
        text: link
        })       

for key in base:
    pages = parse(base[key])
    pages = pages.select('.content ul a')
    links = [] # получаем страницы книги 
    split = base[key].split('/')
    file = Path(f'books/{split[4]}/{split[5]}/{key}')
    file.mkdir(exist_ok=True, parents=True)
    for link in pages:
        link = link.get('href').replace('/','')
        links.append(link)
    for i in links:
        img = parse(base[key]+i)
        img = img.select('.ex img')
        for link in img:
            src = url+link.get('src')  # ссылка на картинку
            img = urllib.request.urlopen(src).read()
            target_folder = Path.cwd() / file
            source_folder = Path.cwd() / f'{i}.jpg'
            target_folder_file = target_folder / f'{i}.jpg'
            print(target_folder_file)
            if Path.exists(target_folder_file):
                print(f'пропуск, файл уже на своем месте --- {target_folder_file}')
            else:
                with open(f'{i}.jpg', "wb") as f_obj:
                    f_obj.write(img)
                    f_obj.close
                    print(f'скачан --- {source_folder}')
                shutil.move(source_folder, target_folder)
                print(f'перемещен --- {target_folder_file}')

          
     
    











