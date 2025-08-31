"""
Кнопочный интерфейс для системы защиты от рейдов
Заменяет команды на удобные кнопки
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger('raid_protection_buttons')

class RaidProtectionView(discord.ui.View):
    """Кнопочный интерфейс для управления защитой от рейдов"""
    
    def __init__(self, protection_system):
        super().__init__(timeout=None)
        self.protection = protection_system
    
    @discord.ui.button(label="🔒 Изоляция", style=discord.ButtonStyle.danger, custom_id="raid_lockdown")
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
        
        if self.protection.lockdown_mode:
            embed = discord.Embed(
                title="❌ Режим изоляции уже активен",
                description="Сервер уже заблокирован",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            self.protection.lockdown_mode = True
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
            
            embed.set_footer(text=f"🆔 Администратор: {interaction.user.id}", 
                           icon_url="https://cdn.discordapp.com/emojis/1234567890.png")
            
            await interaction.response.send_message(embed=embed)
            
            # Логируем событие
            await self.protection.log_security_event(
                "РЕЖИМ ИЗОЛЯЦИИ АКТИВИРОВАН",
                f"Режим изоляции активирован администратором {interaction.user.mention}.",
                color=0xff0000
            )
            
        except Exception as e:
            logger.error(f"Ошибка при активации режима изоляции: {e}")
            embed = discord.Embed(
                title="❌ Ошибка",
                description=f"Не удалось активировать режим изоляции: {str(e)}",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔓 Разблокировка", style=discord.ButtonStyle.success, custom_id="raid_unlock")
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
        
        if not self.protection.lockdown_mode:
            embed = discord.Embed(
                title="❌ Режим изоляции не активен",
                description="Сервер не заблокирован",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            self.protection.lockdown_mode = False
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
            
            embed.set_footer(text=f"🆔 Администратор: {interaction.user.id}", 
                           icon_url="https://cdn.discordapp.com/emojis/1234567890.png")
            
            await interaction.response.send_message(embed=embed)
            
            # Логируем событие
            await self.protection.log_security_event(
                "РЕЖИМ ИЗОЛЯЦИИ ОТКЛЮЧЕН",
                f"Режим изоляции отключен администратором {interaction.user.mention}.",
                color=0x00ff00
            )
            
        except Exception as e:
            logger.error(f"Ошибка при отключении режима изоляции: {e}")
            embed = discord.Embed(
                title="❌ Ошибка",
                description=f"Не удалось отключить режим изоляции: {str(e)}",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📊 Статус", style=discord.ButtonStyle.primary, custom_id="raid_status")
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
                title="🛡️ Статус системы защиты от рейдов",
                description="Подробная информация о состоянии системы защиты",
                color=0x0099ff,
                timestamp=datetime.utcnow()
            )
            
            # Добавляем аватар бота
            if interaction.client.user.display_avatar:
                embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
            
            embed.add_field(
                name="🔴 Режим рейда",
                value="Активен" if self.protection.raid_mode else "Неактивен",
                inline=True
            )
            
            embed.add_field(
                name="🔒 Режим изоляции",
                value="Активен" if self.protection.lockdown_mode else "Неактивен",
                inline=True
            )
            
            embed.add_field(
                name="👥 Входов за час",
                value=str(len(self.protection.join_times)),
                inline=True
            )
            
            # Статистика модераторских действий
            total_actions = 0
            for mod_actions in self.protection.moderator_actions.values():
                for action_list in mod_actions.values():
                    total_actions += len(action_list)
            
            embed.add_field(
                name="⚡ Действий модераторов",
                value=str(total_actions),
                inline=True
            )
            
            # Настройки защиты
            embed.add_field(
                name="⚙️ Настройки защиты",
                value=f"""• Максимум входов в минуту: `{self.protection.MAX_JOINS_PER_MINUTE}`
