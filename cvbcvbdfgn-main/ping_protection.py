
"""
Система защиты от пинга конкретного пользователя
При пинге @kobra228 - предупреждение, при повторном пинге в течение 42 часов - мут на 24 часа
"""

import discord
from discord.ext import commands
import logging
import json
import os
from datetime import datetime, timedelta
from config import LIMONERICX_SERVER_ID

logger = logging.getLogger('ping_protection')

class PingProtectionSystem:
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = LIMONERICX_SERVER_ID
        self.protected_user_id = 1175380582176391258  # ID пользователя kobra228
        self.ping_violations_file = "ping_violations.json"
        self.violations = self.load_violations()
        self.warning_interval = 42 * 3600  # 42 часа в секундах
        self.mute_duration = 24 * 3600  # 24 часа в секундах

    def load_violations(self):
        """Загрузка данных о нарушениях пинга"""
        try:
            if os.path.exists(self.ping_violations_file):
                with open(self.ping_violations_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки нарушений: {e}")
        return {}

    def save_violations(self):
        """Сохранение данных о нарушениях пинга"""
        try:
            with open(self.ping_violations_file, 'w', encoding='utf-8') as f:
                json.dump(self.violations, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения нарушений: {e}")

    def clean_old_violations(self):
        """Очистка старых нарушений (старше 42 часов)"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(seconds=self.warning_interval)
        
        users_to_remove = []
        for user_id, violation_data in self.violations.items():
            last_violation = datetime.fromisoformat(violation_data['last_violation'])
            if last_violation < cutoff_time:
                users_to_remove.append(user_id)
        
        for user_id in users_to_remove:
            del self.violations[user_id]
        
        if users_to_remove:
            self.save_violations()
            logger.info(f"Очищены старые нарушения для {len(users_to_remove)} пользователей")

    async def check_protected_ping(self, message):
        """Проверка на пинг защищенного пользователя"""
        try:
            # Игнорируем ботов
            if message.author.bot:
                return

            # Проверяем, не пингует ли кто-то защищенного пользователя
            mentioned_ids = [user.id for user in message.mentions]
            logger.debug(f"Проверяем сообщение от {message.author.name} в канале {message.channel.name}")
            logger.debug(f"Упомянуты пользователи: {mentioned_ids}")
            logger.debug(f"Защищенный пользователь: {self.protected_user_id}")
            
            if self.protected_user_id in mentioned_ids:
                logger.info(f"🚨 ОБНАРУЖЕН ПИНГ защищенного пользователя от {message.author.name} в канале {message.channel.name}")
                await self.handle_protected_ping(message)

        except Exception as e:
            logger.error(f"Ошибка при проверке защищенного пинга: {e}")

    async def handle_protected_ping(self, message):
        """Обработка пинга защищенного пользователя"""
        try:
            user_id = str(message.author.id)
            current_time = datetime.now()
            
            # Очищаем старые нарушения
            self.clean_old_violations()
            
            # Проверяем, есть ли уже нарушения у этого пользователя
            if user_id in self.violations:
                last_violation = datetime.fromisoformat(self.violations[user_id]['last_violation'])
                time_diff = current_time - last_violation
                
                # Если прошло меньше 42 часов - мутим
                if time_diff.total_seconds() < self.warning_interval:
                    await self.mute_user_for_ping_violation(message)
                    return
            
            # Первое нарушение - предупреждение
            await self.warn_user_for_ping(message)
            
            # Записываем нарушение
            self.violations[user_id] = {
                'username': str(message.author),
                'last_violation': current_time.isoformat(),
                'violation_count': self.violations.get(user_id, {}).get('violation_count', 0) + 1
            }
            self.save_violations()
            
        except Exception as e:
            logger.error(f"Ошибка при обработке пинга: {e}")

    async def warn_user_for_ping(self, message):
        """Предупреждение пользователя за пинг"""
        try:
            # Получаем защищенного пользователя
            protected_user = self.bot.get_user(self.protected_user_id)
            protected_mention = protected_user.mention if protected_user else "этого пользователя"
            
            # Удаляем сообщение с пингом
            try:
                await message.delete()
                logger.info(f"Удалено сообщение с пингом от {message.author.name}")
            except Exception as e:
                logger.error(f"Не удалось удалить сообщение: {e}")
            
            # Создаем embed с предупреждением
            embed = discord.Embed(
                title="⚠️ Предупреждение о пинге",
                description=f"**{message.author.mention}**, пожалуйста, не пингуйте {protected_mention}!",
                color=0xffaa00
            )
            
            embed.add_field(
                name="📋 Важная информация:",
                value=f"• Данный пользователь находится под защитой от пингов\n• При повторном пинге в течение **42 часов** вы получите мут на **24 часа**\n• Используйте другие способы общения",
                inline=False
            )
            
            embed.add_field(
                name="⏰ Интервал защиты:",
                value="42 часа с момента последнего предупреждения",
                inline=True
            )
            
            embed.add_field(
                name="⚡ Наказание:",
                value="Мут на 24 часа при повторном нарушении",
                inline=True
            )
            
            embed.set_footer(
                text="Система защиты от пинга • Соблюдайте правила общения",
                icon_url=message.guild.icon.url if message.guild.icon else None
            )
            
            # Отправляем предупреждение в тот же канал, где был пинг
            try:
                warning_msg = await message.channel.send(embed=embed)
                logger.info(f"Предупреждение отправлено в канал {message.channel.name} пользователю {message.author.name}")
                
                # Удаляем предупреждение через 30 секунд
                import asyncio
                asyncio.create_task(self._delete_message_later(warning_msg, 30))
                
            except discord.Forbidden:
                logger.error(f"Нет прав для отправки сообщения в канал {message.channel.name}")
            except Exception as e:
                logger.error(f"Ошибка при отправке предупреждения: {e}")
            
        except Exception as e:
            logger.error(f"Ошибка при отправке предупреждения: {e}")

    async def mute_user_for_ping_violation(self, message):
        """Мут пользователя за повторный пинг"""
        try:
            # Удаляем сообщение с пингом
            try:
                await message.delete()
                logger.info(f"Удалено сообщение с повторным пингом от {message.author.name}")
            except Exception as e:
                logger.error(f"Не удалось удалить сообщение: {e}")
            
            # Получаем систему мутов
            if not hasattr(self.bot, 'mute_system'):
                logger.error("Система мутов не найдена")
                return
            
            mute_system = self.bot.mute_system
            
            # Проверяем, не замучен ли уже пользователь
            if mute_system.muted_role in message.author.roles:
                embed = discord.Embed(
                    title="⚠️ Пользователь уже замучен",
                    description=f"{message.author.mention} попытался снова пинговать защищенного пользователя, но уже имеет мут.",
                    color=0xff6b6b
                )
                await message.channel.send(embed=embed)
                return
            
            # Мутим пользователя
            await message.author.add_roles(
                mute_system.muted_role, 
                reason="Повторный пинг защищенного пользователя kobra228"
            )
            
            # Получаем защищенного пользователя
            protected_user = self.bot.get_user(self.protected_user_id)
            protected_mention = protected_user.mention if protected_user else "защищенного пользователя"
            
            # Создаем embed с информацией о муте
            embed = discord.Embed(
                title="🔇 Автоматический мут за нарушение",
                description=f"**{message.author.mention}** получил мут за повторный пинг {protected_mention}",
                color=0xff0000
            )
            
            embed.add_field(
                name="⚡ Причина мута:",
                value="Повторный пинг защищенного пользователя в течение 42 часов",
                inline=False
            )
            
            embed.add_field(
                name="⏰ Длительность:",
                value="24 часа",
                inline=True
            )
            
            end_time = datetime.now() + timedelta(seconds=self.mute_duration)
            embed.add_field(
                name="🕐 Окончание мута:",
                value=f"<t:{int(end_time.timestamp())}:F>",
                inline=True
            )
            
            embed.add_field(
                name="📝 Рекомендация:",
                value="Избегайте пинга данного пользователя в будущем",
                inline=False
            )
            
            embed.set_footer(
                text="Автоматическая система защиты от пинга",
                icon_url=message.guild.icon.url if message.guild.icon else None
            )
            
            # Отправляем уведомление о муте в тот же канал, где был пинг
            try:
                await message.channel.send(embed=embed)
                logger.info(f"Уведомление о муте отправлено в канал {message.channel.name}")
            except discord.Forbidden:
                logger.error(f"Нет прав для отправки сообщения в канал {message.channel.name}")
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления о муте: {e}")
            
            # Дублируем в канал мутов если есть
            if hasattr(mute_system, 'mute_channel') and mute_system.mute_channel:
                try:
                    await mute_system.mute_channel.send(embed=embed)
                    logger.info(f"Дублировано в канал мутов")
                except Exception as e:
                    logger.error(f"Ошибка при отправке в канал мутов: {e}")
            
            # Уведомляем пользователя в ЛС
            try:
                dm_embed = discord.Embed(
                    title="🔇 Вы получили автоматический мут",
                    description=f"Вы были автоматически замучены на сервере **{message.guild.name}**",
                    color=0xff0000
                )
                
                dm_embed.add_field(
                    name="⚡ Причина:",
                    value="Повторный пинг защищенного пользователя",
                    inline=False
                )
                
                dm_embed.add_field(
                    name="⏰ Длительность:",
                    value="24 часа",
                    inline=True
                )
                
                dm_embed.add_field(
                    name="🕐 Окончание:",
                    value=f"<t:{int(end_time.timestamp())}:F>",
                    inline=True
                )
                
                dm_embed.add_field(
                    name="📋 Важно:",
                    value="В будущем избегайте пинга данного пользователя. Система автоматически отслеживает нарушения.",
                    inline=False
                )
                
                await message.author.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # Не можем отправить ЛС
            
            # Создаем задачу для автоматического снятия мута
            import asyncio
            asyncio.create_task(self._auto_unmute_ping_violation(message.author, message.guild.name))
            
            # Обновляем счетчик нарушений
            user_id = str(message.author.id)
            if user_id in self.violations:
                self.violations[user_id]['violation_count'] += 1
                self.violations[user_id]['last_violation'] = datetime.now().isoformat()
                self.save_violations()
            
            logger.info(f"Пользователь {message.author.name} замучен на 24 часа за повторный пинг защищенного пользователя")
            
        except Exception as e:
            logger.error(f"Ошибка при муте за нарушение пинга: {e}")

    async def _auto_unmute_ping_violation(self, user, guild_name):
        """Автоматическое снятие мута за нарушение пинга"""
        try:
            import asyncio
            await asyncio.sleep(self.mute_duration)
            
            # Получаем систему мутов
            if hasattr(self.bot, 'mute_system'):
                mute_system = self.bot.mute_system
                
                # Проверяем, все еще ли пользователь замучен
                if mute_system.muted_role in user.roles:
                    await user.remove_roles(
                        mute_system.muted_role, 
                        reason="Автоматическое снятие мута за пинг (24 часа истекли)"
                    )
                    
                    # Уведомление о снятии мута
                    if hasattr(mute_system, 'mute_channel') and mute_system.mute_channel:
                        unmute_embed = discord.Embed(
                            title="🔊 Мут снят автоматически",
                            description=f"Мут пользователя {user.mention} за пинг защищенного пользователя истек",
                            color=0x00ff00,
                            timestamp=datetime.now()
                        )
                        await mute_system.mute_channel.send(embed=unmute_embed)
                    
                    # Уведомляем пользователя
                    try:
                        dm_embed = discord.Embed(
                            title="🔊 Мут снят",
                            description=f"Ваш мут на сервере **{guild_name}** за пинг защищенного пользователя истек",
                            color=0x00ff00
                        )
                        dm_embed.add_field(
                            name="📋 Напоминание:",
                            value="Помните: избегайте пинга защищенных пользователей",
                            inline=False
                        )
                        await user.send(embed=dm_embed)
                    except discord.Forbidden:
                        pass
            
        except Exception as e:
            logger.error(f"Ошибка при автоматическом снятии мута за пинг: {e}")

    async def _delete_message_later(self, message, delay_seconds):
        """Удалить сообщение через указанное время"""
        try:
            import asyncio
            await asyncio.sleep(delay_seconds)
            await message.delete()
        except:
            pass

async def setup_ping_protection(bot):
    """Настройка системы защиты от пинга"""
    try:
        ping_protection = PingProtectionSystem(bot)
        bot.ping_protection = ping_protection
        
        logger.info("Система защиты от пинга настроена для пользователя kobra228")
        
    except Exception as e:
        logger.error(f"Ошибка при настройке системы защиты от пинга: {e}")
