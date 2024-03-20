from backend import Backend
import config
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
    backend_logic = Backend(cfg, config.cidr)
    over_ip_num = (1 << (32 - int(backend_logic.cidr.split("/")[1]))) + 1
    try:
        for i in range(over_ip_num):
            dummy = f"dummy{i}"
            backend_logic.new_user(dummy)
        else:
            assert 1==2
    except SystemError:
        assert True

    finally:
        keys = set(backend_logic.config.keys())
        for user in keys:
            if user.startswith("dummy"):
                del backend_logic.config[user]
        backend_logic.write_cfg()
