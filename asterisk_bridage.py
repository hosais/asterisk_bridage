import asyncio
from panoramisk import Manager

# Replace with your actual Asterisk IP
ASTERISK_HOST = '192.168.137.119' 
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
        print(f"🚀 TRIGGERING ODOO FOR: {phone}")
        
        # POST to Odoo here...
async def main():
    manager = Manager(
        host=ASTERISK_HOST,
        port=ASTERISK_PORT,
        username=USER,
        secret=SECRET
    )

    print(f"--- Attempting to connect to Asterisk at {ASTERISK_HOST} ---")
    
    try:
        await manager.connect()
        # Register the listener for Newstate events
        manager.register_event('Newstate', handle_events)
        print("✅ Connected successfully!")
        print("📡 Listening for ringing events... (Ctrl+C to exit)")
        
        # Keep the event loop alive
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping the monitor. Goodbye!")
