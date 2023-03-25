import os


# config API key
speech_key = 'f5f5f46a17fd41aa8f1124db1d49892a'
speech_region = 'southeastasia'

# config file and path
PATH = os.getcwd()

inputFolders = os.path.join(PATH, 'inputFolders')
imgFolders = os.path.join(PATH, 'imgFolders')
temp = os.path.join(PATH, 'temp')
baseIMG = os.path.join(PATH, 'assest/imgs/baseIMG.png')
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
