
from bs4 import BeautifulSoup as bs
# from selenium import webdriver
import time
import requests

base_url="https://w13.mangafreak.net/Mangalist/All/9"

max_retries = 2
retry_delay = 10
n = 1
ready = 0
while n < max_retries:
  try:
      response = requests.get(base_url)
      if response.ok:
        ready = 1
        break
  except requests.exceptions.RequestException:
     print("Website not availabe...")
  n += 1
  time.sleep(retry_delay)

if ready != 1:
  print("Problem")
else:
  print("All good")

print(response)
soup=bs(response.content,"html.parser")

print(soup)