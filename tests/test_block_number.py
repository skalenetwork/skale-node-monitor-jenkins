import os
import json
from web3 import Web3, HTTPProvider

# ip = "68.183.167.8"
# port = "8003"
# addr = "http://" + ip + ":" + str(port)
# web3 = Web3(HTTPProvider(addr))

directory = "sip_tests/schains"
files = os.listdir(directory)
print(files)


def test():
    for file in files:

        with open(directory + "/" + file) as json_file:
            data = json.load(json_file)
        print(data)
        schain_name = data['schain_info']['schain_struct']['name']
        print(schain_name)

        addrs = ["http://" + node['ip'] + ":" + str(node['rpcPort']) for node in data['schain_info']['schain_nodes']]

        print("------------------")
        print(addrs)

        for node in data['schain_info']['schain_nodes']:
            node_id = node['nodeID']
            ip = node['ip']
            port = node['rpcPort']
            print(node_id, ip, port)

            addr = "http://" + ip + ":" + str(port)
            web3 = Web3(HTTPProvider(addr))
            block_number = web3.eth.blockNumber
            print(f"block number = {block_number}")
            assert block_number >= 0



        # web3 = Web3(HTTPProvider(addr))
        # block_number = web3.eth.blockNumber
        # print(f"block number = {block_number}")
        # assert block_number >= 0