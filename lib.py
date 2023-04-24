"""
Copyright (c) 2023 Linnea Gräf.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import base64
import dataclasses
import json
import os
import typing
import urllib.parse
from pathlib import *

from dotenv import load_dotenv

load_dotenv()
base = Path(__file__).parent.absolute()
path = base / 'accounts.json'

shadowsocksbin = os.environ.get('SSM_BIN')
myname = os.environ.get('SSM_NAME', '')
myip = os.environ.get('SSM_IP')
pidfile = Path(os.environ.get('SSM_PIDFILE', str(base / '.pid')))

users = {}


def load():
    if path.exists():
        with path.open() as fp:
            global users
            users = json.load(fp)


@dataclasses.dataclass
class User:
    name: str
    password: str
    port: int


def save():
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open('w') as fp:
        json.dump(users, fp)


def create_url(user: User, server: str = myip, encode: bool = True) -> str:
    encryption = f'aes-256-gcm:{user.password}'
    if encode:
        encoded_encryption = base64.b64encode(encryption.encode('utf-8')).decode('utf-8')
    else:
        encoded_encryption = encryption
    return f'ss://{encoded_encryption}@{server}:{user.port}' + (
        f'#{urllib.parse.quote(myname.replace("{user}", user.name), safe="")}' if encode and myname else "")


def create_args(user: User) -> list[str]:
    return [shadowsocksbin, '-s', create_url(user, '', False)]


def get_pid() -> typing.Optional[int]:
    if pidfile.exists():
        return int(pidfile.read_text())
    else:
        return None


def set_pid(pid: typing.Optional[int]):
    pidfile.parent.mkdir(parents=True, exist_ok=True)
    if pid:
        pidfile.write_text(str(pid))
    else:
        pidfile.unlink(missing_ok=True)


def add_user(name: str, password: str, port: int):
    users[name] = dict(password=password, port=port)


def get_all_users() -> dict[str, User]:
    user_list = {}
    for name, data in users.items():
        user_list[name] = (User(name, data['password'], data['port']))
    return user_list
