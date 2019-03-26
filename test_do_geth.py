from web3 import Web3, HTTPProvider
import pytest

geth_ips = ['138.68.42.146', '134.209.56.45', '134.209.56.46']

prefix = "paramiko://root@"

testinfra_hosts = [prefix + ip for ip in geth_ips]


@pytest.mark.filterwarnings('ignore')
class TestDOgethNodes:

    def test_docker_containers_are_running(self, host):
        ip = host.backend.host.name
        print(ip)
        cont = "geth"

        cmd = f"docker ps | grep {cont}"
        output_result = host.check_output(cmd)
        print(f"output: {output_result}")
        assert " Up " in output_result, "Container {} should be Up".format(cont)

    def test_disk_space(self, host):

        max_disk_usage = 80  # in %
        mount_usage = {line.split()[5]: line.split()[4] for line in host.check_output("df -h").split('\n')[1:]}

        for key in mount_usage:
            if "snap" not in key:
                print(key, mount_usage[key])
                assert int(mount_usage[key][:-1]) < max_disk_usage, "Disk usage for '{}' should be less than {}%".format(key, max_disk_usage)

    def test_memory(self, host):
        mem_min_limit = 1024  # in MB
        memory_usage = host.check_output("free -m").split('\n')[1].split()

        print(f"Memory free: {memory_usage[3]} buff/cache: {memory_usage[5]}")
        assert int(memory_usage[3]) + int(memory_usage[5]) > 512, "Memory should be more than {}".format(mem_min_limit)

    def test_block_number(self, host):
        ip = host.backend.host.name
        port = 1919
        print(f"ip = {ip}")
        addr = "http://" + ip + ":" + str(port)
        web3 = Web3(HTTPProvider(addr))
        block_number = web3.eth.blockNumber
        print(f"block number = {block_number}")
        assert block_number >= 0
