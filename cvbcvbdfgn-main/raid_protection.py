"""
Система защиты от рейдов и массовых действий для Discord бота
Защищает сервер от спама, массовых банов, мутов и удаления каналов
"""

import discord
from discord.ext import commands, tasks
import logging
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict, deque
from config import LIMONERICX_SERVER_ID

logger = logging.getLogger('raid_protection')

class RaidProtection:
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = LIMONERICX_SERVER_ID
        
        # Настройки защиты
        self.MAX_JOINS_PER_MINUTE = 10  # Максимум входов в минуту
        self.MAX_MESSAGES_PER_MINUTE = 20  # Максимум сообщений в минуту от одного пользователя
        self.MAX_BANS_PER_HOUR = 5  # Максимум банов в час от модератора
        self.MAX_KICKS_PER_HOUR = 10  # Максимум киков в час
        self.MAX_MUTES_PER_HOUR = 15  # Максимум мутов в час
        self.MAX_CHANNEL_DELETIONS_PER_HOUR = 3  # Максимум удалений каналов в час
        
        # Хранение активности
        self.join_times = deque()
        self.user_messages = defaultdict(lambda: deque())
        self.moderator_actions = defaultdict(lambda: {
            'bans': deque(),
            'kicks': deque(), 
            'mutes': deque(),
            'channel_deletions': deque()
        })
        
        # Статусы рейда
        self.raid_mode = False
        self.lockdown_mode = False
        
        # Защищенные роли (не могут быть забанены автоматически)
        self.protected_roles = [
            1375794448650342521,  # Роль из конфига
            # Добавьте другие важные роли
        ]
        
        # Канал для логов безопасности
        self.security_log_channel_id = None  # Будет найден автоматически
        
        self.cleanup_task.start()
    
    def cleanup_old_data(self):
        """Очистка старых данных для экономии памяти"""
        now = datetime.now()
        cutoff_time = now - timedelta(hours=1)
        
        # Очистка времен входа
        while self.join_times and self.join_times[0] < cutoff_time:
            self.join_times.popleft()
        
        # Очистка сообщений пользователей
        for user_id in list(self.user_messages.keys()):
            messages = self.user_messages[user_id]
            while messages and messages[0] < cutoff_time:
                messages.popleft()
            if not messages:
                del self.user_messages[user_id]
        
        # Очистка действий модераторов
        for mod_id in list(self.moderator_actions.keys()):
            actions = self.moderator_actions[mod_id]
            for action_type in actions:
                while actions[action_type] and actions[action_type][0] < cutoff_time:
                    actions[action_type].popleft()
    
    @tasks.loop(minutes=10)
    async def cleanup_task(self):
        """Периодическая очистка данных"""
        self.cleanup_old_data()
    
    async def get_security_log_channel(self):
        """Получить канал для логов безопасности"""
        if not self.security_log_channel_id:
            guild = self.bot.get_guild(self.guild_id)
            if guild:
                # Ищем канал с именем "security" или "безопасность"
                for channel in guild.channels:
                    if any(word in channel.name.lower() for word in ['security', 'безопасность', 'logs', 'логи']):
                        self.security_log_channel_id = channel.id
                        break
        
        return self.bot.get_channel(self.security_log_channel_id) if self.security_log_channel_id else None
    
    async def log_security_event(self, title, description, color=0xff0000, fields=None):
        """Логирование событий безопасности"""
        try:
            channel = await self.get_security_log_channel()
            if not channel:
                logger.warning("Канал для логов безопасности не найден")
                return
            
            embed = discord.Embed(
                title=f"🛡️ {title}",
                description=description,
                color=color,
                timestamp=datetime.now()
            )
            
            if fields:
                for field in fields:
                    embed.add_field(
                        name=field.get('name', 'Информация'),
                        value=field.get('value', 'Нет данных'),
                        inline=field.get('inline', False)
                    )
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Ошибка при логировании события безопасности: {e}")
    
    async def check_raid_joins(self, member):
        """Проверка на рейд по входам"""
        now = datetime.now()
        self.join_times.append(now)
        
        # Подсчет входов за последнюю минуту
        cutoff = now - timedelta(minutes=1)
        recent_joins = sum(1 for join_time in self.join_times if join_time > cutoff)
        
        if recent_joins > self.MAX_JOINS_PER_MINUTE and not self.raid_mode:
            await self.enable_raid_mode()
            await self.log_security_event(
                "ОБНАРУЖЕН РЕЙД",
                f"Обнаружено {recent_joins} входов за последнюю минуту. Активирован режим защиты от рейда.",
                color=0xff0000,
                fields=[
                    {"name": "Входов за минуту", "value": str(recent_joins), "inline": True},
                    {"name": "Лимит", "value": str(self.MAX_JOINS_PER_MINUTE), "inline": True}
                ]
            )
    
    async def enable_raid_mode(self):
        """Включить режим защиты от рейда"""
        if self.raid_mode:
            return
        
        self.raid_mode = True
        guild = self.bot.get_guild(self.guild_id)
        
        if guild:
            try:
                # Повышаем уровень верификации
                await guild.edit(verification_level=discord.VerificationLevel.high)
                
                # Отключаем возможность добавления участников для @everyone
                everyone_role = guild.default_role
                permissions = everyone_role.permissions
                permissions.create_instant_invite = False
                await everyone_role.edit(permissions=permissions)
                
                logger.info("Режим защиты от рейда активирован")
                
                # Автоматическое отключение через 30 минут
                await asyncio.sleep(1800)  # 30 минут
                await self.disable_raid_mode()
                
            except Exception as e:
                logger.error(f"Ошибка при активации режима рейда: {e}")
    
    async def disable_raid_mode(self):
        """Отключить режим защиты от рейда"""
        if not self.raid_mode:
            return
        
        self.raid_mode = False
        guild = self.bot.get_guild(self.guild_id)
        
        if guild:
            try:
                # Возвращаем обычный уровень верификации
                await guild.edit(verification_level=discord.VerificationLevel.medium)
                
                # Возвращаем права на приглашения
                everyone_role = guild.default_role
                permissions = everyone_role.permissions
                permissions.create_instant_invite = True
                await everyone_role.edit(permissions=permissions)
                
                await self.log_security_event(
                    "РЕЖИМ РЕЙДА ОТКЛЮЧЕН",
                    "Режим защиты от рейда автоматически отключен.",
                    color=0x00ff00
                )
                
                logger.info("Режим защиты от рейда отключен")
                
            except Exception as e:
                logger.error(f"Ошибка при отключении режима рейда: {e}")
    
    async def check_message_spam(self, message):
        """Проверка на спам сообщениями"""
        if message.author.bot:
            return
        
        now = datetime.now()
        user_id = message.author.id
        
        self.user_messages[user_id].append(now)
        
        # Подсчет сообщений за последнюю минуту
        cutoff = now - timedelta(minutes=1)
        recent_messages = sum(1 for msg_time in self.user_messages[user_id] if msg_time > cutoff)
        
        if recent_messages > self.MAX_MESSAGES_PER_MINUTE:
            await self.handle_spam_user(message.author, recent_messages)
    
    async def handle_spam_user(self, user, message_count):
        """Обработка пользователя-спамера"""
        try:
            # Проверяем, не является ли пользователь защищенным
            if any(role.id in self.protected_roles for role in user.roles):
                return
            
            # Мут на 10 минут
            mute_role = discord.utils.get(user.guild.roles, name="Muted")
            if mute_role:
                await user.add_roles(mute_role, reason="Автоматический мут за спам")
                
                await self.log_security_event(
                    "ПОЛЬЗОВАТЕЛЬ ЗАМУЧЕН ЗА СПАМ",
                    f"Пользователь {user.mention} был автоматически замучен за спам.",
                    color=0xffa500,
                    fields=[
                        {"name": "Пользователь", "value": f"{user.mention} ({user.id})", "inline": True},
                        {"name": "Сообщений за минуту", "value": str(message_count), "inline": True},
                        {"name": "Длительность мута", "value": "10 минут", "inline": True}
                    ]
                )
                
                # Автоматическое снятие мута через 10 минут
                await asyncio.sleep(600)
                try:
                    await user.remove_roles(mute_role, reason="Автоматическое снятие мута")
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Ошибка при муте спамера: {e}")
    
    async def check_moderator_actions(self, moderator, action_type):
        """Проверка на превышение лимитов модераторских действий"""
        now = datetime.now()
        mod_id = moderator.id
        
        # Проверяем, является ли модератор администратором
        guild = self.bot.get_guild(self.guild_id)
        if guild:
            member = guild.get_member(mod_id)
            if member and member.guild_permissions.administrator:
                # Администраторы не ограничены
                return
        
        self.moderator_actions[mod_id][action_type].append(now)
        
        # Подсчет действий за последний час
        cutoff = now - timedelta(hours=1)
        recent_actions = sum(1 for action_time in self.moderator_actions[mod_id][action_type] if action_time > cutoff)
        
        limits = {
            'bans': self.MAX_BANS_PER_HOUR,
            'kicks': self.MAX_KICKS_PER_HOUR,
            'mutes': self.MAX_MUTES_PER_HOUR,
            'channel_deletions': self.MAX_CHANNEL_DELETIONS_PER_HOUR
        }
        
        current_limit = limits.get(action_type, 999)
        
        if recent_actions > current_limit:
            # Логируем превышение лимита
            await self.log_security_event(
                f"ПРЕВЫШЕН ЛИМИТ ДЕЙСТВИЙ МОДЕРАТОРА",
                f"Модератор {moderator.mention} превысил лимит действий типа '{action_type}'.",
                color=0xff6600,
                fields=[
                    {"name": "Модератор", "value": f"{moderator.mention} ({moderator.id})", "inline": True},
                    {"name": "Тип действия", "value": action_type, "inline": True},
                    {"name": "Действий за час", "value": f"{recent_actions}/{current_limit}", "inline": True}
                ]
            )
            
            # Автоматические действия при превышении лимитов
            await self.handle_moderator_limit_exceeded(moderator, action_type, recent_actions, current_limit)
    
    async def handle_moderator_limit_exceeded(self, moderator, action_type, actions_count, limit):
        """Обработка превышения лимитов модератора"""
        try:
            guild = self.bot.get_guild(self.guild_id)
            if not guild:
                return
            
            member = guild.get_member(moderator.id)
            if not member:
                return
            
            # Определяем действия в зависимости от типа и количества превышений
            if action_type == 'bans' and actions_count > limit:
                # Баны - самые серьезные, временно отключаем права
                await self.temporarily_disable_moderator(member, 'bans', 2)  # 2 часа
                
            elif action_type == 'kicks' and actions_count > limit:
                # Кики - предупреждение и временное ограничение
                await self.warn_moderator(member, 'kicks')
                await self.temporarily_disable_moderator(member, 'kicks', 1)  # 1 час
                
            elif action_type == 'mutes' and actions_count > limit:
                # Муты - предупреждение
                await self.warn_moderator(member, 'mutes')
                
            elif action_type == 'channel_deletions' and actions_count > limit:
                # Удаление каналов - серьезное нарушение
                await self.temporarily_disable_moderator(member, 'channel_deletions', 4)  # 4 часа
                
            # Уведомляем всех администраторов
            await self.notify_administrators(moderator, action_type, actions_count, limit)
            
        except Exception as e:
            logger.error(f"Ошибка при обработке превышения лимита модератора: {e}")
    
    async def temporarily_disable_moderator(self, member, action_type, hours):
        """Временно отключает права модератора"""
        try:
            # Находим роль модератора (предполагаем, что есть роль с правами модерации)
            mod_role = None
            for role in member.roles:
                if role.permissions.manage_messages or role.permissions.kick_members or role.permissions.ban_members:
                    mod_role = role
                    break
            
            if mod_role:
                # Временно убираем роль модератора
                await member.remove_roles(mod_role, reason=f"Превышение лимита {action_type}")
                
                # Запланируем возврат роли через указанное время
                await asyncio.sleep(hours * 3600)  # Конвертируем часы в секунды
                
                # Возвращаем роль
                await member.add_roles(mod_role, reason=f"Автоматическое восстановление после превышения лимита {action_type}")
                
                await self.log_security_event(
                    "ПРАВА МОДЕРАТОРА ВОССТАНОВЛЕНЫ",
                    f"Права модератора {member.mention} восстановлены после превышения лимита {action_type}.",
                    color=0x00ff00
                )
                
        except Exception as e:
            logger.error(f"Ошибка при временном отключении модератора: {e}")
    
    async def warn_moderator(self, member, action_type):
        """Отправляет предупреждение модератору"""
        try:
            embed = discord.Embed(
                title="⚠️ ПРЕДУПРЕЖДЕНИЕ МОДЕРАТОРА",
                description=f"Вы превысили лимит действий типа '{action_type}'. Пожалуйста, будьте более осторожны.",
                color=0xff6600,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="Тип действия",
                value=action_type,
                inline=True
            )
            
            embed.add_field(
                name="Рекомендация",
                value="Делайте перерывы между действиями и убедитесь в их необходимости.",
                inline=False
            )
            
            embed.set_footer(text="Система защиты от рейдов")
            
            try:
                await member.send(embed=embed)
            except:
                # Если не удалось отправить в ЛС, логируем
                logger.warning(f"Не удалось отправить предупреждение модератору {member.id}")
                
        except Exception as e:
            logger.error(f"Ошибка при отправке предупреждения модератору: {e}")
    
    async def notify_administrators(self, moderator, action_type, actions_count, limit):
        """Уведомляет всех администраторов о превышении лимита"""
        try:
            guild = self.bot.get_guild(self.guild_id)
            if not guild:
                return
            
            # Находим всех администраторов
            admins = [member for member in guild.members if member.guild_permissions.administrator]
            
            embed = discord.Embed(
                title="🚨 ПРЕВЫШЕНИЕ ЛИМИТА МОДЕРАТОРА",
                description=f"Модератор {moderator.mention} превысил лимит действий.",
                color=0xff0000,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="Модератор",
                value=f"{moderator.mention} ({moderator.id})",
                inline=True
            )
            
            embed.add_field(
                name="Тип действия",
                value=action_type,
                inline=True
            )
            
            embed.add_field(
                name="Действий за час",
                value=f"{actions_count}/{limit}",
                inline=True
            )
            
            embed.add_field(
                name="Статус",
                value="Автоматические меры применены",
                inline=False
            )
            
            embed.set_footer(text="Система защиты от рейдов")
            
            # Отправляем уведомление в канал безопасности
            security_channel = await self.get_security_log_channel()
            if security_channel:
                await security_channel.send(content=" ".join([admin.mention for admin in admins]), embed=embed)
            
        except Exception as e:
            logger.error(f"Ошибка при уведомлении администраторов: {e}")
    
    async def check_mute_action(self, moderator, target, duration=None):
        """Проверка действия мута"""
        await self.check_moderator_actions(moderator, 'mutes')
        
        # Логируем мут
        duration_text = f" на {duration}" if duration else " навсегда"
        await self.log_security_event(
            "ПОЛЬЗОВАТЕЛЬ ЗАМУЧЕН",
            f"Пользователь {target.mention} был замучен модератором {moderator.mention}{duration_text}.",
            color=0xffaa00,
            fields=[
                {"name": "Модератор", "value": f"{moderator.mention} ({moderator.id})", "inline": True},
                {"name": "Пользователь", "value": f"{target.mention} ({target.id})", "inline": True},
                {"name": "Длительность", "value": duration_text, "inline": True}
                ]
            )
    
    async def protect_channel_deletion(self, channel, user):
        """Защита от удаления каналов"""
        await self.check_moderator_actions(user, 'channel_deletions')
        
        # Логируем удаление канала
        await self.log_security_event(
            "КАНАЛ УДАЛЕН",
            f"Канал '{channel.name}' был удален пользователем {user.mention}.",
            color=0xff4444,
            fields=[
                {"name": "Канал", "value": f"#{channel.name} ({channel.id})", "inline": True},
                {"name": "Удалил", "value": f"{user.mention} ({user.id})", "inline": True},
                {"name": "Тип канала", "value": str(channel.type), "inline": True}
            ]
        )

