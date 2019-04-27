import os
import json
import pytest
from web3 import Web3, HTTPProvider

target = os.environ.get('TARGET')
DATA_DIR = "data"
SCHAINS_DIR = target + "_schains"
directory = os.path.join(DATA_DIR, SCHAINS_DIR)
files = os.listdir(directory)
BLOCK_FILE = target + "_blocks.json"
BLOCK_FILE_PATH = os.path.join(DATA_DIR, BLOCK_FILE)
schains = []

for file in files:

    with open(directory + "/" + file) as json_file:
        data = json.load(json_file)
    # print(data)
    schain_name = data['schain_info']['schain_struct']['name']
    # print(schain_name)

    addrs = ["http://" + node['ip'] + ":" + str(node['rpcPort']) for node in data['schain_info']['schain_nodes']]
    schains.append({'name': schain_name, 'addresses': addrs})

# print(schains)


@pytest.mark.parametrize("schain", schains)
def test(schain):
    print(schain)
    if os.path.exists(BLOCK_FILE_PATH):
        with open(BLOCK_FILE_PATH) as json_file:
            blocks = json.load(json_file)
        print(f'blocks = {blocks}')
    else:
        print(f'no blocks file!')
        blocks = {}
    blocks_obj = {}
    for addr in schain['addresses']:
        web3 = Web3(HTTPProvider(addr))
        block_number = web3.eth.blockNumber
        print(f"block number = {block_number}")
        assert block_number >= 0
        name = schain['name']
        blocks_obj[addr] = block_number
        if blocks:
            print(block_number)
            print(blocks[name][addr])
            is_block_growing = block_number > blocks[name][addr]
            print(f'growing is {is_block_growing}')
            assert is_block_growing
    blocks[name] = blocks_obj
    with open(BLOCK_FILE_PATH, "w") as write_file:
        json.dump(blocks, write_file)

    print(f'blocks = {blocks}')
