""" PagerMaid initialization. """

from sys import version_info, platform
from yaml import load, FullLoader
from shutil import copyfile
from redis import StrictRedis
from logging import basicConfig, getLogger, INFO, DEBUG
from distutils.util import strtobool
from telethon import TelegramClient

path = __path__[0]
config = None
try:
    config = load(open(r"config.yml"), Loader=FullLoader)
except FileNotFoundError:
    print("Configuration file does not exist, generating new configuration file.")
    copyfile(f"{path}/assets/config.gen.yml", "config.yml")
    exit(1)

if strtobool(config['debug']):
    basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=DEBUG
    )
else:
    basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=INFO
    )

logs = getLogger(__name__)

if platform == "linux" or platform == "linux2" or platform == "darwin" or platform == "freebsd7"\
        or platform == "freebsd8" or platform == "freebsdN" or platform == "openbsd6":
    logs.info(
        "Detected platform as " + platform + ", proceeding to early load process of PagerMaid."
    )
else:
    logs.error(
        "Your platform " + platform + " is not supported, please start PagerMaid on Linux or *BSD."
    )
    exit(1)

log_chatid = int(config['log_chatid'])
log = strtobool(config['log'])

if not log_chatid:
    log_chatid = 0
    log = False

if version_info[0] < 3 or version_info[1] < 6:
    logs.error(
        "Please upgrade your python interpreter to at least version 3.6."
    )
    exit(1)

api_key = config['api_key']
api_hash = config['api_hash']
if api_key is None or api_hash is None:
    logs.info(
        "Please place a valid configuration file in the working directory."
    )
    exit(1)

bot = TelegramClient("pagermaid", api_key, api_hash, auto_reconnect=True)
redis = StrictRedis(host='localhost', port=6379, db=14)


def redis_check():
    try:
        redis.ping()
        return True
    except BaseException:
        return False


command_help = {}
