# PyChat server (WebSocket)

This directory contains a minimal WebSocket broadcast server for the `pychat` GUI.

Contents
- `server.py` - asyncio WebSocket broadcast server (uses `websockets` library).
- `client_example.py` - small example client to test connect/send/receive.
- `requirements.txt` - server dependencies.

Quick start (on AlmaLinux 10 VPS)

1. Install Python 3 and virtualenv

```bash
sudo dnf install -y python3 python3-venv
```

2. Create venv and install requirements

```bash
python3 -m venv ~/pychat-venv
. ~/pychat-venv/bin/activate
pip install -r /path/to/pychat/server/requirements.txt
```

3. Open firewall port (8765) and reload

```bash
sudo firewall-cmd --add-port=8765/tcp --permanent
sudo firewall-cmd --reload
```

4. Run server

```bash
python /path/to/pychat/server/server.py
```

5. (Optional) Create a systemd service so the server starts automatically

Create `/etc/systemd/system/pychat-server.service` with the following content (adjust paths):

```
[Unit]
Description=PyChat WebSocket Server
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/pychat
ExecStart=/home/youruser/pychat-venv/bin/python /home/youruser/pychat/server/server.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Then enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now pychat-server
sudo journalctl -u pychat-server -f
```

SELinux notes

If SELinux is enforcing you usually don't need extra rules for running a Python server, but if you place files under non-standard locations you may need to adjust contexts. If you encounter permission denied errors, check `sudo ausearch -m avc -ts recent` and use `semanage fcontext`/`restorecon` as needed.

Testing from the desktop client

Update the GUI client to connect to `ws://your.server.ip:8765` (not implemented automatically in this repo). Alternatively use `client_example.py` from a machine that can reach the server:

```bash
python client_example.py --uri ws://your.server.ip:8765 --send "hello from test"
```
