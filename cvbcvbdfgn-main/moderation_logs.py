"""
Система логирования действий модераторов
Логирует все действия модераторов в специальный канал
"""

import discord
from discord.ext import commands
import logging
from datetime import datetime
import json
import os
from typing import Optional, List, Dict
import asyncio

logger = logging.getLogger(__name__)

# Константы для исключительных ролей
EXEMPT_LOAD_ROLES = [1385306542781497425]  # Роли без ограничений нагрузки
EXEMPT_RESTORE_ROLES = [1385306542781497425]  # Роли без восстановления сообщений

class ModerationLogs:
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1376194575281950741
        self.log_channel = None
        self.enabled = True
        self.message_backup = {}  # Хранилище удаленных сообщений
        self.backup_enabled = True  # Включение/выключение восстановления
        self.pending_reasons = {}  # {moderator_id: asyncio.Task}
        self.pending_log_messages = {}  # {moderator_id: log_message_id}
        
    async def setup_logging(self):
        """Настройка системы логирования"""
        try:
            self.log_channel = self.bot.get_channel(self.log_channel_id)
            if not self.log_channel:
                logger.error(f"Канал логирования не найден: {self.log_channel_id}")
                return False
            
            logger.info(f"Система логирования настроена: {self.log_channel.name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка настройки логирования: {e}")
            return False
    
    async def log_action(self, action_type: str, moderator: discord.Member, target: Optional[discord.Member] = None, 
                        details: str = "", channel: Optional[discord.TextChannel] = None, 
                        reason: str = "", duration: str = "", roles: Optional[List[discord.Role]] = None,
                        permissions: Optional[Dict] = None, old_value: str = "", new_value: str = "",
                        message_content: str = "", emoji_name: str = ""):
        """Логирует действие модератора с улучшенным дизайном"""
        if not self.enabled or not self.log_channel:
            return
        
        try:
            # Исправление типов для roles и permissions
            if roles is None:
                roles = []
            if permissions is None:
                permissions = {}
            
            # Создаем красивый embed для лога
            embed = discord.Embed(
                title=f"🛡️ {action_type}",
                description=f"**Модератор:** {moderator.mention} ({moderator.name}#{moderator.discriminator})",
                color=self._get_action_color(action_type),
                timestamp=datetime.utcnow()
            )
            
            # Добавляем аватар модератора
            if hasattr(moderator, 'display_avatar') and moderator.display_avatar:
                embed.set_thumbnail(url=moderator.display_avatar.url)
            
            # Добавляем информацию о цели действия
            if target:
                target_info = f"{target.mention} ({getattr(target, 'name', '—')}#{getattr(target, 'discriminator', '—')})\nID: {getattr(target, 'id', '—')}"
                embed.add_field(
                    name="👤 Цель",
                    value=target_info,
                    inline=True
                )
            
            # Добавляем канал, если указан
            if channel:
                channel_name = getattr(channel, 'name', None)
                if channel_name is None:
                    # Если это ЛС или неизвестный тип, пишем 'Direct Message'
                    channel_name = 'Direct Message'
                channel_value = channel.mention if hasattr(channel, 'mention') else channel_name
                embed.add_field(
                    name="📺 Канал",
                    value=channel_value,
                    inline=True
                )
            
            # Добавляем причину
            if reason:
                embed.add_field(
                    name="📝 Причина",
                    value=f"```{reason}```",
                    inline=False
                )
            
            # Добавляем длительность
            if duration:
                embed.add_field(
                    name="⏰ Длительность",
                    value=f"`{duration}`",
                    inline=True
                )
            
            # Добавляем роли
            if roles:
                roles_text = ", ".join([role.mention for role in roles])
                embed.add_field(
                    name="🎭 Роли",
                    value=roles_text,
                    inline=False
                )
            
            # Добавляем изменения прав
            if permissions:
                perms_text = ""
                for perm, value in permissions.items():
                    perms_text += f"• {perm}: {'✅' if value else '❌'}\n"
                embed.add_field(
                    name="🔐 Права",
                    value=f"```{perms_text}```",
                    inline=False
                )
            
            # Добавляем изменения значений
            if old_value and new_value:
                embed.add_field(
                    name="🔄 Изменения",
                    value=f"**Было:** `{old_value}`\n**Стало:** `{new_value}`",
                    inline=False
                )
            
            # Добавляем содержимое сообщения
            if message_content:
                # Обрезаем длинные сообщения
                if len(message_content) > 1000:
                    message_content = message_content[:997] + "..."
                embed.add_field(
                    name="💬 Содержимое сообщения",
                    value=f"```{message_content}```",
                    inline=False
                )
            
            # Добавляем информацию об эмодзи
            if emoji_name:
                embed.add_field(
                    name="😀 Эмодзи",
                    value=f"`{emoji_name}`",
                    inline=True
                )
            
            # Добавляем дополнительные детали
            if details:
                embed.add_field(
                    name="📋 Детали",
                    value=f"```{details}```",
                    inline=False
                )
            
            # Добавляем ID участников для справки
            footer_text = f"🆔 Модератор: {moderator.id}"
            if target:
                footer_text += f" | Цель: {target.id}"
            embed.set_footer(text=footer_text, icon_url="https://cdn.discordapp.com/emojis/1234567890.png")
            
            log_message = await self.log_channel.send(embed=embed)
            
            # Проверяем, что модератор — человек, а не бот, и не сам бот
            is_human = hasattr(moderator, 'bot') and not moderator.bot and moderator.id != self.bot.user.id
            # Если причина не указана или явно 'Причина не указана', и модератор — человек, запрашиваем причину
            if (not reason or reason.strip().lower() == "причина не указана") and is_human:
                # Сохраняем ID лог-сообщения для последующего редактирования
                self.pending_log_messages[moderator.id] = log_message.id
                # Отправляем запрос причины ТОЛЬКО модератору, который выполнил действие
                await self._ask_reason(action_type, moderator, target)
            
        except Exception as e:
            logger.error(f"Ошибка логирования действия {action_type}: {e}")
    
    def _get_action_color(self, action_type: str) -> int:
        """Возвращает цвет для типа действия"""
        colors = {
            "Мут": 0xff0000,      # Красный
            "Размут": 0x00ff00,   # Зеленый
            "Бан": 0x8b0000,      # Темно-красный
            "Разбан": 0x00ff00,   # Зеленый
            "Кик": 0xff8c00,      # Оранжевый
            "Удаление сообщения": 0xff0000,  # Красный
            "Редактирование сообщения": 0x0099ff,  # Синий
            "Восстановление сообщения": 0x00ff00,  # Зеленый
            "Удаление канала": 0xff0000,     # Красный
            "Создание канала": 0x00ff00,     # Зеленый
            "Изменение ролей": 0x0099ff,     # Синий
            "Изменение прав роли": 0x0099ff, # Синий
            "Изменение прав канала": 0x0099ff, # Синий
            "Удаление стикера": 0xff0000,    # Красный
            "Удаление эмодзи": 0xff0000,     # Красный
            "Удаление реакции": 0xff0000,    # Красный
            "Изменение никнейма": 0x0099ff,  # Синий
            "Изменение аватара": 0x0099ff,   # Синий
            "Выход из сервера": 0xff8c00,    # Оранжевый
            "Подключение к голосовому": 0x00ff00,  # Зеленый
            "Отключение от голосового": 0xff8c00,  # Оранжевый
            "Изменение статуса": 0x0099ff,   # Синий
            "Изменение настроек сервера": 0x0099ff, # Синий
            "Другое": 0x808080    # Серый
        }
        return colors.get(action_type, colors["Другое"])
    
    async def backup_message(self, message: discord.Message):
        """Сохраняет сообщение для возможного восстановления"""
        if not self.backup_enabled:
            return
            
        try:
            # Безопасное получение имени канала
            channel_name = getattr(message.channel, 'name', None)
            if channel_name is None:
                # Если это DMChannel или другой тип без имени
                if isinstance(message.channel, discord.DMChannel):
                    channel_name = f"DM с {message.channel.recipient.name if message.channel.recipient else 'Unknown'}"
                elif isinstance(message.channel, discord.GroupChannel):
                    channel_name = f"Группа: {getattr(message.channel, 'name', 'Unknown')}"
                else:
                    channel_name = "Unknown Channel"
            
            backup_data = {
                'content': message.content,
                'author_id': message.author.id,
                'author_name': message.author.name,
                'channel_id': message.channel.id,
                'channel_name': channel_name,
                'timestamp': message.created_at.isoformat(),
                'attachments': [att.url for att in message.attachments],
                'embeds': [embed.to_dict() for embed in message.embeds],
                'mentions': [user.id for user in message.mentions],
                'role_mentions': [role.id for role in message.role_mentions]
            }
            
            self.message_backup[message.id] = backup_data
            
            # Ограничиваем размер хранилища (максимум 1000 сообщений)
            if len(self.message_backup) > 1000:
                oldest_key = min(self.message_backup.keys())
                del self.message_backup[oldest_key]
                
        except Exception as e:
            logger.error(f"Ошибка резервного копирования сообщения: {e}")
    
    async def restore_message(self, message_id: int, channel: discord.TextChannel):
        """Восстанавливает удаленное сообщение с улучшенным дизайном"""
        if not self.backup_enabled or message_id not in self.message_backup:
            return False
            
        try:
            backup_data = self.message_backup[message_id]
            
            # Создаем красивый embed для восстановленного сообщения
            embed = discord.Embed(
                title="🔄 Восстановленное сообщение",
                description=backup_data['content'],
                color=0x00ff00,
                timestamp=datetime.fromisoformat(backup_data['timestamp'])
            )
            
            embed.add_field(
                name="👤 Автор",
                value=f"<@{backup_data['author_id']}> ({backup_data['author_name']})",
                inline=True
            )
            
            embed.add_field(
                name="📺 Канал",
                value=f"#{backup_data['channel_name']}",
                inline=True
            )
            
            if backup_data['attachments']:
                embed.add_field(
                    name="📎 Вложения",
                    value=f"Количество: {len(backup_data['attachments'])}",
                    inline=True
                )
            
            embed.set_footer(text=f"🆔 ID сообщения: {message_id} • Восстановлено автоматически", 
                           icon_url="https://cdn.discordapp.com/emojis/1234567890.png")
            
            await channel.send(embed=embed)
            
            # Удаляем из резервной копии
            del self.message_backup[message_id]
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка восстановления сообщения: {e}")
            return False

    async def _ask_reason(self, action_type, moderator, target):
        # Не отправлять повторно, если уже ждем причину
        if moderator.id in self.pending_reasons:
            return
        try:
            # Формируем подробную информацию о цели
            if target:
                target_info = f"{target.mention} ({getattr(target, 'name', '—')}#{getattr(target, 'discriminator', '—')})\nID: {getattr(target, 'id', '—')}"
            else:
                target_info = '—'
            embed = discord.Embed(
                title="🚨 Требуется причина модераторского действия!",
                description=(
                    f"**Вы только что выполнили действие:**\n"
                    f"`{action_type}`\n"
                    f"\n"
                    f"**Цель:** {target_info}\n"
                    f"\n"
                    f"**Пожалуйста, укажите причину этого действия.**\n"
                    f"\n"
                    f"Отправьте причину в ответном сообщении **в течение 3 минут**.\n"
                    f"Если причина не будет указана, действие будет отменено!"
                ),
                color=0xff5555
            )
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/463/463612.png")
            embed.set_footer(text="Ответьте на это сообщение причиной. Не игнорируйте! 📝")
            await moderator.send(embed=embed)
        except Exception:
            return  # Не удалось отправить ЛС (например, закрыты ЛС)
        # Запускаем задачу ожидания причины
        task = asyncio.create_task(self._wait_for_reason(moderator, target, action_type))
        self.pending_reasons[moderator.id] = task

    async def _wait_for_reason(self, moderator, target, action_type):
        def check(msg):
            return (
                msg.author.id == moderator.id and isinstance(msg.channel, discord.DMChannel)
            )
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=180)
            reason = msg.content.strip()
            await moderator.send(f"Спасибо! Причина зафиксирована: {reason}")
            log_message_id = self.pending_log_messages.get(moderator.id)
            if log_message_id and self.log_channel:
                try:
                    log_message = await self.log_channel.fetch_message(log_message_id)
                    embed = log_message.embeds[0]
                    new_embed = discord.Embed.from_dict(embed.to_dict())
                    found = False
                    for i, field in enumerate(new_embed.fields):
                        if field.name == "📝 Причина":
                            new_embed.set_field_at(i, name="📝 Причина", value=f"```{reason}```", inline=field.inline)
                            found = True
                            break
                    if not found:
                        new_embed.add_field(name="📝 Причина", value=f"```{reason}```", inline=False)
                    await log_message.edit(embed=new_embed)
                except Exception as e:
                    await moderator.send(f"Не удалось обновить причину в логах: {e}")
            self.pending_log_messages.pop(moderator.id, None)
        except asyncio.TimeoutError:
            await moderator.send("⏰ Время вышло! Действие будет отменено.")
            # Передаю все возможные параметры для отката
            await self._revert_action(action_type, moderator, target, **self._collect_revert_kwargs(action_type, moderator, target))
            self.pending_log_messages.pop(moderator.id, None)
        finally:
            self.pending_reasons.pop(moderator.id, None)

    def _collect_revert_kwargs(self, action_type, moderator, target):
        # Собирает дополнительные параметры для отката (roles, channel, old_value и т.д.)
        # Можно доработать под нужды каждого действия
        kwargs = {}
        if target:
            kwargs['target_id'] = getattr(target, 'id', None)
            if hasattr(target, 'guild'):
                kwargs['guild'] = target.guild
        # Для ролей
        if hasattr(target, 'roles'):
            kwargs['roles'] = [role for role in getattr(target, 'roles', []) if role.name != '@everyone']
        # Для каналов
        if hasattr(target, 'channel'):
            kwargs['channel'] = getattr(target, 'channel', None)
        # Для старого значения (например, никнейм)
        if hasattr(target, 'old_value'):
            kwargs['old_value'] = getattr(target, 'old_value', None)
        return kwargs

    async def _revert_action(self, action_type, moderator, target, **kwargs):
        try:
            guild = None
            if target and hasattr(target, 'guild'):
                guild = target.guild
            elif 'guild' in kwargs:
                guild = kwargs['guild']
            # Получаем ID цели
            target_id = getattr(target, 'id', None) or kwargs.get('target_id')
            # Откат действий
            if action_type == "Бан":
                if guild and target_id:
                    try:
                        await guild.unban(discord.Object(id=target_id), reason="Действие отменено: причина не указана")
                        await moderator.send(f"✅ Пользователь с ID {target_id} был разбанен (откат бана).")
                    except Exception as e:
                        await moderator.send(f"❌ Не удалось разбанить пользователя: {e}")
                else:
                    await moderator.send("❌ Не удалось определить сервер или ID для разбана.")
            elif action_type == "Разбан":
                # Откат разбана невозможен
                await moderator.send("❌ Откат разбана невозможен.")
            elif action_type == "Мут":
                if guild and target_id:
                    try:
                        member = guild.get_member(target_id)
                        if not member:
                            member = await guild.fetch_member(target_id)
                        muted_role = discord.utils.get(guild.roles, name="Muted")
                        if muted_role and member and muted_role in member.roles:
                            await member.remove_roles(muted_role, reason="Действие отменено: причина не указана")
                            await moderator.send(f"✅ Мут снят с пользователя {member.mention} (откат мута).")
                        else:
                            await moderator.send("❌ Не удалось найти роль Muted или пользователя.")
                    except Exception as e:
                        await moderator.send(f"❌ Не удалось снять мут: {e}")
                else:
                    await moderator.send("❌ Не удалось определить сервер или ID для снятия мута.")
            elif action_type == "Размут":
                # Откат размута невозможен
                await moderator.send("❌ Откат размута невозможен.")
            elif action_type == "Кик":
                # Кика нельзя откатить
                await moderator.send("❌ Откат кика невозможен (Discord не поддерживает возврат кика).")
            elif action_type in ["Добавление ролей", "Снятие ролей"]:
                if guild and target_id and 'roles' in kwargs:
                    try:
                        member = guild.get_member(target_id)
                        if not member:
                            member = await guild.fetch_member(target_id)
                        roles = kwargs['roles']
                        if action_type == "Добавление ролей":
                            await member.remove_roles(*roles, reason="Действие отменено: причина не указана")
                            await moderator.send(f"✅ Роли удалены у пользователя {member.mention} (откат добавления ролей).")
                        else:
                            await member.add_roles(*roles, reason="Действие отменено: причина не указана")
                            await moderator.send(f"✅ Роли возвращены пользователю {member.mention} (откат снятия ролей).")
                    except Exception as e:
                        await moderator.send(f"❌ Не удалось откатить роли: {e}")
                else:
                    await moderator.send("❌ Не удалось определить пользователя или роли для отката.")
            elif action_type in ["Создание роли", "Удаление роли", "Изменение роли", "Изменение прав роли"]:
                await moderator.send("❌ Откат действий с ролями невозможен через Discord API. Обратитесь к администрации.")
            elif action_type == "Создание канала":
                if guild and 'channel' in kwargs:
                    try:
                        channel = kwargs['channel']
                        await channel.delete(reason="Действие отменено: причина не указана")
                        await moderator.send(f"✅ Канал {channel.name} удалён (откат создания канала).")
                    except Exception as e:
                        await moderator.send(f"❌ Не удалось удалить канал: {e}")
                else:
                    await moderator.send("❌ Не удалось определить канал для удаления.")
            elif action_type == "Удаление канала":
                await moderator.send("❌ Откат удаления канала невозможен через Discord API. Обратитесь к администрации.")
            elif action_type == "Изменение канала":
                await moderator.send("❌ Откат изменений канала невозможен через Discord API. Обратитесь к администрации.")
            elif action_type == "Изменение никнейма":
                if guild and target_id and 'old_value' in kwargs:
                    try:
                        member = guild.get_member(target_id)
                        if not member:
                            member = await guild.fetch_member(target_id)
                        await member.edit(nick=kwargs['old_value'], reason="Действие отменено: причина не указана")
                        await moderator.send(f"✅ Никнейм пользователя {member.mention} восстановлен.")
                    except Exception as e:
                        await moderator.send(f"❌ Не удалось восстановить никнейм: {e}")
                else:
                    await moderator.send("❌ Не удалось определить пользователя или старый ник для отката.")
            elif action_type in ["Удаление сообщения", "Редактирование сообщения"]:
                await moderator.send("❌ Откат удаления или редактирования сообщения невозможен через Discord API.")
            elif action_type in ["Добавление эмодзи", "Удаление эмодзи", "Добавление стикера", "Удаление стикера"]:
                await moderator.send("❌ Откат действий с эмодзи/стикерами невозможен через Discord API.")
            elif action_type == "Изменение настроек сервера":
                await moderator.send("❌ Откат изменений настроек сервера невозможен через Discord API.")
            else:
                await moderator.send(f"❌ Откат действия '{action_type}' не реализован. Обратитесь к администрации.")
        except Exception as e:
            await moderator.send(f"❌ Ошибка при откате действия: {e}")

