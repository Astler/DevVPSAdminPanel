import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("TOKEN_KEY")
MY_PROFILE_ID = os.environ.get("MY_PROFILE_ID")

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN_KEY")
GITHUB_REPO = os.environ.get("GITHUB_REPO")
A_PATH = os.environ.get('A_PATH')

FTP_URL = os.environ.get('FTP_URL')
FTP_USER = os.environ.get('FTP_USER')
FTP_PASS = os.environ.get('FTP_PASS')

BE_BANNERS_MAP = os.environ.get('BE_BANNERS_MAP')
BE_SERVER_SAVES = os.environ.get('BE_SERVER_SAVES')
BE_MAP_UPDATE_HOURS = os.environ.get('BE_MAP_UPDATE_HOURS')
BE_PAGE_SIZE = int(os.environ.get('BE_PAGE_SIZE'))

BE_VERSIONS_FILE = os.environ.get('BE_VERSIONS_FILE')
APPS_DATA_ROOT_URL = os.environ.get('APPS_DATA_ROOT_URL')

######
# FB #
######

CERT_PATH = os.environ.get('CERT_PATH')
PROJECT_ID = os.environ.get('PROJECT_ID')

MC_CERT_PATH = os.environ.get('MC_CERT_PATH')
MC_PROJECT_ID = os.environ.get('MC_PROJECT_ID')

if not BOT_TOKEN:
    print('You have forgot to set BOT_TOKEN ' + str(BOT_TOKEN) + '?')
    quit()

WEBHOOK_HOST = f'https://catassistantbot.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = 0

if not str(os.environ.get('PORT')).__contains__("None"):
    WEBAPP_PORT = os.environ.get('PORT', default=8000)

CHATS_ENV = os.environ.get("CHATS").split("|")

chats = [int(admin) for admin in CHATS_ENV]

LINKS_BLACK_LIST_ENV = os.environ.get("LINKS_BLACK_LIST")

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