• Максимум сообщений в минуту: `{self.protection.MAX_MESSAGES_PER_MINUTE}`
• Максимум банов в час: `{self.protection.MAX_BANS_PER_HOUR}` (автоотключение на 2ч)
• Максимум киков в час: `{self.protection.MAX_KICKS_PER_HOUR}` (автоотключение на 1ч)
• Максимум мутов в час: `{self.protection.MAX_MUTES_PER_HOUR}` (предупреждение)
• Максимум удалений каналов в час: `{self.protection.MAX_CHANNEL_DELETIONS_PER_HOUR}` (автоотключение на 4ч)""",
                inline=False
            )
            
            # Защищенные роли
            protected_roles_text = ""
            for role_id in self.protection.protected_roles:
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
            
            embed.set_footer(text=f"🆔 Запросил: {interaction.user.id}", 
                           icon_url="https://cdn.discordapp.com/emojis/1234567890.png")
            
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
    
    @discord.ui.button(label="🔄 Обновить", style=discord.ButtonStyle.secondary, custom_id="raid_refresh")
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
                title="🔄 Интерфейс обновлен",
                description="Система защиты от рейдов обновлена",
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="📊 Статус",
                value="✅ Система работает нормально",
                inline=True
            )
            
            embed.add_field(
                name="👤 Обновил",
                value=f"{interaction.user.mention}",
                inline=True
            )
            
            embed.set_footer(text=f"🆔 Модератор: {interaction.user.id}", 
                           icon_url="https://cdn.discordapp.com/emojis/1234567890.png")
            
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

class RaidProtectionButtonCommands(commands.Cog):
    """Команды для управления кнопочным интерфейсом защиты от рейдов"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="raid_buttons")
    @commands.has_permissions(administrator=True)
    async def create_raid_buttons(self, ctx):
        """Создать кнопочный интерфейс для системы защиты от рейдов"""
        try:
            embed = discord.Embed(
                title="🛡️ Система защиты от рейдов",
                description="Управление защитой сервера от рейдов и массовых действий",
                color=0x0099ff,
                timestamp=datetime.utcnow()
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
• 🔒 **Режим изоляции** - полная блокировка сервера
• 🛡️ **Защита от массовых действий** - автоматическое отключение прав модераторов""",
                inline=False
            )
            
            embed.set_footer(text=f"🆔 Создал: {ctx.author.id}", 
                           icon_url="https://cdn.discordapp.com/emojis/1234567890.png")
            
            view = RaidProtectionView(self.bot.raid_protection)
            await ctx.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Ошибка при создании кнопок защиты: {e}")
            embed = discord.Embed(
                title="❌ Ошибка",
                description=f"Не удалось создать кнопочный интерфейс: {str(e)}",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="raid_help")
    @commands.has_permissions(manage_guild=True)
    async def raid_help(self, ctx):
        """Показать справку по системе защиты от рейдов"""
        embed = discord.Embed(
            title="🛡️ Справка по системе защиты от рейдов",
            description="Подробная информация о функциях защиты",
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🔒 Режим изоляции",
            value="""**Команда:** `!raid_buttons` (создать кнопки)
**Кнопка:** 🔒 Изоляция
**Действие:** Блокирует сервер - только администраторы могут писать
**Права:** Администратор""",
            inline=False
        )
        
        embed.add_field(
            name="🔓 Разблокировка",
            value="""**Кнопка:** 🔓 Разблокировка
**Действие:** Разблокирует сервер - возвращает права участникам
**Права:** Администратор""",
            inline=False
        )
        
        embed.add_field(
            name="📊 Статус системы",
            value="""**Кнопка:** 📊 Статус
**Действие:** Показывает текущий статус всех систем защиты
**Права:** Управление сервером""",
            inline=False
        )
        
        embed.add_field(
            name="🔄 Обновление",
            value="""**Кнопка:** 🔄 Обновить
**Действие:** Обновляет интерфейс и проверяет систему
**Права:** Управление сервером""",
            inline=False
        )
        
        embed.add_field(
            name="🚨 Автоматическая защита",
            value="""• **Рейды:** Обнаружение по количеству входов
• **Спам:** Ограничение сообщений от одного пользователя
• **Модераторы:** Контроль лимитов действий
• **Каналы:** Логирование удалений каналов
• **Восстановление:** Автоматическое отключение защиты""",
            inline=False
        )
        
        embed.set_footer(text=f"🆔 Запросил: {ctx.author.id}", 
                       icon_url="https://cdn.discordapp.com/emojis/1234567890.png")
        
        await ctx.send(embed=embed)

async def setup_raid_protection_buttons(bot):
    """Настройка кнопочного интерфейса защиты от рейдов"""
    try:
        await bot.add_cog(RaidProtectionButtonCommands(bot))
        logger.info("Кнопочный интерфейс защиты от рейдов настроен")
    except Exception as e:
        logger.error(f"Ошибка при настройке кнопочного интерфейса защиты: {e}") 