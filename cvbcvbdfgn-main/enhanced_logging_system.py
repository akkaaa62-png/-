"""
Улучшенная система логирования для Discord бота
Логирует все важные события с детальной информацией
"""

import discord
from discord.ext import commands
import logging
import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import traceback
import psutil
import platform
import aiohttp
import time

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_logs.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class EnhancedLoggingSystem:
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1376194575281950741  # ID канала для логов
        self.log_channel = None
        self.enabled = True
        self.stats = {
            'commands_used': 0,
            'messages_sent': 0,
            'errors_occurred': 0,
            'members_joined': 0,
            'members_left': 0,
            'moderation_actions': 0,
            'start_time': datetime.utcnow(),
            'uptime': timedelta(0)
        }
        self.error_log = []
        self.performance_log = []
        self.command_log = []
        
    async def setup_logging(self):
        """Настройка системы логирования"""
        try:
            self.log_channel = self.bot.get_channel(self.log_channel_id)
            if not self.log_channel:
                logger.error(f"Канал логирования не найден: {self.log_channel_id}")
                return False
            
            logger.info(f"Улучшенная система логирования настроена: {self.log_channel.name}")
            
            # Отправляем сообщение о запуске системы
            await self.log_system_startup()
            return True
            
        except Exception as e:
            logger.error(f"Ошибка настройки улучшенного логирования: {e}")
            return False
    
    async def log_system_startup(self):
        """Логирует запуск системы"""
        embed = discord.Embed(
            title="🚀 Система логирования запущена",
            description="Улучшенная система логирования активирована",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        # Системная информация
        embed.add_field(
            name="💻 Система",
            value=f"OS: {platform.system()} {platform.release()}\nPython: {platform.python_version()}",
            inline=True
        )
        
        embed.add_field(
            name="🤖 Бот",
            value=f"Discord.py: {discord.__version__}\nПинг: {round(self.bot.latency * 1000)}ms",
            inline=True
        )
        
        embed.add_field(
            name="📊 Статистика",
            value=f"Серверов: {len(self.bot.guilds)}\nПользователей: {len(self.bot.users)}",
            inline=True
        )
        
        await self.send_log(embed)
    
    async def log_command_usage(self, ctx, command_name: str, execution_time: float):
        """Логирует использование команды"""
        self.stats['commands_used'] += 1
        
        embed = discord.Embed(
            title="⚡ Использование команды",
            description=f"Команда `{command_name}` была использована",
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="👤 Пользователь",
            value=f"{ctx.author.mention}\nID: {ctx.author.id}",
            inline=True
        )
        
        embed.add_field(
            name="📺 Канал",
            value=f"{ctx.channel.mention}\nID: {ctx.channel.id}",
            inline=True
        )
        
        embed.add_field(
            name="⏱️ Время выполнения",
            value=f"{execution_time:.2f}ms",
            inline=True
        )
        
        embed.add_field(
            name="🔗 Сообщение",
            value=f"[Перейти]({ctx.message.jump_url})",
            inline=True
        )
        
        embed.add_field(
            name="🏷️ Сервер",
            value=f"{ctx.guild.name}\nID: {ctx.guild.id}",
            inline=True
        )
        
        embed.add_field(
            name="📊 Статистика",
            value=f"Всего команд: {self.stats['commands_used']}",
            inline=True
        )
        
        await self.send_log(embed)
        
        # Сохраняем в локальный лог
        self.command_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'command': command_name,
            'user_id': ctx.author.id,
            'user_name': ctx.author.name,
            'channel_id': ctx.channel.id,
            'guild_id': ctx.guild.id,
            'execution_time': execution_time
        })
    
    async def log_member_join(self, member):
        """Логирует присоединение участника"""
        self.stats['members_joined'] += 1
        
        embed = discord.Embed(
            title="🎉 Участник присоединился",
            description=f"{member.mention} присоединился к серверу",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="👤 Информация",
            value=f"**Имя:** {member.name}\n**ID:** {member.id}\n**Создан:** <t:{int(member.created_at.timestamp())}:R>",
            inline=True
        )
        
        embed.add_field(
            name="📊 Статистика сервера",
            value=f"**Участников:** {member.guild.member_count}\n**Присоединилось:** {self.stats['members_joined']}",
            inline=True
        )
        
        embed.add_field(
            name="🔍 Детали",
            value=f"**Бот:** {'Да' if member.bot else 'Нет'}\n**Аккаунт:** {'Новый' if (datetime.utcnow() - member.created_at).days < 7 else 'Старый'}",
            inline=True
        )
        
        if member.display_avatar:
            embed.set_thumbnail(url=member.display_avatar.url)
        
        await self.send_log(embed)
    
    async def log_member_leave(self, member):
        """Логирует выход участника"""
        self.stats['members_left'] += 1
        
        embed = discord.Embed(
            title="👋 Участник покинул сервер",
            description=f"{member.mention} покинул сервер",
            color=0xff6b35,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="👤 Информация",
            value=f"**Имя:** {member.name}\n**ID:** {member.id}\n**Присоединился:** <t:{int(member.joined_at.timestamp())}:R>",
            inline=True
        )
        
        embed.add_field(
            name="📊 Статистика сервера",
            value=f"**Участников:** {member.guild.member_count}\n**Покинуло:** {self.stats['members_left']}",
            inline=True
        )
        
        embed.add_field(
            name="⏱️ Время на сервере",
            value=f"{(datetime.utcnow() - member.joined_at).days} дней",
            inline=True
        )
        
        if member.display_avatar:
            embed.set_thumbnail(url=member.display_avatar.url)
        
        await self.send_log(embed)
    
    async def log_error(self, error: Exception, context: str = "Неизвестно"):
        """Логирует ошибки"""
        self.stats['errors_occurred'] += 1
        
        embed = discord.Embed(
            title="❌ Ошибка",
            description=f"Произошла ошибка: {type(error).__name__}",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🔍 Контекст",
            value=context,
            inline=False
        )
        
        embed.add_field(
            name="📝 Сообщение",
            value=str(error)[:1000],
            inline=False
        )
        
        embed.add_field(
            name="📊 Статистика ошибок",
            value=f"Всего ошибок: {self.stats['errors_occurred']}",
            inline=True
        )
        
        # Полный стек трейс в файл
        error_info = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'traceback': traceback.format_exc()
        }
        
        self.error_log.append(error_info)
        
        # Сохраняем в файл
        with open('error_log.json', 'w', encoding='utf-8') as f:
            json.dump(self.error_log, f, ensure_ascii=False, indent=2)
        
        await self.send_log(embed)
    
    async def log_performance(self, operation: str, duration: float, details: str = ""):
        """Логирует производительность операций"""
        embed = discord.Embed(
            title="⚡ Производительность",
            description=f"Операция: {operation}",
            color=0xffff00 if duration > 1.0 else 0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="⏱️ Время выполнения",
            value=f"{duration:.3f} секунд",
            inline=True
        )
        
        embed.add_field(
            name="📊 Статус",
            value="⚠️ Медленно" if duration > 1.0 else "✅ Нормально",
            inline=True
        )
        
        if details:
            embed.add_field(
                name="🔍 Детали",
                value=details,
                inline=False
            )
        
        await self.send_log(embed)
        
        # Сохраняем в локальный лог
        self.performance_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'operation': operation,
            'duration': duration,
            'details': details
        })
    
    async def log_moderation_action(self, action_type: str, moderator, target, reason: str = "", details: str = ""):
        """Логирует действия модерации"""
        self.stats['moderation_actions'] += 1
        
        color_map = {
            'ban': 0xff0000,
            'unban': 0x00ff00,
            'kick': 0xff6b35,
            'mute': 0xffff00,
            'unmute': 0x00ff00,
            'warn': 0xffa500,
            'timeout': 0xff6b35
        }
        
        embed = discord.Embed(
            title=f"🛡️ Действие модерации: {action_type}",
            description=f"Модератор {moderator.mention} выполнил действие",
            color=color_map.get(action_type.lower(), 0x0099ff),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="👮 Модератор",
            value=f"{moderator.mention}\nID: {moderator.id}",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Цель",
            value=f"{target.mention}\nID: {target.id}",
            inline=True
        )
        
        embed.add_field(
            name="📝 Причина",
            value=reason or "Не указана",
            inline=True
        )
        
        if details:
            embed.add_field(
                name="🔍 Детали",
                value=details,
                inline=False
            )
        
        embed.add_field(
            name="📊 Статистика",
            value=f"Всего действий: {self.stats['moderation_actions']}",
            inline=True
        )
        
        await self.send_log(embed)
    
    async def log_system_status(self):
        """Логирует статус системы"""
        # Обновляем время работы
        self.stats['uptime'] = datetime.utcnow() - self.stats['start_time']
        
        # Получаем информацию о системе
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        embed = discord.Embed(
            title="📊 Статус системы",
            description="Информация о производительности бота",
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="⏱️ Время работы",
            value=str(self.stats['uptime']).split('.')[0],
            inline=True
        )
        
        embed.add_field(
            name="💻 CPU",
            value=f"{cpu_percent}%",
            inline=True
        )
        
        embed.add_field(
            name="🧠 Память",
            value=f"{memory.percent}%",
            inline=True
        )
        
        embed.add_field(
            name="📈 Статистика",
            value=f"Команд: {self.stats['commands_used']}\nСообщений: {self.stats['messages_sent']}\nОшибок: {self.stats['errors_occurred']}",
            inline=True
        )
        
        embed.add_field(
            name="👥 Участники",
            value=f"Присоединилось: {self.stats['members_joined']}\nПокинуло: {self.stats['members_left']}",
            inline=True
        )
        
        embed.add_field(
            name="🛡️ Модерация",
            value=f"Действий: {self.stats['moderation_actions']}",
            inline=True
        )
        
        await self.send_log(embed)
    
    async def log_message_activity(self, message, action: str):
        """Логирует активность сообщений"""
        self.stats['messages_sent'] += 1
        
        embed = discord.Embed(
            title=f"💬 Активность сообщений: {action}",
            description=f"Сообщение от {message.author.mention}",
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="👤 Автор",
            value=f"{message.author.mention}\nID: {message.author.id}",
            inline=True
        )
        
        embed.add_field(
            name="📺 Канал",
            value=f"{message.channel.mention}\nID: {message.channel.id}",
            inline=True
        )
        
        embed.add_field(
            name="📝 Содержимое",
            value=message.content[:100] + "..." if len(message.content) > 100 else message.content,
            inline=False
        )
        
        embed.add_field(
            name="🔗 Ссылка",
            value=f"[Перейти]({message.jump_url})",
            inline=True
        )
        
        await self.send_log(embed)
    
    async def log_voice_activity(self, member, before, after):
        """Логирует активность в голосовых каналах"""
        embed = discord.Embed(
            title="🎤 Голосовая активность",
            description=f"Изменение состояния {member.mention}",
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="👤 Участник",
            value=f"{member.mention}\nID: {member.id}",
            inline=True
        )
        
        if before.channel and after.channel:
            embed.add_field(
                name="🔄 Переход",
                value=f"Из {before.channel.name} в {after.channel.name}",
                inline=True
            )
        elif before.channel and not after.channel:
            embed.add_field(
                name="🚪 Выход",
                value=f"Покинул {before.channel.name}",
                inline=True
            )
        elif not before.channel and after.channel:
            embed.add_field(
                name="🚪 Вход",
                value=f"Присоединился к {after.channel.name}",
                inline=True
            )
        
        embed.add_field(
            name="🔇 Состояние",
            value=f"Мут: {'Да' if after.mute else 'Нет'}\nЗаглушение: {'Да' if after.deaf else 'Нет'}",
            inline=True
        )
        
        await self.send_log(embed)
    
    async def log_reaction_activity(self, payload, action: str):
        """Логирует активность реакций"""
        embed = discord.Embed(
            title=f"😀 Активность реакций: {action}",
            description=f"Реакция {payload.emoji}",
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        user = self.bot.get_user(payload.user_id)
        channel = self.bot.get_channel(payload.channel_id)
        guild = self.bot.get_guild(payload.guild_id)
        
        embed.add_field(
            name="👤 Пользователь",
            value=f"{user.mention if user else 'Неизвестно'}\nID: {payload.user_id}",
            inline=True
        )
        
        embed.add_field(
            name="📺 Канал",
            value=f"{channel.mention if channel else 'Неизвестно'}\nID: {payload.channel_id}",
            inline=True
        )
        
        embed.add_field(
            name="😀 Эмодзи",
            value=f"{payload.emoji}",
            inline=True
        )
        
        await self.send_log(embed)
    
    async def log_channel_activity(self, channel, action: str):
        """Логирует активность каналов"""
        embed = discord.Embed(
            title=f"📺 Активность канала: {action}",
            description=f"Канал {channel.mention}",
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📝 Название",
            value=channel.name,
            inline=True
        )
        
        embed.add_field(
            name="🆔 ID",
            value=channel.id,
            inline=True
        )
        
        embed.add_field(
            name="📋 Тип",
            value=channel.type.name,
            inline=True
        )
        
        if hasattr(channel, 'topic') and channel.topic:
            embed.add_field(
                name="📄 Тема",
                value=channel.topic[:100] + "..." if len(channel.topic) > 100 else channel.topic,
                inline=False
            )
        
        await self.send_log(embed)
    
    async def log_role_activity(self, role, action: str):
        """Логирует активность ролей"""
        embed = discord.Embed(
            title=f"🎭 Активность роли: {action}",
            description=f"Роль {role.mention}",
            color=role.color if role.color != discord.Color.default() else 0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📝 Название",
            value=role.name,
            inline=True
        )
        
        embed.add_field(
            name="🆔 ID",
            value=role.id,
            inline=True
        )
        
        embed.add_field(
            name="👥 Участников",
            value=len(role.members),
            inline=True
        )
        
        embed.add_field(
            name="🔐 Позиция",
            value=role.position,
            inline=True
        )
        
        embed.add_field(
            name="🎨 Цвет",
            value=str(role.color),
            inline=True
        )
        
        embed.add_field(
            name="🔒 Упоминаемая",
            value="Да" if role.mentionable else "Нет",
            inline=True
        )
        
        await self.send_log(embed)
    
    async def send_log(self, embed):
        """Отправляет лог в канал"""
        if not self.enabled or not self.log_channel:
            return
        
        try:
            await self.log_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Ошибка отправки лога: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику"""
        self.stats['uptime'] = datetime.utcnow() - self.stats['start_time']
        return self.stats.copy()
    
    async def save_logs_to_file(self):
        """Сохраняет логи в файл"""
        try:
            logs_data = {
                'stats': self.get_stats(),
                'command_log': self.command_log[-100:],  # Последние 100 команд
                'performance_log': self.performance_log[-50:],  # Последние 50 операций
                'error_log': self.error_log[-20:]  # Последние 20 ошибок
            }
            
            with open('enhanced_logs.json', 'w', encoding='utf-8') as f:
                json.dump(logs_data, f, ensure_ascii=False, indent=2, default=str)
                
            logger.info("Логи сохранены в файл enhanced_logs.json")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения логов: {e}")

async def setup_enhanced_logging(bot):
    """Настройка улучшенной системы логирования"""
    try:
        enhanced_logs = EnhancedLoggingSystem(bot)
        bot.enhanced_logs = enhanced_logs
        
        # Настраиваем систему
        await enhanced_logs.setup_logging()
        
        # Устанавливаем обработчики событий
        await setup_enhanced_log_handlers(bot, enhanced_logs)
        
        logger.info("Улучшенная система логирования настроена")
        
    except Exception as e:
        logger.error(f"Ошибка настройки улучшенной системы логирования: {e}")

async def setup_enhanced_log_handlers(bot, enhanced_logs):
    """Устанавливает обработчики событий для улучшенного логирования"""
    
    @bot.event
    async def on_command(ctx):
        """Логирует использование команд"""
        start_time = time.time()
        
        # Сохраняем время начала для вычисления длительности
        ctx._command_start_time = start_time
    
    @bot.event
    async def on_command_completion(ctx):
        """Логирует завершение команд"""
        if hasattr(ctx, '_command_start_time'):
            execution_time = (time.time() - ctx._command_start_time) * 1000  # в миллисекундах
            await enhanced_logs.log_command_usage(ctx, ctx.command.name, execution_time)
    
    @bot.event
    async def on_command_error(ctx, error):
        """Логирует ошибки команд"""
        await enhanced_logs.log_error(error, f"Команда: {ctx.command.name if ctx.command else 'Неизвестно'}")
    
    @bot.event
    async def on_member_join(member):
        """Логирует присоединение участников"""
        await enhanced_logs.log_member_join(member)
    
    @bot.event
    async def on_member_remove(member):
        """Логирует выход участников"""
        await enhanced_logs.log_member_leave(member)
    
    @bot.event
    async def on_message(message):
        """Логирует сообщения"""
        if not message.author.bot:
            await enhanced_logs.log_message_activity(message, "Отправлено")
    
    @bot.event
    async def on_message_edit(before, after):
        """Логирует редактирование сообщений"""
        if not before.author.bot:
            await enhanced_logs.log_message_activity(after, "Отредактировано")
    
    @bot.event
    async def on_message_delete(message):
        """Логирует удаление сообщений"""
        if not message.author.bot:
            await enhanced_logs.log_message_activity(message, "Удалено")
    
    @bot.event
    async def on_voice_state_update(member, before, after):
        """Логирует изменения голосового состояния"""
        await enhanced_logs.log_voice_activity(member, before, after)
    
    @bot.event
    async def on_raw_reaction_add(payload):
        """Логирует добавление реакций"""
        await enhanced_logs.log_reaction_activity(payload, "Добавлена")
    
    @bot.event
    async def on_raw_reaction_remove(payload):
        """Логирует удаление реакций"""
        await enhanced_logs.log_reaction_activity(payload, "Удалена")
    
    @bot.event
    async def on_guild_channel_create(channel):
        """Логирует создание каналов"""
        await enhanced_logs.log_channel_activity(channel, "Создан")
    
    @bot.event
    async def on_guild_channel_delete(channel):
        """Логирует удаление каналов"""
        await enhanced_logs.log_channel_activity(channel, "Удален")
    
    @bot.event
    async def on_guild_role_create(role):
        """Логирует создание ролей"""
        await enhanced_logs.log_role_activity(role, "Создана")
    
    @bot.event
    async def on_guild_role_delete(role):
        """Логирует удаление ролей"""
        await enhanced_logs.log_role_activity(role, "Удалена")
    
    @bot.event
    async def on_error(event, *args, **kwargs):
        """Логирует общие ошибки"""
        await enhanced_logs.log_error(Exception(f"Ошибка в событии {event}"), f"Событие: {event}")
    
    # Команды для управления системой логирования
    @commands.command(name="logs_stats")
    @commands.has_permissions(administrator=True)
    async def logs_stats(ctx):
        """Показывает статистику логирования"""
        stats = enhanced_logs.get_stats()
        
        embed = discord.Embed(
            title="📊 Статистика логирования",
            description="Подробная статистика работы бота",
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="⏱️ Время работы",
            value=str(stats['uptime']).split('.')[0],
            inline=True
        )
        
        embed.add_field(
            name="⚡ Команды",
            value=f"Использовано: {stats['commands_used']}",
            inline=True
        )
        
        embed.add_field(
            name="💬 Сообщения",
            value=f"Отправлено: {stats['messages_sent']}",
            inline=True
        )
        
        embed.add_field(
            name="❌ Ошибки",
            value=f"Произошло: {stats['errors_occurred']}",
            inline=True
        )
        
        embed.add_field(
            name="👥 Участники",
            value=f"Присоединилось: {stats['members_joined']}\nПокинуло: {stats['members_left']}",
            inline=True
        )
        
        embed.add_field(
            name="🛡️ Модерация",
            value=f"Действий: {stats['moderation_actions']}",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="logs_save")
    @commands.has_permissions(administrator=True)
    async def logs_save(ctx):
        """Сохраняет логи в файл"""
        await enhanced_logs.save_logs_to_file()
        
        embed = discord.Embed(
            title="💾 Логи сохранены",
            description="Логи успешно сохранены в файл enhanced_logs.json",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="logs_status")
    @commands.has_permissions(administrator=True)
    async def logs_status(ctx):
        """Показывает статус системы"""
        await enhanced_logs.log_system_status()
        
        embed = discord.Embed(
            title="✅ Статус отправлен",
            description="Статус системы отправлен в канал логирования",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        await ctx.send(embed=embed)
    
    # Добавляем команды к боту
    bot.add_command(logs_stats)
    bot.add_command(logs_save)
    bot.add_command(logs_status) 