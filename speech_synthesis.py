from global_config import *
from global_functions import *
import requests
import sys
import time
from zipfile import ZipFile
import wave

# config speech server
speech_base_url = f'https://{speech_region}.customvoice.api.speech.microsoft.com/api/texttospeech/3.1-preview1/batchsynthesis'

speech_headers = {"Ocp-Apim-Subscription-Key": f"{speech_key}",
                  "Content-Type": "application/json"}


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


# create time sleep animation
def timeSleepAnimation(time_sleep=5):
    '''
    This function create animation for time sleep

    !time_sleep ``int`` : Seconds \n
    '''
    for i in range(1, time_sleep):
        sys.stdout.write(
            f"\r {i * '.'}")
        time.sleep(1)
    print('\n')


# check audio process status on server
def checkAudioProcessStatus(chapter_title='', processID_url='', end_count=10, time_sleep=5):
    '''
    This function request server to check process ID status and return Audio URL if status successed

    !chapter_title ``str``: the title of story \n
    !processID_url ``str``: the process URL of audio on server \n
    !end_count ``int``: the number of attempts. Default 10 attempts \n
    !time_sleep ``int``: the time to sleep. Default 5s
    '''
    # check process ID and return Failed of process url is none
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

            # if request status code == 200 or 201, request success
            if processID_respone.status_code == 200 or processID_respone.status_code == 201:
                logging.info(
                    f'Success request to check "{chapter_title}" process ID')

                # if process recieve status is Success, return audio URL
                if processID_respone.json()['status'] == 'Succeeded':
                    logging.info(f'"{chapter_title}" status is Succeeded')
                    return processID_respone.json()['outputs']['result']

                # if process recieve status is Failed, check network and API, stop code
                elif processID_respone.json()['status'] == 'Failed':
                    logging.error(
                        f' Faild to check "{chapter_title}" status: {processID_respone.status_code}')
                    logging.error(processID_respone.json())
                    return False

                # if status is started or running, sleep 5s and try request again
                logging.warning(
                    f" \"{chapter_title}\" status is: {processID_respone.json()['status']}. Try again ....")
                timeSleepAnimation(time_sleep)
                continue
            else:
                # if process recieve http not 200 or 201, request is error. sleep 5s and try again
                logging.info(
                    f'Faild to request "{chapter_title}" http to server with status code: {processID_respone.status_code}. Try again....')
                timeSleepAnimation(time_sleep)
                continue

        # if have an error when request, sleeep 5s and try again
        except Exception as message:
            logging.warning('Someting went wrong. Try again...')
            logging.warning(message)
            timeSleepAnimation(time_sleep)
            pass

        finally:
            # if try 10 times failed, stop code, return False
            request_count += 1
            if request_count >= end_count:
                logging.error(
                    'Too many attempt faild to request. Check API, network and try again')
                return False


# download with congpress Bar
def handleDownloadProgressBar(audio_response):
    '''
    This function create animation for download file
    !audio_response ``byte``: this respone of requests function
    '''
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
def handleSaveStory(chapter_title='', audio_content=b''):
    '''
    This function save story from audio request content
    !chapter_title ``str``: name of story \n
    !audio_content ``byte``: content from requests module
    '''
    audio_name = chapter_title.removesuffix('.txt')
    audio_path = os.path.join(zipFolders, f'{audio_name}.zip')

    # open zipfile and write file
    with open(audio_path, 'wb') as f:
        f.write(audio_content)
    logging.info(f'Saving "{audio_name}.zip" was success ')
    return True


# download story and recieve zip file
def handleDownloadStory(chapter_title='', audio_url='', time_sleep=5):
    '''
    This function request server to download audio as zip file
    chapter_title ``str``: Name of story
    audio_url ``str``: URL download story
    time_sleep ``int``: time to sleep
    '''

    audio_name = chapter_title.removesuffix('.txt')
    request_count = 0
    while True:
        try:
            # request audio content from server
            logging.info(f'Downloading "{audio_name}" as zip file')
            audio_response = requests.get(
                audio_url, headers=speech_headers, stream=True)

            # check server recieve status and try again if status not 200 or 201
            if not audio_response.status_code == 200 or audio_response.status_code == 201:
                logging.warning(
                    'Fail to connect server to download audio. Retry again...')
                timeSleepAnimation(time_sleep)
                continue

            # download file with congpress bar
            audio_zipContent = handleDownloadProgressBar(audio_response)
            if not audio_zipContent:
                continue

            # save audio as zip file if download success
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
def handleExtractStory(chapter_title=''):
    '''
    This function extract audio from zip file and save to audio folder
    !chapter_title ``str``: Name of story
    '''
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
    '''
    This function download multi audio from input folder

    '''

    # remove all old audio file in folders
    if len(os.listdir(audioFolders)) != 0:
        for item in os.listdir(audioFolders):
            os.remove(os.path.join(audioFolders, item))

    # remove all old zip file in zip folders
    if len(os.listdir(zipFolders)) != 0:
        for item in os.listdir(zipFolders):
            os.remove(os.path.join(zipFolders, item))

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
        if not handleExtract_result:
            logging.error(
                f'An error white extract "{chapter_title}". Stop')
            return False
    return True


# combine audio file
def handleCombine(audio_list=[]):
    '''
    This function combine auido from list 
    !audio_list ``list``: List of audio 
    '''
    try:
        # check list audio is not emtry
        if len(audio_list) == 0:
            logging.error('List audio is emtry. check audio from audioFolers')
            return False

        # set name after combine audio
        first_data = '_'.join(audio_list[0].split('\\')[-1].split(' ')[0:3])
        last_data = '_'.join(audio_list[-1].split('\\')[-1].split(' ')[0:3])
        audio_out = f'{first_data} - {last_data}.wav'

        # handle combine audio
        logging.info(
            f'Stating combine audio whith step over: {len(audio_list)}')
        audio_data = []
        for infile in audio_list:
            w = wave.open(infile, 'rb')
            audio_data.append([w.getparams(), w.readframes(w.getnframes())])
            w.close()

        output = wave.open(os.path.join(outputAudio, audio_out), 'wb')
        output.setparams(audio_data[0][0])
        for i in range(len(audio_data)):
            output.writeframes(audio_data[i][1])
        output.close()
        logging.info(f'Combineing audio "{audio_out}" was success')
    except Exception as message:
        logging.error(f'Combineing audio "{audio_out}" was Fail')
        logging.error(message)


# combine audio and draw img
def combileAduio(combine_count=3):
    '''
    This function combine audio and draw img with combine conts
    !combine_count ``int``: number of combines, default 3
    '''
    if not os.path.exists(outputAudio):
        os.mkdir(outputAudio)

    if len(os.listdir(outputAudio)) != 0:
        for item in os.listdir(outputAudio):
            os.remove(os.path.join(outputAudio, item))

    audio_list = []
    current_count = 1
    for audio_title in sorted_alphanumeric(os.listdir(audioFolders)):
        audio_list.append(os.path.join(audioFolders, audio_title))
        if current_count >= combine_count:
            # combine audio
            handleCombine(audio_list)
            #
            audio_list = []
            current_count = 0
        current_count += 1
    if audio_list:
        handleCombine(audio_list)


if __name__ == '__main__':
    # downloadListStories()
    combileAduio(3)