async def setup_moderation_logs(bot):
    """Функция для настройки системы логирования"""
    try:
        logs_system = ModerationLogs(bot)
        bot.moderation_logs = logs_system
        
        # Настраиваем систему
        await logs_system.setup_logging()
        
        # Устанавливаем обработчики событий
        await setup_log_handlers(bot, logs_system)
        
        logger.info("Система логирования модерации настроена")
        
    except Exception as e:
        logger.error(f"Ошибка настройки системы логирования: {e}")

async def setup_log_handlers(bot, logs_system):
    """Устанавливает обработчики событий для логирования"""
    
    @bot.event
    async def on_member_ban(guild, user):
        """Логирует бан участника"""
        try:
            async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
                if entry.target.id == user.id:
                    await logs_system.log_action(
                        action_type="Бан",
                        moderator=entry.user,
                        target=user,
                        reason=entry.reason or "Причина не указана"
                    )
                    break
        except Exception as e:
            logger.error(f"Ошибка логирования бана: {e}")
    
    @bot.event
    async def on_member_unban(guild, user):
        """Логирует разбан участника"""
        try:
            async for entry in guild.audit_logs(action=discord.AuditLogAction.unban, limit=1):
                if entry.target.id == user.id:
                    await logs_system.log_action(
                        action_type="Разбан",
                        moderator=entry.user,
                        target=user,
                        reason=entry.reason or "Причина не указана"
                    )
                    break
        except Exception as e:
            logger.error(f"Ошибка логирования разбана: {e}")
    
    @bot.event
    async def on_member_remove(member):
        """Логирует кик участника"""
        try:
            async for entry in member.guild.audit_logs(action=discord.AuditLogAction.kick, limit=1):
                if entry.target.id == member.id:
                    await logs_system.log_action(
                        action_type="Кик",
                        moderator=entry.user,
                        target=member,
                        reason=entry.reason or "Причина не указана"
                    )
                    break
        except Exception as e:
            logger.error(f"Ошибка логирования кика: {e}")
    
    @bot.event
    async def on_member_update(before, after):
        """Логирует изменения участника"""
        try:
            # Изменение ролей
            if before.roles != after.roles:
                added_roles = set(after.roles) - set(before.roles)
                removed_roles = set(before.roles) - set(after.roles)
                
                async for entry in before.guild.audit_logs(action=discord.AuditLogAction.member_role_update, limit=1):
                    if entry.target.id == after.id:
                        if added_roles:
                            await logs_system.log_action(
                                action_type="Добавление ролей",
                                moderator=entry.user,
                                target=after,
                                roles=list(added_roles),
                                reason=entry.reason or "Причина не указана"
                            )
                        if removed_roles:
                            await logs_system.log_action(
                                action_type="Снятие ролей",
                                moderator=entry.user,
                                target=after,
                                roles=list(removed_roles),
                                reason=entry.reason or "Причина не указана"
                            )
                        break
            
            # Изменение никнейма
            if before.nick != after.nick:
                async for entry in before.guild.audit_logs(action=discord.AuditLogAction.member_update, limit=1):
                    if entry.target.id == after.id:
                        await logs_system.log_action(
                            action_type="Изменение никнейма",
                            moderator=entry.user,
                            target=after,
                            old_value=before.nick or "Нет",
                            new_value=after.nick or "Нет",
                            reason=entry.reason or "Причина не указана"
                        )
                        break
                        
        except Exception as e:
            logger.error(f"Ошибка логирования изменения участника: {e}")
    
    @bot.event
    async def on_guild_channel_delete(channel):
        """Логирует удаление канала"""
        try:
            async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
                if entry.target.id == channel.id:
                    await logs_system.log_action(
                        action_type="Удаление канала",
                        moderator=entry.user,
                        channel=channel,
                        details=f"Канал: {channel.name}",
                        reason=entry.reason or "Причина не указана"
                    )
                    break
        except Exception as e:
            logger.error(f"Ошибка логирования удаления канала: {e}")
    
    @bot.event
    async def on_guild_channel_create(channel):
        """Логирует создание канала"""
        try:
            async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1):
                if entry.target.id == channel.id:
                    await logs_system.log_action(
                        action_type="Создание канала",
                        moderator=entry.user,
                        channel=channel,
                        details=f"Канал: {channel.name}",
                        reason=entry.reason or "Причина не указана"
                    )
                    break
        except Exception as e:
            logger.error(f"Ошибка логирования создания канала: {e}")
    
    @bot.event
    async def on_guild_channel_update(before, after):
        """Логирует изменения канала"""
        try:
            async for entry in before.guild.audit_logs(action=discord.AuditLogAction.channel_update, limit=1):
                if entry.target.id == after.id:
                    changes = []
                    
                    # Изменение имени
                    if before.name != after.name:
                        changes.append(f"Имя: {before.name} → {after.name}")
                    
                    # Изменение темы
                    if hasattr(before, 'topic') and hasattr(after, 'topic') and before.topic != after.topic:
                        changes.append("Тема изменена")
                    
                    # Изменение прав
                    if hasattr(before, 'overwrites') and hasattr(after, 'overwrites') and before.overwrites != after.overwrites:
                        changes.append("Права канала изменены")
                    
                    if changes:
                        await logs_system.log_action(
                            action_type="Изменение канала",
                            moderator=entry.user,
                            channel=after,
                            details=f"Канал: {after.name}\nИзменения: {'; '.join(changes)}",
                            reason=entry.reason or "Причина не указана"
                        )
                    break
        except Exception as e:
            logger.error(f"Ошибка логирования изменения канала: {e}")
    
    @bot.event
    async def on_message(message):
        """Резервное копирование сообщений"""
        # Пропускаем сообщения ботов и сообщения в ЛС
        if message.author.bot or isinstance(message.channel, discord.DMChannel):
            return
        
        # Делаем бэкап только сообщений в серверных каналах
        await logs_system.backup_message(message)
    
    @bot.event
    async def on_message_edit(before, after):
        """Логирует редактирование сообщений"""
        try:
            # Пропускаем сообщения ботов, ЛС и если содержимое не изменилось
            if (before.author.bot or 
                isinstance(before.channel, discord.DMChannel) or 
                before.content == after.content):
                return
            
            async for entry in before.guild.audit_logs(action=discord.AuditLogAction.message_delete, limit=1):
                if entry.target.id == before.author.id:
                    await logs_system.log_action(
                        action_type="Редактирование сообщения",
                        moderator=entry.user,
                        target=before.author,
                        channel=before.channel,
                        old_value=before.content,
                        new_value=after.content,
                        message_content=f"Было: {before.content}\nСтало: {after.content}",
                        reason=entry.reason or "Причина не указана"
                    )
                    break
        except Exception as e:
            logger.error(f"Ошибка логирования редактирования сообщения: {e}")
    
    @bot.event
    async def on_message_delete(message):
        """Логирует удаление сообщения и восстанавливает его"""
        try:
            # Пропускаем сообщения ботов и ЛС
            if message.author.bot or isinstance(message.channel, discord.DMChannel):
                return
            
            # Проверяем исключения для специальных ролей
            if any(role.id in EXEMPT_RESTORE_ROLES for role in message.author.roles):
                logger.info(f"Пропускаем восстановление сообщения для пользователя {message.author.name} с исключительной ролью")
                return
            
            # Логируем удаление
            async for entry in message.guild.audit_logs(action=discord.AuditLogAction.message_delete, limit=1):
                if entry.target.id == message.author.id:
                    await logs_system.log_action(
                        action_type="Удаление сообщения",
                        moderator=entry.user,
                        target=message.author,
                        channel=message.channel,
                        message_content=message.content,
                        reason=entry.reason or "Причина не указана"
                    )
                    break
            
            # Восстанавливаем сообщение
            await asyncio.sleep(1)  # Небольшая задержка
            restored = await logs_system.restore_message(message.id, message.channel)
            
            if restored:
                await logs_system.log_action(
                    action_type="Восстановление сообщения",
                    moderator=bot.user,
                    target=message.author,
                    channel=message.channel,
                    details="Сообщение автоматически восстановлено"
                )
                
        except Exception as e:
            logger.error(f"Ошибка обработки удаления сообщения: {e}")
    
    @bot.event
    async def on_raw_reaction_remove(payload):
        """Логирует удаление реакций (эмодзи под сообщениями)"""
        try:
            guild = bot.get_guild(payload.guild_id)
            if not guild:
                return
            
            channel = guild.get_channel(payload.channel_id)
            if not channel:
                return
            
            async for entry in guild.audit_logs(action=discord.AuditLogAction.message_delete, limit=1):
                # Проверяем, что это удаление реакции
                if hasattr(entry, 'extra') and hasattr(entry.extra, 'emoji'):
                    await logs_system.log_action(
                        action_type="Удаление реакции",
                        moderator=entry.user,
                        channel=channel,
                        emoji_name=payload.emoji.name,
                        details=f"Эмодзи: {payload.emoji.name} удален из сообщения",
                        reason=entry.reason or "Причина не указана"
                    )
                    break
        except Exception as e:
            logger.error(f"Ошибка логирования удаления реакции: {e}")
    
    @bot.event
    async def on_guild_emojis_update(guild, before, after):
        """Логирует изменения эмодзи"""
        try:
            added_emojis = set(after) - set(before)
            removed_emojis = set(before) - set(after)
            
            async for entry in guild.audit_logs(action=discord.AuditLogAction.emoji_create, limit=1):
                if added_emojis:
                    await logs_system.log_action(
                        action_type="Добавление эмодзи",
                        moderator=entry.user,
                        details=f"Эмодзи: {', '.join([emoji.name for emoji in added_emojis])}",
                        reason=entry.reason or "Причина не указана"
                    )
                    break
            
            async for entry in guild.audit_logs(action=discord.AuditLogAction.emoji_delete, limit=1):
                if removed_emojis:
                    await logs_system.log_action(
                        action_type="Удаление эмодзи",
                        moderator=entry.user,
                        details=f"Эмодзи: {', '.join([emoji.name for emoji in removed_emojis])}",
                        reason=entry.reason or "Причина не указана"
                    )
                    break
                    
        except Exception as e:
            logger.error(f"Ошибка логирования изменений эмодзи: {e}")
    
    @bot.event
    async def on_guild_stickers_update(guild, before, after):
        """Логирует изменения стикеров"""
        try:
            added_stickers = set(after) - set(before)
            removed_stickers = set(before) - set(after)
            
            async for entry in guild.audit_logs(action=discord.AuditLogAction.sticker_create, limit=1):
                if added_stickers:
                    await logs_system.log_action(
                        action_type="Добавление стикера",
                        moderator=entry.user,
                        details=f"Стикер: {', '.join([sticker.name for sticker in added_stickers])}",
                        reason=entry.reason or "Причина не указана"
                    )
                    break
            
            async for entry in guild.audit_logs(action=discord.AuditLogAction.sticker_delete, limit=1):
                if removed_stickers:
                    await logs_system.log_action(
                        action_type="Удаление стикера",
                        moderator=entry.user,
                        details=f"Стикер: {', '.join([sticker.name for sticker in removed_stickers])}",
                        reason=entry.reason or "Причина не указана"
                    )
                    break
                    
        except Exception as e:
            logger.error(f"Ошибка логирования изменений стикеров: {e}")
    
    @bot.event
    async def on_voice_state_update(member, before, after):
        """Логирует изменения голосового состояния"""
        try:
            # Отключение от голосового канала
            if before.channel and not after.channel:
                async for entry in member.guild.audit_logs(action=discord.AuditLogAction.member_disconnect, limit=1):
                    if entry.target.id == member.id:
                        await logs_system.log_action(
                            action_type="Отключение от голосового",
                            moderator=entry.user,
                            target=member,
                            channel=before.channel,
                            reason=entry.reason or "Причина не указана"
                        )
                        break
            
            # Отключение звука
            if before.mute != after.mute:
                async for entry in member.guild.audit_logs(action=discord.AuditLogAction.member_update, limit=1):
                    if entry.target.id == member.id:
                        action = "Отключение звука" if after.mute else "Включение звука"
                        await logs_system.log_action(
                            action_type=action,
                            moderator=entry.user,
                            target=member,
                            channel=after.channel or before.channel,
                            reason=entry.reason or "Причина не указана"
                        )
                        break
            
            # Заглушение
            if before.deaf != after.deaf:
                async for entry in member.guild.audit_logs(action=discord.AuditLogAction.member_update, limit=1):
                    if entry.target.id == member.id:
                        action = "Заглушение" if after.deaf else "Снятие заглушения"
                        await logs_system.log_action(
                            action_type=action,
                            moderator=entry.user,
                            target=member,
                            channel=after.channel or before.channel,
                            reason=entry.reason or "Причина не указана"
                        )
                        break
                        
        except Exception as e:
            logger.error(f"Ошибка логирования изменений голосового состояния: {e}")
    
    @bot.event
    async def on_guild_role_create(role):
        """Логирует создание роли"""
        try:
            async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_create, limit=1):
                if entry.target.id == role.id:
                    await logs_system.log_action(
                        action_type="Создание роли",
                        moderator=entry.user,
                        details=f"Роль: {role.name}",
                        reason=entry.reason or "Причина не указана"
                    )
                    break
        except Exception as e:
            logger.error(f"Ошибка логирования создания роли: {e}")
    
    @bot.event
    async def on_guild_role_delete(role):
        """Логирует удаление роли"""
        try:
            async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=1):
                if entry.target.id == role.id:
                    await logs_system.log_action(
                        action_type="Удаление роли",
                        moderator=entry.user,
                        details=f"Роль: {role.name}",
                        reason=entry.reason or "Причина не указана"
                    )
                    break
        except Exception as e:
            logger.error(f"Ошибка логирования удаления роли: {e}")
    
    @bot.event
    async def on_guild_role_update(before, after):
        """Логирует изменения роли"""
        try:
            async for entry in before.guild.audit_logs(action=discord.AuditLogAction.role_update, limit=1):
                if entry.target.id == after.id:
                    changes = []
                    
                    # Изменение имени
                    if before.name != after.name:
                        changes.append(f"Имя: {before.name} → {after.name}")
                    
                    # Изменение цвета
                    if before.color != after.color:
                        changes.append(f"Цвет: {before.color} → {after.color}")
                    
                    # Изменение прав
                    if before.permissions != after.permissions:
                        changes.append("Права изменены")
                        
                        # Детали изменений прав
                        old_perms = dict(before.permissions)
                        new_perms = dict(after.permissions)
                        perm_changes = {}
                        
                        for perm in old_perms:
                            if old_perms[perm] != new_perms.get(perm, False):
                                perm_changes[perm] = new_perms.get(perm, False)
                        
                        if perm_changes:
                            await logs_system.log_action(
                                action_type="Изменение прав роли",
                                moderator=entry.user,
                                details=f"Роль: {after.name}",
                                permissions=perm_changes,
                                reason=entry.reason or "Причина не указана"
                            )
                    
                    if changes:
                        await logs_system.log_action(
                            action_type="Изменение роли",
                            moderator=entry.user,
                            details=f"Роль: {after.name}\nИзменения: {'; '.join(changes)}",
                            reason=entry.reason or "Причина не указана"
                        )
                    break
        except Exception as e:
            logger.error(f"Ошибка логирования изменения роли: {e}")
    
    @bot.event
    async def on_guild_update(before, after):
        """Логирует изменения сервера"""
        try:
            async for entry in before.audit_logs(action=discord.AuditLogAction.guild_update, limit=1):
                changes = []
                
                # Изменение имени
                if before.name != after.name:
                    changes.append(f"Имя: {before.name} → {after.name}")
                
                # Изменение аватара
                if before.icon != after.icon:
                    changes.append("Аватар изменен")
                
                # Изменение баннера
                if before.banner != after.banner:
                    changes.append("Баннер изменен")
                
                # Изменение уровня верификации
                if before.verification_level != after.verification_level:
                    changes.append(f"Уровень верификации: {before.verification_level} → {after.verification_level}")
                
                if changes:
                    await logs_system.log_action(
                        action_type="Изменение настроек сервера",
                        moderator=entry.user,
                        details=f"Изменения: {'; '.join(changes)}",
                        reason=entry.reason or "Причина не указана"
                    )
                break
        except Exception as e:
            logger.error(f"Ошибка логирования изменений сервера: {e}")

