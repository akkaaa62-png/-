#!/usr/bin/env python3
"""
Простой тест подключения к Discord API
"""

import asyncio
import aiohttp
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_discord_connection():
    """Тест подключения к Discord API"""
    try:
        logger.info("🔍 Тестируем подключение к Discord API...")
    
        async with aiohttp.ClientSession() as session:
            # Тестируем подключение к Discord API
            async with session.get('https://discord.com/api/v10/gateway') as response:
                if response.status == 200:
                    logger.info("✅ Подключение к Discord API успешно!")
                    data = await response.json()
                    logger.info(f"📊 URL Gateway: {data.get('url', 'Не найден')}")
                    return True
                else:
                    logger.error(f"❌ Ошибка подключения к Discord API: {response.status}")
                    return False
                    
    except aiohttp.ClientConnectorError as e:
        logger.error(f"❌ Ошибка подключения к Discord: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        return False

async def test_internet_connection():
    """Тест общего подключения к интернету"""
    try:
        logger.info("🔍 Тестируем общее подключение к интернету...")
        
        async with aiohttp.ClientSession() as session:
            # Тестируем подключение к Google
            async with session.get('https://www.google.com', timeout=10) as response:
                if response.status == 200:
                    logger.info("✅ Подключение к интернету работает!")
                    return True
                else:
                    logger.error(f"❌ Ошибка подключения к интернету: {response.status}")
                    return False
                    
    except aiohttp.ClientConnectorError as e:
        logger.error(f"❌ Ошибка подключения к интернету: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        return False

async def main():
    """Основная функция тестирования"""
    logger.info("🚀 Начинаем тестирование подключения...")
    
    # Тестируем интернет
    internet_ok = await test_internet_connection()
    
    if internet_ok:
        # Тестируем Discord
        discord_ok = await test_discord_connection()
        
        if discord_ok:
            logger.info("🎉 Все тесты пройдены успешно! Бот должен работать.")
        else:
            logger.error("❌ Discord API недоступен. Возможные причины:")
            logger.error("• Discord заблокирован в вашей сети")
            logger.error("• Проблемы с DNS")
            logger.error("• Необходимо использовать VPN")
    else:
        logger.error("❌ Проблемы с интернет-соединением.")
        logger.error("Проверьте:")
        logger.error("• Подключение к интернету")
        logger.error("• Настройки сети")
        logger.error("• Брандмауэр")

if __name__ == "__main__":
    asyncio.run(main()) 