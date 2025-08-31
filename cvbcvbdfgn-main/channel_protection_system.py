"""
Система защиты каналов от удаления
Автоматически восстанавливает удаленные каналы и наказывает нарушителей
"""

import discord
from discord.ext import commands
import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ChannelProtectionSystem:
    def __init__(self, bot):
        self.bot = bot
        self.protected_channels = {}  # ID канала -> данные канала
        self.deleted_channels = {}    # ID канала -> данные для восстановления
        self.punished_users = {}      # ID пользователя -> время наказания
        self.backup_file = "channel_backups.json"
        self.ignored_category_ids = [1386751637330071695, 1383385103178268672]  # Категории, которые игнорируются защитой
        self.load_backups()
        
    def load_backups(self):
        """Загружает резервные копии каналов из файла"""
        try:
            with open(self.backup_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.protected_channels = data.get('protected_channels', {})
                logger.info(f"Загружено {len(self.protected_channels)} защищенных каналов")
        except FileNotFoundError:
            logger.info("Файл резервных копий не найден, создаем новый")
            self.save_backups()
        except Exception as e:
            logger.error(f"Ошибка загрузки резервных копий: {e}")
    
    def save_backups(self):
        """Сохраняет резервные копии каналов в файл"""
        try:
            data = {
                'protected_channels': self.protected_channels,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения резервных копий: {e}")
    
    async def backup_channel(self, channel: discord.TextChannel):
        """Создает резервную копию канала"""
        try:
            # Получаем последние сообщения (до 100)
            messages = []
            async for message in channel.history(limit=100):
                messages.append({
                    'author_id': message.author.id,
                    'author_name': message.author.name,
                    'content': message.content,
                    'timestamp': message.created_at.isoformat(),
                    'attachments': [att.url for att in message.attachments],
                    'embeds': [embed.to_dict() for embed in message.embeds]
                })
            
            # Сохраняем данные канала
            channel_data = {
                'name': channel.name,
                'topic': channel.topic,
                'position': channel.position,
                'category_id': channel.category.id if channel.category else None,
                'overwrites': {str(target.id): overwrite._values for target, overwrite in channel.overwrites.items()},
                'slowmode_delay': channel.slowmode_delay,
                'nsfw': channel.nsfw,
                'messages': messages,
                'backup_time': datetime.now().isoformat()
            }
            
            self.protected_channels[str(channel.id)] = channel_data
            self.save_backups()
            logger.info(f"Создана резервная копия канала {channel.name} (ID: {channel.id})")
            
        except Exception as e:
            logger.error(f"Ошибка создания резервной копии канала {channel.name}: {e}")
    
    async def restore_channel(self, guild: discord.Guild, channel_id: str) -> Optional[discord.TextChannel]:
        """Восстанавливает канал из резервной копии"""
        try:
            if channel_id not in self.protected_channels:
                logger.error(f"Резервная копия канала {channel_id} не найдена")
                return None
            
            channel_data = self.protected_channels[channel_id]
            
            # Создаем канал
            overwrites = {}
            for target_id, overwrite_data in channel_data['overwrites'].items():
                target = guild.get_member(int(target_id)) or guild.get_role(int(target_id))
                if target:
                    overwrites[target] = discord.PermissionOverwrite(**overwrite_data)
            
            category = None
            if channel_data['category_id']:
                category = guild.get_channel(channel_data['category_id'])
            
            restored_channel = await guild.create_text_channel(
                name=channel_data['name'],
                topic=channel_data['topic'],
                position=channel_data['position'],
                category=category,
                overwrites=overwrites,
                slowmode_delay=channel_data['slowmode_delay'],
                nsfw=channel_data['nsfw']
            )
            
            # Восстанавливаем сообщения
            await self.restore_messages(restored_channel, channel_data['messages'])
            
            logger.info(f"Канал {restored_channel.name} успешно восстановлен")
            return restored_channel
            
        except Exception as e:
            logger.error(f"Ошибка восстановления канала {channel_id}: {e}")
            return None
    
    async def restore_messages(self, channel: discord.TextChannel, messages: List[Dict]):
        """Восстанавливает сообщения в канале"""
        try:
            # Восстанавливаем сообщения в обратном порядке (от старых к новым)
            for message_data in reversed(messages):
                try:
                    # Создаем эмбед с информацией о восстановленном сообщении
                    embed = discord.Embed(
                        title="🔄 Восстановленное сообщение",
                        description=message_data['content'],
                        color=0x00ff00,
                        timestamp=datetime.fromisoformat(message_data['timestamp'])
                    )
                    embed.set_author(
                        name=f"Автор: {message_data['author_name']}",
                        icon_url="https://cdn.discordapp.com/emojis/✅.png"
                    )
                    
                    if message_data['attachments']:
                        embed.add_field(
                            name="📎 Вложения",
                            value=f"Количество: {len(message_data['attachments'])}",
                            inline=True
                        )
                    
                    if message_data['embeds']:
                        embed.add_field(
                            name="🔗 Эмбеды",
                            value=f"Количество: {len(message_data['embeds'])}",
                            inline=True
                        )
                    
                    await channel.send(embed=embed)
                    
                    # Небольшая задержка между сообщениями
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Ошибка восстановления сообщения: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Ошибка восстановления сообщений в канале {channel.name}: {e}")
    
    async def punish_user(self, user: discord.Member, reason: str):
        """Наказывает пользователя за удаление канала"""
        try:
            # Сохраняем текущие роли пользователя
            original_roles = [role.id for role in user.roles if role.name != "@everyone"]
            
            # Удаляем все роли (кроме @everyone)
            roles_to_remove = [role for role in user.roles if role.name != "@everyone"]
            if roles_to_remove:
                await user.remove_roles(*roles_to_remove, reason=f"Наказание за удаление канала: {reason}")
            
            # Записываем информацию о наказании
            punishment_end = datetime.now() + timedelta(hours=2)
            self.punished_users[user.id] = {
                'original_roles': original_roles,
                'punishment_end': punishment_end.isoformat(),
                'reason': reason
            }
            
            # Отправляем уведомление
            embed = discord.Embed(
                title="🚫 Наказание за удаление канала",
                description=f"Пользователь {user.mention} наказан за удаление защищенного канала",
                color=0xff0000
            )
            embed.add_field(name="Причина", value=reason, inline=False)
            embed.add_field(name="Длительность", value="2 часа", inline=True)
            embed.add_field(name="Действие", value="Удаление всех ролей", inline=True)
            embed.add_field(name="Восстановление", value=f"<t:{int(punishment_end.timestamp())}:R>", inline=False)
            
            # Отправляем в системный канал
            system_channel = user.guild.system_channel
            if system_channel:
                await system_channel.send(embed=embed)
            
            logger.info(f"Пользователь {user.name} наказан за удаление канала")
            
        except Exception as e:
            logger.error(f"Ошибка наказания пользователя {user.name}: {e}")
    
    async def restore_user_roles(self, user: discord.Member):
        """Восстанавливает роли пользователя после наказания"""
        try:
            if user.id not in self.punished_users:
                return
            
            punishment_data = self.punished_users[user.id]
            original_roles = punishment_data['original_roles']
            
            # Восстанавливаем роли
            roles_to_add = []
            for role_id in original_roles:
                role = user.guild.get_role(role_id)
                if role and role not in user.roles:
                    roles_to_add.append(role)
            
            if roles_to_add:
                await user.add_roles(*roles_to_add, reason="Восстановление ролей после наказания")
            
            # Удаляем из списка наказанных
            del self.punished_users[user.id]
            
            # Отправляем уведомление
            embed = discord.Embed(
                title="✅ Роли восстановлены",
                description=f"Роли пользователя {user.mention} восстановлены",
                color=0x00ff00
            )
            
            system_channel = user.guild.system_channel
            if system_channel:
                await system_channel.send(embed=embed)
            
            logger.info(f"Роли пользователя {user.name} восстановлены")
            
        except Exception as e:
            logger.error(f"Ошибка восстановления ролей пользователя {user.name}: {e}")
    
    async def check_punishments(self):
        """Проверяет и восстанавливает роли пользователей после наказания"""
        while True:
            try:
                current_time = datetime.now()
                users_to_restore = []
                
                for user_id, punishment_data in self.punished_users.items():
                    punishment_end = datetime.fromisoformat(punishment_data['punishment_end'])
                    if current_time >= punishment_end:
                        users_to_restore.append(user_id)
                
                for user_id in users_to_restore:
                    guild = self.bot.get_guild(1375772175373566012)  # ID вашего сервера
                    if guild:
                        user = guild.get_member(user_id)
                        if user:
                            await self.restore_user_roles(user)
                
                # Проверяем каждые 5 минут
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Ошибка проверки наказаний: {e}")
                await asyncio.sleep(60)
    
    async def setup_protection(self):
        """Настраивает систему защиты"""
        try:
            # Создаем резервные копии всех важных каналов
            guild = self.bot.get_guild(1375772175373566012)  # ID вашего сервера
            if not guild:
                logger.error("Сервер не найден")
                return
            
            important_channels = [
                1385303735281914011,  # Канал приветствий
                1375826419158089751,  # Канал поддержки
                1375818535141376030,  # Заявки в Minecraft администрацию
                1375818773994537001,  # Заявки в Discord администрацию
                1383490270850584707,  # Канал верификации
                # Добавьте другие важные каналы
            ]
            
            for channel_id in important_channels:
                channel = guild.get_channel(channel_id)
                if channel:
                    await self.backup_channel(channel)
            
            # Запускаем проверку наказаний
            asyncio.create_task(self.check_punishments())
            
            logger.info("Система защиты каналов настроена")
            
        except Exception as e:
            logger.error(f"Ошибка настройки системы защиты: {e}")

async def setup_channel_protection(bot):
    """Функция для настройки системы защиты каналов"""
    try:
        protection_system = ChannelProtectionSystem(bot)
        bot.channel_protection = protection_system
        
        @bot.event
        async def on_guild_channel_delete(channel):
            """Событие удаления канала"""
            try:
                # Исключаем каналы из игнорируемых категорий
                if channel.category_id in protection_system.ignored_category_ids:
                    logger.info(f"Канал {channel.name} (ID: {channel.id}) был в игнорируемой категории, защита не применяется.")
                    return
                # Проверяем, является ли канал защищенным
                if str(channel.id) in protection_system.protected_channels:
                    logger.warning(f"🚨 УДАЛЕН ЗАЩИЩЕННЫЙ КАНАЛ: {channel.name} (ID: {channel.id})")
                    # Определяем, кто удалил канал
                    async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
                        if entry.target.id == channel.id:
                            user = entry.user
                            reason = f"Удаление защищенного канала {channel.name}"
                            # Наказываем пользователя
                            await protection_system.punish_user(user, reason)
                            # Восстанавливаем канал
                            restored_channel = await protection_system.restore_channel(channel.guild, str(channel.id))
                            if restored_channel:
                                # Отправляем уведомление о восстановлении
                                embed = discord.Embed(
                                    title="🛡️ Канал восстановлен",
                                    description=f"Защищенный канал {restored_channel.mention} был автоматически восстановлен",
                                    color=0x00ff00
                                )
                                embed.add_field(name="Удален пользователем", value=user.mention, inline=True)
                                embed.add_field(name="Время", value=f"<t:{int(datetime.now().timestamp())}:F>", inline=True)
                                system_channel = channel.guild.system_channel
                                if system_channel:
                                    await system_channel.send(embed=embed)
                            break
            except Exception as e:
                logger.error(f"Ошибка обработки удаления канала: {e}")
        
        # Настраиваем систему защиты
        await protection_system.setup_protection()
        
        logger.info("Система защиты каналов загружена")
        
    except Exception as e:
        logger.error(f"Ошибка загрузки системы защиты каналов: {e}") 