# Команды для управления системой логирования
@commands.command(name="logs_status")
@commands.has_permissions(administrator=True)
async def logs_status(ctx):
    """Показывает статус системы логирования с улучшенным дизайном"""
    logs_system = ctx.bot.moderation_logs
    
    embed = discord.Embed(
        title="📊 Статус системы логирования",
        description="Подробная информация о состоянии системы логирования модерации",
        color=0x0099ff,
        timestamp=datetime.utcnow()
    )
    
    # Добавляем аватар бота
    if ctx.bot.user.display_avatar:
        embed.set_thumbnail(url=ctx.bot.user.display_avatar.url)
    
    embed.add_field(
        name="🔄 Статус системы",
        value="✅ Включена" if logs_system.enabled else "❌ Отключена",
        inline=True
    )
    
    embed.add_field(
        name="📺 Канал логирования",
        value=f"<#{logs_system.log_channel_id}>" if logs_system.log_channel else "❌ Не найден",
        inline=True
    )
    
    embed.add_field(
        name="💾 Резервное копирование",
        value="✅ Включено" if logs_system.backup_enabled else "❌ Отключено",
        inline=True
    )
    
    embed.add_field(
        name="📝 Сообщений в резерве",
        value=f"`{len(logs_system.message_backup)}`",
        inline=True
    )
    
    embed.add_field(
        name="🆔 ID канала",
        value=f"`{logs_system.log_channel_id}`",
        inline=True
    )
    
    embed.add_field(
        name="⏰ Время работы",
        value=f"<t:{int(datetime.utcnow().timestamp())}:R>",
        inline=True
    )
    
    embed.add_field(
        name="📝 Отслеживаемые действия",
        value="""• 👥 **Действия с участниками** - баны, кики, муты, роли
• 🎭 **Действия с ролями** - создание, удаление, изменение прав
• 📺 **Действия с каналами** - создание, удаление, изменение прав
• 💬 **Действия с сообщениями** - удаление, редактирование, восстановление
• 🎨 **Действия с медиа** - эмодзи, стикеры, реакции
• 🔊 **Голосовые действия** - отключения, муты, заглушения
• ⚙️ **Действия с сервером** - настройки, изменения""",
        inline=False
    )
    
    embed.set_footer(text=f"🆔 Бот: {ctx.bot.user.id} • Запросил: {ctx.author.name}", 
                   icon_url="https://cdn.discordapp.com/emojis/1234567890.png")
    
    await ctx.send(embed=embed)

