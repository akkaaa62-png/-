import discord
from discord.ext import commands
import asyncio
import random
import json
import datetime
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from typing import TYPE_CHECKING

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MafiaPlayer:
    def __init__(self, member: discord.Member, role: str = None):
        self.member = member
        self.role = role
        self.is_alive = True
        self.votes_received = 0
        self.vote_target = None
        self.night_action_target = None
        self.is_mafia = role == "Мафия"
        self.is_sheriff = role == "Шериф"
        self.is_civilian = role == "Мирный"
        
    def to_dict(self):
        return {
            "id": self.member.id,
            "name": self.member.display_name,
            "role": self.role,
            "is_alive": self.is_alive,
            "votes_received": self.votes_received,
            "vote_target": self.vote_target.id if self.vote_target else None,
            "night_action_target": self.night_action_target.id if self.night_action_target else None
        }

class MafiaGame:
    def __init__(self, bot, guild: discord.Guild, channel: discord.TextChannel):
        self.bot = bot
        self.guild = guild
        self.channel = channel
        self.players: Dict[int, MafiaPlayer] = {}
        self.registered_players: List[discord.Member] = []
        self.game_state = "waiting"  # waiting, night, day, voting, ended
        self.voice_channel = None
        self.registration_message = None
        self.game_message = None
        self.mafia_chat_channel = None
        self.sheriff_chat_channel = None
        self.min_players = 6
        self.max_players = 12
        self.mafia_count = 0
        self.civilian_count = 0
        self.sheriff_count = 0
        self.current_phase = "registration"
        self.day_number = 0
        self.night_actions = {}
        self.vote_results = {}
        self.game_log = []
        
    async def create_game_channels(self):
        """Создание каналов для игры (использует существующую категорию)"""
        try:
            logger.info(f"Начинаю создание каналов для игры Mafia в гильдии {self.guild.name}")
            
            # Проверяем права бота
            bot_member = self.guild.get_member(self.bot.user.id)
            if not bot_member:
                logger.error("Бот не найден в гильдии!")
                return False
                
            bot_permissions = bot_member.guild_permissions
            logger.info(f"Права бота: manage_channels={bot_permissions.manage_channels}, manage_guild={bot_permissions.manage_guild}")
            
            if not bot_permissions.manage_channels:
                logger.error("У бота нет прав на управление каналами!")
                return False
            
            # Ищем существующую категорию Mafia
            category = discord.utils.get(self.guild.categories, name="🎭 Игра Mafia")
            
            if not category:
                logger.error("Категория Mafia не найдена! Сначала запустите !mafia_setup")
                return False
            
            logger.info(f"Использую существующую категорию: {category.name} (ID: {category.id})")
            
            # Ищем существующие каналы в категории
            self.game_channel = discord.utils.get(category.text_channels, name="🎮 mafia-game")
            self.voice_channel = discord.utils.get(category.voice_channels, name="🎤 Mafia Voice")
            self.mafia_chat_channel = discord.utils.get(category.text_channels, name="🔪 mafia-chat")
            self.sheriff_chat_channel = discord.utils.get(category.text_channels, name="🕵️ sheriff-chat")
            
            # Если каналы не найдены, создаем их
            if not self.game_channel:
                logger.info("Создаю игровой канал '🎮 mafia-game'...")
                self.game_channel = await self.guild.create_text_channel(
                    name="🎮 mafia-game",
                    category=category,
                    overwrites={
                        self.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        self.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True)
                    }
                )
                logger.info(f"Игровой канал создан: {self.game_channel.name}")
            
            if not self.voice_channel:
                logger.info("Создаю голосовой канал '🎤 Mafia Voice'...")
                self.voice_channel = await self.guild.create_voice_channel(
                    name="🎤 Mafia Voice",
                    category=category,
                    user_limit=self.max_players,
                    overwrites={
                        self.guild.default_role: discord.PermissionOverwrite(connect=False),
                        self.guild.me: discord.PermissionOverwrite(connect=True, manage_channels=True)
                    }
                )
                logger.info(f"Голосовой канал создан: {self.voice_channel.name}")
            
            if not self.mafia_chat_channel:
                logger.info("Создаю канал мафии '🔪 mafia-chat'...")
                self.mafia_chat_channel = await self.guild.create_text_channel(
                    name="🔪 mafia-chat",
                    category=category,
                    overwrites={
                        self.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        self.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                    }
                )
                logger.info(f"Канал мафии создан: {self.mafia_chat_channel.name}")
            
            if not self.sheriff_chat_channel:
                logger.info("Создаю канал шерифа '🕵️ sheriff-chat'...")
                self.sheriff_chat_channel = await self.guild.create_text_channel(
                    name="🕵️ sheriff-chat",
                    category=category,
                    overwrites={
                        self.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        self.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                    }
                )
                logger.info(f"Канал шерифа создан: {self.sheriff_chat_channel.name}")
            
            logger.info(f"✅ Все каналы для игры Mafia готовы в гильдии {self.guild.name}")
            return True
            
        except discord.Forbidden as e:
            logger.error(f"❌ Нет прав для создания каналов: {e}")
            return False
        except discord.HTTPException as e:
            logger.error(f"❌ Ошибка HTTP при создании каналов: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка создания каналов: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def start_registration(self):
        """Начало регистрации игроков"""
        embed = discord.Embed(
            title="🎭 Регистрация в игру Mafia",
            description="Нажмите кнопку ниже, чтобы присоединиться к игре!",
            color=0x00ff00
        )
        embed.add_field(
            name="📊 Информация",
            value=f"• Минимум игроков: {self.min_players}\n• Максимум игроков: {self.max_players}\n• Зарегистрировано: {len(self.registered_players)}/{self.max_players}",
            inline=False
        )
        embed.add_field(
            name="🎮 Правила",
            value="• Мафия: уничтожает мирных\n• Мирные: вычисляют мафию\n• Шериф: проверяет роли ночью",
            inline=False
        )
        
        view = MafiaRegistrationView(self)
        self.registration_message = await self.game_channel.send(embed=embed, view=view)
        
    async def add_player(self, member: discord.Member):
        """Добавление игрока в игру"""
        if member in self.registered_players:
            return False, "Вы уже зарегистрированы!"
        
        if len(self.registered_players) >= self.max_players:
            return False, "Игра уже заполнена!"
        
        self.registered_players.append(member)
        
        # Обновляем права доступа к голосовому каналу
        await self.voice_channel.set_permissions(member, connect=True, speak=True)
        
        # Обновляем сообщение регистрации
        await self.update_registration_message()
        
        # Обновляем панель управления
        mafia_system = self.bot.get_cog('MafiaSystem')
        if mafia_system:
            await mafia_system.update_control_panel(self.guild.id)
        
        # Проверяем, можно ли начать игру
        if len(self.registered_players) >= self.min_players:
            await self.check_start_game()
        
        return True, f"✅ {member.display_name} присоединился к игре!"
    
    async def remove_player(self, member: discord.Member):
        """Удаление игрока из игры"""
        if member not in self.registered_players:
            return False, "Вы не зарегистрированы в игре!"
        
        self.registered_players.remove(member)
        
        # Убираем права доступа к голосовому каналу
        await self.voice_channel.set_permissions(member, overwrite=None)
        
        # Обновляем сообщение регистрации
        await self.update_registration_message()
        
        # Обновляем панель управления
        mafia_system = self.bot.get_cog('MafiaSystem')
        if mafia_system:
            await mafia_system.update_control_panel(self.guild.id)
        
        return True, f"❌ {member.display_name} покинул игру!"
    
    async def update_registration_message(self):
        """Обновление сообщения регистрации"""
        if not self.registration_message:
            return
        
        embed = discord.Embed(
            title="🎭 Регистрация в игру Mafia",
            description="Нажмите кнопку ниже, чтобы присоединиться к игре!",
            color=0x00ff00
        )
        
        players_list = "\n".join([f"• {player.display_name}" for player in self.registered_players])
        embed.add_field(
            name=f"📊 Игроки ({len(self.registered_players)}/{self.max_players})",
            value=players_list if players_list else "Пока нет игроков",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Правила",
            value="• Мафия: уничтожает мирных\n• Мирные: вычисляют мафию\n• Шериф: проверяет роли ночью",
            inline=False
        )
        
        view = MafiaRegistrationView(self)
        await self.registration_message.edit(embed=embed, view=view)
    
    async def check_start_game(self):
        """Проверка возможности начала игры"""
        if len(self.registered_players) >= self.min_players:
            embed = discord.Embed(
                title="🎭 Игра готова к началу!",
                description=f"Достаточно игроков для начала игры! ({len(self.registered_players)}/{self.max_players})",
                color=0xffaa00
            )
            embed.add_field(
                name="⏰ Ожидание",
                value="Игра начнется через 30 секунд или когда нажмете кнопку 'Начать сейчас'",
                inline=False
            )
            
            view = MafiaStartView(self)
            await self.game_channel.send(embed=embed, view=view)
    
    async def start_game(self):
        """Начало игры"""
        self.game_state = "starting"
        
        # Закрываем регистрацию
        if self.registration_message:
            view = MafiaRegistrationView(self, disabled=True)
            await self.registration_message.edit(view=view)
        
        # Блокируем голосовой канал от новых участников
        await self.voice_channel.set_permissions(self.guild.default_role, connect=False)
        
        # Распределяем роли
        await self.assign_roles()
        
        # Отправляем роли в личные сообщения
        await self.send_roles_to_players()
        
        # Обновляем панель управления
        mafia_system = self.bot.get_cog('MafiaSystem')
        if mafia_system:
            await mafia_system.update_control_panel(self.guild.id)
        
        # Начинаем первую ночь
        await self.start_night()
    
    async def assign_roles(self):
        """Распределение ролей между игроками"""
        players = self.registered_players.copy()
        random.shuffle(players)
        
        # Определяем количество ролей
        total_players = len(players)
        
        if total_players <= 6:
            self.mafia_count = 1
            self.sheriff_count = 1
            self.civilian_count = total_players - 2
        elif total_players <= 8:
            self.mafia_count = 2
            self.sheriff_count = 1
            self.civilian_count = total_players - 3
        else:
            self.mafia_count = 2
            self.sheriff_count = 1
            self.civilian_count = total_players - 3
        
        # Создаем игроков с ролями
        role_index = 0
        
        # Назначаем мафию
        for i in range(self.mafia_count):
            if role_index < len(players):
                self.players[players[role_index].id] = MafiaPlayer(players[role_index], "Мафия")
                role_index += 1
        
        # Назначаем шерифа
        if role_index < len(players):
            self.players[players[role_index].id] = MafiaPlayer(players[role_index], "Шериф")
            role_index += 1
        
        # Назначаем мирных
        for i in range(self.civilian_count):
            if role_index < len(players):
                self.players[players[role_index].id] = MafiaPlayer(players[role_index], "Мирный")
                role_index += 1
        
        # Настраиваем права доступа к приватным каналам
        mafia_players = [p for p in self.players.values() if p.is_mafia]
        sheriff_players = [p for p in self.players.values() if p.is_sheriff]
        
        for player in mafia_players:
            await self.mafia_chat_channel.set_permissions(player.member, read_messages=True, send_messages=True)
        
        for player in sheriff_players:
            await self.sheriff_chat_channel.set_permissions(player.member, read_messages=True, send_messages=True)
    
    async def send_roles_to_players(self):
        """Отправка ролей игрокам в личные сообщения"""
        for player in self.players.values():
            try:
                embed = discord.Embed(
                    title="🎭 Ваша роль в игре Mafia",
                    color=0x00ff00
                )
                
                if player.is_mafia:
                    embed.description = "🔪 Вы - **Мафия**!"
                    embed.add_field(
                        name="Ваша задача",
                        value="Уничтожить всех мирных жителей. Ночью вы можете выбрать жертву для убийства.",
                        inline=False
                    )
                    embed.add_field(
                        name="Приватный канал",
                        value=f"Используйте канал {self.mafia_chat_channel.mention} для общения с другими мафиози.",
                        inline=False
                    )
                elif player.is_sheriff:
                    embed.description = "🕵️ Вы - **Шериф**!"
                    embed.add_field(
                        name="Ваша задача",
                        value="Помочь мирным жителям найти мафию. Каждую ночь вы можете проверить роль одного игрока.",
                        inline=False
                    )
                    embed.add_field(
                        name="Приватный канал",
                        value=f"Используйте канал {self.sheriff_chat_channel.mention} для общения.",
                        inline=False
                    )
                else:
                    embed.description = "👥 Вы - **Мирный житель**!"
                    embed.add_field(
                        name="Ваша задача",
                        value="Найти и устранить всех членов мафии. Обсуждайте и голосуйте днем.",
                        inline=False
                    )
                
                await player.member.send(embed=embed)
                
            except discord.Forbidden:
                # Если личные сообщения закрыты
                pass
    
    async def start_night(self):
        """Начало ночной фазы"""
        self.game_state = "night"
        self.day_number += 1
        
        # Сбрасываем ночные действия
        self.night_actions = {}
        
        embed = discord.Embed(
            title=f"🌙 Ночь {self.day_number}",
            description="Все закрывают глаза...",
            color=0x000080
        )
        
        alive_players = [p for p in self.players.values() if p.is_alive]
        embed.add_field(
            name="👥 Живые игроки",
            value="\n".join([f"• {p.member.display_name}" for p in alive_players]),
            inline=False
        )
        
        # Создаем кнопки для ночных действий
        view = MafiaNightView(self)
        self.game_message = await self.game_channel.send(embed=embed, view=view)
        
        # Отправляем уведомления в приватные каналы
        await self.send_night_notifications()
    
    async def send_night_notifications(self):
        """Отправка уведомлений о ночной фазе"""
        # Уведомление для мафии
        mafia_players = [p for p in self.players.values() if p.is_alive and p.is_mafia]
        if mafia_players:
            embed = discord.Embed(
                title="🔪 Ночь - время действовать!",
                description="Выберите жертву для убийства:",
                color=0xff0000
            )
            
            alive_civilians = [p for p in self.players.values() if p.is_alive and not p.is_mafia]
            for player in alive_civilians:
                embed.add_field(
                    name=player.member.display_name,
                    value=f"ID: {player.member.id}",
                    inline=True
                )
            
            view = MafiaKillView(self)
            await self.mafia_chat_channel.send(embed=embed, view=view)
        
        # Уведомление для шерифа
        sheriff_players = [p for p in self.players.values() if p.is_alive and p.is_sheriff]
        if sheriff_players:
            embed = discord.Embed(
                title="🕵️ Ночь - время расследования!",
                description="Выберите игрока для проверки:",
                color=0x0000ff
            )
            
            alive_players = [p for p in self.players.values() if p.is_alive and p != sheriff_players[0]]
            for player in alive_players:
                embed.add_field(
                    name=player.member.display_name,
                    value=f"ID: {player.member.id}",
                    inline=True
                )
            
            view = SheriffCheckView(self)
            await self.sheriff_chat_channel.send(embed=embed, view=view)
    
    async def process_night_actions(self):
        """Обработка ночных действий"""
        # Обрабатываем убийство мафии
        mafia_votes = {}
        for player_id, action in self.night_actions.items():
            if self.players[player_id].is_mafia and action:
                target_id = action
                mafia_votes[target_id] = mafia_votes.get(target_id, 0) + 1
        
        # Определяем жертву мафии
        if mafia_votes:
            victim_id = max(mafia_votes, key=mafia_votes.get)
            victim = self.players[victim_id]
            victim.is_alive = False
            self.game_log.append(f"🌙 Ночь {self.day_number}: {victim.member.display_name} был убит мафией")
        
        # Обрабатываем проверку шерифа
        sheriff_players = [p for p in self.players.values() if p.is_alive and p.is_sheriff]
        if sheriff_players:
            sheriff = sheriff_players[0]
            if sheriff.member.id in self.night_actions:
                checked_id = self.night_actions[sheriff.member.id]
                checked_player = self.players[checked_id]
                
                # Отправляем результат шерифу
                embed = discord.Embed(
                    title="🕵️ Результат проверки",
                    description=f"Вы проверили игрока {checked_player.member.display_name}",
                    color=0x0000ff
                )
                
                if checked_player.is_mafia:
                    embed.add_field(name="Результат", value="🔪 Этот игрок - **Мафия**!", inline=False)
                else:
                    embed.add_field(name="Результат", value="👥 Этот игрок - **Мирный житель**!", inline=False)
                
                try:
                    await sheriff.member.send(embed=embed)
                except discord.Forbidden:
                    await self.sheriff_chat_channel.send(f"{sheriff.member.mention}", embed=embed)
    
    async def start_day(self):
        """Начало дневной фазы"""
        self.game_state = "day"
        
        embed = discord.Embed(
            title=f"☀️ День {self.day_number}",
            description="Все просыпаются...",
            color=0xffaa00
        )
        
        # Показываем результаты ночи
        if self.game_log:
            last_night_log = self.game_log[-1]
            embed.add_field(
                name="🌙 Прошлой ночью",
                value=last_night_log,
                inline=False
            )
        
        alive_players = [p for p in self.players.values() if p.is_alive]
        embed.add_field(
            name="👥 Живые игроки",
            value="\n".join([f"• {p.member.display_name}" for p in alive_players]),
            inline=False
        )
        
        embed.add_field(
            name="💬 Обсуждение",
            value="Обсудите события и подозреваемых. Голосование начнется через 2 минуты.",
            inline=False
        )
        
        view = MafiaDayView(self)
        await self.game_channel.send(embed=embed, view=view)
        
        # Запускаем таймер обсуждения
        await asyncio.sleep(120)  # 2 минуты
        
        # Начинаем голосование
        await self.start_voting()
    
    async def start_voting(self):
        """Начало голосования"""
        self.game_state = "voting"
        self.vote_results = {}
        
        # Сбрасываем голоса
        for player in self.players.values():
            player.votes_received = 0
            player.vote_target = None
        
        embed = discord.Embed(
            title=f"🗳️ Голосование - День {self.day_number}",
            description="Голосуйте за игрока, которого хотите казнить:",
            color=0xff0000
        )
        
        alive_players = [p for p in self.players.values() if p.is_alive]
        for player in alive_players:
            embed.add_field(
                name=player.member.display_name,
                value=f"ID: {player.member.id}",
                inline=True
            )
        
        view = MafiaVoteView(self)
        await self.game_channel.send(embed=embed, view=view)
        
        # Запускаем таймер голосования
        await asyncio.sleep(60)  # 1 минута
        
        # Подводим итоги голосования
        await self.process_voting()
    
    async def process_voting(self):
        """Обработка результатов голосования"""
        # Подсчитываем голоса
        vote_counts = {}
        for player_id, vote_target_id in self.vote_results.items():
            if vote_target_id:
                vote_counts[vote_target_id] = vote_counts.get(vote_target_id, 0) + 1
        
        if vote_counts:
            # Находим игрока с наибольшим количеством голосов
            executed_id = max(vote_counts, key=vote_counts.get)
            executed_player = self.players[executed_id]
            executed_player.is_alive = False
            
            embed = discord.Embed(
                title="⚖️ Результат голосования",
                description=f"Игрок {executed_player.member.display_name} был казнен!",
                color=0xff0000
            )
            
            if executed_player.is_mafia:
                embed.add_field(name="Роль казненного", value="🔪 **Мафия**!", inline=False)
            else:
                embed.add_field(name="Роль казненного", value="👥 **Мирный житель**!", inline=False)
            
            self.game_log.append(f"☀️ День {self.day_number}: {executed_player.member.display_name} был казнен (голосов: {vote_counts[executed_id]})")
            
        else:
            embed = discord.Embed(
                title="⚖️ Результат голосования",
                description="Никто не был казнен (нет голосов)",
                color=0xffff00
            )
        
        await self.game_channel.send(embed=embed)
        
        # Проверяем условия победы
        if await self.check_win_conditions():
            return
        
        # Начинаем следующую ночь
        await asyncio.sleep(5)
        await self.start_night()
    
    async def check_win_conditions(self):
        """Проверка условий победы"""
        alive_players = [p for p in self.players.values() if p.is_alive]
        alive_mafia = [p for p in alive_players if p.is_mafia]
        alive_civilians = [p for p in alive_players if not p.is_mafia]
        
        # Мафия побеждает
        if len(alive_mafia) >= len(alive_civilians):
            await self.end_game("Мафия")
            return True
        
        # Мирные побеждают
        if len(alive_mafia) == 0:
            await self.end_game("Мирные жители")
            return True
        
        return False
    
    async def end_game(self, winner: str):
        """Завершение игры"""
        self.game_state = "ended"
        
        embed = discord.Embed(
            title="🎭 Игра завершена!",
            description=f"Победители: **{winner}**!",
            color=0x00ff00
        )
        
        # Показываем всех игроков и их роли
        roles_info = ""
        for player in self.players.values():
            role_emoji = "🔪" if player.is_mafia else "🕵️" if player.is_sheriff else "👥"
            status = "✅ Жив" if player.is_alive else "💀 Мертв"
            roles_info += f"{role_emoji} {player.member.display_name} - {player.role} ({status})\n"
        
        embed.add_field(
            name="👥 Все игроки и роли",
            value=roles_info,
            inline=False
        )
        
        # Показываем лог игры
        if self.game_log:
            log_text = "\n".join(self.game_log[-10:])  # Последние 10 событий
            embed.add_field(
                name="📜 Лог игры",
                value=log_text,
                inline=False
            )
        
        await self.game_channel.send(embed=embed)
        
        # Удаляем временные каналы через 30 секунд
        await asyncio.sleep(30)
        await self.cleanup_channels()
    
    async def cleanup_channels(self):
        """Очистка временных каналов"""
        try:
            if self.voice_channel:
                await self.voice_channel.delete()
            if self.mafia_chat_channel:
                await self.mafia_chat_channel.delete()
            if self.sheriff_chat_channel:
                await self.sheriff_chat_channel.delete()
            if self.game_channel:
                await self.game_channel.delete()
            
            # Удаляем категорию, если она пуста
            category = self.game_channel.category if self.game_channel else None
            if category and len(category.channels) == 0:
                await category.delete()
                
        except Exception as e:
            logger.error(f"Ошибка при очистке каналов: {e}")

# Кнопки для регистрации
class MafiaRegistrationView(discord.ui.View):
    def __init__(self, game: MafiaGame, disabled: bool = False):
        super().__init__(timeout=None)
        self.game = game
        if disabled:
            for child in self.children:
                child.disabled = True
    
    @discord.ui.button(label="🎭 Присоединиться", style=discord.ButtonStyle.green, custom_id="mafia_join")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        success, message = await self.game.add_player(interaction.user)
        await interaction.response.send_message(message, ephemeral=True)
    
    @discord.ui.button(label="❌ Покинуть", style=discord.ButtonStyle.red, custom_id="mafia_leave")
    async def leave_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        success, message = await self.game.remove_player(interaction.user)
        await interaction.response.send_message(message, ephemeral=True)

# Кнопки для начала игры
class MafiaStartView(discord.ui.View):
    def __init__(self, game: MafiaGame):
        super().__init__(timeout=None)
        self.game = game
    
    @discord.ui.button(label="🚀 Начать сейчас", style=discord.ButtonStyle.green, custom_id="mafia_start_now")
    async def start_now_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🎭 Игра начинается!", ephemeral=True)
        await self.game.start_game()
    
    @discord.ui.button(label="⏰ Ждать 30 сек", style=discord.ButtonStyle.blurple, custom_id="mafia_start_timer")
    async def start_timer_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⏰ Игра начнется через 30 секунд!", ephemeral=True)
        await asyncio.sleep(30)
        await self.game.start_game()

# Кнопки для ночной фазы
class MafiaNightView(discord.ui.View):
    def __init__(self, game: MafiaGame):
        super().__init__(timeout=None)
        self.game = game
    
    @discord.ui.button(label="🌙 Завершить ночь", style=discord.ButtonStyle.blurple, custom_id="mafia_end_night")
    async def end_night_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🌙 Ночь завершена!", ephemeral=True)
        await self.game.process_night_actions()
        await self.game.start_day()

# Кнопки для дневной фазы
class MafiaDayView(discord.ui.View):
    def __init__(self, game: MafiaGame):
        super().__init__(timeout=None)
        self.game = game
    
    @discord.ui.button(label="☀️ Начать голосование", style=discord.ButtonStyle.green, custom_id="mafia_start_vote")
    async def start_vote_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🗳️ Голосование начинается!", ephemeral=True)
        await self.game.start_voting()

# Кнопки для убийства (мафия)
class MafiaKillView(discord.ui.View):
    def __init__(self, game: MafiaGame):
        super().__init__(timeout=None)
        self.game = game
    
    @discord.ui.button(label="🔪 Убить игрока", style=discord.ButtonStyle.red, custom_id="mafia_kill")
    async def kill_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Проверяем, что это мафия
        player = self.game.players.get(interaction.user.id)
        if not player or not player.is_mafia or not player.is_alive:
            await interaction.response.send_message("❌ Вы не можете выполнить это действие!", ephemeral=True)
            return
        
        # Создаем модальное окно для выбора жертвы
        modal = MafiaKillModal(self.game)
        await interaction.response.send_modal(modal)

# Кнопки для проверки (шериф)
class SheriffCheckView(discord.ui.View):
    def __init__(self, game: MafiaGame):
        super().__init__(timeout=None)
        self.game = game
    
    @discord.ui.button(label="🕵️ Проверить игрока", style=discord.ButtonStyle.blurple, custom_id="sheriff_check")
    async def check_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Проверяем, что это шериф
        player = self.game.players.get(interaction.user.id)
        if not player or not player.is_sheriff or not player.is_alive:
            await interaction.response.send_message("❌ Вы не можете выполнить это действие!", ephemeral=True)
            return
        
        # Создаем модальное окно для выбора игрока
        modal = SheriffCheckModal(self.game)
        await interaction.response.send_modal(modal)

# Кнопки для голосования
class MafiaVoteView(discord.ui.View):
    def __init__(self, game: MafiaGame):
        super().__init__(timeout=None)
        self.game = game
    
    @discord.ui.button(label="🗳️ Голосовать", style=discord.ButtonStyle.green, custom_id="mafia_vote")
    async def vote_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Проверяем, что игрок жив
        player = self.game.players.get(interaction.user.id)
        if not player or not player.is_alive:
            await interaction.response.send_message("❌ Вы не можете голосовать!", ephemeral=True)
            return
        
        # Создаем модальное окно для голосования
        modal = MafiaVoteModal(self.game)
        await interaction.response.send_modal(modal)

# Кнопки панели управления Mafia
class MafiaControlPanelView(discord.ui.View):
    def __init__(self, mafia_system: "MafiaSystem"):
        super().__init__(timeout=None)
        self.mafia_system = mafia_system
    
    @discord.ui.button(label="🎭 Создать игру", style=discord.ButtonStyle.green, custom_id="mafia_create")
    async def create_game_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Проверяем права
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ У вас нет прав для создания игры!", ephemeral=True)
            return
        
        guild_id = interaction.guild.id
        
        # Проверяем, нет ли уже активной игры
        if guild_id in self.mafia_system.active_games:
            await interaction.response.send_message("❌ В этой гильдии уже есть активная игра Mafia!", ephemeral=True)
            return
        
        await interaction.response.send_message("🎭 Создаю игру Mafia...", ephemeral=True)
        
        try:
            # Создаем новую игру
            game = MafiaGame(self.mafia_system.bot, interaction.guild, interaction.channel)
            
            # Создаем каналы
            logger.info(f"Попытка создания каналов для игры Mafia пользователем {interaction.user.name}")
            
            if await game.create_game_channels():
                self.mafia_system.active_games[guild_id] = game
                await game.start_registration()
                
                # Обновляем панель управления
                await self.mafia_system.update_control_panel(guild_id)
                
                await interaction.followup.send(f"✅ Игра Mafia создана! Перейдите в канал {game.game_channel.mention}", ephemeral=True)
                logger.info(f"Игра Mafia успешно создана пользователем {interaction.user.name}")
            else:
                await interaction.followup.send("❌ Ошибка при создании каналов для игры Mafia! Проверьте права бота.", ephemeral=True)
                logger.error(f"Не удалось создать каналы для игры Mafia пользователем {interaction.user.name}")
                
        except Exception as e:
            logger.error(f"Ошибка при создании игры Mafia: {e}")
            import traceback
            logger.error(traceback.format_exc())
            await interaction.followup.send(f"❌ Неожиданная ошибка при создании игры: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="🛑 Остановить игру", style=discord.ButtonStyle.red, custom_id="mafia_stop")
    async def stop_game_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Проверяем права
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ У вас нет прав для остановки игры!", ephemeral=True)
            return
        
        guild_id = interaction.guild.id
        
        if guild_id not in self.mafia_system.active_games:
            await interaction.response.send_message("❌ В этой гильдии нет активной игры Mafia!", ephemeral=True)
            return
        
        await interaction.response.send_message("🛑 Останавливаю игру Mafia...", ephemeral=True)
        
        game = self.mafia_system.active_games[guild_id]
        await game.cleanup_channels()
        del self.mafia_system.active_games[guild_id]
        
        # Обновляем панель управления
        await self.mafia_system.update_control_panel(guild_id)
        
        await interaction.followup.send("✅ Игра Mafia остановлена и каналы удалены!", ephemeral=True)
    
    @discord.ui.button(label="📊 Статус", style=discord.ButtonStyle.blurple, custom_id="mafia_status")
    async def status_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        
        if guild_id not in self.mafia_system.active_games:
            await interaction.response.send_message("🔴 Игра Mafia неактивна", ephemeral=True)
            return
        
        game = self.mafia_system.active_games[guild_id]
        
        embed = discord.Embed(
            title="📊 Статус игры Mafia",
            color=0x00ff00
        )
        
        embed.add_field(
            name="👥 Игроки",
            value=f"Зарегистрировано: {len(game.registered_players)}/{game.max_players}",
            inline=True
        )
        
        embed.add_field(
            name="🎮 Фаза",
            value=game.current_phase,
            inline=True
        )
        
        embed.add_field(
            name="📍 Канал",
            value=game.game_channel.mention if game.game_channel else "Не найден",
            inline=True
        )
        
        if game.registered_players:
            players_list = "\n".join([f"• {player.display_name}" for player in game.registered_players])
            embed.add_field(
                name="📋 Список игроков",
                value=players_list,
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔄 Обновить", style=discord.ButtonStyle.gray, custom_id="mafia_refresh")
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        
        # Обновляем панель управления
        await self.mafia_system.update_control_panel(guild_id)
        
        await interaction.response.send_message("🔄 Панель управления обновлена!", ephemeral=True)

# Модальное окно для убийства
class MafiaKillModal(discord.ui.Modal, title="🔪 Выбор жертвы"):
    def __init__(self, game: MafiaGame):
        super().__init__()
        self.game = game
        self.target_id = discord.ui.TextInput(
            label="ID игрока для убийства",
            placeholder="Введите ID игрока",
            required=True,
            min_length=1,
            max_length=20
        )
        self.add_item(self.target_id)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            target_id = int(self.target_id.value)
            target_player = self.game.players.get(target_id)
            
            if not target_player or not target_player.is_alive:
                await interaction.response.send_message("❌ Неверный ID игрока или игрок мертв!", ephemeral=True)
                return
            
            if target_player.is_mafia:
                await interaction.response.send_message("❌ Вы не можете убить другого мафиози!", ephemeral=True)
                return
            
            # Записываем действие
            self.game.night_actions[interaction.user.id] = target_id
            
            await interaction.response.send_message(f"✅ Вы выбрали {target_player.member.display_name} как жертву!", ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Неверный формат ID!", ephemeral=True)

# Модальное окно для проверки
class SheriffCheckModal(discord.ui.Modal, title="🕵️ Проверка игрока"):
    def __init__(self, game: MafiaGame):
        super().__init__()
        self.game = game
        self.target_id = discord.ui.TextInput(
            label="ID игрока для проверки",
            placeholder="Введите ID игрока",
            required=True,
            min_length=1,
            max_length=20
        )
        self.add_item(self.target_id)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            target_id = int(self.target_id.value)
            target_player = self.game.players.get(target_id)
            
            if not target_player or not target_player.is_alive:
                await interaction.response.send_message("❌ Неверный ID игрока или игрок мертв!", ephemeral=True)
                return
            
            # Записываем действие
            self.game.night_actions[interaction.user.id] = target_id
            
            await interaction.response.send_message(f"✅ Вы выбрали {target_player.member.display_name} для проверки!", ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Неверный формат ID!", ephemeral=True)

# Модальное окно для голосования
class MafiaVoteModal(discord.ui.Modal, title="🗳️ Голосование"):
    def __init__(self, game: MafiaGame):
        super().__init__()
        self.game = game
        self.target_id = discord.ui.TextInput(
            label="ID игрока для казни",
            placeholder="Введите ID игрока",
            required=True,
            min_length=1,
            max_length=20
        )
        self.add_item(self.target_id)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            target_id = int(self.target_id.value)
            target_player = self.game.players.get(target_id)
            
            if not target_player or not target_player.is_alive:
                await interaction.response.send_message("❌ Неверный ID игрока или игрок мертв!", ephemeral=True)
                return
            
            # Записываем голос
            self.game.vote_results[interaction.user.id] = target_id
            
            await interaction.response.send_message(f"✅ Вы проголосовали за казнь {target_player.member.display_name}!", ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Неверный формат ID!", ephemeral=True)

class MafiaSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games: Dict[int, MafiaGame] = {}  # guild_id -> game
        self.control_panels: Dict[int, discord.Message] = {}  # guild_id -> control panel message
        self.mafia_categories: Dict[int, discord.CategoryChannel] = {}  # guild_id -> category
    
    async def setup_mafia_category(self, guild: discord.Guild):
        """Автоматическое создание категории Mafia с защитой от дублирования"""
        try:
            guild_id = guild.id
            
            # Проверяем, есть ли уже категория Mafia
            existing_category = discord.utils.get(guild.categories, name="🎭 Игра Mafia")
            
            if existing_category:
                logger.info(f"✅ Категория Mafia уже существует в {guild.name}: {existing_category.name}")
                self.mafia_categories[guild_id] = existing_category
                return existing_category
            
            # Проверяем права бота
            bot_member = guild.get_member(self.bot.user.id)
            if not bot_member:
                logger.error(f"❌ Бот не найден в гильдии {guild.name}")
                return None
                
            bot_permissions = bot_member.guild_permissions
            if not bot_permissions.manage_channels:
                logger.error(f"❌ У бота нет прав на управление каналами в {guild.name}")
                return None
            
            logger.info(f"🔨 Создаю категорию Mafia в {guild.name}...")
            
            # Создаем категорию
            category = await guild.create_category(
                name="🎭 Игра Mafia",
                overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
                }
            )
            
            logger.info(f"✅ Категория Mafia создана: {category.name} (ID: {category.id})")
            
            # Создаем основные каналы
            await self._create_mafia_channels(category)
            
            # Сохраняем ссылку на категорию
            self.mafia_categories[guild_id] = category
            
            return category
            
        except discord.Forbidden as e:
            logger.error(f"❌ Нет прав для создания категории Mafia в {guild.name}: {e}")
            return None
        except discord.HTTPException as e:
            logger.error(f"❌ Ошибка HTTP при создании категории Mafia в {guild.name}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка создания категории Mafia в {guild.name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    async def _create_mafia_channels(self, category: discord.CategoryChannel):
        """Создание каналов в категории Mafia"""
        try:
            # Создаем текстовый канал для игры
            game_channel = await category.guild.create_text_channel(
                name="🎮 mafia-game",
                category=category,
                overwrites={
                    category.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    category.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True)
                }
            )
            logger.info(f"✅ Создан игровой канал: {game_channel.name}")
            
            # Создаем голосовой канал
            voice_channel = await category.guild.create_voice_channel(
                name="🎤 Mafia Voice",
                category=category,
                user_limit=12,
                overwrites={
                    category.guild.default_role: discord.PermissionOverwrite(connect=False),
                    category.guild.me: discord.PermissionOverwrite(connect=True, manage_channels=True)
                }
            )
            logger.info(f"✅ Создан голосовой канал: {voice_channel.name}")
            
            # Создаем приватный канал для мафии
            mafia_chat = await category.guild.create_text_channel(
                name="🔪 mafia-chat",
                category=category,
                overwrites={
                    category.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    category.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
            )
            logger.info(f"✅ Создан канал мафии: {mafia_chat.name}")
            
            # Создаем приватный канал для шерифа
            sheriff_chat = await category.guild.create_text_channel(
                name="🕵️ sheriff-chat",
                category=category,
                overwrites={
                    category.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    category.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
            )
            logger.info(f"✅ Создан канал шерифа: {sheriff_chat.name}")
            
            # Создаем канал для панели управления
            control_channel = await category.guild.create_text_channel(
                name="🎛️ mafia-control",
                category=category,
                overwrites={
                    category.guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
                    category.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True)
                }
            )
            logger.info(f"✅ Создан канал управления: {control_channel.name}")
            
            # Создаем панель управления в новом канале
            await self.create_mafia_control_panel(category.guild, control_channel)
            
            return {
                'game_channel': game_channel,
                'voice_channel': voice_channel,
                'mafia_chat': mafia_chat,
                'sheriff_chat': sheriff_chat,
                'control_channel': control_channel
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания каналов Mafia: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    async def create_mafia_control_panel(self, guild: discord.Guild, channel: discord.TextChannel):
        """Создание панели управления Mafia"""
        embed = discord.Embed(
            title="🎭 Панель управления игрой Mafia",
            description="Управляйте игрой Mafia через кнопки ниже",
            color=0x00ff00
        )
        
        # Проверяем статус игры
        guild_id = guild.id
        if guild_id in self.active_games:
            game = self.active_games[guild_id]
            embed.add_field(
                name="📊 Статус игры",
                value=f"🟢 **Активна**\nИгроков: {len(game.registered_players)}/{game.max_players}\nФаза: {game.current_phase}",
                inline=True
            )
            embed.add_field(
                name="📍 Игровой канал",
                value=game.game_channel.mention if game.game_channel else "Не найден",
                inline=True
            )
        else:
            embed.add_field(
                name="📊 Статус игры",
                value="🔴 **Неактивна**\nИгра не запущена",
                inline=True
            )
            embed.add_field(
                name="📍 Игровой канал",
                value="Не создан",
                inline=True
            )
        
        embed.add_field(
            name="🎮 Информация",
            value="• Минимум игроков: 6\n• Максимум игроков: 12\n• Роли: Мафия, Мирные, Шериф\n• Все управление через кнопки",
            inline=False
        )
        
        view = MafiaControlPanelView(self)
        
        # Удаляем старую панель, если есть
        if guild_id in self.control_panels:
            try:
                await self.control_panels[guild_id].delete()
            except:
                pass
        
        # Создаем новую панель
        message = await channel.send(embed=embed, view=view)
        self.control_panels[guild_id] = message
        
        return message
    
    async def update_control_panel(self, guild_id: int):
        """Обновление панели управления"""
        if guild_id not in self.control_panels:
            return
        
        try:
            message = self.control_panels[guild_id]
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return
            
            embed = discord.Embed(
                title="🎭 Панель управления игрой Mafia",
                description="Управляйте игрой Mafia через кнопки ниже",
                color=0x00ff00
            )
            
            if guild_id in self.active_games:
                game = self.active_games[guild_id]
                embed.add_field(
                    name="📊 Статус игры",
                    value=f"🟢 **Активна**\nИгроков: {len(game.registered_players)}/{game.max_players}\nФаза: {game.current_phase}",
                    inline=True
                )
                embed.add_field(
                    name="📍 Игровой канал",
                    value=game.game_channel.mention if game.game_channel else "Не найден",
                    inline=True
                )
            else:
                embed.add_field(
                    name="📊 Статус игры",
                    value="🔴 **Неактивна**\nИгра не запущена",
                    inline=True
                )
                embed.add_field(
                    name="📍 Игровой канал",
                    value="Не создан",
                    inline=True
                )
            
            embed.add_field(
                name="🎮 Информация",
                value="• Минимум игроков: 6\n• Максимум игроков: 12\n• Роли: Мафия, Мирные, Шериф\n• Все управление через кнопки",
                inline=False
            )
            
            view = MafiaControlPanelView(self)
            await message.edit(embed=embed, view=view)
            
        except Exception as e:
                         logger.error(f"Ошибка обновления панели управления: {e}")
    
    @commands.command(name="mafia_setup")
    @commands.has_permissions(manage_channels=True)
    async def setup_mafia_category_command(self, ctx):
        """Создать категорию Mafia с каналами"""
        try:
            embed = discord.Embed(
                title="🔧 Настройка категории Mafia",
                description="Создаю категорию Mafia с каналами...",
                color=0x00ff00
            )
            msg = await ctx.send(embed=embed)
            
            # Создаем категорию
            category = await self.setup_mafia_category(ctx.guild)
            
            if category:
                embed.description = "✅ Категория Mafia успешно создана!"
                embed.add_field(
                    name="📁 Категория",
                    value=f"🎭 {category.name}",
                    inline=True
                )
                embed.add_field(
                    name="🆔 ID",
                    value=category.id,
                    inline=True
                )
                embed.add_field(
                    name="📊 Каналы",
                    value="• 🎮 mafia-game\n• 🎤 Mafia Voice\n• 🔪 mafia-chat\n• 🕵️ sheriff-chat\n• 🎛️ mafia-control",
                    inline=False
                )
                embed.color = 0x00ff00
            else:
                embed.description = "❌ Не удалось создать категорию Mafia"
                embed.color = 0xff0000
                embed.add_field(
                    name="Возможные причины",
                    value="• У бота нет прав на управление каналами\n• Ошибка подключения к Discord\n• Категория уже существует",
                    inline=False
                )
            
            await msg.edit(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Ошибка при создании категории Mafia: {e}")
            logger.error(f"Ошибка в setup_mafia_category_command: {e}")

    @commands.command(name="mafia_panel")
    @commands.has_permissions(manage_channels=True)
    async def create_mafia_panel(self, ctx):
        """Создать панель управления игрой Mafia"""
        await self.create_mafia_control_panel(ctx.guild, ctx.channel)
        await ctx.send("✅ Панель управления игрой Mafia создана! Используйте кнопки для управления игрой.", delete_after=5)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Автоматическое создание категории Mafia при добавлении бота на сервер"""
        try:
            logger.info(f"🎉 Бот добавлен на сервер: {guild.name}")
            logger.info(f"🔧 Автоматически создаю категорию Mafia для {guild.name}")
            await self.setup_mafia_category(guild)
        except Exception as e:
            logger.error(f"❌ Ошибка автоматического создания категории Mafia для {guild.name}: {e}")

    @commands.command(name="mafia_debug")
    @commands.has_permissions(administrator=True)
    async def mafia_debug(self, ctx):
        """Диагностика системы Mafia и прав бота"""
        embed = discord.Embed(
            title="🔧 Диагностика системы Mafia",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        
        # Проверяем права бота
        bot_member = ctx.guild.get_member(self.bot.user.id)
        if bot_member:
            permissions = bot_member.guild_permissions
            embed.add_field(
                name="🤖 Права бота",
                value=f"• Управление каналами: {'✅' if permissions.manage_channels else '❌'}\n"
                      f"• Управление сервером: {'✅' if permissions.manage_guild else '❌'}\n"
                      f"• Управление ролями: {'✅' if permissions.manage_roles else '❌'}\n"
                      f"• Отправка сообщений: {'✅' if permissions.send_messages else '❌'}\n"
                      f"• Встраивание ссылок: {'✅' if permissions.embed_links else '❌'}",
                inline=True
            )
        else:
            embed.add_field(
                name="🤖 Права бота",
                value="❌ Бот не найден на сервере",
                inline=True
            )
        
        # Проверяем активные игры
        guild_id = ctx.guild.id
        if guild_id in self.active_games:
            game = self.active_games[guild_id]
            embed.add_field(
                name="🎮 Активная игра",
                value=f"• Игроков: {len(game.registered_players)}/{game.max_players}\n"
                      f"• Фаза: {game.current_phase}\n"
                      f"• Канал: {game.game_channel.mention if game.game_channel else 'Не найден'}",
                inline=True
            )
        else:
            embed.add_field(
                name="🎮 Активная игра",
                value="🔴 Нет активной игры",
                inline=True
            )
        
        # Проверяем панель управления
        if guild_id in self.control_panels:
            embed.add_field(
                name="🎛️ Панель управления",
                value="✅ Создана",
                inline=True
            )
        else:
            embed.add_field(
                name="🎛️ Панель управления",
                value="❌ Не создана",
                inline=True
            )
        
        # Информация о сервере
        embed.add_field(
            name="📊 Информация о сервере",
            value=f"• Название: {ctx.guild.name}\n"
                  f"• ID: {ctx.guild.id}\n"
                  f"• Участников: {ctx.guild.member_count}\n"
                  f"• Каналов: {len(ctx.guild.channels)}",
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    mafia_system = MafiaSystem(bot)
    await bot.add_cog(mafia_system)
    
    # Автоматически создаем категорию Mafia для всех серверов бота
    for guild in bot.guilds:
        try:
            logger.info(f"🔧 Настраиваю категорию Mafia для сервера: {guild.name}")
            await mafia_system.setup_mafia_category(guild)
        except Exception as e:
            logger.error(f"❌ Ошибка настройки категории Mafia для {guild.name}: {e}")
    
    logger.info("✅ Система Mafia загружена и настроена") 