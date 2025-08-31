"""
Система автоматической панели управления защитой
Создает канал "🛡️-защита" с кнопками управления
"""

import discord
from discord.ext import commands
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger('protection_panel')

class ProtectionPanelView(discord.ui.View):
    """Панель управления защитой с кнопками"""
    
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(label="🔒 Изоляция", style=discord.ButtonStyle.danger, custom_id="protection_lockdown")
    async def lockdown_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Включить режим изоляции сервера"""
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Ошибка доступа",
                description="У вас нет прав администратора для использования этой функции",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            if hasattr(self.bot, 'raid_protection'):
                protection = self.bot.raid_protection
                
                if protection.lockdown_mode:
                    embed = discord.Embed(
                        title="❌ Режим изоляции уже активен",
                        description="Сервер уже заблокирован",
                        color=0xff0000,
                        timestamp=datetime.utcnow()
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                
                # Активируем режим изоляции
                protection.lockdown_mode = True
                guild = interaction.guild
                
                # Отключаем сообщения для @everyone
                everyone_role = guild.default_role
                permissions = everyone_role.permissions
                permissions.send_messages = False
                permissions.add_reactions = False
                await everyone_role.edit(permissions=permissions)
                
                embed = discord.Embed(
                    title="🔒 РЕЖИМ ИЗОЛЯЦИИ АКТИВИРОВАН",
                    description="Сервер заблокирован. Только администраторы могут писать сообщения.",
                    color=0xff0000,
                    timestamp=datetime.utcnow()
                )
                
                embed.add_field(
                    name="👤 Активировал",
                    value=f"{interaction.user.mention}",
                    inline=True
                )
                
                embed.add_field(
                    name="⏰ Время",
                    value=f"<t:{int(datetime.utcnow().timestamp())}:F>",
                    inline=True
                )
                
                embed.add_field(
                    name="📋 Статус",
                    value="🔴 Сервер заблокирован",
                    inline=False
                )
                
                await interaction.response.send_message(embed=embed)
                
                # Логируем событие
                if hasattr(protection, 'log_security_event'):
                    await protection.log_security_event(
                        "РЕЖИМ ИЗОЛЯЦИИ АКТИВИРОВАН",
                        f"Режим изоляции активирован администратором {interaction.user.mention}.",
                        color=0xff0000
                    )
                
            else:
                embed = discord.Embed(
                    title="❌ Система защиты не найдена",
                    description="Система защиты от рейдов не инициализирована",
                    color=0xff0000,
                    timestamp=datetime.utcnow()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
        except Exception as e:
            logger.error(f"Ошибка при активации режима изоляции: {e}")
            embed = discord.Embed(
                title="❌ Ошибка",
                description=f"Не удалось активировать режим изоляции: {str(e)}",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔓 Разблокировка", style=discord.ButtonStyle.success, custom_id="protection_unlock")
    async def unlock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Отключить режим изоляции сервера"""
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Ошибка доступа",
                description="У вас нет прав администратора для использования этой функции",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            if hasattr(self.bot, 'raid_protection'):
                protection = self.bot.raid_protection
                
                if not protection.lockdown_mode:
                    embed = discord.Embed(
                        title="❌ Режим изоляции не активен",
                        description="Сервер не заблокирован",
                        color=0xff0000,
                        timestamp=datetime.utcnow()
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                
                # Отключаем режим изоляции
                protection.lockdown_mode = False
                guild = interaction.guild
                
                # Возвращаем права на сообщения
                everyone_role = guild.default_role
                permissions = everyone_role.permissions
                permissions.send_messages = True
                permissions.add_reactions = True
                await everyone_role.edit(permissions=permissions)
                
                embed = discord.Embed(
                    title="🔓 РЕЖИМ ИЗОЛЯЦИИ ОТКЛЮЧЕН",
                    description="Сервер разблокирован. Участники снова могут писать сообщения.",
                    color=0x00ff00,
                    timestamp=datetime.utcnow()
                )
                
                embed.add_field(
                    name="👤 Отключил",
                    value=f"{interaction.user.mention}",
                    inline=True
                )
                
                embed.add_field(
                    name="⏰ Время",
                    value=f"<t:{int(datetime.utcnow().timestamp())}:F>",
                    inline=True
                )
                
                embed.add_field(
                    name="📋 Статус",
                    value="🟢 Сервер разблокирован",
                    inline=False
                )
                
                await interaction.response.send_message(embed=embed)
                
                # Логируем событие
                if hasattr(protection, 'log_security_event'):
                    await protection.log_security_event(
                        "РЕЖИМ ИЗОЛЯЦИИ ОТКЛЮЧЕН",
                        f"Режим изоляции отключен администратором {interaction.user.mention}.",
                        color=0x00ff00
                    )
                
            else:
                embed = discord.Embed(
                    title="❌ Система защиты не найдена",
                    description="Система защиты от рейдов не инициализирована",
                    color=0xff0000,
                    timestamp=datetime.utcnow()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
        except Exception as e:
            logger.error(f"Ошибка при отключении режима изоляции: {e}")
            embed = discord.Embed(
                title="❌ Ошибка",
                description=f"Не удалось отключить режим изоляции: {str(e)}",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📊 Статус", style=discord.ButtonStyle.primary, custom_id="protection_status")
    async def status_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Показать статус системы защиты"""
        if not interaction.user.guild_permissions.manage_guild:
            embed = discord.Embed(
                title="❌ Ошибка доступа",
                description="У вас нет прав для просмотра статуса защиты",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            embed = discord.Embed(
                title="🛡️ Статус системы защиты",
                description="Текущее состояние всех систем защиты сервера",
                color=0x0099ff,
                timestamp=datetime.utcnow()
            )
            
            if hasattr(self.bot, 'raid_protection'):
                protection = self.bot.raid_protection
                
                # Статус режимов
                embed.add_field(
                    name="🔒 Режим изоляции",
                    value="🟢 Активен" if protection.lockdown_mode else "🔴 Неактивен",
                    inline=True
                )
                
                embed.add_field(
                    name="🚨 Режим рейда",
                    value="🟢 Активен" if protection.raid_mode else "🔴 Неактивен",
                    inline=True
                )
                
                embed.add_field(
                    name="📈 Активность",
                    value=f"**Входов за минуту:** {len(protection.recent_joins)}\n**Сообщений за минуту:** {len(protection.recent_messages)}",
                    inline=True
                )
                
                # Настройки защиты
                embed.add_field(
                    name="⚙️ Настройки защиты",
                    value=f"""• Максимум входов в минуту: `{protection.MAX_JOINS_PER_MINUTE}`
• Максимум сообщений в минуту: `{protection.MAX_MESSAGES_PER_MINUTE}`
• Максимум банов в час: `{protection.MAX_BANS_PER_HOUR}` (автоотключение на 2ч)
• Максимум киков в час: `{protection.MAX_KICKS_PER_HOUR}` (автоотключение на 1ч)
• Максимум мутов в час: `{protection.MAX_MUTES_PER_HOUR}` (предупреждение)
• Максимум удалений каналов в час: `{protection.MAX_CHANNEL_DELETIONS_PER_HOUR}` (автоотключение на 4ч)""",
                    inline=False
                )
                
                # Защищенные роли
                protected_roles_text = ""
                for role_id in protection.protected_roles:
                    role = interaction.guild.get_role(role_id)
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
                
            else:
                embed.add_field(
                    name="❌ Система защиты не найдена",
                    value="Система защиты от рейдов не инициализирована!",
                    inline=False
                )
            
            embed.set_footer(text=f"🆔 Запросил: {interaction.user.id}")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Ошибка при получении статуса защиты: {e}")
            embed = discord.Embed(
                title="❌ Ошибка",
                description=f"Не удалось получить статус защиты: {str(e)}",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔄 Обновить", style=discord.ButtonStyle.secondary, custom_id="protection_refresh")
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Обновить интерфейс защиты"""
        if not interaction.user.guild_permissions.manage_guild:
            embed = discord.Embed(
                title="❌ Ошибка доступа",
                description="У вас нет прав для обновления интерфейса",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            embed = discord.Embed(
                title="✅ Интерфейс обновлен",
                description="Панель управления защитой обновлена",
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="🔄 Статус",
                value="Интерфейс успешно обновлен",
                inline=True
            )
            
            embed.add_field(
                name="⏰ Время",
                value=f"<t:{int(datetime.utcnow().timestamp())}:F>",
                inline=True
            )
            
            embed.set_footer(text=f"🆔 Обновил: {interaction.user.id}")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении интерфейса: {e}")
            embed = discord.Embed(
                title="❌ Ошибка",
                description=f"Не удалось обновить интерфейс: {str(e)}",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup_protection_panel(bot):
    """Настройка автоматической панели управления защитой"""
    try:
        # Находим или создаем канал защиты
        guild = bot.get_guild(1375772175373566012)  # ID сервера Limonericx
        if not guild:
            logger.error("Сервер Limonericx не найден")
            return
        
        # Ищем канал защиты
        protection_channel = None
        for channel in guild.channels:
            if channel.name == "🛡️-защита" and isinstance(channel, discord.TextChannel):
                protection_channel = channel
                break
        
        # Если канал не найден, создаем его
        if not protection_channel:
            try:
                # Создаем категорию для управления, если её нет
                admin_category = None
                for category in guild.categories:
                    if category.name == "🛠️-УПРАВЛЕНИЕ":
                        admin_category = category
                        break
                
                if not admin_category:
                    admin_category = await guild.create_category("🛠️-УПРАВЛЕНИЕ")
                
                # Создаем канал защиты
                protection_channel = await guild.create_text_channel(
                    "🛡️-защита",
                    category=admin_category,
                    topic="Панель управления защитой сервера"
                )
                
                logger.info(f"Создан канал защиты: {protection_channel.name}")
                
            except Exception as e:
                logger.error(f"Ошибка создания канала защиты: {e}")
                return
        
        # Создаем панель управления
        embed = discord.Embed(
            title="🛡️ Панель управления защитой",
            description="Управление всеми системами защиты сервера",
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
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
• 🔒 **Режим изоляции** - полная блокировка сервера
• 🛡️ **Защита от массовых действий** - автоматическое отключение прав модераторов""",
            inline=False
        )
        
        embed.set_footer(text="🛡️ Система защиты Limonericx")
        
        # Создаем кнопки
        view = ProtectionPanelView(bot)
        
        # Отправляем панель в канал
        await protection_channel.send(embed=embed, view=view)
        
        logger.info("Панель управления защитой создана и отправлена в канал")
        
    except Exception as e:
        logger.error(f"Ошибка настройки панели защиты: {e}")
        import traceback
        logger.error(traceback.format_exc()) 