"""
Система тикетов технической поддержки для Discord бота
Обрабатывает создание тикетов с формой для ника Minecraft и описания проблемы
"""

import discord
from discord.ext import commands
import asyncio
import logging
from datetime import datetime
from config import (
    SUPPORT_CHANNEL_ID,
    SUPPORT_EMBED_COLOR,
    SUPPORT_TITLE,
    SUPPORT_DESCRIPTION,
    SUPPORT_FIELDS,
    SUPPORT_BUTTON_LABEL,
    TICKET_CATEGORIES,
    SUPPORT_ROLE_ID,
    TICKETS_CATEGORY_ID
)

logger = logging.getLogger(__name__)

class TicketModal(discord.ui.Modal, title='Создание тикета тех. поддержки'):
    def __init__(self, ticket_category):
        super().__init__()
        self.ticket_category = ticket_category
        
    minecraft_nick = discord.ui.TextInput(
        label='Ваш ник в Minecraft',
        placeholder='Введите точный ник на сервере...',
        required=True,
        max_length=16
    )
    
    problem_description = discord.ui.TextInput(
        label='Описание проблемы',
        placeholder='Опишите подробно что произошло, когда, при каких обстоятельствах...',
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )
    
    additional_info = discord.ui.TextInput(
        label='Дополнительная информация (необязательно)',
        placeholder='Время события, скриншоты (ссылки), другие детали...',
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Создаем или находим категорию для тикетов
            guild = interaction.guild
            support_role = guild.get_role(SUPPORT_ROLE_ID)
            
            tickets_category = None
            for category in guild.categories:
                if category.name == "🎫 Тикеты поддержки":
                    tickets_category = category
                    break
            
            if not tickets_category:
                # Создаем категорию для тикетов
                tickets_category = await guild.create_category(
                    "🎫 Тикеты поддержки",
                    overwrites={
                        guild.default_role: discord.PermissionOverwrite(view_channel=False),
                        support_role: discord.PermissionOverwrite(
                            view_channel=True,
                            send_messages=True,
                            read_message_history=True,
                            manage_messages=True
                        )
                    }
                )
            
            # Создаем приватный канал для тикета
            ticket_name = f"тикет-{interaction.user.name}-{interaction.id}"[:50]
            
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True
                ),
                support_role: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    manage_messages=True,
                    manage_channels=True
                )
            }
            
            ticket_channel = await guild.create_text_channel(
                ticket_name,
                category=tickets_category,
                overwrites=overwrites,
                topic=f"Тикет поддержки от {interaction.user.name} | Minecraft: {self.minecraft_nick.value}"
            )
            
            # Создаем embed для тикета в приватном канале
            embed = discord.Embed(
                title=f"🎫 Тикет поддержки: {self.ticket_category['label']}",
                color=SUPPORT_EMBED_COLOR,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="👤 Пользователь Discord",
                value=interaction.user.mention,
                inline=True
            )
            
            embed.add_field(
                name="🎮 Ник в Minecraft",
                value=f"`{self.minecraft_nick.value}`",
                inline=True
            )
            
            embed.add_field(
                name="📂 Категория",
                value=f"{self.ticket_category['emoji']} {self.ticket_category['label']}",
                inline=True
            )
            
            embed.add_field(
                name="📝 Описание проблемы",
                value=self.problem_description.value,
                inline=False
            )
            
            if self.additional_info.value:
                embed.add_field(
                    name="ℹ️ Дополнительная информация",
                    value=self.additional_info.value,
                    inline=False
                )
            
            embed.set_footer(
                text=f"ID тикета: {interaction.id} • Канал: #{ticket_channel.name}",
                icon_url=interaction.user.display_avatar.url
            )
            
            # Создаем кнопки для управления тикетом
            view = TicketControlView(ticket_channel)
            
            # Отправляем тикет в приватный канал
            await ticket_channel.send(
                f"Добро пожаловать, {interaction.user.mention}! {support_role.mention if support_role else '@Поддержка'} поможет вам с проблемой.",
                embed=embed,
                view=view
            )
            
            # Отвечаем пользователю
            success_embed = discord.Embed(
                title="✅ Тикет создан успешно!",
                description=f"Ваш приватный тикет создан: {ticket_channel.mention}\n\nМодераторы уже уведомлены и ответят в ближайшее время.",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
            
            logger.info(f'Создан приватный тикет от {interaction.user.name} (Minecraft: {self.minecraft_nick.value}) в канале {ticket_channel.name}')
                
        except Exception as e:
            logger.error(f'Ошибка при создании тикета: {e}')
            await interaction.response.send_message("❌ Произошла ошибка при создании тикета. Попробуйте позже.", ephemeral=True)

class TicketControlView(discord.ui.View):
    def __init__(self, ticket_channel):
        super().__init__(timeout=None)
        self.ticket_channel = ticket_channel
    
    @discord.ui.button(label='✅ Взять в работу', style=discord.ButtonStyle.success)
    async def take_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ У вас нет прав для работы с тикетами", ephemeral=True)
            return
        
        # Логика взятия тикета в работу
        embed = discord.Embed(
            title="✅ Тикет взят в работу",
            description=f"Тикет взят в работу модератором {interaction.user.mention}",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label='🔒 Закрыть тикет', style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ У вас нет прав для закрытия тикетов", ephemeral=True)
            return
        
        # Логика закрытия тикета
        embed = discord.Embed(
            title="🔒 Тикет закрыт",
            description=f"Тикет закрыт модератором {interaction.user.mention}",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class CategorySelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        
    @discord.ui.select(
        placeholder="Выберите категорию проблемы...",
        options=[
            discord.SelectOption(
                label=cat["label"],
                value=cat["value"],
                emoji=cat["emoji"]
            ) for cat in TICKET_CATEGORIES
        ]
    )
    async def select_category(self, interaction: discord.Interaction, select: discord.ui.Select):
        selected_category = next(cat for cat in TICKET_CATEGORIES if cat["value"] == select.values[0])
        modal = TicketModal(selected_category)
        await interaction.response.send_modal(modal)

class SupportTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label=SUPPORT_BUTTON_LABEL, style=discord.ButtonStyle.primary, emoji="🎫")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = CategorySelectView()
        
        embed = discord.Embed(
            title="📋 Выбор категории тикета",
            description="Пожалуйста, выберите категорию, которая лучше всего описывает вашу проблему:",
            color=SUPPORT_EMBED_COLOR
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup_support_system(bot):
    """Настройка системы поддержки"""
    try:
        support_channel = bot.get_channel(SUPPORT_CHANNEL_ID)
        if not support_channel:
            logger.error(f'Канал поддержки не найден: {SUPPORT_CHANNEL_ID}')
            return
        
        # Создаем красивое сообщение с информацией о поддержке
        embed = discord.Embed(
            title=SUPPORT_TITLE,
            description=SUPPORT_DESCRIPTION,
            color=SUPPORT_EMBED_COLOR
        )
        
        # Добавляем поля с информацией
        for field in SUPPORT_FIELDS:
            embed.add_field(
                name=field["name"],
                value=field["value"],
                inline=field["inline"]
            )
        
        embed.set_footer(
            text="Команда поддержки Limonericx • Мы всегда готовы помочь!",
            icon_url=support_channel.guild.icon.url if support_channel.guild.icon else None
        )
        
        # Создаем кнопку для создания тикета
        view = SupportTicketView()
        
        # Очищаем канал от старых сообщений бота (опционально)
        async for message in support_channel.history(limit=10):
            if message.author == bot.user:
                try:
                    await message.delete()
                except:
                    pass
        
        # Отправляем новое сообщение с системой тикетов
        await support_channel.send(embed=embed, view=view)
        
        logger.info(f'Система поддержки настроена в канале: {support_channel.name}')
        
    except Exception as e:
        logger.error(f'Ошибка настройки системы поддержки: {e}')