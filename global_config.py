import os

# config API key
speech_key = '75042b7cd0a542738009d53541cd2686'
speech_region = 'southeastasia'

# config file and path
PATH = os.getcwd()
inputFolders = os.path.join(PATH, 'inputFolders')
temp = os.path.join(PATH, 'temp')
baseIMG = os.path.join(PATH, 'assest/imgs/baseIMG.png')
imgFolders = os.path.join(PATH, 'imgFolders')
zipFolders = os.path.join(PATH, 'temp\zipFolders')
audioFolders = os.path.join(PATH, 'audioFolders')


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
