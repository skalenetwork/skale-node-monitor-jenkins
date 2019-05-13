import os
import json
import pytest
from web3 import Web3, HTTPProvider

OMITTED_IPS = []
OMITTED_SCHAINES = ['QAHIX5SL']
target = os.environ.get('TARGET')
DATA_DIR = "data"
SCHAINS_DIR = target + "_schains"
directory = os.path.join(DATA_DIR, SCHAINS_DIR)
files = os.listdir(directory)
BLOCKS_FILE = target + "_blocks.json"
BLOCKS_FILE_PATH = os.path.join(DATA_DIR, BLOCKS_FILE)
schains = []

for file in files:
    with open(directory + "/" + file) as json_file:
        data = json.load(json_file)
    schain_name = data['schain_info']['schain_struct']['name']
    addrs = ["http://" + node['ip'] + ":" + str(node['rpcPort']) for node in data['schain_info']['schain_nodes']]
    if schain_name not in OMITTED_SCHAINES:
        schains.append({'name': schain_name, 'addresses': addrs})
print(f's-chains (len = {len(schains)}) = {schains}')


@pytest.mark.parametrize("schain", schains)
def test(schain):
    name = schain['name']
    print(f'\nTesting {name}, {schain["addresses"]}')
    if os.path.exists(BLOCKS_FILE_PATH):
        with open(BLOCKS_FILE_PATH) as json_file:
            blocks = json.load(json_file)
    else:
        print(f'File with previous results doesn\'t exist!')
        blocks = {}
    blocks_obj = {}
    for addr in schain['addresses']:
        print(f'Endpoint = {addr}')
        web3 = Web3(HTTPProvider(addr))
        block_number = web3.eth.blockNumber
        print(f"Current block number = {block_number}")
        assert block_number >= 0

        blocks_obj[addr] = block_number
        if blocks.get(name):
            print(f'Previous block number = {blocks[name][addr]}')
            is_block_growing = block_number > blocks[name][addr]
            print(f'Growing is {is_block_growing}')
            assert is_block_growing

    print('Saving block numbers to file...')
    blocks[name] = blocks_obj
    with open(BLOCKS_FILE_PATH, "w") as write_file:
        json.dump(blocks, write_file)
