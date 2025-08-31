"""
Система заявок в администрацию для Discord бота
Обрабатывает заявки в администрацию Minecraft и Discord серверов
"""

import discord
from discord.ext import commands
import logging
from datetime import datetime
from config import (
    MINECRAFT_ADMIN_APPLICATION_CHANNEL_ID,
    MINECRAFT_ADMIN_RESPONSES_CHANNEL_ID,
    MINECRAFT_ADMIN_EMBED_COLOR,
    MINECRAFT_ADMIN_TITLE,
    MINECRAFT_ADMIN_DESCRIPTION,
    MINECRAFT_ADMIN_FIELDS,
    MINECRAFT_ADMIN_BUTTON_LABEL,
    DISCORD_ADMIN_APPLICATION_CHANNEL_ID,
    DISCORD_ADMIN_RESPONSES_CHANNEL_ID,
    DISCORD_ADMIN_EMBED_COLOR,
    DISCORD_ADMIN_TITLE,
    DISCORD_ADMIN_DESCRIPTION,
    DISCORD_ADMIN_FIELDS,
    DISCORD_ADMIN_BUTTON_LABEL
)

logger = logging.getLogger(__name__)

class MinecraftAdminApplicationModal(discord.ui.Modal, title='Заявка в администрацию Minecraft'):
    def __init__(self):
        super().__init__()
        
    minecraft_nick = discord.ui.TextInput(
        label='Ваш ник в Minecraft',
        placeholder='Введите точный игровой ник...',
        required=True,
        max_length=16
    )
    
    reason = discord.ui.TextInput(
        label='Почему именно вас должны взять?',
        placeholder='Расскажите о своих качествах, опыте, мотивации...',
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )
    
    age = discord.ui.TextInput(
        label='Ваш возраст',
        placeholder='Укажите полных лет...',
        required=True,
        max_length=2
    )
    
    experience = discord.ui.TextInput(
        label='Опыт администрирования',
        placeholder='Расскажите о вашем опыте модерирования/администрирования...',
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Проверяем возраст
            try:
                age_num = int(self.age.value)
                if age_num < 16:
                    await interaction.response.send_message(
                        "❌ Минимальный возраст для подачи заявки в администрацию Minecraft - 16 лет.",
                        ephemeral=True
                    )
                    return
            except ValueError:
                await interaction.response.send_message(
                    "❌ Пожалуйста, укажите возраст числом (например: 18).",
                    ephemeral=True
                )
                return
            
            # Создаем embed для заявки
            embed = discord.Embed(
                title="🛡️ Новая заявка в администрацию Minecraft",
                color=MINECRAFT_ADMIN_EMBED_COLOR,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="👤 Подал заявку",
                value=f"{interaction.user.mention}\n`{interaction.user.name}`",
                inline=True
            )
            
            embed.add_field(
                name="🎮 Ник в Minecraft",
                value=f"`{self.minecraft_nick.value}`",
                inline=True
            )
            
            embed.add_field(
                name="🎂 Возраст",
                value=f"{self.age.value} лет",
                inline=True
            )
            
            embed.add_field(
                name="📝 Почему должны взять",
                value=self.reason.value,
                inline=False
            )
            
            if self.experience.value:
                embed.add_field(
                    name="⭐ Опыт администрирования",
                    value=self.experience.value,
                    inline=False
                )
            
            embed.set_footer(
                text=f"ID заявки: {interaction.id}",
                icon_url=interaction.user.display_avatar.url
            )
            
            # Создаем кнопки для рассмотрения заявки
            view = ApplicationReviewView(application_type="minecraft")
            
            # Отправляем заявку в канал рассмотрения
            responses_channel = interaction.guild.get_channel(MINECRAFT_ADMIN_RESPONSES_CHANNEL_ID)
            if responses_channel:
                await responses_channel.send(embed=embed, view=view)
                
                # Отвечаем пользователю
                success_embed = discord.Embed(
                    title="✅ Заявка подана успешно!",
                    description=f"Ваша заявка в администрацию Minecraft отправлена на рассмотрение.\n\nИгровой ник: `{self.minecraft_nick.value}`\nРезультат рассмотрения сообщат в личные сообщения в течение 3-7 дней.",
                    color=0x00ff00
                )
                await interaction.response.send_message(embed=success_embed, ephemeral=True)
                
                logger.info(f'Подана заявка в администрацию Minecraft от {interaction.user.name} (ник: {self.minecraft_nick.value})')
            else:
                await interaction.response.send_message("❌ Ошибка: канал для заявок не найден!", ephemeral=True)
                
        except Exception as e:
            logger.error(f'Ошибка при подаче заявки в администрацию Minecraft: {e}')
            await interaction.response.send_message("❌ Произошла ошибка при подаче заявки. Попробуйте позже.", ephemeral=True)

class DiscordAdminApplicationModal(discord.ui.Modal, title='Заявка в администрацию Discord'):
    def __init__(self):
        super().__init__()
        
    discord_nick = discord.ui.TextInput(
        label='Ваш ник в Discord',
        placeholder='Ваш текущий ник в Discord...',
        required=True,
        max_length=32
    )
    
    reason = discord.ui.TextInput(
        label='Почему именно вас должны взять?',
        placeholder='Расскажите о своих качествах, опыте модерирования Discord...',
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )
    
    age = discord.ui.TextInput(
        label='Ваш возраст',
        placeholder='Укажите полных лет...',
        required=True,
        max_length=2
    )
    
    experience = discord.ui.TextInput(
        label='Опыт модерирования Discord',
        placeholder='Расскажите о вашем опыте работы с Discord, ботами, модерированием...',
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Проверяем возраст
            try:
                age_num = int(self.age.value)
                if age_num < 15:
                    await interaction.response.send_message(
                        "❌ Минимальный возраст для подачи заявки в администрацию Discord - 15 лет.",
                        ephemeral=True
                    )
                    return
            except ValueError:
                await interaction.response.send_message(
                    "❌ Пожалуйста, укажите возраст числом (например: 17).",
                    ephemeral=True
                )
                return
            
            # Создаем embed для заявки
            embed = discord.Embed(
                title="🎫 Новая заявка в администрацию Discord",
                color=DISCORD_ADMIN_EMBED_COLOR,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="👤 Подал заявку",
                value=f"{interaction.user.mention}\n`{interaction.user.name}`",
                inline=True
            )
            
            embed.add_field(
                name="💬 Ник в Discord",
                value=f"`{self.discord_nick.value}`",
                inline=True
            )
            
            embed.add_field(
                name="🎂 Возраст",
                value=f"{self.age.value} лет",
                inline=True
            )
            
            embed.add_field(
                name="📝 Почему должны взять",
                value=self.reason.value,
                inline=False
            )
            
            if self.experience.value:
                embed.add_field(
                    name="⭐ Опыт модерирования Discord",
                    value=self.experience.value,
                    inline=False
                )
            
            embed.set_footer(
                text=f"ID заявки: {interaction.id}",
                icon_url=interaction.user.display_avatar.url
            )
            
            # Создаем кнопки для рассмотрения заявки
            view = ApplicationReviewView(application_type="discord")
            
            # Отправляем заявку в канал рассмотрения
            responses_channel = interaction.guild.get_channel(DISCORD_ADMIN_RESPONSES_CHANNEL_ID)
            if responses_channel:
                await responses_channel.send(embed=embed, view=view)
                
                # Отвечаем пользователю
                success_embed = discord.Embed(
                    title="✅ Заявка подана успешно!",
                    description=f"Ваша заявка в администрацию Discord отправлена на рассмотрение.\n\nDiscord ник: `{self.discord_nick.value}`\nРезультат рассмотрения сообщат в личные сообщения в течение 2-5 дней.",
                    color=0x00ff00
                )
                await interaction.response.send_message(embed=success_embed, ephemeral=True)
                
                logger.info(f'Подана заявка в администрацию Discord от {interaction.user.name} (ник: {self.discord_nick.value})')
            else:
                await interaction.response.send_message("❌ Ошибка: канал для заявок не найден!", ephemeral=True)
                
        except Exception as e:
            logger.error(f'Ошибка при подаче заявки в администрацию Discord: {e}')
            await interaction.response.send_message("❌ Произошла ошибка при подаче заявки. Попробуйте позже.", ephemeral=True)

class ApplicationReviewView(discord.ui.View):
    def __init__(self, application_type):
        super().__init__(timeout=None)
        self.application_type = application_type
    
    @discord.ui.button(label='✅ Принять', style=discord.ButtonStyle.success)
    async def accept_application(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ У вас нет прав администратора", ephemeral=True)
            return
        
        # Логика принятия заявки
        embed = discord.Embed(
            title="✅ Заявка принята",
            description=f"Заявка принята администратором {interaction.user.mention}",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label='❌ Отклонить', style=discord.ButtonStyle.danger)
    async def reject_application(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ У вас нет прав администратора", ephemeral=True)
            return
        
        # Логика отклонения заявки
        embed = discord.Embed(
            title="❌ Заявка отклонена",
            description=f"Заявка отклонена администратором {interaction.user.mention}",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label='📋 На рассмотрении', style=discord.ButtonStyle.secondary)
    async def review_application(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            embed = interaction.message.embeds[0]
            embed.color = 0xffaa00  # Оранжевый - на рассмотрении
            embed.title = embed.title.replace("Новая заявка", "📋 Заявка на рассмотрении")
            
            embed.add_field(
                name="👀 Взял на рассмотрение",
                value=f"{interaction.user.mention}\n⏰ {discord.utils.format_dt(discord.utils.utcnow(), 'R')}",
                inline=True
            )
            
            button.disabled = True
            await interaction.response.edit_message(embed=embed, view=self)
            
            logger.info(f'Заявка в администрацию {self.application_type} взята на рассмотрение пользователем {interaction.user.name}')
        except Exception as e:
            logger.error(f'Ошибка при взятии заявки на рассмотрение: {e}')
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ Ошибка при обработке заявки", ephemeral=True)
                else:
                    await interaction.followup.send("❌ Ошибка при обработке заявки", ephemeral=True)
            except:
                pass

class MinecraftAdminApplicationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label=MINECRAFT_ADMIN_BUTTON_LABEL, style=discord.ButtonStyle.primary, emoji="🛡️")
    async def create_minecraft_application(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = MinecraftAdminApplicationModal()
        await interaction.response.send_modal(modal)

class DiscordAdminApplicationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label=DISCORD_ADMIN_BUTTON_LABEL, style=discord.ButtonStyle.primary, emoji="🎫")
    async def create_discord_application(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = DiscordAdminApplicationModal()
        await interaction.response.send_modal(modal)

async def setup_minecraft_admin_applications(bot):
    """Настройка системы заявок в администрацию Minecraft"""
    try:
        application_channel = bot.get_channel(MINECRAFT_ADMIN_APPLICATION_CHANNEL_ID)
        if not application_channel:
            logger.error(f'Канал для заявок в администрацию Minecraft не найден: {MINECRAFT_ADMIN_APPLICATION_CHANNEL_ID}')
            return
        
        # Создаем красивое сообщение с информацией о заявках
        embed = discord.Embed(
            title=MINECRAFT_ADMIN_TITLE,
            description=MINECRAFT_ADMIN_DESCRIPTION,
            color=MINECRAFT_ADMIN_EMBED_COLOR
        )
        
        # Добавляем поля с информацией
        for field in MINECRAFT_ADMIN_FIELDS:
            embed.add_field(
                name=field["name"],
                value=field["value"],
                inline=field["inline"]
            )
        
        embed.set_footer(
            text="Администрация Limonericx • Присоединяйтесь к нашей команде!",
            icon_url=application_channel.guild.icon.url if application_channel.guild.icon else None
        )
        
        # Создаем кнопку для подачи заявки
        view = MinecraftAdminApplicationView()
        
        # Очищаем канал от старых сообщений бота
        async for message in application_channel.history(limit=10):
            if message.author == bot.user:
                try:
                    await message.delete()
                except:
                    pass
        
        # Отправляем новое сообщение с системой заявок
        await application_channel.send(embed=embed, view=view)
        
        logger.info(f'Система заявок в администрацию Minecraft настроена в канале: {application_channel.name}')
        
    except Exception as e:
        logger.error(f'Ошибка настройки системы заявок в администрацию Minecraft: {e}')

async def setup_discord_admin_applications(bot):
    """Настройка системы заявок в администрацию Discord"""
    try:
        application_channel = bot.get_channel(DISCORD_ADMIN_APPLICATION_CHANNEL_ID)
        if not application_channel:
            logger.error(f'Канал для заявок в администрацию Discord не найден: {DISCORD_ADMIN_APPLICATION_CHANNEL_ID}')
            return
        
        # Создаем красивое сообщение с информацией о заявках
        embed = discord.Embed(
            title=DISCORD_ADMIN_TITLE,
            description=DISCORD_ADMIN_DESCRIPTION,
            color=DISCORD_ADMIN_EMBED_COLOR
        )
        
        # Добавляем поля с информацией
        for field in DISCORD_ADMIN_FIELDS:
            embed.add_field(
                name=field["name"],
                value=field["value"],
                inline=field["inline"]
            )
        
        embed.set_footer(
            text="Администрация Discord Limonericx • Помогите нам модерировать сервер!",
            icon_url=application_channel.guild.icon.url if application_channel.guild.icon else None
        )
        
        # Создаем кнопку для подачи заявки
        view = DiscordAdminApplicationView()
        
        # Очищаем канал от старых сообщений бота
        async for message in application_channel.history(limit=10):
            if message.author == bot.user:
                try:
                    await message.delete()
                except:
                    pass
        
        # Отправляем новое сообщение с системой заявок
        await application_channel.send(embed=embed, view=view)
        
        logger.info(f'Система заявок в администрацию Discord настроена в канале: {application_channel.name}')
        
    except Exception as e:
        logger.error(f'Ошибка настройки системы заявок в администрацию Discord: {e}')