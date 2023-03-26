import requests
from requests_html import HTML
from global_functions import *
from global_config import *


menu_list_url = 'https://bachngocsach.com.vn/reader/quang-am-chi-ngoai-convert/muc-luc?page=all'
base_url = 'https://bachngocsach.com.vn'


scawl_headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
}


# handle request
def handleRequests(url):
    try:
        respone = requests.get(url, headers=scawl_headers)
        if respone.status_code == 200 or respone.status_code == 201:
            return {'status_code': 200, 'result': respone.text}
        else:
            raise HttpRequestExceptions(respone.status_code)
    except HttpRequestExceptions as status_code:
        logging.error(
            f'An error while requets with status code: {status_code}')


# get menu list from BNS page
def getBNSmemuLists(chapter_start=1, chapter_counts=0):

    chapter_end = chapter_start + chapter_counts
    menu_lists = HTML(html=handleRequests(menu_list_url)['result']).find(
        '#mucluc-list>ul>li')
    chapter_lists = {}
    if chapter_counts == 0 or chapter_start == 0:
        for index, menu_list in enumerate(menu_lists):
            currentChapter = index + 1
            chapter_name = menu_list.find('.chuong-name', first=True).text
            chapter_link = menu_list.find(
                '.chuong-link', first=True).attrs['href']
            chapter_lists[chapter_name] = chapter_link
    else:
        for index, menu_list in enumerate(menu_lists):
            currentChapter = index + 1
            if currentChapter >= chapter_start and currentChapter < chapter_end:
                chapter_name = menu_list.find('.chuong-name', first=True).text
                chapter_link = menu_list.find(
                    '.chuong-link', first=True).attrs['href']
                chapter_lists[chapter_name] = chapter_link
    logging.info('Get menu lists success')
    if not chapter_lists:
        logging.warning(
            'Cannot file and chapter list. Please check link and try again')
        exit(1)
    return chapter_lists


# crawl chapter data and write file .txt
def handle_crawl_chapter(chapter_start, chapter_lists={}):
    chapter_count = chapter_start
    for chapter_name, chapter_link in chapter_lists.items():
        chapter_name = clearSpecialCharacters(chapter_name)
        chapter_path = os.path.join(
            inputFolders, f'C{chapter_count} {chapter_name}')
        chapter_crawls = HTML(html=handleRequests(
            base_url + chapter_link)['result'])
        logging.info(f'load "chapter {chapter_name}" succes ')

        # save chapter contents to text file
        chapter_content = chapter_crawls.find('#noi-dung', first=True).text
        chapter_data_format = f'{chapter_name}. {format_text(chapter_content)}. '
        with open(f'{chapter_path}.txt', 'w', encoding='utf-8') as file:
            file.write(chapter_data_format)
        logging.info(f'save story "{chapter_name}.txt" to inputFolder')
        chapter_count += 1


# main function crwal data
def crawl_stories(chapter_start=1, chapter_counts=0):
    if len(os.listdir(inputFolders)) != 0:
        logging.info(F'Deleteing all file in inputFolders.....')
        for file in os.listdir(inputFolders):
            os.remove(os.path.join(inputFolders, file))
    logging.info(
        f'Starting request story from "chapter {chapter_start}" to "chapter {chapter_start + chapter_counts-1}"....')
    chapter_lists = getBNSmemuLists(
        chapter_start, chapter_counts)
    handle_crawl_chapter(chapter_start, chapter_lists)


crawl_stories(chapter_start=20, chapter_counts=10)
