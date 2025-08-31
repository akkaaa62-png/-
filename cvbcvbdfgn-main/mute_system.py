
"""
Система мутов для Discord бота
Позволяет мутить пользователей через форму вместо команд в чате
"""

import discord
from discord.ext import commands
import asyncio
import logging
from datetime import datetime, timedelta
import re
from config import LIMONERICX_SERVER_ID

logger = logging.getLogger('mute_system')

# ID ролей, которые могут мутить
MUTE_ROLES = [
    1376140341417349142,  # Первая роль
    1376140589443190855,  # Вторая роль  
    1376140769831817318   # Третья роль
]

class MuteModal(discord.ui.Modal, title='Замутить пользователя'):
    def __init__(self, target_user):
        super().__init__()
        self.target_user = target_user
        
    time = discord.ui.TextInput(
        label='Время мута',
        placeholder='Например: 30м, 2ч, 1д, 5с...',
        required=True,
        max_length=10
    )
    
    reason = discord.ui.TextInput(
        label='Причина мута',
        placeholder='Укажите причину мута...',
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            mute_system = interaction.client.mute_system
            
            # Парсим время
            mute_seconds = mute_system.parse_time(self.time.value)
            if mute_seconds <= 0:
                await interaction.response.send_message("❌ Неверный формат времени! Используйте: 30м, 2ч, 1д и т.д.", ephemeral=True)
                return

            # Максимальное время мута - 30 дней
            if mute_seconds > 30 * 86400:
                await interaction.response.send_message("❌ Максимальное время мута - 30 дней!", ephemeral=True)
                return

            # Проверяем, не замучен ли уже пользователь
            if mute_system.muted_role in self.target_user.roles:
                await interaction.response.send_message("❌ Пользователь уже замучен!", ephemeral=True)
                return

            # Мутим пользователя
            await self.target_user.add_roles(mute_system.muted_role, reason=f"Мут от {interaction.user}: {self.reason.value}")

            # Создаем embed с информацией о муте
            embed = discord.Embed(
                title="🔇 Пользователь замучен",
                color=0xff6b6b,
                timestamp=datetime.now()
            )

            embed.add_field(name="👤 Пользователь", value=self.target_user.mention, inline=True)
            embed.add_field(name="👮 Модератор", value=interaction.user.mention, inline=True)
            embed.add_field(name="⏰ Время", value=mute_system.format_time(mute_seconds), inline=True)
            embed.add_field(name="📝 Причина", value=self.reason.value, inline=False)

            # Время окончания мута
            end_time = datetime.now() + timedelta(seconds=mute_seconds)
            embed.add_field(
                name="🕐 Окончание мута",
                value=f"<t:{int(end_time.timestamp())}:F>",
                inline=False
            )

            await interaction.response.send_message(embed=embed)

            # Уведомляем пользователя в ЛС
            try:
                dm_embed = discord.Embed(
                    title="🔇 Вы были замучены",
                    description=f"Вы получили мут на сервере **{interaction.guild.name}**",
                    color=0xff6b6b
                )
                dm_embed.add_field(name="⏰ Время", value=mute_system.format_time(mute_seconds), inline=True)
                dm_embed.add_field(name="📝 Причина", value=self.reason.value, inline=True)
                dm_embed.add_field(name="🕐 Окончание", value=f"<t:{int(end_time.timestamp())}:F>", inline=False)

                await self.target_user.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # Не можем отправить ЛС

            # Создаем задачу для автоматического снятия мута
            asyncio.create_task(mute_system._auto_unmute(self.target_user, mute_seconds, interaction.guild.name))

            logger.info(f"Пользователь {self.target_user.name} замучен модератором {interaction.user.name} на {mute_system.format_time(mute_seconds)}")

        except discord.Forbidden:
            await interaction.response.send_message("❌ У меня нет прав для мута этого пользователя!", ephemeral=True)
        except Exception as e:
            logger.error(f"Ошибка при муте пользователя: {e}")
            await interaction.response.send_message("❌ Произошла ошибка при муте пользователя!", ephemeral=True)

class UnmuteModal(discord.ui.Modal, title='Размутить пользователя'):
    def __init__(self, target_user):
        super().__init__()
        self.target_user = target_user
        
    reason = discord.ui.TextInput(
        label='Причина размута (необязательно)',
        placeholder='Укажите причину размута...',
        required=False,
        max_length=200
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            mute_system = interaction.client.mute_system
            
            # Проверяем, замучен ли пользователь
            if mute_system.muted_role not in self.target_user.roles:
                await interaction.response.send_message("❌ Пользователь не замучен!", ephemeral=True)
                return

            # Размучиваем пользователя
            await self.target_user.remove_roles(mute_system.muted_role, reason=f"Размут от {interaction.user}: {self.reason.value or 'Причина не указана'}")

            # Создаем embed с информацией о размуте
            embed = discord.Embed(
                title="🔊 Пользователь размучен",
                color=0x00ff00,
                timestamp=datetime.now()
            )

            embed.add_field(name="👤 Пользователь", value=self.target_user.mention, inline=True)
            embed.add_field(name="👮 Модератор", value=interaction.user.mention, inline=True)
            
            if self.reason.value:
                embed.add_field(name="📝 Причина", value=self.reason.value, inline=False)

            await interaction.response.send_message(embed=embed)

            # Уведомляем пользователя в ЛС
            try:
                dm_embed = discord.Embed(
                    title="🔊 Вас размутили",
                    description=f"Ваш мут на сервере **{interaction.guild.name}** был снят модератором",
                    color=0x00ff00
                )
                if self.reason.value:
                    dm_embed.add_field(name="📝 Причина", value=self.reason.value, inline=False)
                await self.target_user.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # Не можем отправить ЛС

            logger.info(f"Пользователь {self.target_user.name} размучен модератором {interaction.user.name}")

        except discord.Forbidden:
            await interaction.response.send_message("❌ У меня нет прав для размута этого пользователя!", ephemeral=True)
        except Exception as e:
            logger.error(f"Ошибка при размуте пользователя: {e}")
            await interaction.response.send_message("❌ Произошла ошибка при размуте пользователя!", ephemeral=True)

class UserSelectView(discord.ui.View):
    def __init__(self, action_type):
        super().__init__(timeout=300)
        self.action_type = action_type  # "mute" или "unmute"
    
    @discord.ui.select(
        cls=discord.ui.UserSelect,
        placeholder="Выберите пользователя...",
        min_values=1,
        max_values=1
    )
    async def select_user(self, interaction: discord.Interaction, select: discord.ui.UserSelect):
        selected_user = select.values[0]
        
        # Проверяем, что пользователь не выбрал сам себя
        if selected_user == interaction.user:
            await interaction.response.send_message("❌ Вы не можете замутить/размутить сами себя!", ephemeral=True)
            return

        # Проверяем, что пользователь не выбрал бота
        if selected_user.bot:
            await interaction.response.send_message("❌ Нельзя мутить/размутить ботов!", ephemeral=True)
            return

        # Проверяем, что у пользователя нет защищенных ролей
        member = interaction.guild.get_member(selected_user.id)
        if member and any(role.id in MUTE_ROLES for role in member.roles):
            await interaction.response.send_message("❌ Нельзя мутить/размутить пользователей с правами модератора!", ephemeral=True)
            return

        if self.action_type == "mute":
            modal = MuteModal(member)
        else:
            modal = UnmuteModal(member)
        
        await interaction.response.send_modal(modal)

class MuteControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label='🔇 Замутить пользователя', style=discord.ButtonStyle.danger)
    async def mute_user_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Проверяем права пользователя
        if not any(role.id in MUTE_ROLES for role in interaction.user.roles):
            await interaction.response.send_message("❌ У вас нет прав для мута пользователей!", ephemeral=True)
            return
        
        view = UserSelectView("mute")
        embed = discord.Embed(
            title="🔇 Выбор пользователя для мута",
            description="Выберите пользователя, которого хотите замутить:",
            color=0xff6b6b
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label='🔊 Размутить пользователя', style=discord.ButtonStyle.success)
    async def unmute_user_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Проверяем права пользователя
        if not any(role.id in MUTE_ROLES for role in interaction.user.roles):
            await interaction.response.send_message("❌ У вас нет прав для размута пользователей!", ephemeral=True)
            return
        
        view = UserSelectView("unmute")
        embed = discord.Embed(
            title="🔊 Выбор пользователя для размута",
            description="Выберите пользователя, которого хотите размутить:",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class MuteSystem:
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = LIMONERICX_SERVER_ID
        self.mute_channel = None
        self.muted_role = None

    async def setup(self):
        """Настройка системы мутов"""
        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            logger.error(f"Сервер с ID {self.guild_id} не найден")
            return

        # Создаем канал "🔇・муты"
        channel_name = "🔇・муты"
        existing_channel = discord.utils.get(guild.channels, name=channel_name)

        if not existing_channel:
            try:
                # Создаем канал с правильными правами
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    guild.me: discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=True,
                        manage_messages=True
                    )
                }

                # Добавляем права для ролей, которые могут мутить
                for role_id in MUTE_ROLES:
                    role = guild.get_role(role_id)
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(
                            view_channel=True,
                            send_messages=True
                        )

                self.mute_channel = await guild.create_text_channel(
                    channel_name,
                    overwrites=overwrites,
                    topic="Канал для управления мутами пользователей через формы"
                )
                logger.info(f"Создан канал мутов: {self.mute_channel.name}")
            except Exception as e:
                logger.error(f"Ошибка при создании канала мутов: {e}")
                return
        else:
            self.mute_channel = existing_channel
            logger.info(f"Найден существующий канал мутов: {self.mute_channel.name}")

        # Создаем или находим роль "Muted"
        muted_role = discord.utils.get(guild.roles, name="Muted")
        if not muted_role:
            try:
                muted_role = await guild.create_role(
                    name="Muted",
                    color=discord.Color.dark_gray(),
                    reason="Роль для замученных пользователей"
                )

                # Настраиваем права роли во всех каналах
                for channel in guild.channels:
                    try:
                        if isinstance(channel, discord.TextChannel):
                            await channel.set_permissions(
                                muted_role,
                                send_messages=False,
                                add_reactions=False,
                                create_public_threads=False,
                                create_private_threads=False,
                                send_messages_in_threads=False
                            )
                        elif isinstance(channel, discord.VoiceChannel):
                            await channel.set_permissions(
                                muted_role,
                                speak=False,
                                use_voice_activation=False
                            )
                    except discord.Forbidden:
                        logger.warning(f"Нет прав для настройки роли в канале {channel.name}")
                    except Exception as e:
                        logger.error(f"Ошибка при настройке роли в канале {channel.name}: {e}")

                logger.info("Создана роль Muted с настройкой прав")
            except Exception as e:
                logger.error(f"Ошибка при создании роли Muted: {e}")
                return

        self.muted_role = muted_role

        # Отправляем панель управления в канал
        if self.mute_channel:
            await self.send_mute_panel()

    async def send_mute_panel(self):
        """Отправка панели управления мутами"""
        embed = discord.Embed(
            title="🔇 Система управления мутами",
            description="**Новая система мутов через формы!**\n\nТеперь для мута и размута используются удобные формы вместо команд в чате.",
            color=0xff6b6b
        )

        embed.add_field(
            name="🆕 Как пользоваться:",
            value="• Нажмите кнопку **🔇 Замутить пользователя**\n• Выберите пользователя из списка\n• Заполните форму с временем и причиной\n• Подтвердите мут",
            inline=False
        )

        embed.add_field(
            name="⏰ Форматы времени:",
            value="• `5м` или `5min` - 5 минут\n• `2ч` или `2h` - 2 часа\n• `1д` или `1d` - 1 день\n• `30с` или `30s` - 30 секунд",
            inline=False
        )

        embed.add_field(
            name="✨ Преимущества новой системы:",
            value="• Удобные формы для ввода данных\n• Выбор пользователя из списка\n• Автоматическая проверка прав\n• Красивое оформление\n• Автоматические уведомления",
            inline=False
        )

        embed.add_field(
            name="🔑 Права доступа:",
            value="Использовать систему мутов могут только пользователи с определенными ролями модератора.",
            inline=False
        )

        embed.set_footer(text="Выберите действие с помощью кнопок ниже")

        view = MuteControlView()

        # Очищаем канал от старых сообщений бота
        try:
            async for message in self.mute_channel.history(limit=10):
                if message.author == self.bot.user:
                    await message.delete()
        except:
            pass

        await self.mute_channel.send(embed=embed, view=view)

    def parse_time(self, time_str):
        """Парсинг времени из строки"""
        time_regex = re.compile(r'(\d+)([смчдsmhd])')
        matches = time_regex.findall(time_str.lower())

        total_seconds = 0
        for amount, unit in matches:
            amount = int(amount)
            if unit in ['с', 's']:
                total_seconds += amount
            elif unit in ['м', 'm']:
                total_seconds += amount * 60
            elif unit in ['ч', 'h']:
                total_seconds += amount * 3600
            elif unit in ['д', 'd']:
                total_seconds += amount * 86400

        return total_seconds

    def format_time(self, seconds):
        """Форматирование времени в читаемый вид"""
        if seconds < 60:
            return f"{seconds} сек."
        elif seconds < 3600:
            return f"{seconds // 60} мин."
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            if minutes > 0:
                return f"{hours} ч. {minutes} мин."
            return f"{hours} ч."
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            if hours > 0:
                return f"{days} д. {hours} ч."
            return f"{days} д."

    async def _auto_unmute(self, user, mute_seconds, guild_name):
        """Автоматическое снятие мута через указанное время"""
        try:
            await asyncio.sleep(mute_seconds)
            
            # Проверяем, все еще ли пользователь на сервере и замучен
            if self.muted_role in user.roles:
                await user.remove_roles(self.muted_role, reason="Автоматическое снятие мута")

                # Уведомление о снятии мута
                unmute_embed = discord.Embed(
                    title="🔊 Мут снят автоматически",
                    description=f"Мут пользователя {user.mention} истек",
                    color=0x00ff00,
                    timestamp=datetime.now()
                )
                await self.mute_channel.send(embed=unmute_embed)

                # Уведомляем пользователя
                try:
                    dm_embed = discord.Embed(
                        title="🔊 Мут снят",
                        description=f"Ваш мут на сервере **{guild_name}** истек",
                        color=0x00ff00
                    )
                    await user.send(embed=dm_embed)
                except discord.Forbidden:
                    pass
                except Exception as e:
                    logger.error(f"Ошибка при отправке ЛС о размуте: {e}")
                    
        except Exception as e:
            logger.error(f"Ошибка при автоматическом снятии мута: {e}")

async def setup_mute_system(bot):
    """Настройка системы мутов"""
    try:
        mute_system = MuteSystem(bot)
        await mute_system.setup()

        bot.mute_system = mute_system
        logger.info("Система мутов настроена")

    except Exception as e:
        logger.error(f"Ошибка при настройке системы мутов: {e}")
