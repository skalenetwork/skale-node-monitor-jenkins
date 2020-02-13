import os

target = os.environ.get('TARGET')


def test_case_1():
    print(target)
    assert target == 'paris'
