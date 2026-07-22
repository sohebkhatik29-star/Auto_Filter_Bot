import logging
from motor.motor_asyncio import AsyncIOMotorClient
from info import CLONE_DB_URI, DATABASE_NAME
from dreamxbotz.Bot.clients import start_clone_bot, CLONES

# Initialize Clone MongoDB Connection
if CLONE_DB_URI:
    clone_client = AsyncIOMotorClient(CLONE_DB_URI)
    clone_db = clone_client[DATABASE_NAME]
    clones_collection = clone_db['clone_bots']
else:
    clones_collection = None

async def add_clone_bot(user_id: int, bot_token: str, bot_username: str, bot_id: int):
    """
    Save new clone bot details to DB
    """
    if clones_collection is None:
        return False
    
    clone_data = {
        "_id": bot_id,
        "user_id": user_id,
        "bot_token": bot_token,
        "bot_username": bot_username
    }
    
    try:
        await clones_collection.update_one({"_id": bot_id}, {"$set": clone_data}, upsert=True)
        return True
    except Exception as e:
        logging.error(f"Error adding clone to DB: {e}")
        return False

async def get_clone_bot(user_id: int):
    """
    Get clone bot by user ID
    """
    if clones_collection is None:
        return None
    return await clones_collection.find_one({"user_id": user_id})

async def delete_clone_bot(user_id: int):
    """
    Remove clone bot from DB
    """
    if clones_collection is None:
        return False
    try:
        result = await clones_collection.delete_one({"user_id": user_id})
        return result.deleted_count > 0
    except Exception as e:
        logging.error(f"Error deleting clone from DB: {e}")
        return False

async def get_all_clones():
    """
    Fetch all active clone bots
    """
    if clones_collection is None:
        return []
    clones = []
    async for clone in clones_collection.find():
        clones.append(clone)
    return clones

async def restart_clones(main_bot):
    """
    Restart all registered clone bots on main bot startup
    """
    if clones_collection is None:
        return
    
    clones = await get_all_clones()
    logging.info(f"🔄 Restoring {len(clones)} Clone Bots...")
    
    for clone in clones:
        bot_token = clone.get("bot_token")
        user_id = clone.get("user_id")
        
        if bot_token:
            try:
                app, err = await start_clone_bot(bot_token, user_id)
                if err:
                    logging.error(f"Failed to restart clone (@{clone.get('bot_username')}): {err}")
                else:
                    logging.info(f"✅ Successfully restored clone: @{clone.get('bot_username')}")
            except Exception as e:
                logging.error(f"Exception restarting clone: {e}")

