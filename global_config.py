import os

# config API key
speech_key = '8fd8f7efbd9646f2b86f9482af1abf04'
speech_region = 'southeastasia'

# config file and path
PATH = os.getcwd()
inputFolders = os.path.join(PATH, 'inputFolders')
temp = os.path.join(PATH, 'temp')
baseIMG = os.path.join(PATH, 'assest/imgs/baseIMG.png')
imgFolders = os.path.join(PATH, 'imgFolders')
zipFolders = os.path.join(PATH, 'temp\zipFolders')
audioFolders = os.path.join(PATH, 'audioFolders')
outputAudio = os.path.join(PATH, 'outputAudio')

if not os.path.exists(inputFolders):
    os.mkdir(inputFolders)

if not os.path.exists(temp):
    os.mkdir(temp)

if not os.path.exists(zipFolders):
    os.mkdir(zipFolders)

if not os.path.exists(imgFolders):
    os.mkdir(imgFolders)

if not os.path.exists(audioFolders):
    os.mkdir(audioFolders)


