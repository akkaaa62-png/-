#!/usr/bin/env python3
"""
Discord Welcome Bot for Limonericx Server
Main entry point for the bot application
"""

import asyncio
import logging
import os
from bot import DiscordWelcomeBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to start the Discord bot"""
    try:
        # Initialize the bot
        bot = DiscordWelcomeBot()
        
        # Start the bot
        await bot.start_bot()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error occurred: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
