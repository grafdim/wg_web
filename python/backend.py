import utils
from asyncio import Lock

class Backend:
    def __init__(self, cfg_path, cidr):
        self.path = cfg_path
        self.config = utils.parse_config(self.path)
        self.cidr = cidr
        self.lock = Lock()

    def new_user(self, username: str):
        if username in self.config.keys():
            raise KeyError("User already exists!")
        rand_ip = self.new_rand_ip()
        cfg, private = utils.gen_user_keys()
        cfg |= {"AllowedIPs": rand_ip+"/32"}
        self.config |= {username: cfg}
        self.write_cfg()
        return cfg | {"PrivateKey": private}

    def write_cfg(self):
        with open(self.path, "w") as f:
            f.write(utils.repr_config(self.config))

    def del_user(self, user: str):
        del self.config[user]
        self.write_cfg()


    def new_rand_ip(self):
        reserved = utils.reserved_ips(self.path)
        reserved_bits = int(self.cidr.split("/")[1])
        if len(reserved) > (1 << (32 - reserved_bits)) - 2:
            raise SystemError(f"Ip range {self.cidr} exhausted.")
        rand_ip = utils.randIP(self.cidr)
        while rand_ip in reserved:
            rand_ip = utils.randIP(self.cidr)
        return rand_ip
