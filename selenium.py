from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options


options = Options()
options.add_argument("headless")

edgeBrowser = webdriver.Edge(
    r"F:\edgedriver_win64\msedgedriver.exe", options=options)
edgeBrowser.get(
    'https://bachngocsach.vip/dich/quang-am-chi-ngoai/382/chuong-1303-muc-doan-hong-nhan-thien-nhai-lo-vien-4/291856.html')

els = elem = WebDriverWait(edgeBrowser, 30).until(
    EC.presence_of_element_located((By.ID, "chapter-id")))  # This is a dummy element

data = els.text

edgeBrowser.close()
print(data)
