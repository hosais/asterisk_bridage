# asterisk_bridge
When a call comes from FXS to Asterisk, this app receives the event from Asterisk and gets the caller's phone number. It then passes it to Odoo to activate an action.

---

### Step 1: Configure Asterisk (AMI)
Edit `/etc/asterisk/manager.conf` and add this:

```ini
[general]
enabled = yes
port = 5038
bindaddr = 0.0.0.0

[odoopopup]
secret = yourpassword123
deny = 0.0.0.0/0.0.0.0
permit = 0.0.0.0/0.0.0.0
read = call,reporting,originate
write = system,call,all
```
Reload with: `asterisk -rx "manager reload"`

---

### Step 2: The Python Listener
Install the library: `pip install panoramisk`

**File:** `asterisk_monitor.py`
```python
import asyncio
import time
from panoramisk import Manager

# Configuration
ASTERISK_HOST = '192.168.1.XXX' 
ASTERISK_PORT = 5038
USER = 'odoopopup'
SECRET = 'yourpassword123'

# Simple memory to prevent duplicate popups: { 'linkedid': timestamp }
seen_calls = {}

async def handle_events(manager, message):
    if message.get('Event') == 'Newstate' and message.get('ChannelStateDesc') == 'Ringing':
        lid = message.get('Linkedid')
        phone = message.get('ConnectedLineNum')
        now = time.time()

        # 1. Validation
        if not phone or phone == "<unknown>":
            return

        # 2. Deduplication (30-second window)
        if lid in seen_calls:
            if (now - seen_calls[lid]) < 30:
                return

        # 3. Success Trigger
        seen_calls[lid] = now
        print(f"🚀 TRIGGERING ODOO FOR: {phone}")
        # Next: Add your requests.post here

async def main():
    manager = Manager(
        host=ASTERISK_HOST,
        port=ASTERISK_PORT,
        username=USER,
        secret=SECRET
    )
    
    try:
        await manager.connect()
        # Register the listener
        manager.register_event('Newstate', handle_events)
        print("Connected! Waiting for calls...")
        
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

### Step 3: Run the Test
Run the script on your Proxmox/LXC terminal:
```bash
python3 asterisk_monitor.py
```
