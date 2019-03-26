import os
import json
import pytest
from web3 import Web3, HTTPProvider


directory = "tests/paris_schains"
files = os.listdir(directory)
# print(files)

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
    for addr in schain['addresses']:
        web3 = Web3(HTTPProvider(addr))
        block_number = web3.eth.blockNumber
        print(f"block number = {block_number}")
        assert block_number >= 0