# Команды для управления защитой
class RaidProtectionCommands(commands.Cog):
    def __init__(self, bot, protection_system):
        self.bot = bot
        self.protection = protection_system
    
    @commands.command(name='lockdown')
    @commands.has_permissions(administrator=True)
    async def lockdown(self, ctx):
        """Включить режим изоляции сервера"""
        if self.protection.lockdown_mode:
            await ctx.send("❌ Режим изоляции уже активен!")
            return
        
        self.protection.lockdown_mode = True
        guild = ctx.guild
        
        # Отключаем сообщения для @everyone
        everyone_role = guild.default_role
        permissions = everyone_role.permissions
        permissions.send_messages = False
        permissions.add_reactions = False
        await everyone_role.edit(permissions=permissions)
        
        embed = discord.Embed(
            title="🔒 РЕЖИМ ИЗОЛЯЦИИ АКТИВИРОВАН",
            description="Сервер заблокирован. Только администраторы могут писать сообщения.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        
        await self.protection.log_security_event(
            "РЕЖИМ ИЗОЛЯЦИИ АКТИВИРОВАН",
            f"Режим изоляции активирован администратором {ctx.author.mention}.",
            color=0xff0000
        )
    
    @commands.command(name='unlock')
    @commands.has_permissions(administrator=True)
    async def unlock(self, ctx):
        """Отключить режим изоляции сервера"""
        if not self.protection.lockdown_mode:
            await ctx.send("❌ Режим изоляции не активен!")
            return
        
        self.protection.lockdown_mode = False
        guild = ctx.guild
        
        # Возвращаем права на сообщения
        everyone_role = guild.default_role
        permissions = everyone_role.permissions
        permissions.send_messages = True
        permissions.add_reactions = True
        await everyone_role.edit(permissions=permissions)
        
        embed = discord.Embed(
            title="🔓 РЕЖИМ ИЗОЛЯЦИИ ОТКЛЮЧЕН",
            description="Сервер разблокирован. Участники снова могут писать сообщения.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
        
        await self.protection.log_security_event(
            "РЕЖИМ ИЗОЛЯЦИИ ОТКЛЮЧЕН",
            f"Режим изоляции отключен администратором {ctx.author.mention}.",
            color=0x00ff00
        )
    
    @commands.command(name='raidstatus')
    @commands.has_permissions(manage_guild=True)
    async def raid_status(self, ctx):
        """Показать статус системы защиты"""
        embed = discord.Embed(
            title="🛡️ Статус системы защиты",
            color=0x0099ff
        )
        
        embed.add_field(
            name="Режим рейда",
            value="🔴 Активен" if self.protection.raid_mode else "🟢 Неактивен",
            inline=True
        )
        
        embed.add_field(
            name="Режим изоляции",
            value="🔴 Активен" if self.protection.lockdown_mode else "🟢 Неактивен",
            inline=True
        )
        
        embed.add_field(
            name="Входов за час",
            value=str(len(self.protection.join_times)),
            inline=True
        )
        
        await ctx.send(embed=embed)

async def setup_raid_protection(bot):
    """Настройка системы защиты от рейдов"""
    try:
        protection = RaidProtection(bot)
        bot.raid_protection = protection
        
        # Добавляем команды
        await bot.add_cog(RaidProtectionCommands(bot, protection))
        
        # Настройка событий
        @bot.event
        async def on_member_join(member):
            if member.guild.id == LIMONERICX_SERVER_ID:
                await protection.check_raid_joins(member)
        
        @bot.event
        async def on_message(message):
            if message.guild and message.guild.id == LIMONERICX_SERVER_ID:
                await protection.check_message_spam(message)
        
        @bot.event
        async def on_member_ban(guild, user):
            if guild.id == LIMONERICX_SERVER_ID:
                # Получаем информацию о том, кто забанил через audit log
                async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
                    if entry.target.id == user.id:
                        await protection.check_moderator_actions(entry.user, 'bans')
                        break
        
        @bot.event
        async def on_member_remove(member):
            if member.guild.id == LIMONERICX_SERVER_ID:
                # Проверяем, был ли это кик через audit log
                async for entry in member.guild.audit_logs(action=discord.AuditLogAction.kick, limit=1):
                    if entry.target.id == member.id:
                        await protection.check_moderator_actions(entry.user, 'kicks')
                        break
        
        @bot.event
        async def on_guild_channel_delete(channel):
            if channel.guild.id == LIMONERICX_SERVER_ID:
                # Получаем информацию о том, кто удалил канал
                async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
                    if entry.target.id == channel.id:
                        await protection.protect_channel_deletion(channel, entry.user)
                        break
        
        # Обработка мутов через audit log
        @bot.event
        async def on_member_update(before, after):
            if before.guild.id == LIMONERICX_SERVER_ID:
                # Проверяем, был ли добавлен мут
                if before.timed_out_until != after.timed_out_until and after.timed_out_until:
                    # Получаем информацию о том, кто замутил через audit log
                    async for entry in after.guild.audit_logs(action=discord.AuditLogAction.member_update, limit=5):
                        if entry.target.id == after.id and entry.after.timed_out_until:
                            await protection.check_mute_action(entry.user, after, str(after.timed_out_until - datetime.now()))
                        break
        
        logger.info("Система защиты от рейдов настроена")
        
    except Exception as e:
        logger.error(f"Ошибка при настройке системы защиты от рейдов: {e}")
