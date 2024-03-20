from backend import Backend
import pytest
import config
import utils
import ipaddress
cfg = "./wg0.conf"


def test_backend_init():
    backend_logic = Backend(cfg, config.cidr)
    assert len(backend_logic.config) != 0

def test_user_functionality():
    backend_logic = Backend(cfg, config.cidr)
    new_user = "test_user_2"
    backend_logic.new_user(new_user)
    assert new_user in backend_logic.config
    backend_logic.del_user(new_user)
    assert new_user not in backend_logic.config

def test_ip_range_exception():
    with pytest.raises(SystemError) as execinfo:
        backend_logic = Backend(cfg, config.cidr)
        over_ip_num = (1 << (32 - int(backend_logic.cidr.split("/")[1]))) + 1
        for i in range(over_ip_num):
            dummy = f"dummy{i}"
            backend_logic.new_user(dummy)
    assert execinfo.type is SystemError
    keys = set(backend_logic.config.keys())
    for user in keys:
        if user.startswith("dummy"):
            del backend_logic.config[user]
    backend_logic.write_cfg()


def test_double_add_same_user_exception():
    backend_logic = Backend(cfg,config.cidr)
    with pytest.raises(KeyError) as info:
        new_user = "dummy_double"
        backend_logic.new_user(new_user)
        backend_logic.new_user(new_user)
    assert info.type is KeyError
    backend_logic.del_user(new_user)

def test_nonexistant_user_delete():
    backend_logic = Backend(cfg,config.cidr)
    with pytest.raises(KeyError) as info:
        user = "IdoNotExist"
        backend_logic.del_user(user)
    assert info.type is KeyError


def test_random_ip_generation():
    test_network = "10.0.0.0/19"
    free_bits = 32 - int(test_network.split("/")[1])
    for _ in range(1 << free_bits):
        assert ipaddress.ip_address(utils.randIP(test_network)) in ipaddress.ip_network(test_network)
