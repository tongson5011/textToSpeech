from global_config import *
from global_functions import *
import requests
import sys
import time
from zipfile import ZipFile

speech_base_url = f'https://{speech_region}.customvoice.api.speech.microsoft.com/api/texttospeech/3.1-preview1/batchsynthesis'

speech_headers = {"Ocp-Apim-Subscription-Key": f"{speech_key}",
                  "Content-Type": "application/json"}


def timeSleepAnimation(time_sleep):
    for i in range(1, time_sleep):
        sys.stdout.write(
            f"\r {i * '.'}")
        time.sleep(1)
    print('\n')


# post story to speech server
def postStoryToSpeechServer(chapter_title='', chapter_content='', count_try=5, time_sleep=5):
    '''
    This function post chapter content to speech server and get server process ID if server response success \n

    :chapter_title ``str``: title name of story \n
    :chapter_content ``str``: content of story \n
    :count_try ``int``: maximum number of attempt, default: ``5`` \n 
    :time_sleep ``int``: time sleep, default ``500ms``.
    '''

    # check content data
    if not chapter_content:
        logging.error(
            'Chapter content is not emtry. Plese check chapter content')
        return False
    # ssml config
    voice = 'vi-VN-NamMinhNeural'
    rate = '+5.00%'
    pitch = '-12.00%'

    # payload data
    payload = {
        "displayName": "batch synthesis sample",
        "description": "my ssml test",
        "textType": "SSML",
        "inputs": [
            {
                "text": f'''
                <speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="vi-VN">
                    <voice name="{voice}">
                        <prosody rate="{rate}" pitch="{pitch}">{chapter_content}</prosody>
                    </voice>
                </speak>
                '''
            },
        ],
        "properties": {
            "timeToLive": "PT10M",
            "outputFormat": "riff-24khz-16bit-mono-pcm",
            "wordBoundaryEnabled": False,
            "sentenceBoundaryEnabled": False,
            "concatenateResult": False,
            "decompressOutputFiles": False
        },
    }

    request_count = 0
    while True:
        try:
            # Try post chapter content to speech server
            response = requests.post(
                url=speech_base_url, headers=speech_headers, json=payload)

            # if server respone 200 or 201, return server process ID
            if response.status_code == 201 or response.status_code == 200:
                processID = response.json()['id']
                logging.info(
                    f'Success post "{chapter_title}" to speech server')
                logging.info(f'"{chapter_title}" process ID: {processID}')
                return processID

            # post chapter content to server is failed. Show log, sleep 5s and try again....
            logging.warning(
                f'Fail to post "{chapter_title}" to speech server with status code: {response.status_code}. Try again....')
            logging.warning(f'{response.json()}')
            timeSleepAnimation(time_sleep)

        # an error when post chapter content to server is failed. Show log, sleep 5s and try again....
        except Exception as message:
            logging.warning(
                f'An error while post "{chapter_title}" to speech server. Try again')
            logging.warning(message)
            time.sleep(time_sleep)
            continue

        finally:
            time.sleep(1)
            # count the number of requests
            request_count += 1
            if request_count >= count_try:
                logging.error(
                    f'Too many attempt fail when  post "{chapter_title}" to speech server. Please check API and network and try again')
                return False


# milti post story to server
def multiPostStoriesToServer(chapter_start=0, chapter_count=0):
    chapter_current = 0
    list_procesIDs = {}
    audioProcess_url = {}
    # loop edge chapter in input folders
    for chapter_title in sorted_alphanumeric(os.listdir(inputFolders)):
        logging.info('------------------------------------------------')
        logging.info(f'Loading "{chapter_title}" from inputFolders')

        # default chapter start and count = 0. get all chapter in input folders
        if chapter_start == 0 or chapter_count == 0:
            chapter_path = os.path.join(inputFolders, chapter_title)

        # if chapter start and ount not 0. get range chapter in input folders
        else:
            chapter_current += 1
            chapter_end = chapter_start + chapter_count
            if chapter_current >= chapter_start and chapter_current <= chapter_end:
                chapter_path = os.path.join(inputFolders, chapter_title)

        logging.info(f'Getting "{chapter_title}"')
        # open chapter and read chapter content
        with open(chapter_path, 'r', encoding='utf-8') as f:
            chapter_content = f.read()
        logging.info(f'Loading "{chapter_title}" content')

        # post chapter to speech server
        logging.info(f'Stating post "{chapter_title}" to  speech server')
        process_id = postStoryToSpeechServer(chapter_title, chapter_content)
        if process_id:
            list_procesIDs[chapter_title] = process_id
            logging.info(f'Adding "{chapter_title}" process ID to list')
        else:
            logging.error(
                f'An error white get "{chapter_title}" process ID to list')
            return False
    return list_procesIDs


def timeSleepAnimation(time_sleep):
    for i in range(1, time_sleep):
        sys.stdout.write(
            f"\r {i * '.'}")
        time.sleep(1)
    print('\n')


