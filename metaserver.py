"""
Copyright (c) 2023 Linnea Gräf.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import atexit
import dataclasses
import os
import signal
import subprocess
import sys

import lib

lib.load()

if lib.get_pid():
    print("Found running process at .pid")
    sys.exit(1)

lib.set_pid(os.getpid())


@dataclasses.dataclass
class Process:
    name: str
    password: str
    port: int
    proc: subprocess.Popen


processes: dict[str, Process] = {}


def reload():
    print("Reload started")
    lib.load()
    to_remove = []
    for proc in processes.values():
        user = lib.get_all_users().get(proc.name)
        should_terminate = user is None or proc.name != user.name or proc.password != user.password or proc.port != user.port
        if should_terminate:
            print(f"Terminating process for user {proc.name}")
            proc.proc.kill()
        if should_terminate or proc.proc.poll() is not None:
            to_remove.append(proc.name)

    for rem in to_remove:
        print(f"Removed data for dead process {rem}")
        del processes[rem]

    for user in lib.get_all_users().values():
        if user.name in processes:
            print(f"Skipping process creation for user {user.name} since a process already exists")
            continue
        print(f"Spawning new process for user {user.name} on port {user.port}")
        print(f"User facing url: {lib.create_url(user)}")
        proc = subprocess.Popen(lib.create_args(user))
        processes[user.name] = (Process(user.name, user.password, user.port, proc))
    print("Reload finished")


print(f"Meta Server started. Use python manage.py reload {os.getpid()} to reload.")

reload()
signal.signal(signal.SIGHUP, lambda x, y: reload())


def sigint(a, b):
    print("Exiting")
    lib.set_pid(None)
    for proc in processes.values():
        print(f"Killing process {proc.name}")
        proc.proc.kill()
    processes.clear()
    if a != 'bad':
        sys.exit(1)


atexit.register(sigint, 'bad', 0)
signal.signal(signal.SIGINT, sigint)

while True:
    signal.pause()
