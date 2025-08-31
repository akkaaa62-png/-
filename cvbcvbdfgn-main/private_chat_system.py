
"""
Система приватных чатов для Discord бота
Позволяет пользователям создавать приватные каналы с панелью управления
"""

import discord
from discord.ext import commands
import logging
from datetime import datetime
from config import LIMONERICX_SERVER_ID

logger = logging.getLogger('private_chat')

class PrivateChatControlPanel(discord.ui.View):
    """Панель управления приватным чатом"""
    
    def __init__(self, channel, owner):
        super().__init__(timeout=None)
        self.channel = channel
        self.owner = owner
        self.custom_id = f"private_chat_panel_{channel.id}"
    
    @discord.ui.button(label='👥 Пригласить', style=discord.ButtonStyle.primary, emoji='👥')
    async def invite_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Пригласить пользователя в приватный чат"""
        if interaction.user.id != self.owner.id:
            await interaction.response.send_message("❌ Только владелец может приглашать пользователей!", ephemeral=True)
            return
        
        modal = InviteUserModal(self.channel)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label='🚫 Удалить', style=discord.ButtonStyle.danger, emoji='🚫')
    async def remove_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Удалить пользователя из приватного чата"""
        if interaction.user.id != self.owner.id:
            await interaction.response.send_message("❌ Только владелец может удалять пользователей!", ephemeral=True)
            return
        
        modal = RemoveUserModal(self.channel)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label='⚙️ Настройки', style=discord.ButtonStyle.secondary, emoji='⚙️')
    async def channel_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Настройки канала"""
        if interaction.user.id != self.owner.id:
            await interaction.response.send_message("❌ Только владелец может изменять настройки!", ephemeral=True)
            return
        
        modal = ChannelSettingsModal(self.channel)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label='📋 Участники', style=discord.ButtonStyle.secondary, emoji='📋')
    async def list_members(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Показать список участников"""
        members = []
        for overwrite in self.channel.overwrites:
            if isinstance(overwrite, discord.Member) and overwrite != self.owner:
                members.append(overwrite.mention)
        
        embed = discord.Embed(
            title=f"👥 Участники канала {self.channel.name}",
            color=0x0099ff
        )
        
        embed.add_field(
            name="👑 Владелец",
            value=self.owner.mention,
            inline=False
        )
        
        if members:
            embed.add_field(
                name="👥 Участники",
                value="\n".join(members),
                inline=False
            )
        else:
            embed.add_field(
                name="👥 Участники",
                value="Нет приглашенных участников",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label='🗑️ Удалить чат', style=discord.ButtonStyle.danger, emoji='🗑️')
    async def delete_chat(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Удалить приватный чат"""
        if interaction.user.id != self.owner.id:
            await interaction.response.send_message("❌ Только владелец может удалить чат!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="⚠️ Подтверждение удаления",
            description=f"Вы уверены, что хотите удалить канал {self.channel.mention}?\n\n**Это действие нельзя отменить!**",
            color=0xff0000
        )
        
        confirm_view = ConfirmDeleteView(self.channel)
        await interaction.response.send_message(embed=embed, view=confirm_view, ephemeral=True)

class InviteUserModal(discord.ui.Modal):
    """Модальное окно для приглашения пользователя"""
    
    def __init__(self, channel):
        super().__init__(title="👥 Пригласить пользователя")
        self.channel = channel
    
    user_input = discord.ui.TextInput(
        label="Пользователь",
        placeholder="Введите @пользователь или ID пользователя",
        required=True,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Попытка найти пользователя
            user_text = self.user_input.value.strip()
            user = None
            
            # Если это упоминание пользователя
            if user_text.startswith('<@') and user_text.endswith('>'):
                user_id = user_text[2:-1]
                if user_id.startswith('!'):
                    user_id = user_id[1:]
                user = interaction.guild.get_member(int(user_id))
            
            # Если это ID пользователя
            elif user_text.isdigit():
                user = interaction.guild.get_member(int(user_text))
            
            # Если это имя пользователя
            else:
                user = discord.utils.get(interaction.guild.members, name=user_text)
                if not user:
                    user = discord.utils.get(interaction.guild.members, display_name=user_text)
            
            if not user:
                await interaction.response.send_message("❌ Пользователь не найден!", ephemeral=True)
                return
            
            if user.bot:
                await interaction.response.send_message("❌ Нельзя приглашать ботов!", ephemeral=True)
                return
            
            # Проверяем, есть ли уже доступ
            if self.channel.permissions_for(user).view_channel:
                await interaction.response.send_message(f"❌ {user.mention} уже имеет доступ к каналу!", ephemeral=True)
                return
            
            # Добавляем права доступа
            await self.channel.set_permissions(
                user,
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
                add_reactions=True
            )
            
            # Уведомляем об успехе
            embed = discord.Embed(
                title="✅ Пользователь приглашен!",
                description=f"{user.mention} теперь имеет доступ к каналу {self.channel.mention}",
                color=0x00ff00
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Отправляем уведомление в канал
            welcome_embed = discord.Embed(
                title="👋 Новый участник!",
                description=f"{user.mention} был приглашен в приватный чат!",
                color=0x00ff00
            )
            await self.channel.send(embed=welcome_embed)
            
        except Exception as e:
            logger.error(f"Ошибка при приглашении пользователя: {e}")
            await interaction.response.send_message("❌ Произошла ошибка при приглашении пользователя!", ephemeral=True)

class RemoveUserModal(discord.ui.Modal):
    """Модальное окно для удаления пользователя"""
    
    def __init__(self, channel):
        super().__init__(title="🚫 Удалить пользователя")
        self.channel = channel
    
    user_input = discord.ui.TextInput(
        label="Пользователь",
        placeholder="Введите @пользователь или ID пользователя",
        required=True,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Аналогичная логика поиска пользователя
            user_text = self.user_input.value.strip()
            user = None
            
            if user_text.startswith('<@') and user_text.endswith('>'):
                user_id = user_text[2:-1]
                if user_id.startswith('!'):
                    user_id = user_id[1:]
                user = interaction.guild.get_member(int(user_id))
            elif user_text.isdigit():
                user = interaction.guild.get_member(int(user_text))
            else:
                user = discord.utils.get(interaction.guild.members, name=user_text)
                if not user:
                    user = discord.utils.get(interaction.guild.members, display_name=user_text)
            
            if not user:
                await interaction.response.send_message("❌ Пользователь не найден!", ephemeral=True)
                return
            
            # Проверяем, есть ли доступ
            if not self.channel.permissions_for(user).view_channel:
                await interaction.response.send_message(f"❌ {user.mention} не имеет доступа к каналу!", ephemeral=True)
                return
            
            # Удаляем права доступа
            await self.channel.set_permissions(user, overwrite=None)
            
            embed = discord.Embed(
                title="✅ Пользователь удален!",
                description=f"{user.mention} больше не имеет доступа к каналу {self.channel.mention}",
                color=0xff8800
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Уведомление в канал
            leave_embed = discord.Embed(
                title="👋 Участник покинул чат",
                description=f"{user.mention} был удален из приватного чата",
                color=0xff8800
            )
            await self.channel.send(embed=leave_embed)
            
        except Exception as e:
            logger.error(f"Ошибка при удалении пользователя: {e}")
            await interaction.response.send_message("❌ Произошла ошибка при удалении пользователя!", ephemeral=True)

class ChannelSettingsModal(discord.ui.Modal):
    """Модальное окно для настроек канала"""
    
    def __init__(self, channel):
        super().__init__(title="⚙️ Настройки канала")
        self.channel = channel
    
    name_input = discord.ui.TextInput(
        label="Название канала",
        placeholder="Введите новое название канала",
        required=False,
        max_length=100
    )
    
    topic_input = discord.ui.TextInput(
        label="Описание канала",
        placeholder="Введите описание канала",
        required=False,
        max_length=1024,
        style=discord.TextStyle.paragraph
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            changes = []
            
            if self.name_input.value.strip():
                new_name = self.name_input.value.strip()
                if not new_name.startswith('приватный-'):
                    new_name = f"приватный-{new_name}"
                await self.channel.edit(name=new_name)
                changes.append(f"Название: {new_name}")
            
            if self.topic_input.value.strip():
                await self.channel.edit(topic=self.topic_input.value.strip())
                changes.append(f"Описание: {self.topic_input.value.strip()}")
            
            if changes:
                embed = discord.Embed(
                    title="✅ Настройки обновлены!",
                    description="\n".join(changes),
                    color=0x00ff00
                )
            else:
                embed = discord.Embed(
                    title="ℹ️ Изменений нет",
                    description="Настройки канала не были изменены",
                    color=0x0099ff
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Ошибка при изменении настроек: {e}")
            await interaction.response.send_message("❌ Произошла ошибка при изменении настроек!", ephemeral=True)

class ConfirmDeleteView(discord.ui.View):
    """Подтверждение удаления канала"""
    
    def __init__(self, channel):
        super().__init__(timeout=60)
        self.channel = channel
    
    @discord.ui.button(label='✅ Да, удалить', style=discord.ButtonStyle.danger)
    async def confirm_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_message("🗑️ Канал будет удален через 5 секунд...", ephemeral=True)
            
            import asyncio
            await asyncio.sleep(5)
            
            await self.channel.delete(reason=f"Удален владельцем {interaction.user}")
            
        except Exception as e:
            logger.error(f"Ошибка при удалении канала: {e}")
    
    @discord.ui.button(label='❌ Отмена', style=discord.ButtonStyle.secondary)
    async def cancel_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ Удаление отменено", ephemeral=True)

class CreatePrivateChatModal(discord.ui.Modal):
    """Модальное окно для создания приватного чата"""
    
    def __init__(self):
        super().__init__(title="💬 Создать приватный чат")
    
    chat_name = discord.ui.TextInput(
        label="Название чата",
        placeholder="Введите название для вашего приватного чата",
        required=True,
        max_length=50
    )
    
    chat_description = discord.ui.TextInput(
        label="Описание чата (необязательно)",
        placeholder="Краткое описание вашего приватного чата",
        required=False,
        max_length=200,
        style=discord.TextStyle.paragraph
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            guild = interaction.guild
            user = interaction.user
            
            # Ищем или создаем категорию для приватных чатов
            category = discord.utils.get(guild.categories, name="🔒 Приватные чаты")
            if not category:
                category = await guild.create_category(
                    "🔒 Приватные чаты",
                    overwrites={
                        guild.default_role: discord.PermissionOverwrite(view_channel=False)
                    }
                )
            
            # Создаем канал
            channel_name = f"приватный-{self.chat_name.value.lower().replace(' ', '-')}"
            
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True,
                    add_reactions=True,
                    manage_messages=True
                )
            }
            
            channel = await guild.create_text_channel(
                channel_name,
                category=category,
                overwrites=overwrites,
                topic=self.chat_description.value if self.chat_description.value else f"Приватный чат пользователя {user.display_name}"
            )
            
            # Создаем embed с информацией о чате
            embed = discord.Embed(
                title="🎉 Приватный чат создан!",
                description=f"Добро пожаловать в ваш приватный чат, {user.mention}!",
                color=0x00ff00
            )
            
            embed.add_field(
                name="📋 Информация",
                value=f"**Название:** {self.chat_name.value}\n**Владелец:** {user.mention}\n**Создан:** <t:{int(datetime.now().timestamp())}:F>",
                inline=False
            )
            
            embed.add_field(
                name="🎮 Управление чатом",
                value="Используйте кнопки ниже для управления вашим приватным чатом:",
                inline=False
            )
            
            embed.set_footer(text="Только вы можете управлять этим чатом")
            
            # Панель управления
            control_panel = PrivateChatControlPanel(channel, user)
            
            await channel.send(embed=embed, view=control_panel)
            
            # Ответ пользователю
            success_embed = discord.Embed(
                title="✅ Успешно!",
                description=f"Ваш приватный чат {channel.mention} создан!\nПерейдите в канал для управления им.",
                color=0x00ff00
            )
            
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
            
            logger.info(f"Создан приватный чат {channel.name} пользователем {user.name}")
            
        except Exception as e:
            logger.error(f"Ошибка при создании приватного чата: {e}")
            await interaction.response.send_message("❌ Произошла ошибка при создании приватного чата!", ephemeral=True)

class PrivateChatView(discord.ui.View):
    """Основная панель для создания приватных чатов"""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label='💬 Создать приватный чат', style=discord.ButtonStyle.primary, emoji='💬')
    async def create_private_chat(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Проверяем, есть ли у пользователя уже приватные чаты (лимит 3)
        guild = interaction.guild
        user = interaction.user
        
        user_channels = []
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel) and channel.category:
                if channel.category.name == "🔒 Приватные чаты":
                    permissions = channel.permissions_for(user)
                    if permissions.manage_messages:  # Владелец имеет права на управление сообщениями
                        user_channels.append(channel)
        
        if len(user_channels) >= 3:
            embed = discord.Embed(
                title="❌ Лимит достигнут",
                description="Вы можете создать максимум 3 приватных чата. Удалите один из существующих чатов для создания нового.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        modal = CreatePrivateChatModal()
        await interaction.response.send_modal(modal)

async def setup_private_chat_system(bot):
    """Настройка системы приватных чатов"""
    try:
        guild = bot.get_guild(LIMONERICX_SERVER_ID)
        if not guild:
            logger.error("Сервер не найден")
            return
        
        # Ищем или создаем канал для создания приватных чатов
        channel_name = "💬・создать-приватный-чат"
        channel = discord.utils.get(guild.channels, name=channel_name)
        
        if not channel:
            # Создаем канал
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=False,
                    add_reactions=False
                )
            }
            
            channel = await guild.create_text_channel(
                channel_name,
                overwrites=overwrites,
                topic="Создавайте приватные чаты для общения с друзьями!"
            )
        
        # Создаем embed с информацией
        embed = discord.Embed(
            title="💬 Создание приватных чатов",
            description="Здесь вы можете создать свой собственный приватный чат для общения с друзьями!",
            color=0x0099ff
        )
        
        embed.add_field(
            name="🔹 Что это такое?",
            value="Приватные чаты - это персональные каналы, которые видны только вам и приглашенным пользователям.",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Возможности",
            value="• Приглашать и удалять участников\n• Изменять название и описание\n• Управлять настройками канала\n• Полный контроль над чатом",
            inline=True
        )
        
        embed.add_field(
            name="📋 Ограничения",
            value="• Максимум 3 чата на пользователя\n• Только текстовые каналы\n• Автоудаление неактивных чатов через 30 дней",
            inline=True
        )
        
        embed.add_field(
            name="🚀 Как начать?",
            value="Нажмите кнопку **«Создать приватный чат»** ниже и следуйте инструкциям!",
            inline=False
        )
        
        embed.set_footer(text="💡 Совет: Используйте приватные чаты для организации игр, проектов или просто общения с друзьями!")
        
        # Панель для создания чатов
        view = PrivateChatView()
        
        # Очищаем канал и отправляем новое сообщение
        async for message in channel.history(limit=100):
            try:
                await message.delete()
            except:
                pass
        
        await channel.send(embed=embed, view=view)
        
        logger.info(f"Система приватных чатов настроена в канале: {channel.name}")
        
    except Exception as e:
        logger.error(f"Ошибка при настройке системы приватных чатов: {e}")
