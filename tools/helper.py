from skale import Skale
from skale.utils.web3_utils import init_web3
from skale.wallets import Web3Wallet
import os
import socket

DATA_DIR = 'data'
TARGET = os.environ.get('TARGET')
NODES_FILE = 'nodes.json'
ABI_FILE = 'manager.json'
# NODES_FILE_PATH = os.path.join(DATA_DIR, TARGET, NODES_FILE)
ABI_FILE_PATH = os.path.join(DATA_DIR, TARGET, ABI_FILE)
ETH_PRIVATE_KEY = os.environ['ETH_PRIVATE_KEY']

EXCEPTIONS_FILE = 'exceptions.json'
EXCEPTIONS_FILE_PATH = os.path.join(DATA_DIR, TARGET, EXCEPTIONS_FILE)


ERROR_TEXT = "Initialization of monitor started"
CHECK_PERIOD = 10
LINES_COUNT = 10000000
FORMAT = '%Y-%m-%d %H:%M:%S.%f'


ENDPOINT = os.environ['ENDPOINT']


def init_skale_with_w3_wallet():
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    return Skale(ENDPOINT, ABI_FILE_PATH, wallet)


def ip_from_bytes(bytes):
    return socket.inet_ntoa(bytes)