def checkAudioProcessStatus(chapter_title='', processID_url='', end_count=10, time_sleep=5):
    if not processID_url:
        logging.error(
            'processID_url is empy. Please check post story to server')
        return False

    processID_url = f'{speech_base_url}/{processID_url}'
    request_count = 0

    while True:
        try:
            logging.info(
                f'Stating request "{chapter_title}" to check process status')
            processID_respone = requests.get(
                url=processID_url, headers=speech_headers)
            if processID_respone.status_code == 200 or processID_respone.status_code == 201:
                logging.info(
                    f'Success request to check "{chapter_title}" process ID')
                if processID_respone.json()['status'] == 'Succeeded':
                    logging.info(f'"{chapter_title}" status is Succeeded')
                    return processID_respone.json()['outputs']['result']
                elif processID_respone.json()['status'] == 'Failed':
                    logging.error(
                        f' Faild to check "{chapter_title}" status: {processID_respone.status_code}')
                    logging.error(processID_respone.json())
                    return False
                logging.warning(
                    f" \"{chapter_title}\" status is: {processID_respone.json()['status']}. Try again ....")
                timeSleepAnimation(time_sleep)
                continue
            else:
                logging.info(
                    f'Faild to request "{chapter_title}" http to server with status code: {processID_respone.status_code}. Try again....')
                timeSleepAnimation(time_sleep)
                continue
        except Exception as message:
            logging.warning('Someting went wrong. Try again...')
            logging.warning(message)
            timeSleepAnimation(time_sleep)
            pass
        finally:
            request_count += 1
            if request_count >= end_count:
                logging.error(
                    'Too many attempt faild to request. Check API, network and try again')
                return False


# download with congpress Bar
def handleDownloadProgressBar(audio_response):
    total = int(audio_response.headers.get('content-length', 0))
    initChunk = 0
    audioZipContent = b''
    totalContent = int(total/100)
    for chunk in audio_response.iter_content(totalContent):
        audioZipContent += chunk
        initChunk += len(chunk)
        currentChunk = initChunk / total
        halfChunk = 50 * initChunk / total
        totalBar = (50 - int(halfChunk)) * ' '
        currentBar = int(halfChunk) * '.'
        sys.stdout.write(
            f"\r Downloading file: {int(currentChunk * 100)}% [{currentBar} {totalBar}] {initChunk}/{total}")
    print('\n')
    return audioZipContent

# save auido result to zip folder


def handleSaveStory(chapter_title, audio_content):

    # remove all old zip file in zip folders
    if len(os.listdir(zipFolders)) != 0:
        for item in os.listdir(zipFolders):
            os.remove(os.path.join(zipFolders, item))

    audio_name = chapter_title.removesuffix('.txt')
    audio_path = os.path.join(zipFolders, f'{audio_name}.zip')
    with open(audio_path, 'wb') as f:
        f.write(audio_content)
    logging.info(f'Saving "{audio_name}.zip" was success ')
    return True


# download story was zip file
def handleDownloadStory(chapter_title, audio_url, time_sleep=5):
    audio_name = chapter_title.removesuffix('.txt')
    request_count = 0
    while True:
        try:
            logging.info(f'Downloading "{audio_name}" as zip file')
            audio_response = requests.get(
                audio_url, headers=speech_headers, stream=True)

            if not audio_response.status_code == 200 or audio_response.status_code == 201:
                logging.warning(
                    'Fail to connect server to download audio. Retry again...')
                timeSleepAnimation(time_sleep)
                continue

            audio_zipContent = handleDownloadProgressBar(audio_response)
            save_story_result = handleSaveStory(
                chapter_title, audio_zipContent)

            if not save_story_result:
                logging.error('An error when save story')
                return False
            return True

        except Exception as message:
            logging.warning(message)
            logging.warning(f'Someting went wrong. Retry download audio....')
            timeSleepAnimation(time_sleep)
            continue

        finally:
            request_count += 1
            if request_count >= 10:
                logging.error(
                    'Too many attempt download audio was fail. check your API or network ')
                return False


# extract story from zip folder
def handleExtractStory(chapter_title):

    # remove all old audio file in folders
    if len(os.listdir(audioFolders)) != 0:
        for item in os.listdir(audioFolders):
            os.remove(os.path.join(audioFolders, item))

    try:
        audio_name = chapter_title.removesuffix('.txt')
        logging.info(
            f'Extracting {audio_name} from zipFolders and save to audioFolders')

        audioZip_path = os.path.join(zipFolders, f'{audio_name}.zip')
        audio_path = os.path.join(audioFolders, f'{audio_name}.wav')
        with ZipFile(f'{audioZip_path}', 'r') as archiveFile:
            with archiveFile.open(archiveFile.namelist()[1]) as file:
                audio_content = file.read()

        with open(audio_path, 'wb') as f:
            f.write(audio_content)
        logging.info(f'Saving "{audio_name}.wav" was success')
        return True
    except Exception as message:
        logging.error(message)
        return False


# download story and extract to audio folder
def downloadListStories():
    list_procesIDs = multiPostStoriesToServer()
    if not list_procesIDs:
        logging.error('Handling error. Stop code')
        return False
    # loop edge processID and check process ID status
    for chapter_title, processID in list_procesIDs.items():
        logging.info('------------------------------------------------')
        audio_url = checkAudioProcessStatus(chapter_title, processID)
        if not audio_url:
            logging.error(
                f'An error white add "{chapter_title}" URL to list_processID_url')
            return False
        handleDownloadStory(chapter_title, audio_url)

        # extract zip file and save audio to audioFolders
        handleExtract_result = handleExtractStory(chapter_title)
        if not audio_url:
            logging.error(
                f'An error white extract "{chapter_title}". Stop')
            return False
    return True


downloadListStories()
