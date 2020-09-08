# import json
import re

import pytest
from tools.helper import init_skale_with_w3_wallet, ip_from_bytes, ERROR_TEXT, LINES_COUNT

# with open(EXCEPTIONS_FILE_PATH) as json_file:
#     data = json.load(json_file)
# bad_ips = data["ips"]
# print(f'bad ips = {bad_ips}')


def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)


prefix = "paramiko://ubuntu@"


# ips = [node for node in nodes if node not in bad_ips]

skale = init_skale_with_w3_wallet()
ips = skale.nodes.get_active_node_ips()

testinfra_hosts = [prefix + ip_from_bytes(ip) for ip in ips]
# print(testinfra_hosts)


# @pytest.mark.skip(reason="skip to save time for debug")
@pytest.mark.filterwarnings('ignore')
def test_sla_logs(host):
    ip = host.backend.host.name
    # print(f'ip = {ip}')

    err_count = 0
    err_skipped_count = 0
    # cmd = f'sudo docker logs --tail {LINES_COUNT} skale_sla 2>&1| grep "{ERROR_TEXT}" || true'
    cmd = f'sudo docker logs skale_sla 2>&1 | grep "{ERROR_TEXT}" || true'
    output_result = host.check_output(cmd)
    print(f'res = {output_result}')
    if output_result:
        print(f"output: {output_result}")
        lines = output_result.splitlines()
        # print(f"all lines: {lines}")

        print('Lines with errors:')
        for line in lines:
            # print(f'{line}')
            # match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}', line)
            # cur_log_time = datetime.strptime(match.group(), FORMAT)
            # # print(f'extracted = {cur_log_time}')

            if ERROR_TEXT in line:
                # print(f'Error in SLA on host {ip}')
                err_count += 1
    print(f'Errors: {err_count}, Skipped: {err_skipped_count}')
    assert err_count == 1, "Multiple init was in sla-agent for {}".format(ip)
    # assert len(failed_conts) == 0, "There are errors in IMA logs - in {} containers: {}".format(len(failed_conts), failed_conts)


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
