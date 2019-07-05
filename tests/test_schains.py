import os
import json
import pytest
from web3 import Web3, HTTPProvider

BASE_DATA_DIR = "data"
TARGET = os.environ.get('TARGET')
DATA_DIR = os.path.join(BASE_DATA_DIR, TARGET)
SCHAINS_DIR = "schains"
SCHAINS_DIR_PATH = os.path.join(DATA_DIR, SCHAINS_DIR)

BLOCKS_FILE = "blocks.json"
BLOCKS_FILE_PATH = os.path.join(DATA_DIR, BLOCKS_FILE)

EXCEPTIONS_FILE = 'exceptions.json'
EXCEPTIONS_FILE_PATH = os.path.join(DATA_DIR, EXCEPTIONS_FILE)


schains = []

with open(EXCEPTIONS_FILE_PATH) as json_file:
    data = json.load(json_file)
bad_ips = data["ips"]
bad_schains = data["schains"]
print(f'bad ips = {bad_ips}')
print(f'bad schains = {bad_schains}')

files = os.listdir(SCHAINS_DIR_PATH)
for file in files:
    with open(os.path.join(SCHAINS_DIR_PATH, file)) as json_file:
        data = json.load(json_file)

    schain_name = data['schain_info']['schain_struct']['name']
    if schain_name not in bad_schains:
        for snode in data['schain_info']['schain_nodes']:
            if snode['ip'] not in bad_ips:
                schains.append({'name': schain_name, 'ip': snode['ip'], 'httpRpcPort': snode['httpRpcPort']})

print(f's-chains for test(len = {len(schains)}): {schains}')


@pytest.mark.parametrize("schain", schains)
def test_schains(schain):
    name = schain['name']
    ip = schain['ip']
    addr = "http://" + ip + ":" + str(schain['httpRpcPort'])
    print(f'\nChecking {name}, {addr}')

    response = os.system("ping -c 1 " + ip)
    assert response == 0

    if os.path.exists(BLOCKS_FILE_PATH):
        with open(BLOCKS_FILE_PATH) as json_file:
            blocks = json.load(json_file)
    else:
        print(f'File with previous results doesn\'t exist!')
        blocks = {}

    block_obj = {}
    web3 = Web3(HTTPProvider(addr))
    block_number = web3.eth.blockNumber
    print(f"Current block number = {block_number}")
    assert block_number >= 0

    block_obj['name'] = name
    block_obj['block'] = block_number
    if blocks.get(addr):
        print(f'Previous block number = {blocks[addr]["block"]}')
        is_block_growing = block_number > blocks[addr]['block']
        print(f'Growing is {is_block_growing}')
        assert is_block_growing

    print('Saving block number to file...')
    blocks[addr] = block_obj
    with open(BLOCKS_FILE_PATH, "w") as write_file:
        json.dump(blocks, write_file)

