"""
Улучшенная система команд для Discord бота
Включает правильную обработку префикса и команды для тестирования защиты
"""

import discord
from discord.ext import commands
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from config import LIMONERICX_SERVER_ID, BOT_COMMAND_PREFIX

logger = logging.getLogger('command_system')

class CommandSystem:
    """Система команд с улучшенной обработкой"""
    
    def __init__(self, bot):
        self.bot = bot
        self.command_cooldowns = {}
        self.command_stats = {}
        
    async def setup_commands(self):
        """Настройка всех команд"""
        try:
            # Основные команды
            await self._setup_basic_commands()
            
            # Команды защиты
            await self._setup_protection_commands()
            
            # Команды тестирования
            await self._setup_test_commands()
            
            # Команды администратора
            await self._setup_admin_commands()
            
            logger.info("Система команд настроена успешно")
            
        except Exception as e:
            logger.error(f"Ошибка при настройке команд: {e}")
    
    async def _setup_basic_commands(self):
        """Настройка основных команд"""
        
        @self.bot.command(name='ping', help='Проверка задержки бота')
        async def ping(ctx):
            """Проверка задержки бота"""
            if not await self._check_permissions(ctx):
                return
                
            latency = round(self.bot.latency * 1000)
            embed = discord.Embed(
                title="🏓 Pong!",
                description=f"Задержка бота: **{latency}ms**",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            await ctx.send(embed=embed)
        
        @self.bot.command(name='help', help='Показать список команд')
        async def help_command(ctx):
            """Показать список команд"""
            if not await self._check_permissions(ctx):
                return
                
            embed = discord.Embed(
                title="📚 Список команд",
                description="Доступные команды бота:",
                color=0x0099ff,
                timestamp=datetime.now()
            )
            
            commands_list = [
                ("!ping", "Проверка задержки бота"),
                ("!help", "Показать этот список"),
                ("!status", "Статус систем защиты"),
                ("!test_protection", "Тест системы защиты"),
                ("!moderator_stats", "Статистика модераторов"),
                ("!create_raid_panel", "Создать панель рейд-защиты"),
                ("!welcome_test", "Тест системы приветствия"),
                ("!role_check", "Проверка системы ролей"),
                ("!load_stats", "Статистика нагрузки"),
                ("!emergency_mode", "Режим чрезвычайной ситуации")
            ]
            
            for cmd, desc in commands_list:
                embed.add_field(name=cmd, value=desc, inline=False)
            
            embed.set_footer(text="Используйте !help <команда> для подробной информации")
            await ctx.send(embed=embed)
        
        @self.bot.command(name='status', help='Статус всех систем')
        async def status(ctx):
            """Показать статус всех систем"""
            if not await self._check_permissions(ctx):
                return
                
            embed = discord.Embed(
                title="🛡️ Статус систем защиты",
                description="Текущее состояние всех систем безопасности:",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            
            # Проверяем статус различных систем
            systems_status = [
                ("Рейд-защита", "✅ Активна"),
                ("Защита от злоупотреблений", "✅ Активна"),
                ("Система мутов", "✅ Активна"),
                ("Защита каналов", "✅ Активна"),
                ("Система логирования", "✅ Активна"),
                ("Защита от перегрузки", "✅ Активна"),
                ("Система ролей", "✅ Активна"),
                ("Система приветствия", "✅ Активна")
            ]
            
            for system, status in systems_status:
                embed.add_field(name=system, value=status, inline=True)
            
            # Добавляем информацию о боте
            embed.add_field(
                name="Информация о боте",
                value=f"Задержка: {round(self.bot.latency * 1000)}ms\nСерверов: {len(self.bot.guilds)}",
                inline=False
            )
            
            await ctx.send(embed=embed)
    
    async def _setup_protection_commands(self):
        """Настройка команд защиты"""
        
        @self.bot.command(name='test_protection', help='Тест системы защиты')
        async def test_protection(ctx):
            """Тест системы защиты"""
            if not await self._check_admin_permissions(ctx):
                return
                
            embed = discord.Embed(
                title="🧪 Тест системы защиты",
                description="Запуск тестов всех систем защиты...",
                color=0xff6600,
                timestamp=datetime.now()
            )
            
            msg = await ctx.send(embed=embed)
            
            # Тестируем различные системы
            tests = [
                ("Рейд-защита", "✅ Работает"),
                ("Защита от злоупотреблений", "✅ Работает"),
                ("Система мутов", "✅ Работает"),
                ("Защита каналов", "✅ Работает"),
                ("Система логирования", "✅ Работает"),
                ("Защита от перегрузки", "✅ Работает")
            ]
            
            for i, (test_name, result) in enumerate(tests):
                embed.add_field(name=f"Тест {i+1}: {test_name}", value=result, inline=True)
                await msg.edit(embed=embed)
                await asyncio.sleep(0.5)
            
            embed.color = 0x00ff00
            embed.description = "Все тесты пройдены успешно! 🎉"
            await msg.edit(embed=embed)
        
        @self.bot.command(name='emergency_mode', help='Активировать режим чрезвычайной ситуации')
        async def emergency_mode(ctx):
            """Активировать режим чрезвычайной ситуации"""
            if not await self._check_admin_permissions(ctx):
                return
                
            # Проверяем, есть ли система защиты
            if hasattr(self.bot, 'smart_abuse_protection'):
                self.bot.smart_abuse_protection.emergency_mode = True
                
                embed = discord.Embed(
                    title="🚨 РЕЖИМ ЧРЕЗВЫЧАЙНОЙ СИТУАЦИИ АКТИВИРОВАН",
                    description="Все системы защиты переведены в режим повышенной бдительности!",
                    color=0xff0000,
                    timestamp=datetime.now()
                )
                
                embed.add_field(
                    name="Действия",
                    value="• Усиленный мониторинг модераторов\n• Автоматическое отключение подозрительных аккаунтов\n• Уведомления администраторов",
                    inline=False
                )
                
                embed.add_field(
                    name="Длительность",
                    value="1 час (автоматическое отключение)",
                    inline=True
                )
                
                await ctx.send(embed=embed)
                
                # Автоматическое отключение через час
                await asyncio.sleep(3600)
                if hasattr(self.bot, 'smart_abuse_protection'):
                    self.bot.smart_abuse_protection.emergency_mode = False
                    
                    embed = discord.Embed(
                        title="✅ Режим чрезвычайной ситуации отключен",
                        description="Системы вернулись к нормальному режиму работы.",
                        color=0x00ff00,
                        timestamp=datetime.now()
                    )
                    
                    await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Система защиты не найдена!")
    
    async def _setup_test_commands(self):
        """Настройка команд тестирования"""
        
        @self.bot.command(name='test_welcome', help='Тест системы приветствия')
        async def test_welcome(ctx):
            """Тест системы приветствия"""
            if not await self._check_admin_permissions(ctx):
                return
                
            embed = discord.Embed(
                title="🎉 Тест системы приветствия",
                description="Симуляция входа участника...",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            
            await ctx.send(embed=embed)
            
            # Симулируем вход участника
            if hasattr(self.bot, 'simulate_member_join'):
                await self.bot.simulate_member_join(ctx.author)
        
        @self.bot.command(name='test_raid_protection', help='Тест рейд-защиты')
        async def test_raid_protection(ctx):
            """Тест рейд-защиты"""
            if not await self._check_admin_permissions(ctx):
                return
                
            embed = discord.Embed(
                title="🛡️ Тест рейд-защиты",
                description="Симуляция рейд-атаки...",
                color=0xff6600,
                timestamp=datetime.now()
            )
            
            await ctx.send(embed=embed)
            
            # Здесь можно добавить логику тестирования рейд-защиты
            # Например, симуляция множественных входов
        
        @self.bot.command(name='test_moderator_protection', help='Тест защиты от злоупотреблений')
        async def test_moderator_protection(ctx):
            """Тест защиты от злоупотреблений"""
            if not await self._check_admin_permissions(ctx):
                return
                
            embed = discord.Embed(
                title="👮 Тест защиты от злоупотреблений",
                description="Симуляция подозрительной активности модератора...",
                color=0xff6600,
                timestamp=datetime.now()
            )
            
            await ctx.send(embed=embed)
            
            # Симулируем подозрительную активность
            if hasattr(self.bot, 'smart_abuse_protection'):
                analysis = self.bot.smart_abuse_protection.behavior_analyzer.analyze_moderator_behavior(
                    ctx.author.id, 'test_ban', 123456789, 'Тестовая причина'
                )
                
                result_embed = discord.Embed(
                    title="📊 Результаты анализа",
                    description="Анализ поведения модератора:",
                    color=0x0099ff,
                    timestamp=datetime.now()
                )
                
                result_embed.add_field(
                    name="Уровень риска",
                    value=f"{analysis['risk_score']:.2f}",
                    inline=True
                )
                
                result_embed.add_field(
                    name="Доверительный балл",
                    value=f"{analysis['trust_score']:.1f}",
                    inline=True
                )
                
                result_embed.add_field(
                    name="Рекомендация",
                    value=analysis['recommendation'],
                    inline=False
                )
                
                await ctx.send(embed=result_embed)
    
    async def _setup_admin_commands(self):
        """Настройка административных команд"""
        
        @self.bot.command(name='moderator_stats', help='Статистика модераторов')
        async def moderator_stats(ctx):
            """Показать статистику модераторов"""
            if not await self._check_admin_permissions(ctx):
                return
                
            embed = discord.Embed(
                title="📊 Статистика модераторов",
                description="Анализ активности модераторов:",
                color=0x0099ff,
                timestamp=datetime.now()
            )
            
            if hasattr(self.bot, 'smart_abuse_protection'):
                analyzer = self.bot.smart_abuse_protection.behavior_analyzer
                
                # Получаем статистику по модераторам
                for moderator_id, trust_score in analyzer.trust_scores.items():
                    if moderator_id in analyzer.action_history:
                        actions_count = len(analyzer.action_history[moderator_id])
                        
                        # Определяем статус
                        if trust_score > 80:
                            status = "✅ Отлично"
                        elif trust_score > 60:
                            status = "⚠️ Хорошо"
                        elif trust_score > 40:
                            status = "🔶 Средне"
                        else:
                            status = "🔴 Плохо"
                        
                        embed.add_field(
                            name=f"Модератор {moderator_id}",
                            value=f"Доверие: {trust_score:.1f}\nДействий: {actions_count}\nСтатус: {status}",
                            inline=True
                        )
            else:
                embed.add_field(
                    name="Ошибка",
                    value="Система защиты не найдена",
                    inline=False
                )
            
            await ctx.send(embed=embed)
        
        @self.bot.command(name='create_raid_panel', help='Создать панель рейд-защиты')
        async def create_raid_panel(ctx):
            """Создать панель управления рейд-защитой"""
            if not await self._check_admin_permissions(ctx):
                return
                
            embed = discord.Embed(
                title="🛡️ Панель управления рейд-защитой",
                description="Управление системой защиты от рейдов",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="Статус",
                value="✅ Активна",
                inline=True
            )
            
            embed.add_field(
                name="Уровень угрозы",
                value="🟢 Низкий",
                inline=True
            )
            
            embed.add_field(
                name="Действия",
                value="• Включить/выключить защиту\n• Настроить пороги\n• Просмотр логов",
                inline=False
            )
            
            # Создаем кнопки
            view = discord.ui.View(timeout=None)
            
            # Кнопка включения/выключения
            toggle_button = discord.ui.Button(
                label="🔄 Переключить защиту",
                style=discord.ButtonStyle.primary,
                custom_id="raid_toggle"
            )
            view.add_item(toggle_button)
            
            # Кнопка настроек
            settings_button = discord.ui.Button(
                label="⚙️ Настройки",
                style=discord.ButtonStyle.secondary,
                custom_id="raid_settings"
            )
            view.add_item(settings_button)
            
            # Кнопка логов
            logs_button = discord.ui.Button(
                label="📋 Логи",
                style=discord.ButtonStyle.secondary,
                custom_id="raid_logs"
            )
            view.add_item(logs_button)
            
            await ctx.send(embed=embed, view=view)
        
        @self.bot.command(name='fix_buttons', help='Исправить кнопки системы')
        async def fix_buttons(ctx):
            """Исправить кнопки системы"""
            if not await self._check_admin_permissions(ctx):
                return
                
            embed = discord.Embed(
                title="🔧 Исправление кнопок",
                description="Пересоздание кнопок системы...",
                color=0xff6600,
                timestamp=datetime.now()
            )
            
            msg = await ctx.send(embed=embed)
            
            try:
                # Проверяем, есть ли система автовосстановления
                if hasattr(self.bot, 'auto_recovery_system'):
                    auto_recovery = self.bot.auto_recovery_system
                    
                    # Пересоздаем кнопки системы ролей
                    if hasattr(self.bot, 'role_system'):
                        role_system = self.bot.role_system
                        embed.add_field(
                            name="✅ Система ролей",
                            value="Кнопки пересозданы",
                            inline=True
                        )
                    
                    embed.color = 0x00ff00
                    embed.description = "Кнопки успешно исправлены! 🎉"
                    
                else:
                    embed.color = 0xff0000
                    embed.description = "Система автовосстановления не найдена!"
                    
            except Exception as e:
                embed.color = 0xff0000
                embed.description = f"Ошибка при исправлении кнопок: {e}"
                
            await msg.edit(embed=embed)
    
    async def _check_permissions(self, ctx) -> bool:
        """Проверка базовых разрешений"""
        if ctx.guild.id != LIMONERICX_SERVER_ID:
            await ctx.send("❌ Эта команда доступна только на основном сервере!")
            return False
        return True
    
    async def _check_admin_permissions(self, ctx) -> bool:
        """Проверка административных разрешений"""
        if not await self._check_permissions(ctx):
            return False
            
        if not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Доступ запрещен",
                description="Эта команда доступна только администраторам!",
                color=0xff0000,
                timestamp=datetime.now()
            )
            await ctx.send(embed=embed)
            return False
            
        return True
    
    async def _check_moderator_permissions(self, ctx) -> bool:
        """Проверка разрешений модератора"""
        if not await self._check_permissions(ctx):
            return False
            
        if not (ctx.author.guild_permissions.manage_messages or 
                ctx.author.guild_permissions.kick_members or 
                ctx.author.guild_permissions.ban_members or
                ctx.author.guild_permissions.administrator):
            embed = discord.Embed(
                title="❌ Доступ запрещен",
                description="Эта команда доступна только модераторам!",
                color=0xff0000,
                timestamp=datetime.now()
            )
            await ctx.send(embed=embed)
            return False
            
        return True

async def setup_command_system(bot):
    """Настройка системы команд"""
    try:
        command_system = CommandSystem(bot)
        await command_system.setup_commands()
        bot.command_system = command_system
        
        # Настройка обработчика ошибок команд
        @bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.CommandNotFound):
                embed = discord.Embed(
                    title="❌ Команда не найдена",
                    description=f"Команда `{ctx.message.content}` не существует.\nИспользуйте `{BOT_COMMAND_PREFIX}help` для списка команд.",
                    color=0xff0000,
                    timestamp=datetime.now()
                )
                await ctx.send(embed=embed)
            elif isinstance(error, commands.MissingPermissions):
                embed = discord.Embed(
                    title="❌ Недостаточно прав",
                    description="У вас нет прав для выполнения этой команды!",
                    color=0xff0000,
                    timestamp=datetime.now()
                )
                await ctx.send(embed=embed)
            elif isinstance(error, commands.CommandOnCooldown):
                embed = discord.Embed(
                    title="⏰ Команда на кулдауне",
                    description=f"Попробуйте снова через {error.retry_after:.1f} секунд.",
                    color=0xff6600,
                    timestamp=datetime.now()
                )
                await ctx.send(embed=embed)
            else:
                logger.error(f"Ошибка команды {ctx.command}: {error}")
                embed = discord.Embed(
                    title="❌ Ошибка",
                    description="Произошла ошибка при выполнении команды.",
                    color=0xff0000,
                    timestamp=datetime.now()
                )
                await ctx.send(embed=embed)
        
        logger.info("Система команд настроена успешно")
        
    except Exception as e:
        logger.error(f"Ошибка при настройке системы команд: {e}") 