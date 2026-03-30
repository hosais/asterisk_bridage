# this version show all the message info from asterisk
import os
import asyncio
from panoramisk import Manager
# --- SMART FILE LOCATOR ---
# This finds the absolute path to the folder containing this script
base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, '.env')

if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip().strip('"').strip("'")
    print(f"~\~E Loaded configuration from: {env_path}")
else:
    print(f"~]~L ERROR: .env file NOT FOUND at {env_path}")
# ---------------------------

# Configuration
ASTERISK_HOST = os.getenv('ASTERISK_HOST')
ASTERISK_PORT = os.getenv('ASTERISK_PORT', 5038)
USER = os.getenv('USER')
SECRET = os.getenv('SECRET')

#########  This shows all messages and with the all info ##############
async def handle_events(manager, message):
    #Print EVERYTHING so we can see the raw data
    if message.get('Event') == 'Newstate' and message.get('ChannelStateDesc') == 'Ringing':
        print("--- RAW EVENT START ---")
        for key, value in message.items():
            print(f"{key}: {value}")
        print("--- RAW EVENT END ---\n")
############# This shows all messages and with the all info ##############
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
