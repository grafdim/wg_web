from functools import reduce
from subprocess import Popen, PIPE
from random import randint
from ipaddress import ip_address
import re

def randIP(ip_cidr: str) -> str:
    base_ip, reserved_bits = ip_cidr.split("/")
    max_num = (1 << (32 - int(reserved_bits))) - 1
    ip_num = int(ip_address(base_ip))
    rand_num = randint(1, max_num)
    return str(ip_address(ip_num ^ rand_num))


def entryToDict(en: str) -> dict:
    e1, e2 = en.split("=")
    return {e1.strip(): e2.strip()}

def entry(txt: str) -> dict:
    lines = txt.strip().split("\n")
    lines = (line.strip() for line in lines)
    lines = (line.split("=") for line in lines)
    entries = ({e[0][0].strip() : e[0][1].strip()} for e in lines)
    return reduce(lambda acc, x: acc | x, entries, {})


def parse_config(path: str) -> dict:
    with open(path, 'r', encoding="utf-8") as f:
        txt = f.read()
        peer = r"\[Peer\]\s*#(.+)\s*(.+\s*.+\s*.+)\s*"
        peer_dict = {}
        peers_match = re.findall(peer,txt)
        if len(peers_match) > 0:
            for peer in peers_match:
                pname = peer[0]
                pstr = peer[1]
                binds = re.findall(r'(.+)\s+=\s+(.+)\s*', pstr)
                bdict = {k: v for (k, v) in binds}
                peer_dict |= {pname: bdict}

        iface = r'\[Interface\]\s*(.*\s*.*\s*.*\s*.*\s*.*\s*.*\s*)'
        interface = re.findall(iface, txt)
        binds = re.findall(r'(.+)\s+=\s+(.+)\s*', interface[0])
        interface_dict = {"Interface": {k: v for (k, v) in binds}}
        return interface_dict | peer_dict

def reserved_ips(cfg: str) -> tuple:
    ipregexp = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    with open(cfg, 'r') as f:
        txt = f.read()
        matches = re.finditer(ipregexp, txt)
        matches = (ip.group() for ip in matches)
        return tuple(matches)



def repr_config(entity: dict) -> str:
    txt = "[Interface]\n"
    for key, val in entity["Interface"].items():
        txt += f"{key} = {val}\n"
    for key, val in entity.items():
        if key != "Interface":
            txt += f"[Peer] # {key}\n"
            for k, v in val.items():
                txt += f"{k} = {v}\n"
    return txt + "\n\n"


def gen_user_keys() -> dict:
    proc = Popen(['wg', 'genkey'], stdout=PIPE, text=True)
    private, _ = proc.communicate()
    proc = Popen(['wg', 'pubkey'], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True)
    proc.stdin.write(private)
    public, _ = proc.communicate()
    proc = Popen(["wg", "genpsk"], stdout=PIPE, text=True)
    psk, _ = proc.communicate()
    return ({
            "PublicKey": public,
            "PresharedKey": psk
            }, private)
