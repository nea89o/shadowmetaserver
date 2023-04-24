#!/usr/bin/env python3
"""
Copyright (c) 2023 Linnea Gräf.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import argparse
import os
import random
import signal
import string
import subprocess
import sys

import lib

lib.load()
parser = argparse.ArgumentParser()
if __name__ == '__main__':

    sub = parser.add_subparsers(dest='command', required=True)

    add = sub.add_parser('add', help="Add a user")
    add.add_argument('username', help="User name")
    add.add_argument('--password', '--pass', '-P', help="Set specific password")
    add.add_argument('--random-password', '-r', help="Use random password", action='store_const', const=True,
                     default=False, dest='random')
    add.add_argument('--port', '-p', help="Port", required=True)

    delete = sub.add_parser('delete', help="Delete a user")
    delete.add_argument('username', help="User name")

    list_cmd = sub.add_parser('list', help="List all users")
    list_cmd.add_argument('--with-urls', '-u', help="Display client urls (which contain login information)",
                          action='store_const', const=True, default=False, dest="urls")

    get_url = sub.add_parser("get-url", help="Get a users url")
    get_url.add_argument('username', help="User name")
    stop = sub.add_parser("stop", help="Stop the metaserver")
    start = sub.add_parser("start", help="Start the metaserver")

    reload = sub.add_parser('reload', help="Reload the metaserver")

    args = parser.parse_args()
    if args.command == "stop":
        if lib.get_pid() is None:
            print("No daemon found")
            sys.exit(1)
        os.kill(lib.get_pid(), signal.SIGINT)

    if args.command == "start":
        if lib.get_pid() is not None:
            print(f"Already found daemon with pid {lib.get_pid()}")
            sys.exit(1)
        subprocess.Popen([sys.executable, str(lib.base / 'metaserver.py')], start_new_session=True)

    if args.command == 'get-url':
        user = lib.get_all_users().get(args.username)
        if user is None:
            print("No user found")
            sys.exit(1)

        print(lib.create_url(user))

    if args.command == 'list':
        for user in lib.get_all_users().values():
            print(end=f"{user.name} - {user.port}")
            if args.urls:
                print(f' - {lib.create_url(user)}')
            else:
                print()

    if args.command == 'add':
        port = int(args.port)
        password = args.password
        if (password is not None) + args.random != 1:
            print("Either specify a password with --password or with --random-password")
            sys.exit(1)
        if args.random:
            password = ''.join(random.choice(string.hexdigits) for _ in range(20))
        if args.username in lib.users:
            print("This user already exists")
            sys.exit(1)
        if port in [u.port for u in lib.get_all_users().values()]:
            print("This port is already in use")
            sys.exit(1)
        lib.add_user(args.username, password, port)
        lib.save()
    if args.command == 'delete':
        del lib.users[args.username]
        lib.save()

    if args.command == 'reload':
        if lib.get_pid() is None:
            print("No daemon found")
            sys.exit(1)
        os.kill(lib.get_pid(), signal.SIGHUP)
