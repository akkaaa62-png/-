"""
Discord Welcome Bot Implementation
Handles member join/leave events and sends appropriate messages
"""

import discord
from discord.ext import commands
import logging
import asyncio
from support_system import setup_support_system
from admin_applications import setup_minecraft_admin_applications, setup_discord_admin_applications
from raid_protection import setup_raid_protection
from raid_protection_buttons import setup_raid_protection_buttons
from verification_system import setup_verification_system
from mute_system import setup_mute_system
from private_chat_system import setup_private_chat_system
from ping_protection import setup_ping_protection
from channel_protection_system import setup_channel_protection
from moderation_logs import setup_moderation_logs
from enhanced_logging_system import setup_enhanced_logging
from music_system import setup_music_system
from auto_recovery_system import setup_auto_recovery, global_error_handler
from command_system import setup_command_system
from mafia_system import setup as setup_mafia_system

from protection_panel_system import setup_protection_panel
from config import (
    DISCORD_TOKEN,
    LIMONERICX_SERVER_ID,
    WELCOME_CHANNEL_ID,
    WELCOME_COLOR,
    GOODBYE_COLOR,
    WELCOME_TITLE,
    WELCOME_DESCRIPTION,
    WELCOME_FIELDS,
    GOODBYE_TITLE,
    GOODBYE_DESCRIPTION,
    WELCOME_BUTTON_ENABLED,
    WELCOME_BUTTON_LABEL,
    WELCOME_BUTTON_URL,
    BOT_COMMAND_PREFIX,
    BOT_ACTIVITY_NAME
)
from datetime import datetime, timedelta
from discord.ui import View, Select

logger = logging.getLogger(__name__)

