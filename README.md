# asterisk_bridge

A lightweight Python service that monitors an Asterisk PBX to trigger an incoming call. When a call comes from FXS to Asterisk, this app receives the event from Asterisk and gets the caller's phone number. It then passes it to Odoo to activate an action.


🚀 Features
1. Real-time Monitoring: Uses the panoramisk library for AMI event handling.
2. Smart Deduplication: Uses Linkedid tracking to ensure a single call doesn't trigger Odoo multiple times (e.g., when multiple handsets ring).
3. Environment Aware: Automatically locates and loads .env files from the script's local directory.
4. Clean Filtering: Ignores NO phone# or unknonw# and non-ringing state changes.

🛠️ Prerequisites
Python 3.8+
Asterisk PBX with AMI enabled (manager.conf).
Install Panoramisk library: pip install panoramisk

⚙️ Configuration
Create a .env file in the same directory as the script:
```ini
ASTERISK_HOST=127.0.0.1
ASTERISK_PORT=5038
USER=your_ami_username
SECRET=your_ami_password
```
Edit `/etc/asterisk/manager.conf` and add this:
```ini

[general]
enabled = yes
port = 5038
bindaddr = 0.0.0.0

[odoopopup]
secret = yourpassword123
deny = 0.0.0.0/0.0.0.0
permit = 0.0.0.0/0.0.0.0 ; In production, change this to your Proxmox/Python IP for security
read = call,reporting,originate
write = system,call,all
```

Reload with: `asterisk -rx "manager reload"`
Note: Ensure your AMI user in Asterisk has read=call permissions to see Newstate events.

🖥️ Usage
Run the script directly: asterisk_bridage.py

### The Python Listener
Install the library: `pip install panoramisk`


### Run the Test
Run the script on your Proxmox/LXC terminal:
```bash
python3 asterisk_monitor.py
```
