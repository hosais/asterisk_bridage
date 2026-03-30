# asterisk_bridage
When a call from FXS to asterisk, this app receive from asterisk and get caller phone #. then it pass it to odoo or activate some action.



Step 1: Configure Asterisk (AMI)
Tell Asterisk to allow a remote connection. Log into your Asterisk console (or via SSH) and edit the manager configuration.
1. Open the file: nano /etc/asterisk/manager.conf
2. Ensure the [general] section has enabled = yes.
3. Add a specific user for your Python script at the bottom:
Ini, TOML
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
4. Reload Asterisk Manager: Run this command in your terminal: asterisk -rx "manager reload"

Step 2: The Python Listener (The "Test" Script)
We will use the panoramisk library because it handles the messy TCP socket logic for you and is very stable.
1. Install the library:
Bash
pip install panoramisk
2. Create the script asterisk_monitor.py:
Python
import asyncio
from panoramisk import Manager
# Configuration
ASTERISK_HOST = '192.168.1.XXX' # Replace with your Asterisk IP
ASTERISK_PORT = 5038
USER = 'odoopopup'
SECRET = 'yourpassword123'

#########  This shows all messages and with the all info ##############
#async def handle_events(manager, message):
#    Print EVERYTHING so we can see the raw data
#    if message.get('Event') == 'Newstate' and message.get('ChannelStateDesc') == 'Ringing':
#        print("--- RAW EVENT START ---")
#        for key, value in message.items():
#            print(f"{key}: {value}")
#        print("--- RAW EVENT END ---\n")
############# This shows all messages and with the all info ##############

import time

# Simple memory: { 'linkedid': timestamp }
seen_calls = {}
async def handle_events(manager, message):
    if message.get('Event') == 'Newstate' and message.get('ChannelStateDesc') == 'Ringing':

        lid = message.get('Linkedid')
        # Get the number, default to None if missing
        phone = message.get('ConnectedLineNum')
        now = time.time()

        # 1. Basic Validation: Is there actually a number?
        if not phone or phone == "<unknown>":
            print(f"DEBUG: Call received on {lid} but no Caller ID found.")
            return

        # 2. Deduplication: Have we handled this Linkedid in the last 30s?
        if lid in seen_calls:
            if (now - seen_calls[lid]) < 30:
		return

        # 3. Success: Record and Trigger
        seen_calls[lid] = now
        print(f"~_~Z~@ TRIGGERING ODOO FOR: {phone}")

        # POST to Odoo here...






async def main():
    manager = Manager(
        host=ASTERISK_HOST,
        port=ASTERISK_PORT,
        username=USER,
        secret=SECRET
    )
print(f"Connecting to Asterisk at {ASTERISK_HOST}...")
    
    try:
        await manager.connect()
        # We register the 'Newstate' event which carries the 'Ringing' status
        manager.register_event('Newstate', callback)
        print("Connected! Waiting for calls... (Press Ctrl+C to stop)")
        
        # Keep the script running forever
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"Error: {e}")
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping listener...")

Step 3: Run the Test
1. Run the script on your Proxmox terminal:
Bash
python3 asterisk_monitor.py
2. Place a call to your system via your FXS Gateway.
3. Watch the terminal. You should see the "🔔 INCOMING CALL DETECTED!" message appear immediately.
<img width="1524" height="4594" alt="image" src="https://github.com/user-attachments/assets/95509128-12cc-4a9d-b4f2-24afdc89429d" />