@commands.command(name="logs_toggle")
@commands.has_permissions(administrator=True)
async def logs_toggle(ctx):
    """Включает/выключает систему логирования"""
    logs_system = ctx.bot.moderation_logs
    logs_system.enabled = not logs_system.enabled
    
    embed = discord.Embed(
        title="🔄 Переключение системы логирования",
        description=f"Система логирования **{'включена' if logs_system.enabled else 'отключена'}**",
        color=0x00ff00 if logs_system.enabled else 0xff0000,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name="📊 Статус",
        value="✅ Включена" if logs_system.enabled else "❌ Отключена",
        inline=True
    )
    
    embed.add_field(
        name="📺 Канал",
        value=f"<#{logs_system.log_channel_id}>" if logs_system.log_channel else "❌ Не найден",
        inline=True
    )
    
    embed.set_footer(text=f"🆔 Модератор: {ctx.author.id}", 
                   icon_url="https://cdn.discordapp.com/emojis/1234567890.png")
    
    await ctx.send(embed=embed)

@commands.command(name="backup_toggle")
@commands.has_permissions(administrator=True)
async def backup_toggle(ctx):
    """Включает/выключает резервное копирование сообщений"""
    logs_system = ctx.bot.moderation_logs
    logs_system.backup_enabled = not logs_system.backup_enabled
    
    embed = discord.Embed(
        title="💾 Переключение резервного копирования",
        description=f"Резервное копирование **{'включено' if logs_system.backup_enabled else 'отключено'}**",
        color=0x00ff00 if logs_system.backup_enabled else 0xff0000,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name="📊 Статус",
        value="✅ Включено" if logs_system.backup_enabled else "❌ Отключено",
        inline=True
    )
    
    embed.add_field(
        name="📝 Сообщений в резерве",
        value=f"`{len(logs_system.message_backup)}`",
        inline=True
    )
    
    embed.set_footer(text=f"🆔 Модератор: {ctx.author.id}", 
                   icon_url="https://cdn.discordapp.com/emojis/1234567890.png")
    
    await ctx.send(embed=embed)

