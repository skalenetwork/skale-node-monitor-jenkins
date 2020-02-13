from web3 import Web3, HTTPProvider
import pytest
import testinfra


hosts = [
    testinfra.get_host("paramiko://ubuntu@18.218.24.50", ssh_identity_file="/home/alex/Documents/AWS/eth_net.pem"),
    testinfra.get_host("paramiko://ubuntu@13.59.228.21", ssh_identity_file="/home/alex/Documents/AWS/eth_net.pem"),
]


# def setup_module(module):
#     global host
#     host = testinfra.get_host("paramiko://ubuntu@18.218.24.50", ssh_identity_file="/home/alex/Documents/AWS/eth_net.pem")
#     print(host)

@pytest.mark.parametrize("host", hosts)
@pytest.mark.filterwarnings('ignore')
def test_docker_containers_are_running(host):
    ip = host.backend.host.name
    print(ip)
    cont = "test-geth"

    cmd = f"docker ps | grep {cont}"
    output_result = host.check_output(cmd)
    print(f"output: {output_result}")
    assert " Up " in output_result, "Container {} should be Up".format(cont)


@pytest.mark.parametrize("host", hosts)
@pytest.mark.filterwarnings('ignore')
def test_disk_space(host):

    max_disk_usage = 80  # in %
    mount_usage = {line.split()[5]: line.split()[4] for line in host.check_output("df -h").split('\n')[1:]}

    for key in mount_usage:
        if "snap" not in key:
            print(key, mount_usage[key])
            assert int(mount_usage[key][:-1]) < max_disk_usage, "Disk usage for '{}' should be less than {}%".format(key, max_disk_usage)


@pytest.mark.parametrize("host", hosts)
@pytest.mark.filterwarnings('ignore')
def test_memory(host):
    mem_min_limit = 1024  # in MB
    memory_usage = host.check_output("free -m").split('\n')[1].split()

    print(f"Memory free: {memory_usage[3]} buff/cache: {memory_usage[5]}")
    assert int(memory_usage[3]) + int(memory_usage[5]) > 512, "Memory should be more than {}".format(mem_min_limit)
