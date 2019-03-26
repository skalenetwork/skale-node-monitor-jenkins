import paramiko


def setup_module(module):
    key = paramiko.RSAKey.from_private_key_file("/home/alex/Documents/AWS/eth_net.pem")
    global client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("connecting")
    client.connect(hostname="18.218.24.50", username="ubuntu", pkey=key)
    print("connected")


def teardown_module(module):
    client.close()


def test_docker_containers_are_running():

    cont = "test-geth"
    cmd = f"docker ps | grep {cont}"
    print(f"Executing {cmd}")
    stdin , stdout, stderr = client.exec_command(cmd)
    output_result = stdout.read().decode('utf-8')
    print(output_result)

    assert " Up " in output_result, "Container {} should be Up".format(cont)
    print("Errors:")
    print(stderr.read())


# commands = [ "docker ps | grep test-geth" ]
# for command in commands:
#     print("Executing {}".format( command ))
#     stdin , stdout, stderr = client.exec_command(command)
#     print(stdout.read())
#     print( "Errors")
#     print(stderr.read())
# client.close()