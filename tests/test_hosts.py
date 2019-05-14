import pytest
import json
import os

DATA_DIR = "data"
TARGET = os.environ.get('TARGET')
NODES_FILE = TARGET + "_schains.json"
NODES_FILE_PATH = os.path.join(DATA_DIR, NODES_FILE)


BAD_IPS_FILE = TARGET + "_exceptions.json"
BAD_IPS_FILE_PATH = os.path.join(DATA_DIR, BAD_IPS_FILE)

with open(BAD_IPS_FILE_PATH) as json_file:
    data = json.load(json_file)
bad_ips = data["ips"]
bad_schains = data["schains"]
print(f'bad ips = {bad_ips}')
print(f'bad schains = {bad_schains}')


def get_nodes():

    try:
        print("Reading nodes data...")
        with open(NODES_FILE_PATH) as json_file:
            data = json.load(json_file)
        return data  # {"array":
    except KeyError as err:
        print(f"Cannot read ip data (KeyError)")
        raise err
    except FileNotFoundError as err:
        print(f"Cannot read ip data (FileNotFoundError)")
        raise err
    except Exception as err:
        print(f"Cannot read ip data from the file: {err}")
        raise err


nodes = {}
for node in get_nodes():
    schains = [schain["name"] for schain in node["schains"]]
    nodes[node["node"]["ip"]] = schains

print(f'nodes ({len(nodes)}) = {nodes}')

prefix = "paramiko://root@"

ips = [node for node in nodes if node not in bad_ips]
print(ips)
testinfra_hosts = [prefix + ip for ip in ips]
print(testinfra_hosts)


@pytest.mark.filterwarnings('ignore')
def test_docker_containers_are_running(host):
    ip = host.backend.host.name
    schain_prefix = "skale_schain_"
    schain_conts = [schain_prefix + node for node in nodes[ip]]
    ktm_prefix = "skale_ktm_"
    ktm_conts = [ktm_prefix + node for node in nodes[ip]]

    admin_cont = "skale_admin"

    containers = [admin_cont] + schain_conts + ktm_conts
    print(containers)
    for cont in containers:
        cmd = f"docker ps | grep {cont}"
        output_result = host.check_output(cmd)
        print(f"output: {output_result}")
        assert " Up " in output_result, "Container {} should be Up".format(cont)


@pytest.mark.filterwarnings('ignore')
def test_disk_space(host):

    max_disk_usage = 80
    mount_usage = {line.split()[5]: line.split()[4] for line in host.check_output("df -h").split('\n')[1:]}

    for key in mount_usage:
        print(key, mount_usage[key])
        assert int(mount_usage[key][:-1]) < max_disk_usage, "Disk usage for '{}' should be less than {}%".format(key, max_disk_usage)


@pytest.mark.filterwarnings('ignore')
def test_memory(host):
    mem_min_limit = 1024  # in MB
    memory_usage = host.check_output("free -m").split('\n')[1].split()

    print(f"Memory free: {memory_usage[3]} buff/cache: {memory_usage[5]}")
    assert int(memory_usage[3]) + int(memory_usage[5]) > 512, "Memory should be more than {}".format(mem_min_limit)
