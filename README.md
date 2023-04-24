# Shadowsocks Multi User Set-Up

Set up and manage multiple [shadowsocks](https://github.com/shadowsocks/go-shadowsocks2) servers.

 - Currently, no firewall integration
 - Random password generator
 - Manage your own ports for each user, ig
 - Gives you the client links

## Installation

 - Install `go install github.com/shadowsocks/go-shadowsocks2@latest`
 - Run `pip install -r requirements.txt`
 - Copy `.env.example` to `.env` and customize

## Usage

 - Create users: `python manage.py add nea -r -p 9999`
 - Delete users `python manage.py delete nea`
 - Start the server: `python manage.py start`
 - Stop the server (and all proxies): `python manage.py stop`
 - Reload the server (without killing existing proxies (except if those accounts are now deleted)): `python manage.py reload`
 - List all users: `python manage.py list`
 - Get urls: `python manage.py get-url nea`

Also see `python manage.py -h` or `python manage.py <anysubcommand> -h`