class DiscordWelcomeBot:
    """Discord bot class for handling welcome and goodbye messages"""

    def __init__(self):
        """Initialize the Discord bot with required intents"""
        # Set up bot intents
        intents = discord.Intents.default()
        intents.members = True  # Required for member join/leave events
        intents.message_content = True  # Required for message content access
        intents.guilds = True  # Required for guild events

        # Initialize bot
        self.bot = commands.Bot(
            command_prefix=BOT_COMMAND_PREFIX,
            intents=intents,
            help_command=None
        )

        # Set up event handlers
        self._setup_events()

    def _setup_events(self):
        """Set up bot event handlers"""

        @self.bot.event
        async def on_ready():
            """Event triggered when bot is ready and connected"""
            logger.info(f'{self.bot.user} подключился к Discord!')
            logger.info(f'Bot ID: {self.bot.user.id}')

            # Set bot activity status
            activity = discord.Game(name=BOT_ACTIVITY_NAME)
            await self.bot.change_presence(activity=activity)

            # Log server information
            guild = self.bot.get_guild(LIMONERICX_SERVER_ID)
            if guild:
                logger.info(f'Подключен к серверу: {guild.name} (ID: {guild.id})')
                logger.info(f'Количество участников: {guild.member_count}')
            else:
                logger.warning(f'Не удалось найти сервер с ID: {LIMONERICX_SERVER_ID}')

            # Check if welcome channel exists
            channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
            if channel:
                logger.info(f'Канал приветствия найден: {channel.name} (ID: {channel.id})')

                # Проверяем права бота в канале
                permissions = channel.permissions_for(guild.me)
                logger.info(f'Права в канале приветствия: send_messages={permissions.send_messages}, embed_links={permissions.embed_links}')
            else:
                logger.error(f'Канал приветствия не найден с ID: {WELCOME_CHANNEL_ID}')

            # --- Система команд ---
            try:
                await setup_command_system(self.bot)
                logger.info('Система команд настроена')
            except Exception as e:
                logger.error(f'Ошибка настройки системы команд: {e}')

            # Setup enhanced logging system FIRST
            try:
                await setup_enhanced_logging(self.bot)
                logger.info('Улучшенная система логирования настроена')
            except Exception as e:
                logger.error(f'Ошибка настройки улучшенной системы логирования: {e}')

            # Setup music system
            try:
                await setup_music_system(self.bot)
                logger.info('Система музыки настроена')
            except Exception as e:
                logger.error(f'Ошибка настройки системы музыки: {e}')

            # Setup support ticket system
            try:
                await setup_support_system(self.bot)
                logger.info('Система тикетов технической поддержки настроена')
            except Exception as e:
                logger.error(f'Ошибка настройки системы поддержки: {e}')

            # Setup admin application systems
            try:
                await setup_minecraft_admin_applications(self.bot)
                logger.info('Система заявок в администрацию Minecraft настроена')
            except Exception as e:
                logger.error(f'Ошибка настройки системы заявок в администрацию Minecraft: {e}')
                import traceback
                logger.error(traceback.format_exc())

            try:
                await setup_discord_admin_applications(self.bot)
                logger.info('Система заявок в администрацию Discord настроена')
            except Exception as e:
                logger.error(f'Ошибка настройки системы заявок в администрацию Discord: {e}')
                import traceback
                logger.error(traceback.format_exc())

            # Setup raid protection system
            try:
                await setup_raid_protection(self.bot)
                logger.info('Система защиты от рейдов настроена')
            except Exception as e:
                logger.error(f'Ошибка настройки системы защиты от рейдов: {e}')

            # Setup raid protection buttons
            try:
                await setup_raid_protection_buttons(self.bot)
                logger.info('Кнопочный интерфейс защиты от рейдов настроен')
            except Exception as e:
                logger.error(f'Ошибка настройки кнопочного интерфейса защиты от рейдов: {e}')

            # Setup verification system
            try:
                await setup_verification_system(self.bot)
                logger.info('Система верификации настроена')
            except Exception as e:
                logger.error(f'Ошибка настройки системы верификации: {e}')

            # Setup mute system
            try:
                await setup_mute_system(self.bot)
                logger.info('Система мутов настроена')
            except Exception as e:
                logger.error(f'Ошибка настройки системы мутов: {e}')

            # Setup private chat system
            try:
                await setup_private_chat_system(self.bot)
                logger.info('Система приватных чатов настроена')
            except Exception as e:
                logger.error(f'Ошибка настройки системы приватных чатов: {e}')

            # Setup ping protection system
            try:
                await setup_ping_protection(self.bot)
                logger.info('Система защиты от пинга настроена')
            except Exception as e:
                logger.error(f'Ошибка настройки системы защиты от пинга: {e}')

            # Setup channel protection system
            try:
                await setup_channel_protection(self.bot)
                logger.info('Система защиты каналов настроена')
            except Exception as e:
                logger.error(f'Ошибка настройки системы защиты каналов: {e}')

            # Setup role system
            try:
                await setup_role_system(self.bot)
                logger.info('Система ролей настроена')
                if hasattr(self.bot, 'role_system'):
                    await setup_role_activity_handlers(self.bot, self.bot.role_system)
                    logger.info('Обработчики активности ролей настроены')
                    # Сразу отправляем задание недели при запуске
                    await self.bot.role_system.update_weekly_goal()
                    logger.info('Новое задание недели отправлено сразу после запуска бота')
            except Exception as e:
                logger.error(f'Ошибка настройки системы ролей: {e}')

            # Setup moderation logs system
            try:
                await setup_moderation_logs(self.bot)
                logger.info('Система логирования модерации настроена')
            except Exception as e:
                logger.error(f'Ошибка настройки системы логирования модерации: {e}')

            # Загружаем отладочные команды
            try:
                if 'debug_commands' not in self.bot.extensions:
                    await self.bot.load_extension('debug_commands')
                    logger.info('Отладочные команды загружены')
                else:
                    logger.warning('Отладочные команды уже были загружены, пропускаю повторную загрузку.')
            except Exception as e:
                logger.warning(f'Не удалось загрузить отладочные команды: {e}')

            # Setup auto recovery system
            try:
                await setup_auto_recovery(self.bot)
                logger.info('Система автоматического восстановления настроена')
            except Exception as e:
                logger.error(f'Ошибка настройки системы автоматического восстановления: {e}')

            # Setup Mafia game system
            try:
                await setup_mafia_system(self.bot)
                logger.info('Система игры Mafia настроена')
            except Exception as e:
                logger.error(f'Ошибка настройки системы игры Mafia: {e}')

            # Setup protection panel system
            try:
                await setup_protection_panel(self.bot)
                logger.info('Панель управления защитой настроена')
            except Exception as e:
                logger.error(f'Ошибка настройки панели управления защитой: {e}')

        @self.bot.event
        async def on_member_join(member):
            """Event triggered when a member joins the server"""
            try:
                logger.info(f'🎉 СОБЫТИЕ ПРИСОЕДИНЕНИЯ: {member.name} (ID: {member.id}) присоединился к серверу {member.guild.name}')
                logger.info(f'🔍 Детали участника: создан {member.created_at}, аватар: {member.display_avatar.url}')
                logger.info(f'🔍 Детали сервера: ID {member.guild.id}, участников: {member.guild.member_count}')

                # Check if the member joined the correct server
                if member.guild.id != LIMONERICX_SERVER_ID:
                    logger.info(f'Пропускаем - участник присоединился к другому серверу: {member.guild.id}')
                    return

                # Get the welcome channel
                channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
                if not channel:
                    logger.error(f'❌ Канал приветствия не найден: {WELCOME_CHANNEL_ID}')
                    # Попробуем найти канал по названию
                    for ch in member.guild.text_channels:
                        if 'привет' in ch.name.lower() or 'welcome' in ch.name.lower():
                            logger.info(f'🔍 Найден альтернативный канал: {ch.name} (ID: {ch.id})')
                            channel = ch
                            break
                    if not channel:
                        logger.error(f'❌ Доступные каналы: {[ch.name for ch in member.guild.text_channels]}')
                        return

                logger.info(f'📝 Отправляем приветствие в канал: {channel.name} (ID: {channel.id})')
                
                # Проверяем права бота в канале
                bot_member = member.guild.get_member(self.bot.user.id)
                if not bot_member:
                    logger.error(f'❌ Бот не найден на сервере')
                    return
                    
                permissions = channel.permissions_for(bot_member)
                logger.info(f'🔍 Права бота в канале: send_messages={permissions.send_messages}, embed_links={permissions.embed_links}, view_channel={permissions.view_channel}')

                if not permissions.view_channel:
                    logger.error(f'❌ Бот не может видеть канал {channel.name}')
                    return

                if not permissions.send_messages:
                    logger.error(f'❌ Бот не может отправлять сообщения в канал {channel.name}')
                    return

                if not permissions.embed_links:
                    logger.error(f'❌ Бот не может отправлять эмбеды в канал {channel.name}')
                    return

                # Create beautiful welcome embed with green sidebar
                embed = discord.Embed(
                    title=WELCOME_TITLE,
                    description=f"{WELCOME_DESCRIPTION}\n\n{member.mention}",
                    color=WELCOME_COLOR
                )

                # Add fields with information
                for field in WELCOME_FIELDS:
                    embed.add_field(
                        name=field["name"],
                        value=field["value"],
                        inline=field["inline"]
                    )

                # Add user avatar as thumbnail
                try:
                    embed.set_thumbnail(url=member.display_avatar.url)
                except Exception as e:
                    logger.warning(f'⚠️ Не удалось установить аватар: {e}')

                # Add footer with server info
                try:
                    footer_text = f"Участник #{member.guild.member_count} • Добро пожаловать!"
                    footer_icon = member.guild.icon.url if member.guild.icon else None
                    embed.set_footer(text=footer_text, icon_url=footer_icon)
                except Exception as e:
                    logger.warning(f'⚠️ Не удалось установить footer: {e}')

                # Send embed message (with button only if enabled and URL provided)
                try:
                    if WELCOME_BUTTON_ENABLED and WELCOME_BUTTON_URL:
                        view = discord.ui.View(timeout=None)
                        button = discord.ui.Button(
                            label=WELCOME_BUTTON_LABEL,
                            url=WELCOME_BUTTON_URL,
                            style=discord.ButtonStyle.link
                        )
                        view.add_item(button)
                        message = await channel.send(embed=embed, view=view)
                    else:
                        message = await channel.send(embed=embed)

                    logger.info(f'✅ Приветствие успешно отправлено для {member.name} (ID сообщения: {message.id})')
                    
                except discord.Forbidden as e:
                    logger.error(f'❌ Нет разрешения для отправки сообщения в канал приветствия: {e}')
                except discord.HTTPException as e:
                    logger.error(f'❌ Ошибка HTTP при отправке приветствия: {e}')
                    # Попробуем отправить простое сообщение без эмбеда
                    try:
                        simple_message = f"🎉 {member.mention} {WELCOME_DESCRIPTION}"
                        await channel.send(simple_message)
                        logger.info(f'✅ Простое приветствие отправлено для {member.name}')
                    except Exception as e2:
                        logger.error(f'❌ Не удалось отправить даже простое приветствие: {e2}')

            except Exception as e:
                logger.error(f'❌ Неожиданная ошибка при приветствии: {e}')
                import traceback
                logger.error(traceback.format_exc())

        @self.bot.event
        async def on_member_remove(member):
            """Event triggered when a member leaves the server"""
            try:
                logger.info(f'👋 СОБЫТИЕ УХОДА: {member.name} (ID: {member.id}) покинул сервер {member.guild.name}')
                logger.info(f'🔍 Участников осталось: {member.guild.member_count}')

                # Check if the member left the correct server
                if member.guild.id != LIMONERICX_SERVER_ID:
                    logger.info(f'Пропускаем - участник покинул другой сервер: {member.guild.id}')
                    return

                # Get the welcome channel
                channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
                if not channel:
                    logger.error(f'❌ Канал приветствия не найден: {WELCOME_CHANNEL_ID}')
                    # Попробуем найти канал по названию
                    for ch in member.guild.text_channels:
                        if 'привет' in ch.name.lower() or 'welcome' in ch.name.lower():
                            logger.info(f'🔍 Найден альтернативный канал: {ch.name} (ID: {ch.id})')
                            channel = ch
                            break
                    if not channel:
                        logger.error(f'❌ Доступные каналы: {[ch.name for ch in member.guild.text_channels]}')
                        return

                # Проверяем права бота в канале
                bot_member = member.guild.get_member(self.bot.user.id)
                if not bot_member:
                    logger.error(f'❌ Бот не найден на сервере')
                    return
                    
                permissions = channel.permissions_for(bot_member)
                if not permissions.view_channel:
                    logger.error(f'❌ Бот не может видеть канал {channel.name}')
                    return

                if not permissions.send_messages:
                    logger.error(f'❌ Бот не может отправлять сообщения в канал {channel.name}')
                    return

                # Create beautiful goodbye embed with orange sidebar
                embed = discord.Embed(
                    title=GOODBYE_TITLE,
                    description=f"{member.mention}\n\n{GOODBYE_DESCRIPTION}",
                    color=GOODBYE_COLOR
                )

                # Add user avatar as thumbnail
                try:
                    embed.set_thumbnail(url=member.display_avatar.url)
                except Exception as e:
                    logger.warning(f'⚠️ Не удалось установить аватар: {e}')

                # Add footer with server info
                try:
                    footer_text = f"До свидания! • Участников осталось: {member.guild.member_count}"
                    footer_icon = member.guild.icon.url if member.guild.icon else None
                    embed.set_footer(text=footer_text, icon_url=footer_icon)
                except Exception as e:
                    logger.warning(f'⚠️ Не удалось установить footer: {e}')

                # Send beautiful embed message
                try:
                    message = await channel.send(embed=embed)
                    logger.info(f'✅ Прощание отправлено для {member.name} (ID сообщения: {message.id})')
                except discord.Forbidden as e:
                    logger.error(f'❌ Нет разрешения для отправки сообщения: {e}')
                except discord.HTTPException as e:
                    logger.error(f'❌ Ошибка HTTP при отправке прощания: {e}')
                    # Попробуем отправить простое сообщение без эмбеда
                    try:
                        simple_message = f"👋 {member.mention} {GOODBYE_DESCRIPTION}"
                        await channel.send(simple_message)
                        logger.info(f'✅ Простое прощание отправлено для {member.name}')
                    except Exception as e2:
                        logger.error(f'❌ Не удалось отправить даже простое прощание: {e2}')

            except Exception as e:
                logger.error(f'❌ Неожиданная ошибка при прощании: {e}')
                import traceback
                logger.error(traceback.format_exc())

        @self.bot.event
        async def on_message(message):
            """Event triggered when a message is sent"""
            # Игнорируем сообщения от ботов
            if message.author.bot:
                return

            try:
                # Обработка сообщений в ЛС
                if isinstance(message.channel, discord.DMChannel):
                    logger.info(f"Получено ЛС от {message.author.name} ({message.author.id}): {message.content}")
                    
                    # Проверяем, идет ли процесс верификации
                    if hasattr(self.bot, 'verification_system'):
                        verification_system = self.bot.verification_system
                        if message.author.id in verification_system.pending_verifications:
                            # Обрабатываем ответ на капчу
                            try:
                                success, response_message = await verification_system.check_captcha_response(
                                    message.author, message.content
                                )
                                logger.info(f"Обработка капчи для {message.author.name}: {response_message}")
                                return  # Не отправляем автоматический ответ во время верификации
                            except Exception as e:
                                logger.error(f"Ошибка при обработке капчи: {e}")
                    
                    # Автоматический ответ в ЛС (только если не идет верификация)
                    try:
                        help_embed = discord.Embed(
                            title="🤖 Привет!",
                            description="Я бот сервера Limonericx.\n\n🔐 **Верификация проходит через капчу в ЛС** - перейдите на сервер и нажмите кнопку.",
                            color=0x9932cc
                        )
                        help_embed.add_field(
                            name="📍 Как пройти верификацию:",
                            value="1. Перейдите в канал верификации\n2. Нажмите кнопку '🔐 Пройти верификацию'\n3. Решите капчу в этих личных сообщениях\n4. Получите роль участника!",
                            inline=False
                        )
                        help_embed.add_field(
                            name="🔗 Полезные каналы",
                            value="• Канал верификации\n• Техническая поддержка\n• Правила сервера",
                            inline=False
                        )
                        await message.author.send(embed=help_embed)
                        logger.info(f"Отправлено информационное сообщение пользователю {message.author.name}")
                    except Exception as e:
                        logger.error(f"Ошибка при отправке информационного сообщения: {e}")
                    
                    # Возвращаемся, чтобы не обрабатывать команды в ЛС
                    return

                # Очистка канала верификации от лишних сообщений
                if hasattr(self.bot, 'verification_system'):
                    verification_system = self.bot.verification_system
                    if hasattr(verification_system, 'verification_channel_id') and message.channel.id == verification_system.verification_channel_id:
                        try:
                            # Удаляем любые сообщения пользователей в канале верификации
                            await message.delete()
                            
                            # Отправляем напоминание о кнопке
                            reminder_embed = discord.Embed(
                                title="🔘 Используйте кнопку",
                                description=f"{message.author.mention}, для верификации нажмите кнопку выше!",
                                color=0xff8c00
                            )
                            reminder = await message.channel.send(embed=reminder_embed)
                            asyncio.create_task(self._delete_reminder_later(reminder, 5))
                            
                        except Exception as e:
                            logger.error(f"Ошибка при очистке канала верификации: {e}")
                            try:
                                await message.delete()
                            except:
                                pass

                        except Exception as e:
                            logger.error(f"Ошибка в обработке сообщения от {message.author}: {e}")

                # Проверяем защиту от пинга (до обработки команд)
                if hasattr(self.bot, 'ping_protection'):
                    await self.bot.ping_protection.check_protected_ping(message)

                # Добавляем опыт за сообщение (система уровней)
                if hasattr(self.bot, 'level_system'):
                    await self.bot.level_system.add_message_xp(message.author)

                # Обрабатываем команды (только не в ЛС)
                if not isinstance(message.channel, discord.DMChannel):
                    # Проверяем ограничения нагрузки
                    if hasattr(self.bot, 'load_protection'):
                        # Проверяем rate limiting
                        if self.bot.load_protection.is_rate_limited(message.author.id, message.author):
                            await message.channel.send("⚠️ Слишком много запросов! Подождите немного.\n\n💡 **Для снятия ограничений нужна роль** <@&1385306542781497425>")
                            return
                            
                        # Проверяем отключенные функции
                        if self.bot.load_protection.is_feature_disabled('commands', message.author):
                            await message.channel.send("⚠️ Команды временно недоступны из-за высокой нагрузки.\n\n💡 **Для снятия ограничений нужна роль** <@&1385306542781497425>")
                            return
                    
                    # Записываем метрики нагрузки
                    if hasattr(self.bot, 'load_protection'):
                        self.bot.load_protection.record_request(
                            message.author.id, 
                            message.channel.id
                        )
                    
                    await self.bot.process_commands(message)
            
            except Exception as e:
                logger.error(f"Ошибка в обработке сообщения от {message.author}: {e}")

        @self.bot.event
        async def on_error(event, *args, **kwargs):
            """Global error handler for bot events"""
            logger.error(f'Ошибка в событии {event}: {args}')
            import traceback
            logger.error(traceback.format_exc())
            
            # Запускаем автоматическое восстановление
            if hasattr(self.bot, 'auto_recovery'):
                await global_error_handler(self.bot, Exception(f"Event error: {event}"), context={"event": event, "args": args, "kwargs": kwargs})

        @self.bot.event
        async def on_interaction(interaction):
            """Handle all interactions including buttons"""
            try:
                logger.info(f'Взаимодействие: {interaction.type} от {interaction.user.name} в {interaction.channel}')
                
                # Если это не команда, то это view взаимодействие
                if interaction.type == discord.InteractionType.component:
                    logger.info(f'Компонент взаимодействие: {interaction.data}')
                    
            except Exception as e:
                logger.error(f'Ошибка в обработке взаимодействия: {e}')
                import traceback
                logger.error(traceback.format_exc())

        @self.bot.event
        async def on_command_error(ctx, error):
            """Handle command errors"""
            if isinstance(error, commands.CommandNotFound):
                return  # Ignore unknown commands

            logger.error(f'Ошибка команды в {ctx.channel}: {error}')

            try:
                await ctx.send(f'Произошла ошибка: {str(error)}')
            except discord.HTTPException:
                logger.error('Не удалось отправить сообщение об ошибке')

        # Команды для мониторинга нагрузки
        @self.bot.command(name='loadstats')
        async def load_stats(ctx):
            """Показывает статистику нагрузки на бота"""
            if not ctx.author.guild_permissions.administrator:
                await ctx.send("❌ У вас нет прав для использования этой команды!")
                return
                
            try:
                if hasattr(self.bot, 'load_protection'):
                    stats = await self.bot.load_protection.get_load_stats()
                    
                    embed = discord.Embed(
                        title="📊 Статистика нагрузки на бота",
                        color=0x00ff00,
                        timestamp=discord.utils.utcnow()
                    )
                    
                    # Уровень нагрузки
                    load_colors = {
                        'normal': 0x00ff00,
                        'medium': 0xffff00,
                        'high': 0xff8800,
                        'critical': 0xff0000
                    }
                    
                    embed.color = load_colors.get(stats.get('current_load_level', 'normal'), 0x00ff00)
                    
                    embed.add_field(
                        name="🔍 Текущее состояние",
                        value=f"**Уровень нагрузки:** {stats.get('current_load_level', 'unknown')}\n"
                              f"**Режим оптимизации:** {'Да' if stats.get('optimization_mode') else 'Нет'}\n"
                              f"**Отключенные функции:** {', '.join(stats.get('disabled_features', [])) or 'Нет'}",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="💻 Системные ресурсы",
                        value=f"**CPU:** {stats.get('cpu_percent', 0):.1f}%\n"
                              f"**RAM:** {stats.get('memory_percent', 0):.1f}% ({stats.get('memory_mb', 0):.1f} MB)\n"
                              f"**Время ответа:** {stats.get('average_response_time', 0):.2f}s",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="📈 Активность",
                        value=f"**Запросы/мин:** {stats.get('requests_per_minute', 0)}\n"
                              f"**Всего запросов:** {stats.get('total_requests', 0)}\n"
                              f"**Медленные ответы:** {stats.get('slow_responses', 0)}",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="⚠️ События",
                        value=f"**Перегрузки:** {stats.get('overload_events', 0)}\n"
                              f"**Оптимизации:** {stats.get('optimizations_applied', 0)}\n"
                              f"**Время работы:** {stats.get('uptime_hours', 0):.1f}ч",
                        inline=True
                    )
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Система защиты от перегрузки не активна!")
                    
            except Exception as e:
                logger.error(f"Ошибка получения статистики нагрузки: {e}")
                await ctx.send("❌ Ошибка получения статистики нагрузки!")

        @self.bot.command(name='loadreset')
        async def load_reset(ctx):
            """Сбрасывает оптимизации нагрузки"""
            if not ctx.author.guild_permissions.administrator:
                await ctx.send("❌ У вас нет прав для использования этой команды!")
                return
                
            try:
                if hasattr(self.bot, 'load_protection'):
                    await self.bot.load_protection.reset_optimizations()
                    await ctx.send("✅ Оптимизации нагрузки сброшены!")
                else:
                    await ctx.send("❌ Система защиты от перегрузки не активна!")
                    
            except Exception as e:
                logger.error(f"Ошибка сброса оптимизаций: {e}")
                await ctx.send("❌ Ошибка сброса оптимизаций!")

        @self.bot.command(name='welcome_test')
        async def welcome_test(ctx):
            """Тестирует систему приветствий"""
            if not ctx.author.guild_permissions.administrator:
                await ctx.send("❌ У вас нет прав для использования этой команды!")
                return
                
            try:
                # Проверяем конфигурацию
                embed = discord.Embed(
                    title="🔍 Диагностика системы приветствий",
                    color=0x0099ff,
                    timestamp=discord.utils.utcnow()
                )
                
                # Проверяем сервер
                guild = self.bot.get_guild(LIMONERICX_SERVER_ID)
                if guild:
                    embed.add_field(
                        name="✅ Сервер",
                        value=f"**Название:** {guild.name}\n**ID:** {guild.id}\n**Участников:** {guild.member_count}",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name="❌ Сервер",
                        value=f"Сервер с ID {LIMONERICX_SERVER_ID} не найден!",
                        inline=True
                    )
                
                # Проверяем канал приветствия
                channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
                if channel:
                    # Проверяем права бота
                    bot_member = guild.get_member(self.bot.user.id) if guild else None
                    if bot_member:
                        permissions = channel.permissions_for(bot_member)
                        embed.add_field(
                            name="✅ Канал приветствия",
                            value=f"**Название:** {channel.name}\n**ID:** {channel.id}\n**Права:** send_messages={permissions.send_messages}, embed_links={permissions.embed_links}",
                            inline=True
                        )
                    else:
                        embed.add_field(
                            name="❌ Канал приветствия",
                            value=f"Бот не найден на сервере!",
                            inline=True
                        )
                else:
                    embed.add_field(
                        name="❌ Канал приветствия",
                        value=f"Канал с ID {WELCOME_CHANNEL_ID} не найден!",
                        inline=True
                    )
                
                # Проверяем конфигурацию
                embed.add_field(
                    name="⚙️ Конфигурация",
                    value=f"**Цвет приветствия:** {hex(WELCOME_COLOR)}\n**Цвет прощания:** {hex(GOODBYE_COLOR)}\n**Кнопка включена:** {WELCOME_BUTTON_ENABLED}",
                    inline=True
                )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Ошибка диагностики приветствий: {e}")
                await ctx.send(f"❌ Ошибка диагностики: {e}")

        @self.bot.command(name='welcome_simulate')
        async def welcome_simulate(ctx):
            """Симулирует приветствие пользователя"""
            if not ctx.author.guild_permissions.administrator:
                await ctx.send("❌ У вас нет прав для использования этой команды!")
                return
                
            try:
                await self.simulate_member_join(ctx.author)
                await ctx.send("✅ Симуляция приветствия выполнена! Проверьте канал приветствия.")
                
            except Exception as e:
                logger.error(f"Ошибка симуляции приветствия: {e}")
                await ctx.send(f"❌ Ошибка симуляции: {e}")

        @self.bot.command(name='goodbye_simulate')
        async def goodbye_simulate(ctx):
            """Симулирует прощание пользователя"""
            if not ctx.author.guild_permissions.administrator:
                await ctx.send("❌ У вас нет прав для использования этой команды!")
                return
                
            try:
                await self.simulate_member_remove(ctx.author)
                await ctx.send("✅ Симуляция прощания выполнена! Проверьте канал приветствия.")
                
            except Exception as e:
                logger.error(f"Ошибка симуляции прощания: {e}")
                await ctx.send(f"❌ Ошибка симуляции: {e}")

        @self.bot.command(name='role_system_check')
        async def role_system_check(ctx):
            """Проверяет и исправляет систему ролей"""
            if not ctx.author.guild_permissions.administrator:
                await ctx.send("❌ У вас нет прав для использования этой команды!")
                return
                
            try:
                embed = discord.Embed(
                    title="🔍 Диагностика системы ролей",
                    color=0x0099ff,
                    timestamp=discord.utils.utcnow()
                )
                
                # Проверяем наличие системы ролей
                if not hasattr(self.bot, 'role_system'):
                    embed.add_field(
                        name="❌ Система ролей",
                        value="Система ролей не инициализирована!",
                        inline=False
                    )
                    embed.add_field(
                        name="🔧 Рекомендация",
                        value="Перезапустите бота или используйте команду `!fix_role_system`",
                        inline=False
                    )
                    await ctx.send(embed=embed)
                    return
                
                role_system = self.bot.role_system
                
                # Проверяем сервер
                if not role_system.guild:
                    embed.add_field(
                        name="❌ Сервер",
                        value="Сервер не найден!",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name="✅ Сервер",
                        value=f"**Название:** {role_system.guild.name}\n**ID:** {role_system.guild.id}",
                        inline=True
                    )
                
                # Проверяем канал ролей
                if not role_system.roles_channel:
                    embed.add_field(
                        name="❌ Канал ролей",
                        value="Канал ролей не найден!",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name="✅ Канал ролей",
                        value=f"**Название:** {role_system.roles_channel.name}\n**ID:** {role_system.roles_channel.id}",
                        inline=True
                    )
                
                # Проверяем задачи
                tasks_status = []
                if hasattr(role_system, 'update_king_of_day') and role_system.update_king_of_day.is_running():
                    tasks_status.append("✅ Обновление короля дня")
                else:
                    tasks_status.append("❌ Обновление короля дня")
                    
                embed.add_field(
                    name="🔄 Задачи",
                    value="\n".join(tasks_status),
                    inline=False
                )
                
                # Проверяем текущее задание недели
                if role_system.current_weekly_task:
                    embed.add_field(
                        name="🎯 Текущее задание недели",
                        value=f"**Название:** {role_system.current_weekly_task['title']}\n**Тип:** {role_system.current_weekly_task['type']}",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="❌ Задание недели",
                        value="Текущее задание не установлено!",
                        inline=False
                    )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Ошибка проверки системы ролей: {e}")
                await ctx.send(f"❌ Ошибка проверки системы ролей: {e}")

        @self.bot.command(name='activity_stats')
        async def activity_stats(ctx, member: discord.Member = None):
            """Показывает статистику активности пользователя или общую статистику"""
            if not ctx.author.guild_permissions.manage_roles:
                await ctx.send("❌ У вас нет прав для использования этой команды!")
                return
                
            try:
                if not hasattr(self.bot, 'role_system'):
                    await ctx.send("❌ Система ролей не инициализирована!")
                    return
                
                role_system = self.bot.role_system
                
                if member:
                    # Статистика конкретного пользователя
                    stats = role_system.get_activity_stats(member.id)
                    embed = discord.Embed(
                        title=f"📊 Статистика активности {member.display_name}",
                        color=0x3498db,
                        timestamp=discord.utils.utcnow()
                    )
                    embed.add_field(
                        name="💬 Сообщения",
                        value=f"{stats['messages']} сообщений",
                        inline=True
                    )
                    embed.add_field(
                        name="🎤 Время в войсе",
                        value=f"{stats['voice_time']} минут",
                        inline=True
                    )
                    embed.add_field(
                        name="👍 Реакции",
                        value=f"{stats['reactions']} реакций",
                        inline=True
                    )
                    embed.add_field(
                        name="📨 Приглашения",
                        value=f"{stats['invites']} приглашений",
                        inline=True
                    )
                else:
                    # Общая статистика
                    stats = role_system.get_activity_stats()
                    embed = discord.Embed(
                        title="📊 Общая статистика активности",
                        color=0x2ecc71,
                        timestamp=discord.utils.utcnow()
                    )
                    embed.add_field(
                        name="👥 Участников",
                        value=f"{stats['total_users']} отслеживается",
                        inline=True
                    )
                    embed.add_field(
                        name="💬 Сообщений",
                        value=f"{stats['total_messages']} всего",
                        inline=True
                    )
                    embed.add_field(
                        name="🎤 Время в войсе",
                        value=f"{stats['total_voice_time']} минут всего",
                        inline=True
                    )
                    embed.add_field(
                        name="👍 Реакций",
                        value=f"{stats['total_reactions']} всего",
                        inline=True
                    )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Ошибка получения статистики активности: {e}")
                await ctx.send(f"❌ Ошибка получения статистики: {e}")

        @self.bot.command(name='welcome_fix')
        async def welcome_fix(ctx):
            """Исправляет проблемы с системой приветствий"""
            if not ctx.author.guild_permissions.administrator:
                await ctx.send("❌ У вас нет прав для использования этой команды!")
                return
                
            try:
                embed = discord.Embed(
                    title="🔧 Исправление системы приветствий",
                    color=0x00ff00,
                    timestamp=discord.utils.utcnow()
                )
                
                # Проверяем и исправляем конфигурацию
                fixes_applied = []
                
                # Проверяем сервер
                guild = self.bot.get_guild(LIMONERICX_SERVER_ID)
                if guild:
                    embed.add_field(
                        name="✅ Сервер",
                        value=f"**Название:** {guild.name}\n**ID:** {guild.id}",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name="❌ Сервер",
                        value=f"Сервер с ID {LIMONERICX_SERVER_ID} не найден!",
                        inline=True
                    )
                    return
                
                # Проверяем канал приветствия
                channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
                if channel:
                    embed.add_field(
                        name="✅ Канал приветствия",
                        value=f"**Название:** {channel.name}\n**ID:** {channel.id}",
                        inline=True
                    )
                else:
                    # Ищем альтернативный канал
                    for ch in guild.text_channels:
                        if 'привет' in ch.name.lower() or 'welcome' in ch.name.lower():
                            embed.add_field(
                                name="🔧 Найден альтернативный канал",
                                value=f"**Название:** {ch.name}\n**ID:** {ch.id}\nОбновите WELCOME_CHANNEL_ID в config.py",
                                inline=True
                            )
                            fixes_applied.append(f"Найден альтернативный канал: {ch.name} (ID: {ch.id})")
                            break
                    else:
                        embed.add_field(
                            name="❌ Канал приветствия",
                            value="Канал не найден! Создайте канал с 'привет' или 'welcome' в названии",
                            inline=True
                        )
                
                # Проверяем права бота
                bot_member = guild.get_member(self.bot.user.id)
                if bot_member and channel:
                    permissions = channel.permissions_for(bot_member)
                    missing_permissions = []
                    
                    if not permissions.view_channel:
                        missing_permissions.append("Просмотр канала")
                    if not permissions.send_messages:
                        missing_permissions.append("Отправка сообщений")
                    if not permissions.embed_links:
                        missing_permissions.append("Отправка эмбедов")
                    
                    if missing_permissions:
                        embed.add_field(
                            name="⚠️ Отсутствующие права",
                            value=f"Боту нужны права: {', '.join(missing_permissions)}",
                            inline=True
                        )
                        fixes_applied.append(f"Необходимо дать права: {', '.join(missing_permissions)}")
                    else:
                        embed.add_field(
                            name="✅ Права бота",
                            value="Все необходимые права есть",
                            inline=True
                        )
                
                # Проверяем конфигурацию
                config_status = []
                if WELCOME_COLOR:
                    config_status.append("✅ Цвет приветствия")
                else:
                    config_status.append("❌ Цвет приветствия")
                    
                if GOODBYE_COLOR:
                    config_status.append("✅ Цвет прощания")
                else:
                    config_status.append("❌ Цвет прощания")
                    
                if WELCOME_TITLE:
                    config_status.append("✅ Заголовок приветствия")
                else:
                    config_status.append("❌ Заголовок приветствия")
                
                embed.add_field(
                    name="⚙️ Конфигурация",
                    value="\n".join(config_status),
                    inline=True
                )
                
                # Рекомендации
                if fixes_applied:
                    embed.add_field(
                        name="🔧 Рекомендации",
                        value="\n".join([f"• {fix}" for fix in fixes_applied]),
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="✅ Система готова",
                        value="Все проверки пройдены успешно!",
                        inline=False
                    )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Ошибка исправления приветствий: {e}")
                await ctx.send(f"❌ Ошибка исправления: {e}")

        @self.bot.command(name='test_welcome_system')
        async def test_welcome_system(ctx):
            """Тестирование системы приветствий и проверка всех систем"""
            if not ctx.author.guild_permissions.administrator:
                await ctx.send("❌ У вас нет прав администратора для использования этой команды!")
                return
                
            try:
                embed = discord.Embed(
                    title="🧪 Тестирование системы приветствий",
                    description="Проверка всех компонентов системы",
                    color=0x0099ff,
                    timestamp=discord.utils.utcnow()
                )
                
                # Проверяем сервер
                guild = self.bot.get_guild(LIMONERICX_SERVER_ID)
                if guild:
                    embed.add_field(
                        name="✅ Сервер",
                        value=f"**Название:** {guild.name}\n**ID:** {guild.id}\n**Участников:** {guild.member_count}",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name="❌ Сервер",
                        value=f"Сервер с ID {LIMONERICX_SERVER_ID} не найден!",
                        inline=True
                    )
                
                # Проверяем канал приветствия
                channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
                if channel:
                    # Проверяем права бота
                    bot_member = guild.get_member(self.bot.user.id) if guild else None
                    if bot_member:
                        permissions = channel.permissions_for(bot_member)
                        embed.add_field(
                            name="✅ Канал приветствия",
                            value=f"**Название:** {channel.name}\n**ID:** {channel.id}\n**Права:** send_messages={permissions.send_messages}, embed_links={permissions.embed_links}",
                            inline=True
                        )
                    else:
                        embed.add_field(
                            name="❌ Канал приветствия",
                            value=f"Бот не найден на сервере!",
                            inline=True
                        )
                else:
                    embed.add_field(
                        name="❌ Канал приветствия",
                        value=f"Канал с ID {WELCOME_CHANNEL_ID} не найден!",
                        inline=True
                    )
                
                # Проверяем систему защиты от рейдов
                if hasattr(self.bot, 'raid_protection'):
                    embed.add_field(
                        name="✅ Система защиты от рейдов",
                        value=f"**Статус:** Активна\n**Режим рейда:** {'Активен' if self.bot.raid_protection.raid_mode else 'Неактивен'}\n**Режим изоляции:** {'Активен' if self.bot.raid_protection.lockdown_mode else 'Неактивен'}",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name="❌ Система защиты от рейдов",
                        value="Система не найдена!",
                        inline=True
                    )
                
                # Проверяем кнопочный интерфейс
                embed.add_field(
                    name="🔘 Кнопочный интерфейс",
                    value="**Команда:** `!raid_buttons` - создать кнопки защиты\n**Команда:** `!raid_help` - справка по защите",
                    inline=False
                )
                
                # Проверяем конфигурацию
                embed.add_field(
                    name="⚙️ Конфигурация",
                    value=f"**Цвет приветствия:** {hex(WELCOME_COLOR)}\n**Цвет прощания:** {hex(GOODBYE_COLOR)}\n**Кнопка включена:** {WELCOME_BUTTON_ENABLED}",
                    inline=True
                )
                
                embed.set_footer(text=f"🆔 Тестировал: {ctx.author.id}")
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Ошибка тестирования системы приветствий: {e}")
                await ctx.send(f"❌ Ошибка тестирования: {e}")

        @self.bot.command(name='create_protection_panel')
        async def create_protection_panel(ctx):
            """Создать панель управления защитой от рейдов"""
            if not ctx.author.guild_permissions.administrator:
                await ctx.send("❌ У вас нет прав администратора для использования этой команды!")
                return
                
            try:
                embed = discord.Embed(
                    title="🛡️ Панель управления защитой от рейдов",
                    description="Управление защитой сервера от рейдов и массовых действий",
                    color=0x0099ff,
                    timestamp=discord.utils.utcnow()
                )
                
                # Добавляем аватар бота
                if self.bot.user.display_avatar:
                    embed.set_thumbnail(url=self.bot.user.display_avatar.url)
                
                embed.add_field(
                    name="🔒 Изоляция",
                    value="Заблокировать сервер - только администраторы смогут писать",
                    inline=False
                )
                
                embed.add_field(
                    name="🔓 Разблокировка",
                    value="Разблокировать сервер - вернуть права участникам",
                    inline=False
                )
                
                embed.add_field(
                    name="📊 Статус",
                    value="Показать текущий статус системы защиты",
                    inline=False
                )
                
                embed.add_field(
                    name="🔄 Обновить",
                    value="Обновить интерфейс и проверить систему",
                    inline=False
                )
                
                embed.add_field(
                    name="📋 Функции защиты",
                    value="""• 🚨 **Автоматическое обнаружение рейдов** - по количеству входов
• 💬 **Защита от спама** - ограничение сообщений
• ⚡ **Контроль модераторов** - лимиты на действия
• 🛡️ **Защита каналов** - логирование удалений
• 🔒 **Режим изоляции** - полная блокировка сервера""",
                    inline=False
                )
                
                embed.set_footer(text=f"🆔 Создал: {ctx.author.id}")
                
                # Создаем кнопки
                from raid_protection_buttons import RaidProtectionView
                view = RaidProtectionView(self.bot.raid_protection)
                
                await ctx.send(embed=embed, view=view)
                
            except Exception as e:
                logger.error(f"Ошибка создания панели защиты: {e}")
                await ctx.send(f"❌ Ошибка создания панели: {e}")

        @self.bot.command(name='test_moderator_protection')
        async def test_moderator_protection(ctx):
            """Тестирование системы защиты от массовых действий модераторов"""
            if not ctx.author.guild_permissions.administrator:
                await ctx.send("❌ У вас нет прав администратора для использования этой команды!")
                return
                
            try:
                embed = discord.Embed(
                    title="🛡️ Тестирование защиты от массовых действий",
                    description="Проверка системы защиты модераторов",
                    color=0x0099ff,
                    timestamp=discord.utils.utcnow()
                )
                
                # Проверяем систему защиты от рейдов
                if hasattr(self.bot, 'raid_protection'):
                    protection = self.bot.raid_protection
                    
                    embed.add_field(
                        name="✅ Система защиты активна",
                        value=f"**Статус:** Работает\n**Режим рейда:** {'Активен' if protection.raid_mode else 'Неактивен'}\n**Режим изоляции:** {'Активен' if protection.lockdown_mode else 'Неактивен'}",
                        inline=True
                    )
                    
                    # Показываем лимиты
                    embed.add_field(
                        name="📊 Лимиты действий",
                        value=f"**Баны:** {protection.MAX_BANS_PER_HOUR}/час\n**Кики:** {protection.MAX_KICKS_PER_HOUR}/час\n**Муты:** {protection.MAX_MUTES_PER_HOUR}/час\n**Удаления каналов:** {protection.MAX_CHANNEL_DELETIONS_PER_HOUR}/час",
                        inline=True
                    )
                    
                    # Статистика действий модераторов
                    total_actions = 0
                    for mod_actions in protection.moderator_actions.values():
                        for action_list in mod_actions.values():
                            total_actions += len(action_list)
                    
                    embed.add_field(
                        name="📈 Статистика действий",
                        value=f"**Всего действий:** {total_actions}\n**Активных модераторов:** {len(protection.moderator_actions)}",
                        inline=True
                    )
                    
                    # Показываем защищенные роли
                    protected_roles_text = ""
                    for role_id in protection.protected_roles:
                        role = ctx.guild.get_role(role_id)
                        if role:
                            protected_roles_text += f"• {role.mention}\n"
                        else:
                            protected_roles_text += f"• <@&{role_id}> (не найдена)\n"
                    
                    if protected_roles_text:
                        embed.add_field(
                            name="🛡️ Защищенные роли",
                            value=protected_roles_text,
                            inline=False
                        )
                    
                    # Информация о функциях защиты
                    embed.add_field(
                        name="🔧 Функции защиты",
                        value="""• **Автоматическое отключение прав** - при превышении лимитов
• **Предупреждения модераторам** - в личные сообщения
• **Уведомления администраторам** - о превышении лимитов
• **Временные ограничения** - автоматическое восстановление
• **Логирование всех действий** - подробные записи""",
                        inline=False
                    )
                    
                else:
                    embed.add_field(
                        name="❌ Система защиты не найдена",
                        value="Система защиты от рейдов не инициализирована!",
                        inline=False
                    )
                
                embed.set_footer(text=f"🆔 Тестировал: {ctx.author.id}")
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Ошибка тестирования защиты модераторов: {e}")
                await ctx.send(f"❌ Ошибка тестирования: {e}")

        @self.bot.command(name='moderator_stats')
        async def moderator_stats(ctx):
            """Показать статистику действий модераторов"""
            if not ctx.author.guild_permissions.manage_guild:
                await ctx.send("❌ У вас нет прав для просмотра статистики модераторов!")
                return
                
            try:
                if not hasattr(self.bot, 'raid_protection'):
                    await ctx.send("❌ Система защиты от рейдов не найдена!")
                    return
                
                protection = self.bot.raid_protection
                
                embed = discord.Embed(
                    title="📊 Статистика действий модераторов",
                    description="Подробная информация о действиях модераторов за последний час",
                    color=0x0099ff,
                    timestamp=discord.utils.utcnow()
                )
                
                if not protection.moderator_actions:
                    embed.add_field(
                        name="📈 Активность",
                        value="За последний час действий модераторов не зафиксировано",
                        inline=False
                    )
                else:
                    for mod_id, actions in protection.moderator_actions.items():
                        member = ctx.guild.get_member(mod_id)
                        if member:
                            mod_name = member.display_name
                            mod_mention = member.mention
                        else:
                            mod_name = f"Пользователь {mod_id}"
                            mod_mention = f"<@{mod_id}>"
                        
                        # Подсчитываем действия за последний час
                        now = datetime.now()
                        cutoff = now - timedelta(hours=1)
                        
                        action_counts = {}
                        for action_type, action_times in actions.items():
                            recent_actions = sum(1 for action_time in action_times if action_time > cutoff)
                            if recent_actions > 0:
                                action_counts[action_type] = recent_actions
                        
                        if action_counts:
                            action_text = ""
                            for action_type, count in action_counts.items():
                                action_text += f"• **{action_type}:** {count}\n"
                            
                            embed.add_field(
                                name=f"👤 {mod_name}",
                                value=f"{mod_mention}\n{action_text}",
                                inline=True
                            )
                
                embed.set_footer(text=f"🆔 Запросил: {ctx.author.id}")
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Ошибка получения статистики модераторов: {e}")
                await ctx.send(f"❌ Ошибка получения статистики: {e}")

        # --- Категории для меню ---
        CATEGORIES = {
            "Обязанности": {
                "emoji": "📝",
                "text": "**Обязанности младшего состава:**\n- Отслеживание нарушений в чате.\n- Рассмотрение жалоб на игроков и донатеров.\n- Проявление активности на Minecraft-сервере и в Discord.\n- Ответы в канале 'Вопрос-Ответ'.\n- Помощь стажерам и администраторам (в зависимости от должности).\n\n*При назначении на пост стажеру присваивается пробный срок. По его истечении стажер может выполнять обязанности самостоятельно. Выход из пробного срока и дальнейшие повышения происходят по усмотрению Главного Администратора.*"
            },
            "Иерархия": {
                "emoji": "🏆",
                "text": "**Система иерархии**\nИерархия — это порядок подчиненности, регулирующий взаимоотношения между низшими и высшими рангами. Соблюдение иерархии — важный аспект в администрации.\n\nИерархия:  <@&1375792232606470185> > <@&1375790652255895553> > <@&1375789810895294504> > <@&1375788638465556572> > <@&1375793459457163466> > <@&1375784491968368720> > <@&1375787383504506960>"
            },
            "Отпуск": {
                "emoji": "🌴",
                "text": "**Система отпусков**\nОтпуск предоставляется сроком на 7 дней в любое удобное время, при условии, что администратор отработал на посту 2 недели. Интервал между отпусками — 4 недели.\n\n*В форс-мажорных обстоятельствах отпуск может быть предоставлен в любое время. За обман — наказание от 1 варна до снятия с должности.*"
            },
            "Зарплата": {
                "emoji": "💰",
                "text": "**Зарплата**\n- Выдается еженедельно в Neru-коинах (можно тратить на сайте).\n- Ответственные: <@&1375784491968368720>\n- Выплата по субботам, возможна задержка до 3 дней.\n- Не выплачивается при варне или в отпуске.\n- Максимум — 900 Neru-коинов.\n- Курс: 1 рубль = 1 Neru-Coin.\n\n**Критерии:**\n- Survival Lite/Ultra: минимум 15 баллов/неделя.\n- BedWars: минимум 25 баллов/неделя.\n- Анархия/Creative+: минимум 15 баллов/неделя."
            },
            "Премии и штрафы": {
                "emoji": "🎁",
                "text": "**Премии**\n- Решают: <@&1375784491968368720>\n- Размер: 30–100 Neru-коинов.\n\n**Штрафы**\n- За нарушение правил или плохую работу.\n- Может включать лишение зарплаты, Neru-коинов или доп. квоту."
            },
            "Баллы и услуги": {
                "emoji": "🎯",
                "text": "**Баллы**\n- 1 правильный пруф = +1 балл.\n- 1 правильно рассмотренная жалоба = +2 балла.\n- Ответ в 'Вопрос-Ответ' = +1 балл.\n\n**Услуги за Neru:**\n- Снять 1 warn = 250 Neru-койнов.\n- Отпуск на 1/2/3 недели = 120/240/480 Neru-койнов."
            },
            "Норма и повышения": {
                "emoji": "📈",
                "text": "**Недельная норма**\n- Подсчет пруфов — каждую пятницу с 17:00 до 00:00 МСК.\n\n**Повышения**\n- Пройти пробный срок.\n- Набрать порог по пруфам за неделю.\n- Отыграть 10 часов на режиме.\n\n*В зависимости от режима количество наказаний варьируется.*"
            },
            "Виды наказаний": {
                "emoji": "⚠️",
                "text": "**Виды наказаний**\n1. Варн — максимум 3, далее снятие и ЧС.\n2. Дизлайк — 7 за неделю = варн.\n3. Предупреждение — 3 за 3 дня = +0.5 warn.\n4. Доп. квота — за легкие недочеты."
            },
            "Правила администрации": {
                "emoji": "📜",
                "text": "**Правила администрации**\n- 1.1 Младшая администрация не может разбирать жалобы на персонал. Наказание: +1 warn.\n- 1.2 Запрещено отвечать в 'Вопрос-Ответ' без разрешения. Наказание: +0.5 warn.\n- ... (и так далее, по списку)"
            },
            "Форма ответов": {
                "emoji": "📝",
                "text": "**Форма ответов на жалобы**\n**Принятие жалобы на игрока:**\nЗдравствуйте, уважаемый игрок!  \n- Нарушитель будет наказан, спасибо за жалобу.\n\n**Принятие жалобы на персонал:**\nЗдравствуйте, уважаемый игрок!  \n- Администратор исправил свою ошибку, с ним была проведена беседа, спасибо за жалобу.\n\n**Отказ жалобы:**\nЗдравствуйте, уважаемый игрок!  \n- Нарушений не выявлено / недостаточно доказательств / жалоба составлена неверно и т.д."
            }
        }

        class RulesSelect(Select):
            def __init__(self):
                options = [
                    discord.SelectOption(
                        label=cat,
                        emoji=data["emoji"],
                        description=cat
                    ) for cat, data in CATEGORIES.items()
                ]
                super().__init__(placeholder="Выберите категорию...", min_values=1, max_values=1, options=options)

            async def callback(self, interaction: discord.Interaction):
                cat = self.values[0]
                data = CATEGORIES[cat]
                embed = discord.Embed(
                    title=f"{data['emoji']} {cat}",
                    description=data["text"],
                    color=0x3498db
                )
                await interaction.response.edit_message(embed=embed, view=self.view)

        class RulesView(View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(RulesSelect())

        # Команда для отправки меню в нужный канал
        @self.bot.command(name="send_staff_rules")
        @commands.has_permissions(administrator=True)
        async def send_staff_rules(ctx):
            channel = self.bot.get_channel(1375942175291867247)
            embed = discord.Embed(
                title="📘 Свод правил для младшего персонала",
                description="Выберите интересующую категорию ниже, чтобы просмотреть подробности.",
                color=0x2ecc71
            )
            await channel.send(embed=embed, view=RulesView())
            await ctx.send("✅ Меню с правилами отправлено в канал для младшего персонала!")

    async def start_bot(self):
        """Start the Discord bot"""
        try:
            logger.info("Запуск Discord бота...")
            
            # Увеличиваем таймаут подключения
            import aiohttp
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30, ttl_dns_cache=300)
            timeout = aiohttp.ClientTimeout(total=60, connect=30)
            
            # Создаем сессию с увеличенным таймаутом
            session = aiohttp.ClientSession(connector=connector, timeout=timeout)
            self.bot.http._HTTPClient__session = session
            
            await self.bot.start(DISCORD_TOKEN)
        except Exception as e:
            logger.error(f"Неожиданная ошибка при запуске бота: {e}")
            logger.info("Бот отключен")
            raise

    async def _delete_reminder_later(self, message, delay_seconds):
        """Удалить напоминание через указанное время"""
        try:
            await asyncio.sleep(delay_seconds)
            await message.delete()
        except:
            pass

    async def simulate_member_join(self, member):
        """Симуляция события присоединения участника для тестирования"""
        logger.info(f'🧪 СИМУЛЯЦИЯ ПРИСОЕДИНЕНИЯ: {member.name}')
        
        try:
            # Проверяем сервер
            if member.guild.id != LIMONERICX_SERVER_ID:
                logger.info(f'Пропускаем - не тот сервер: {member.guild.id}')
                return

            # Получаем канал
            channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
            if not channel:
                logger.error(f'❌ Канал приветствия не найден: {WELCOME_CHANNEL_ID}')
                return

            logger.info(f'📝 Отправляем тестовое приветствие в канал: {channel.name}')

            # Создаем embed
            embed = discord.Embed(
                title="🧪 " + WELCOME_TITLE + " (ТЕСТ)",
                description=f"{WELCOME_DESCRIPTION}\n\n{member.mention}",
                color=WELCOME_COLOR
            )

            # Добавляем поля
            for field in WELCOME_FIELDS:
                embed.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field["inline"]
                )

            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(
                text=f"ТЕСТ • Участник #{member.guild.member_count} • Добро пожаловать!",
                icon_url=member.guild.icon.url if member.guild.icon else None
            )

            # Отправляем
            if WELCOME_BUTTON_ENABLED and WELCOME_BUTTON_URL:
                view = discord.ui.View(timeout=None)
                button = discord.ui.Button(
                    label=WELCOME_BUTTON_LABEL,
                    url=WELCOME_BUTTON_URL,
                    style=discord.ButtonStyle.link
                )
                view.add_item(button)
                message = await channel.send(embed=embed, view=view)
            else:
                message = await channel.send(embed=embed)

            logger.info(f'✅ Тестовое приветствие отправлено (ID: {message.id})')

        except Exception as e:
            logger.error(f'❌ Ошибка в симуляции приветствия: {e}')
            raise

    async def simulate_member_remove(self, member):
        """Симуляция события ухода участника для тестирования"""
        logger.info(f'🧪 СИМУЛЯЦИЯ УХОДА: {member.name}')
        
        try:
            # Проверяем сервер
            if member.guild.id != LIMONERICX_SERVER_ID:
                return

            # Получаем канал
            channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
            if not channel:
                logger.error(f'❌ Канал приветствия не найден: {WELCOME_CHANNEL_ID}')
                return

            # Создаем embed
            embed = discord.Embed(
                title="🧪 " + GOODBYE_TITLE + " (ТЕСТ)",
                description=f"{member.mention}\n\n{GOODBYE_DESCRIPTION}",
                color=GOODBYE_COLOR
            )

            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(
                text=f"ТЕСТ • До свидания! • Участников осталось: {member.guild.member_count}",
                icon_url=member.guild.icon.url if member.guild.icon else None
            )

            message = await channel.send(embed=embed)
            logger.info(f'✅ Тестовое прощание отправлено (ID: {message.id})')

        except Exception as e:
            logger.error(f'❌ Ошибка в симуляции прощания: {e}')
            raise

    def add_command(self, command):
        """Add a custom command to the bot"""
        self.bot.add_command(command)

    async def stop_bot(self):
        """Gracefully stop the bot"""
        logger.info('Остановка бота...')
        if not self.bot.is_closed():
            await self.bot.close()

async def setup_extensions(bot):
    """Настройка всех расширений"""
    try:
        logger.info("Настройка расширений...")
        
        # Настройка систем
        await setup_welcome_system(bot)
        await setup_support_system(bot)
        await setup_admin_applications(bot)
        await setup_verification_system(bot)
        await setup_raid_protection(bot)
        await setup_mute_system(bot)
        await setup_private_chat_system(bot)
        await setup_ping_protection(bot)
        await setup_enhanced_logging(bot)
        await setup_music_system(bot)
        await setup_test_music(bot)  # Добавляем тестовую систему
        
        logger.info("Все расширения настроены")
        
    except Exception as e:
        logger.error(f"Ошибка настройки расширений: {e}")
        import traceback
        logger.error(traceback.format_exc())
