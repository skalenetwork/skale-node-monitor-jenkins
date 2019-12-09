from dateutil.parser import parse
import json
import os
import re
from datetime import datetime, timedelta

import pytest


DATA_DIR = 'data'
TARGET = os.environ.get('TARGET')
NODES_FILE = 'nodes.json'
NODES_FILE_PATH = os.path.join(DATA_DIR, TARGET, NODES_FILE)

EXCEPTIONS_FILE = 'exceptions.json'
EXCEPTIONS_FILE_PATH = os.path.join(DATA_DIR, TARGET, EXCEPTIONS_FILE)

IMA_ERROR_TEXT = "Loop"
CHECK_PERIOD = 10
LINES_COUNT = 300
FORMAT = '%Y-%m-%d %H:%M:%S.%f'

with open(EXCEPTIONS_FILE_PATH) as json_file:
    data = json.load(json_file)
bad_ips = data["ips"]
bad_schains = data["schains"]
print(f'bad ips = {bad_ips}')
print(f'bad schains = {bad_schains}')


def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)


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


@pytest.mark.skip(reason="skip to save time")
@pytest.mark.filterwarnings('ignore')
def test_docker_containers_are_running(host):
    ip = host.backend.host.name
    schain_prefix = "skale_schain_"
    schain_conts = [schain_prefix + schain_name for schain_name in nodes[ip] if schain_name not in bad_schains]
    ktm_prefix = "skale_ima_"
    ktm_conts = [ktm_prefix + schain_name for schain_name in nodes[ip] if schain_name not in bad_schains]

    admin_cont = "skale_admin"

    containers = [admin_cont] + schain_conts + ktm_conts
    print(containers)
    for cont in containers:
        cmd = f"docker ps | grep {cont}"
        output_result = host.check_output(cmd)
        print(f"output: {output_result}")
        assert " Up " in output_result, "Container {} should be Up".format(cont)


@pytest.mark.filterwarnings('ignore')
def test_ima_logs(host):
    ip = host.backend.host.name

    ktm_prefix = "skale_ima_"
    ktm_conts = [ktm_prefix + schain_name for schain_name in nodes[ip] if schain_name not in bad_schains]

    print(ktm_conts)

    now = datetime.utcnow()
    print(now)
    prev_check_time = now - timedelta(minutes=CHECK_PERIOD)
    print(f'Prev check time: {prev_check_time}')
    failed_conts = []
    for cont in ktm_conts:
        err_count = 0
        err_count2 = 0
        cmd = f'docker logs --tail {LINES_COUNT} {cont} 2>&1| grep "{IMA_ERROR_TEXT}"'
        output_result = escape_ansi(host.check_output(cmd))

        # print(f"output: {output_result}")
        lines = output_result.splitlines()
        # print(f"all lines: {lines}")

        print('line by line:')
        for line in lines:
            print(f'line = {line}')
            # print(parse(line, fuzzy_with_tokens=True))
            # cur_log_time = parse(line, fuzzy_with_tokens=True)[0]
            # cur_log_time = parse(line, fuzzy=False)
            match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}', line)
            cur_log_time = datetime.strptime(match.group(), FORMAT)
            print(f'extracted = {cur_log_time}')

            if cur_log_time < prev_check_time:
                print('skipping')
                err_count2 += 1
                continue
            if IMA_ERROR_TEXT in line:
                print(f'Error in IMA {cont} on host {ip}')
                err_count += 1
        if err_count > 0:
            failed_conts.append(cont)
        print(err_count, err_count2)
    assert len(failed_conts) == 0, "There are errors in IMA logs - in {} containers: {}".format(len(failed_conts), failed_conts)


@pytest.mark.skip(reason="skip to save time for debug")
@pytest.mark.filterwarnings('ignore')
def test_disk_space(host):

    max_disk_usage = 80
    mount_usage = {line.split()[5]: line.split()[4] for line in host.check_output("df -h").split('\n')[1:]}

    for key in mount_usage:
        print(key, mount_usage[key])
        assert int(mount_usage[key][:-1]) < max_disk_usage, "Disk usage for '{}' should be less than {}%".format(key, max_disk_usage)


@pytest.mark.skip(reason="skip to save time time for debug")
@pytest.mark.filterwarnings('ignore')
def test_memory(host):
    mem_min_limit = 400  # in MB
    memory_usage = host.check_output("free -m").split('\n')[1].split()

    print(f"Memory free: {memory_usage[3]} buff/cache: {memory_usage[5]}")
    assert int(memory_usage[3]) + int(memory_usage[5]) > mem_min_limit, "Memory should be more than {}".format(mem_min_limit)
