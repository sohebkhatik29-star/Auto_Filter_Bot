import asyncio
import logging
from info import *
from pyrogram import Client
from dreamxbotz.util.config_parser import TokenParser
from . import multi_clients, work_loads, dreamxbotz

# Active Clone Bots Dictionary
CLONES = {}
CLONE_TOKENS = {}

async def initialize_clients():
    multi_clients[0] = dreamxbotz
    work_loads[0] = 0
    all_tokens = TokenParser().parse_from_env()
    if not all_tokens:
        print("No additional clients found, using default client")
        return
    
    async def start_client(client_id, token):
        try:
            print(f"Starting - Client {client_id}")
            if client_id == len(all_tokens):
                await asyncio.sleep(2)
                print("This will take some time, please wait...")
            client = await Client(
                name=str(client_id),
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=token,
                sleep_threshold=SLEEP_THRESHOLD,
                no_updates=True,
                in_memory=True
            ).start()
            work_loads[client_id] = 0
            return client_id, client
        except Exception:
            logging.error(f"Failed starting Client - {client_id} Error:", exc_info=True)
            return None
    
    clients = await asyncio.gather(*[start_client(i, token) for i, token in all_tokens.items() if token])
    valid_clients = {c[0]: c[1] for c in clients if c is not None}
    multi_clients.update(valid_clients)
    
    if len(multi_clients) > 1:
        MULTI_CLIENT = True
        print("Multi-Client Mode Enabled")
    else:
        print("No additional clients were initialized, using default client")


# ============================
# Clone Bot Helper Functions
# ============================

async def start_clone_bot(bot_token: str, user_id: int = None):
    """
    Dynamically start a new clone bot using user's bot token
    """
    if not bot_token:
        return None, "Invalid Token"
    
    if bot_token in CLONE_TOKENS:
        return CLONE_TOKENS[bot_token], "Already Running"

    try:
        app = Client(
            name=f"clone_{bot_token[:10]}",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=bot_token,
            plugins=dict(root="plugins"),
            in_memory=True
        )
        await app.start()
        bot_info = await app.get_me()
        
        # Save running clone instance
        CLONES[bot_info.id] = app
        CLONE_TOKENS[bot_token] = app
        
        logging.info(f"🤖 Clone Bot Started: @{bot_info.username} ({bot_info.id})")
        return app, None

    except Exception as e:
        logging.error(f"Failed to start Clone Bot: {e}")
        return None, str(e)


async def stop_clone_bot(bot_id_or_token):
    """
    Stop a running clone bot by ID or Token
    """
    try:
        client = None
        if isinstance(bot_id_or_token, int) and bot_id_or_token in CLONES:
            client = CLONES.pop(bot_id_or_token)
            # Remove from token dict
            for tok, cl in list(CLONE_TOKENS.items()):
                if cl == client:
                    CLONE_TOKENS.pop(tok, None)
                    break
        elif bot_id_or_token in CLONE_TOKENS:
            client = CLONE_TOKENS.pop(bot_id_or_token)
            # Remove from id dict
            for b_id, cl in list(CLONES.items()):
                if cl == client:
                    CLONES.pop(b_id, None)
                    break

        if client:
            await client.stop()
            logging.info("🛑 Clone Bot Stopped Successfully.")
            return True
    except Exception as e:
        logging.error(f"Error stopping clone bot: {e}")
    return False
