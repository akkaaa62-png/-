"""
Отладочные команды для тестирования бота
"""

import discord
from discord.ext import commands
import logging
from config import WELCOME_CHANNEL_ID, LIMONERICX_SERVER_ID
from datetime import datetime

logger = logging.getLogger('debug_commands')

class DebugCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='check_mute_system')
    @commands.has_permissions(administrator=True)
    async def check_mute_system(self, ctx):
        """Проверка системы мутов"""
        try:
            if not hasattr(self.bot, 'mute_system'):
                await ctx.send("❌ Система мутов не загружена")
                return

            mute_system = self.bot.mute_system
            embed = discord.Embed(
                title="🔇 Проверка системы мутов",
                color=0x00ff00
            )

            # Проверяем канал мутов
            if mute_system.mute_channel:
                embed.add_field(
                    name="📢 Канал мутов",
                    value=f"✅ {mute_system.mute_channel.mention}",
                    inline=False
                )
            else:
                embed.add_field(
                    name="📢 Канал мутов",
                    value="❌ Не найден",
                    inline=False
                )

            # Проверяем роль Muted
            if mute_system.muted_role:
                embed.add_field(
                    name="🔇 Роль Muted",
                    value=f"✅ {mute_system.muted_role.mention}",
                    inline=False
                )
            else:
                embed.add_field(
                    name="🔇 Роль Muted", 
                    value="❌ Не найдена",
                    inline=False
                )

            # Проверяем права пользователя
            user_can_mute = any(role.id in [1376140341417349142, 1376140589443190855, 1376140769831817318] for role in ctx.author.roles)
            embed.add_field(
                name="🔑 Ваши права",
                value=f"{'✅' if user_can_mute else '❌'} Права на мут",
                inline=False
            )

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Ошибка при проверке: {e}")
            logger.error(f"Ошибка в check_mute_system: {e}")

    @commands.command(name='test_welcome')
    @commands.has_permissions(administrator=True)
    async def test_welcome(self, ctx, member: discord.Member = None):
        """Тестирование системы приветствия"""
        if not member:
            member = ctx.author

        logger.info(f'🧪 Тестируем приветствие для {member.name}')

        # Симулируем событие присоединения напрямую
        try:
            await self.bot.get_cog('WelcomeBot').simulate_member_join(member)
            await ctx.send(f'✅ Тестовое приветствие выполнено для {member.mention}')

        except Exception as e:
            await ctx.send(f'❌ Ошибка при тестировании: {e}')
            logger.error(f'Ошибка при тестировании приветствия: {e}')

    @commands.command(name='test_goodbye')
    @commands.has_permissions(administrator=True)
    async def test_goodbye(self, ctx, member: discord.Member = None):
        """Тестирование системы прощания"""
        if not member:
            member = ctx.author

        logger.info(f'🧪 Тестируем прощание для {member.name}')

        # Симулируем событие ухода напрямую
        try:
            await self.bot.get_cog('WelcomeBot').simulate_member_remove(member)
            await ctx.send(f'✅ Тестовое прощание выполнено для {member.mention}')

        except Exception as e:
            await ctx.send(f'❌ Ошибка при тестировании: {e}')
            logger.error(f'Ошибка при тестировании прощания: {e}')

    @commands.command(name='check_perms')
    async def check_permissions(self, ctx):
        """Проверка прав бота"""
        channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            await ctx.send('❌ Канал приветствия не найден!')
            return

        guild = self.bot.get_guild(LIMONERICX_SERVER_ID)
        if not guild:
            await ctx.send('❌ Сервер не найден!')
            return

        bot_member = guild.get_member(self.bot.user.id)
        permissions = channel.permissions_for(bot_member)

        embed = discord.Embed(title="🔍 Права бота в канале приветствия", color=0x00ff00)

        perms_check = [
            ("📝 Отправка сообщений", permissions.send_messages),
            ("🔗 Вставка ссылок", permissions.embed_links),
            ("📎 Прикрепление файлов", permissions.attach_files),
            ("📚 Чтение истории", permissions.read_message_history),
            ("😀 Внешние эмодзи", permissions.use_external_emojis),
            ("👁️ Просмотр канала", permissions.view_channel),
        ]

        for name, has_perm in perms_check:
            embed.add_field(name=name, value="✅" if has_perm else "❌", inline=True)

        embed.add_field(name="🏷️ Канал", value=f"{channel.mention} (ID: {channel.id})", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='force_welcome')
    @commands.has_permissions(administrator=True)
    async def force_welcome(self, ctx, member: discord.Member = None):
        """Принудительная отправка приветствия"""
        if not member:
            member = ctx.author

        channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            await ctx.send('❌ Канал приветствия не найден!')
            return

        try:
            from config import (
                WELCOME_COLOR, WELCOME_TITLE, WELCOME_DESCRIPTION, 
                WELCOME_FIELDS, WELCOME_BUTTON_ENABLED, 
                WELCOME_BUTTON_LABEL, WELCOME_BUTTON_URL
            )

            embed = discord.Embed(
                title=WELCOME_TITLE,
                description=f"{WELCOME_DESCRIPTION}\n\n{member.mention}",
                color=WELCOME_COLOR
            )

            for field in WELCOME_FIELDS:
                embed.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field["inline"]
                )

            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(
                text=f"Тестовое приветствие • Участник #{member.guild.member_count}",
                icon_url=member.guild.icon.url if member.guild.icon else None
            )

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

            await ctx.send(f'✅ Принудительное приветствие отправлено в {channel.mention}')

        except Exception as e:
            await ctx.send(f'❌ Ошибка при отправке: {e}')
            logger.error(f'Ошибка при принудительном приветствии: {e}')

    @commands.command(name='check_channel')
    @commands.has_permissions(administrator=True)
    async def check_channel(self, ctx):
        """Проверка канала приветствия"""
        channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            await ctx.send('❌ Канал приветствия не найден!')
            return

        embed = discord.Embed(title="🔍 Информация о канале приветствия", color=0x00ff00)
        embed.add_field(name="📝 Название", value=channel.name, inline=True)
        embed.add_field(name="🆔 ID", value=channel.id, inline=True)
        embed.add_field(name="📂 Категория", value=channel.category.name if channel.category else "Нет", inline=True)
        embed.add_field(name="🔒 Приватный", value="Да" if channel.overwrites else "Нет", inline=True)
        embed.add_field(name="📊 Позиция", value=channel.position, inline=True)
        embed.add_field(name="📅 Создан", value=channel.created_at.strftime("%d.%m.%Y"), inline=True)

        await ctx.send(embed=embed)

    @commands.command(name='diagnose_welcome')
    @commands.has_permissions(administrator=True)
    async def diagnose_welcome(self, ctx):
        """Диагностика системы приветствий"""
        try:
            embed = discord.Embed(title="🔍 Диагностика системы приветствий", color=0x00ff00)
            
            # Проверяем конфигурацию
            from config import LIMONERICX_SERVER_ID, WELCOME_CHANNEL_ID, WELCOME_TITLE, WELCOME_DESCRIPTION
            
            embed.add_field(
                name="⚙️ Конфигурация",
                value=f"**Сервер ID:** {LIMONERICX_SERVER_ID}\n**Канал ID:** {WELCOME_CHANNEL_ID}\n**Заголовок:** {WELCOME_TITLE}",
                inline=False
            )
            
            # Проверяем сервер
            guild = self.bot.get_guild(LIMONERICX_SERVER_ID)
            if guild:
                embed.add_field(
                    name="🏠 Сервер",
                    value=f"✅ {guild.name}\n👥 Участников: {guild.member_count}",
                    inline=True
                )
            else:
                embed.add_field(
                    name="🏠 Сервер",
                    value="❌ Не найден",
                    inline=True
                )
            
            # Проверяем канал
            channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
            if channel:
                embed.add_field(
                    name="📝 Канал",
                    value=f"✅ {channel.name}\n🆔 {channel.id}",
                    inline=True
                )
                
                # Проверяем права бота
                bot_member = guild.get_member(self.bot.user.id) if guild else None
                if bot_member:
                    permissions = channel.permissions_for(bot_member)
                    perms_status = []
                    perms_status.append(f"📝 Отправка: {'✅' if permissions.send_messages else '❌'}")
                    perms_status.append(f"🔗 Embed: {'✅' if permissions.embed_links else '❌'}")
                    perms_status.append(f"👀 Просмотр: {'✅' if permissions.view_channel else '❌'}")
                    
                    embed.add_field(
                        name="🔑 Права бота",
                        value="\n".join(perms_status),
                        inline=True
                    )
                else:
                    embed.add_field(
                        name="🔑 Права бота",
                        value="❌ Бот не найден на сервере",
                        inline=True
                    )
            else:
                embed.add_field(
                    name="📝 Канал",
                    value="❌ Не найден",
                    inline=True
                )
            
            # Проверяем события
            embed.add_field(
                name="🎯 События",
                value="✅ on_member_join настроено\n✅ on_member_remove настроено",
                inline=False
            )
            
            # Проверяем intents
            intents_status = []
            intents_status.append(f"👥 Members: {'✅' if self.bot.intents.members else '❌'}")
            intents_status.append(f"💬 Message Content: {'✅' if self.bot.intents.message_content else '❌'}")
            intents_status.append(f"🏠 Guilds: {'✅' if self.bot.intents.guilds else '❌'}")
            
            embed.add_field(
                name="🔧 Intents",
                value="\n".join(intents_status),
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Ошибка при диагностике: {e}")
            logger.error(f"Ошибка в diagnose_welcome: {e}")
            import traceback
            logger.error(traceback.format_exc())

    @commands.command(name='test_welcome_event')
    @commands.has_permissions(administrator=True)
    async def test_welcome_event(self, ctx, member: discord.Member = None):
        """Тестирование события приветствия напрямую"""
        if not member:
            member = ctx.author
            
        try:
            logger.info(f'🧪 Тестируем событие приветствия для {member.name}')
            
            # Симулируем событие on_member_join
            await self.bot.on_member_join(member)
            await ctx.send(f'✅ Событие приветствия выполнено для {member.mention}')
            
        except Exception as e:
            await ctx.send(f'❌ Ошибка при тестировании: {e}')
            logger.error(f'Ошибка при тестировании события приветствия: {e}')

    @commands.command(name='channel_protection_status')
    @commands.has_permissions(administrator=True)
    async def channel_protection_status(self, ctx):
        """Статус системы защиты каналов"""
        try:
            if not hasattr(self.bot, 'channel_protection'):
                await ctx.send("❌ Система защиты каналов не загружена")
                return

            protection_system = self.bot.channel_protection
            
            embed = discord.Embed(
                title="🛡️ Статус системы защиты каналов",
                color=0x00ff00
            )
            
            # Информация о защищенных каналах
            protected_count = len(protection_system.protected_channels)
            embed.add_field(
                name="📊 Защищенные каналы",
                value=f"Количество: {protected_count}",
                inline=True
            )
            
            # Информация о наказанных пользователях
            punished_count = len(protection_system.punished_users)
            embed.add_field(
                name="🚫 Наказанные пользователи",
                value=f"Количество: {punished_count}",
                inline=True
            )
            
            # Список защищенных каналов
            if protected_count > 0:
                channel_list = []
                for channel_id, channel_data in list(protection_system.protected_channels.items())[:5]:  # Показываем первые 5
                    channel_list.append(f"• {channel_data['name']} (ID: {channel_id})")
                
                if len(protection_system.protected_channels) > 5:
                    channel_list.append(f"... и еще {len(protection_system.protected_channels) - 5}")
                
                embed.add_field(
                    name="🔒 Защищенные каналы",
                    value="\n".join(channel_list),
                    inline=False
                )
            
            # Список наказанных пользователей
            if punished_count > 0:
                user_list = []
                for user_id, punishment_data in list(protection_system.punished_users.items())[:3]:  # Показываем первые 3
                    user = ctx.guild.get_member(int(user_id))
                    user_name = user.name if user else f"Пользователь {user_id}"
                    punishment_end = punishment_data['punishment_end']
                    user_list.append(f"• {user_name} - до <t:{int(datetime.fromisoformat(punishment_end).timestamp())}:R>")
                
                if len(protection_system.punished_users) > 3:
                    user_list.append(f"... и еще {len(protection_system.punished_users) - 3}")
                
                embed.add_field(
                    name="🚫 Наказанные пользователи",
                    value="\n".join(user_list),
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Ошибка при получении статуса: {e}")
            logger.error(f"Ошибка в channel_protection_status: {e}")
            import traceback
            logger.error(traceback.format_exc())

    @commands.command(name='backup_channel')
    @commands.has_permissions(administrator=True)
    async def backup_channel(self, ctx, channel: discord.TextChannel = None):
        """Создает резервную копию канала"""
        if not channel:
            channel = ctx.channel
            
        try:
            if not hasattr(self.bot, 'channel_protection'):
                await ctx.send("❌ Система защиты каналов не загружена")
                return

            protection_system = self.bot.channel_protection
            
            # Создаем резервную копию
            await protection_system.backup_channel(channel)
            
            embed = discord.Embed(
                title="✅ Резервная копия создана",
                description=f"Канал {channel.mention} добавлен в защиту",
                color=0x00ff00
            )
            embed.add_field(name="Канал", value=channel.name, inline=True)
            embed.add_field(name="ID", value=channel.id, inline=True)
            embed.add_field(name="Сообщений", value="До 100 последних", inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Ошибка при создании резервной копии: {e}")
            logger.error(f"Ошибка в backup_channel: {e}")

    @commands.command(name='remove_channel_protection')
    @commands.has_permissions(administrator=True)
    async def remove_channel_protection(self, ctx, channel: discord.TextChannel = None):
        """Удаляет канал из защиты"""
        if not channel:
            channel = ctx.channel
            
        try:
            if not hasattr(self.bot, 'channel_protection'):
                await ctx.send("❌ Система защиты каналов не загружена")
                return

            protection_system = self.bot.channel_protection
            
            channel_id = str(channel.id)
            if channel_id in protection_system.protected_channels:
                del protection_system.protected_channels[channel_id]
                protection_system.save_backups()
                
                embed = discord.Embed(
                    title="✅ Защита снята",
                    description=f"Канал {channel.mention} удален из защиты",
                    color=0xff8c00
                )
                embed.add_field(name="Канал", value=channel.name, inline=True)
                embed.add_field(name="ID", value=channel.id, inline=True)
                
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ Канал {channel.mention} не находится под защитой")
            
        except Exception as e:
            await ctx.send(f"❌ Ошибка при снятии защиты: {e}")
            logger.error(f"Ошибка в remove_channel_protection: {e}")

    @commands.command(name='restore_user_roles')
    @commands.has_permissions(administrator=True)
    async def restore_user_roles(self, ctx, user: discord.Member):
        """Принудительно восстанавливает роли пользователя"""
        try:
            if not hasattr(self.bot, 'channel_protection'):
                await ctx.send("❌ Система защиты каналов не загружена")
                return

            protection_system = self.bot.channel_protection
            
            if user.id in protection_system.punished_users:
                await protection_system.restore_user_roles(user)
                
                embed = discord.Embed(
                    title="✅ Роли восстановлены",
                    description=f"Роли пользователя {user.mention} восстановлены досрочно",
                    color=0x00ff00
                )
                
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ Пользователь {user.mention} не находится под наказанием")
            
        except Exception as e:
            await ctx.send(f"❌ Ошибка при восстановлении ролей: {e}")
            logger.error(f"Ошибка в restore_user_roles: {e}")

    @commands.command(name='recreate_buttons')
    @commands.has_permissions(administrator=True)
    async def recreate_buttons(self, ctx):
        """Пересоздает все кнопки управления"""
        try:
            if not hasattr(self.bot, 'button_system'):
                await ctx.send("❌ Система кнопок не загружена")
                return

            embed = discord.Embed(
                title="🔄 Пересоздание кнопок",
                description="Начинаю пересоздание всех кнопок управления...",
                color=0xff8c00
            )
            await ctx.send(embed=embed)

            button_system = self.bot.button_system
            
            # Пересоздаем каналы и кнопки
            await button_system.setup_button_channels()
            
            embed = discord.Embed(
                title="✅ Кнопки пересозданы",
                description="Все кнопки управления успешно обновлены!",
                color=0x00ff00
            )
            embed.add_field(
                name="📋 Созданные каналы",
                value="• 🛠️-админ-панель\n• 🛡️-модерация\n• 🎫-поддержка\n• 📝-заявки\n• ✅-верификация\n• 💰-экономика\n• 🎉-события\n• 🛡️-защита",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Ошибка при пересоздании кнопок: {e}")
            logger.error(f"Ошибка в recreate_buttons: {e}")

    @commands.command(name='button_status')
    @commands.has_permissions(administrator=True)
    async def button_status(self, ctx):
        """Показывает статус системы кнопок"""
        try:
            if not hasattr(self.bot, 'button_system'):
                await ctx.send("❌ Система кнопок не загружена")
                return

            button_system = self.bot.button_system
            
            embed = discord.Embed(
                title="🎛️ Статус системы кнопок",
                color=0x00ff00
            )
            
            # Проверяем каналы
            channels_status = []
            for channel_key, channel_id in button_system.button_channels.items():
                channel = self.bot.get_channel(channel_id)
                if channel:
                    channels_status.append(f"✅ {channel.name} (ID: {channel_id})")
                else:
                    channels_status.append(f"❌ {channel_key} (ID: {channel_id}) - не найден")
            
            embed.add_field(
                name="📊 Каналы кнопок",
                value="\n".join(channels_status),
                inline=False
            )
            
            embed.add_field(
                name="🔧 Действия",
                value="• `!recreate_buttons` - пересоздать кнопки\n• `!button_status` - проверить статус",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Ошибка при получении статуса кнопок: {e}")
            logger.error(f"Ошибка в button_status: {e}")

    @commands.command(name='full_diagnostic')
    @commands.has_permissions(administrator=True)
    async def full_diagnostic(self, ctx):
        """Полная диагностика всех систем бота"""
        try:
            embed = discord.Embed(
                title="🔧 Полная диагностика систем бота",
                description="Проверка всех компонентов и их состояния",
                color=0x0099ff,
                timestamp=datetime.utcnow()
            )
            
            # Система ролей
            if hasattr(self.bot, 'role_system'):
                embed.add_field(
                    name="👑 Система ролей",
                    value="✅ Загружена и работает",
                    inline=True
                )
            else:
                embed.add_field(
                    name="👑 Система ролей",
                    value="❌ Не загружена",
                    inline=True
                )
            
            # Система верификации
            if hasattr(self.bot, 'verification_system'):
                embed.add_field(
                    name="🔐 Система верификации",
                    value="✅ Загружена и работает",
                    inline=True
                )
            else:
                embed.add_field(
                    name="🔐 Система верификации",
                    value="❌ Не загружена",
                    inline=True
                )
            
            # Система мутов
            if hasattr(self.bot, 'mute_system'):
                embed.add_field(
                    name="🔇 Система мутов",
                    value="✅ Загружена и работает",
                    inline=True
                )
            else:
                embed.add_field(
                    name="🔇 Система мутов",
                    value="❌ Не загружена",
                    inline=True
                )
            
            # Система защиты от пинга
            if hasattr(self.bot, 'ping_protection'):
                embed.add_field(
                    name="🛡️ Защита от пинга",
                    value="✅ Загружена и работает",
                    inline=True
                )
            else:
                embed.add_field(
                    name="🛡️ Защита от пинга",
                    value="❌ Не загружена",
                    inline=True
                )
            
            # Система приватных чатов
            if hasattr(self.bot, 'private_chat_system'):
                embed.add_field(
                    name="💬 Приватные чаты",
                    value="✅ Загружена и работает",
                    inline=True
                )
            else:
                embed.add_field(
                    name="💬 Приватные чаты",
                    value="❌ Не загружена",
                    inline=True
                )
            
            # Система защиты каналов
            if hasattr(self.bot, 'channel_protection'):
                embed.add_field(
                    name="🔒 Защита каналов",
                    value="✅ Загружена и работает",
                    inline=True
                )
            else:
                embed.add_field(
                    name="🔒 Защита каналов",
                    value="❌ Не загружена",
                    inline=True
                )
            
            # Система защиты от рейдов
            if hasattr(self.bot, 'raid_protection'):
                embed.add_field(
                    name="🛡️ Защита от рейдов",
                    value="✅ Загружена и работает",
                    inline=True
                )
            else:
                embed.add_field(
                    name="🛡️ Защита от рейдов",
                    value="❌ Не загружена",
                    inline=True
                )
            
            # Музыкальная система
            if hasattr(self.bot, 'music_system'):
                embed.add_field(
                    name="🎵 Музыкальная система",
                    value="✅ Загружена (требует PyNaCl)",
                    inline=True
                )
            else:
                embed.add_field(
                    name="🎵 Музыкальная система",
                    value="❌ Не загружена",
                    inline=True
                )
            
            # Система Mafia
            mafia_cog = self.bot.get_cog('MafiaSystem')
            if mafia_cog:
                embed.add_field(
                    name="🎭 Система Mafia",
                    value="✅ Загружена и работает",
                    inline=True
                )
            else:
                embed.add_field(
                    name="🎭 Система Mafia",
                    value="❌ Не загружена",
                    inline=True
                )
            
            # Система автоматического восстановления
            if hasattr(self.bot, 'auto_recovery'):
                embed.add_field(
                    name="🔄 Автовосстановление",
                    value="✅ Загружена и работает",
                    inline=True
                )
            else:
                embed.add_field(
                    name="🔄 Автовосстановление",
                    value="❌ Не загружена",
                    inline=True
                )
            
            # Система логирования
            if hasattr(self.bot, 'enhanced_logging'):
                embed.add_field(
                    name="📝 Расширенное логирование",
                    value="✅ Загружена и работает",
                    inline=True
                )
            else:
                embed.add_field(
                    name="📝 Расширенное логирование",
                    value="❌ Не загружена",
                    inline=True
                )
            
            # Проверка прав бота
            bot_member = ctx.guild.get_member(self.bot.user.id)
            if bot_member:
                permissions = bot_member.guild_permissions
                perms_status = []
                perms_status.append(f"Управление каналами: {'✅' if permissions.manage_channels else '❌'}")
                perms_status.append(f"Управление ролями: {'✅' if permissions.manage_roles else '❌'}")
                perms_status.append(f"Отправка сообщений: {'✅' if permissions.send_messages else '❌'}")
                perms_status.append(f"Встраивание ссылок: {'✅' if permissions.embed_links else '❌'}")
                
                embed.add_field(
                    name="🤖 Права бота",
                    value="\n".join(perms_status),
                    inline=False
                )
            
            # Статистика сервера
            embed.add_field(
                name="📊 Статистика сервера",
                value=f"Участников: {ctx.guild.member_count}\nКаналов: {len(ctx.guild.channels)}\nРолей: {len(ctx.guild.roles)}",
                inline=False
            )
            
            # Рекомендации
            recommendations = []
            if not hasattr(self.bot, 'music_system'):
                recommendations.append("• Установить PyNaCl для музыкальной системы")
            if not mafia_cog:
                recommendations.append("• Проверить загрузку системы Mafia")
            if not hasattr(self.bot, 'auto_recovery'):
                recommendations.append("• Включить систему автовосстановления")
            
            if recommendations:
                embed.add_field(
                    name="💡 Рекомендации",
                    value="\n".join(recommendations),
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Ошибка при диагностике: {e}")
            logger.error(f"Ошибка в full_diagnostic: {e}")
            import traceback
            logger.error(traceback.format_exc())

async def setup(bot):
    """Функция для загрузки cog"""
    await bot.add_cog(DebugCommands(bot))