@commands.command(name="logs_test")
@commands.has_permissions(administrator=True)
async def logs_test(ctx):
    """Отправляет тестовое сообщение в канал логирования"""
    logs_system = ctx.bot.moderation_logs
    
    if not logs_system.log_channel:
        embed = discord.Embed(
            title="❌ Ошибка",
            description="Канал логирования не найден",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        await ctx.send(embed=embed)
        return
    
    await logs_system.log_action(
        action_type="Тест системы",
        moderator=ctx.author,
        target=ctx.author,
        details="Это тестовое сообщение для проверки системы логирования",
        reason="Тестирование системы"
    )
    
    embed = discord.Embed(
        title="✅ Тест выполнен",
        description="Тестовое сообщение отправлено в канал логирования",
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name="📺 Канал",
        value=f"<#{logs_system.log_channel_id}>",
        inline=True
    )
    
    embed.set_footer(text=f"🆔 Модератор: {ctx.author.id}", 
                   icon_url="https://cdn.discordapp.com/emojis/1234567890.png")
    
    await ctx.send(embed=embed)

@commands.command(name="clear_backup")
@commands.has_permissions(administrator=True)
async def clear_backup(ctx):
    """Очищает резервные копии сообщений"""
    logs_system = ctx.bot.moderation_logs
    count = len(logs_system.message_backup)
    logs_system.message_backup.clear()
    
    embed = discord.Embed(
        title="🗑️ Очистка резервных копий",
        description=f"Очищено **{count}** резервных копий сообщений",
        color=0xff8c00,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name="📝 Удалено сообщений",
        value=f"`{count}`",
        inline=True
    )
    
    embed.add_field(
        name="💾 Размер резерва",
        value="`0`",
        inline=True
    )
    
    embed.set_footer(text=f"🆔 Модератор: {ctx.author.id}", 
                   icon_url="https://cdn.discordapp.com/emojis/1234567890.png")
    
    await ctx.send(embed=embed) 