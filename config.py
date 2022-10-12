import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TOKEN_KEY")
MY_PROFILE_ID = os.getenv("MY_PROFILE_ID")

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN_KEY")
GITHUB_REPO = os.getenv("GITHUB_REPO")
A_PATH = os.getenv('A_PATH')

FTP_URL = os.getenv('FTP_URL')
FTP_USER = os.getenv('FTP_USER')
FTP_PASS = os.getenv('FTP_PASS')

BE_BANNERS_MAP = os.getenv('BE_BANNERS_MAP')
BE_SERVER_SAVES = os.getenv('BE_SERVER_SAVES')
BE_MAP_UPDATE_HOURS = os.getenv('BE_MAP_UPDATE_HOURS')

BE_VERSIONS_FILE = os.getenv('BE_VERSIONS_FILE')
APPS_DATA_ROOT_URL = os.getenv('APPS_DATA_ROOT_URL')

######
# FB #
######

CERT_PATH = os.getenv('CERT_PATH')
PROJECT_ID = os.getenv('PROJECT_ID')

if not BOT_TOKEN:
    print('You have forgot to set BOT_TOKEN ' + str(BOT_TOKEN) + '?')
    quit()

WEBHOOK_HOST = f'https://catassistantbot.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = 0

if not str(os.getenv('PORT')).__contains__("None"):
    WEBAPP_PORT = os.getenv('PORT', default=8000)

CHATS_ENV = os.getenv("CHATS").split("|")

chats = [int(admin) for admin in CHATS_ENV]

LINKS_BLACK_LIST_ENV = os.getenv("LINKS_BLACK_LIST")

links_black_list = [
    "astler.test",
    "cutt.ly",
    "cutt.us",
    "tinyurl.com",
    "cuti.cc",
    "gee.su",
]

if LINKS_BLACK_LIST_ENV is not None:
    links_black_list.extend(LINKS_BLACK_LIST_ENV.split("|"))


version = "0"

changes = """Изменения

"""
