"""
Система автоматического воспроизведения музыки
Автоматически присоединяется к голосовому каналу и играет расслабляющую музыку
"""

import discord
from discord.ext import commands
import asyncio
import logging
import yt_dlp
import os
from typing import Optional, Dict, List
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class MusicSystem:
    def __init__(self, bot):
        self.bot = bot
        self.voice_channel_id = 1375822431687671850  # ID голосового канала
        self.voice_client: Optional[discord.VoiceClient] = None
        self.music_queue: List[str] = []
        self.current_track = None
        self.is_playing = False
        self.loop_enabled = True  # Автоматическое зацикливание
        self.volume = 0.5  # Громкость (0.0 - 1.0)
        self.auto_join_enabled = True  # Автоматическое присоединение
        
        # Список расслабляющей музыки (YouTube URLs)
        self.relaxing_music = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Замените на реальные ссылки
            "https://www.youtube.com/watch?v=9bZkp7q19f0",
            "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
            "https://www.youtube.com/watch?v=ZZ5LpwO-An4",
            "https://www.youtube.com/watch?v=OPf0YbXqDm0"
        ]
        
        # Настройки yt-dlp
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }
        
        # Создаем папку для загрузок
        os.makedirs('downloads', exist_ok=True)
        
    async def setup_music_system(self):
        """Настройка системы музыки"""
        try:
            # Проверяем канал
            channel = self.bot.get_channel(self.voice_channel_id)
            if not channel:
                logger.error(f"Голосовой канал не найден: {self.voice_channel_id}")
                return False
            
            if not isinstance(channel, discord.VoiceChannel):
                logger.error(f"Канал {self.voice_channel_id} не является голосовым")
                return False
            
            logger.info(f"Система музыки настроена для канала: {channel.name} (ID: {channel.id})")
            
            # Проверяем права бота в канале
            permissions = channel.permissions_for(channel.guild.me)
            logger.info(f"Права бота в голосовом канале: connect={permissions.connect}, speak={permissions.speak}")
            
            if not permissions.connect:
                logger.error("Бот не имеет права подключаться к голосовому каналу")
                return False
            
            if not permissions.speak:
                logger.error("Бот не имеет права говорить в голосовом канале")
                return False
            
            # Загружаем музыку в очередь
            await self.load_music_queue()
            
            # Проверяем, есть ли уже участники в канале
            if len(channel.members) > 0:
                logger.info(f"В канале уже есть {len(channel.members)} участников, подключаемся...")
                await self.join_voice_channel()
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка настройки системы музыки: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def load_music_queue(self):
        """Загружает музыку в очередь"""
        try:
            logger.info("Загрузка музыки в очередь...")
            
            # Добавляем расслабляющую музыку в очередь
            for url in self.relaxing_music:
                self.music_queue.append(url)
            
            logger.info(f"Загружено {len(self.music_queue)} треков в очередь")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки музыки: {e}")
    
    async def join_voice_channel(self):
        """Присоединяется к голосовому каналу"""
        try:
            logger.info(f"Попытка присоединения к голосовому каналу {self.voice_channel_id}")
            
            channel = self.bot.get_channel(self.voice_channel_id)
            if not channel:
                logger.error("Голосовой канал не найден")
                return False
            
            # Проверяем, не подключены ли уже
            if self.voice_client and self.voice_client.is_connected():
                logger.info("Бот уже подключен к голосовому каналу")
                return True
            
            # Проверяем права бота
            permissions = channel.permissions_for(channel.guild.me)
            if not permissions.connect:
                logger.error("Бот не имеет права подключаться к голосовому каналу")
                return False
            
            # Подключаемся к каналу
            logger.info(f"Подключаемся к каналу: {channel.name}")
            self.voice_client = await channel.connect()
            logger.info(f"Бот успешно присоединился к голосовому каналу: {channel.name}")
            
            # Начинаем воспроизведение
            await self.start_playing()
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка присоединения к голосовому каналу: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def leave_voice_channel(self):
        """Покидает голосовой канал"""
        try:
            if self.voice_client and self.voice_client.is_connected():
                await self.voice_client.disconnect()
                self.voice_client = None
                self.is_playing = False
                logger.info("Бот покинул голосовой канал")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка отключения от голосового канала: {e}")
            return False
    
    async def start_playing(self):
        """Начинает воспроизведение музыки"""
        try:
            if not self.voice_client or not self.voice_client.is_connected():
                logger.warning("Бот не подключен к голосовому каналу")
                return
            
            if self.is_playing:
                logger.info("Музыка уже воспроизводится")
                return
            
            self.is_playing = True
            logger.info("Начинаем воспроизведение музыки")
            
            # Запускаем цикл воспроизведения
            asyncio.create_task(self.play_music_loop())
            
        except Exception as e:
            logger.error(f"Ошибка начала воспроизведения: {e}")
    
    async def play_music_loop(self):
        """Цикл воспроизведения музыки"""
        try:
            while self.is_playing and self.voice_client and self.voice_client.is_connected():
                if not self.music_queue:
                    logger.warning("Очередь музыки пуста")
                    break
                
                # Берем следующий трек
                track_url = self.music_queue.pop(0)
                self.current_track = track_url
                
                logger.info(f"Воспроизводим: {track_url}")
                
                try:
                    # Загружаем и воспроизводим трек
                    await self.play_track(track_url)
                    
                    # Если включено зацикливание, добавляем трек обратно в конец очереди
                    if self.loop_enabled:
                        self.music_queue.append(track_url)
                    
                except Exception as e:
                    logger.error(f"Ошибка воспроизведения трека {track_url}: {e}")
                    continue
                
                # Небольшая пауза между треками
                await asyncio.sleep(1)
            
            self.is_playing = False
            logger.info("Цикл воспроизведения завершен")
            
        except Exception as e:
            logger.error(f"Ошибка в цикле воспроизведения: {e}")
            self.is_playing = False
    
    async def play_track(self, url: str):
        """Воспроизводит один трек"""
        try:
            # Создаем временный файл для загрузки
            temp_filename = f"temp_{datetime.now().timestamp()}.mp3"
            
            # Настройки для загрузки
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'downloads/{temp_filename}',
                'quiet': True,
                'no_warnings': True,
            }
            
            # Загружаем аудио
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            
            # Проверяем, что файл существует
            if not os.path.exists(filename):
                logger.error(f"Файл не найден: {filename}")
                return
            
            # Воспроизводим
            if self.voice_client and self.voice_client.is_connected():
                self.voice_client.play(
                    discord.FFmpegPCMAudio(filename),
                    after=lambda e: logger.info(f"Трек завершен: {e}" if e else "Трек завершен")
                )
                
                # Устанавливаем громкость
                if hasattr(self.voice_client, 'source'):
                    self.voice_client.source = discord.PCMVolumeTransformer(self.voice_client.source)
                    self.voice_client.source.volume = self.volume
                
                # Ждем завершения воспроизведения
                while self.voice_client.is_playing():
                    await asyncio.sleep(1)
                
                # Удаляем временный файл
                try:
                    os.remove(filename)
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Ошибка воспроизведения трека: {e}")
    
    async def stop_playing(self):
        """Останавливает воспроизведение"""
        try:
            self.is_playing = False
            
            if self.voice_client and self.voice_client.is_playing():
                self.voice_client.stop()
            
            logger.info("Воспроизведение остановлено")
            
        except Exception as e:
            logger.error(f"Ошибка остановки воспроизведения: {e}")
    
    async def set_volume(self, volume: float):
        """Устанавливает громкость (0.0 - 1.0)"""
        try:
            self.volume = max(0.0, min(1.0, volume))
            
            if self.voice_client and hasattr(self.voice_client, 'source'):
                if hasattr(self.voice_client.source, 'volume'):
                    self.voice_client.source.volume = self.volume
            
            logger.info(f"Громкость установлена: {self.volume}")
            
        except Exception as e:
            logger.error(f"Ошибка установки громкости: {e}")
    
    async def toggle_loop(self):
        """Переключает зацикливание"""
        try:
            self.loop_enabled = not self.loop_enabled
            status = "включено" if self.loop_enabled else "выключено"
            logger.info(f"Зацикливание {status}")
            return self.loop_enabled
            
        except Exception as e:
            logger.error(f"Ошибка переключения зацикливания: {e}")
            return False
    
    def get_status(self) -> Dict:
        """Возвращает статус системы музыки"""
        return {
            'is_connected': self.voice_client and self.voice_client.is_connected(),
            'is_playing': self.is_playing,
            'current_track': self.current_track,
            'queue_length': len(self.music_queue),
            'volume': self.volume,
            'loop_enabled': self.loop_enabled,
            'auto_join_enabled': self.auto_join_enabled,
            'channel_id': self.voice_channel_id
        }

async def setup_music_system(bot):
    """Настройка системы музыки"""
    try:
        music_system = MusicSystem(bot)
        bot.music_system = music_system
        
        # Настраиваем систему
        await music_system.setup_music_system()
        
        # Устанавливаем обработчики событий
        await setup_music_handlers(bot, music_system)
        
        logger.info("Система музыки настроена")
        
    except Exception as e:
        logger.error(f"Ошибка настройки системы музыки: {e}")
        import traceback
        logger.error(traceback.format_exc())

async def setup_music_handlers(bot, music_system):
    """Устанавливает обработчики событий для системы музыки"""
    
    @bot.event
    async def on_voice_state_update(member, before, after):
        """Обрабатывает изменения голосового состояния"""
        try:
            logger.info(f"Голосовое состояние изменилось: {member.name} - {before.channel} -> {after.channel}")
            
            # Проверяем, что это наш канал
            if after.channel and after.channel.id == music_system.voice_channel_id:
                # Кто-то присоединился к каналу
                if not before.channel or before.channel.id != music_system.voice_channel_id:
                    logger.info(f"Участник {member.name} присоединился к музыкальному каналу")
                    
                    # Если бот еще не подключен, подключаемся
                    if not music_system.voice_client or not music_system.voice_client.is_connected():
                        logger.info("Бот не подключен, подключаемся...")
                        await music_system.join_voice_channel()
                    else:
                        logger.info("Бот уже подключен к каналу")
            
            # Проверяем, если кто-то покинул канал
            elif before.channel and before.channel.id == music_system.voice_channel_id:
                if not after.channel or after.channel.id != music_system.voice_channel_id:
                    logger.info(f"Участник {member.name} покинул музыкальный канал")
                    
                    # Проверяем, остались ли участники в канале
                    channel = bot.get_channel(music_system.voice_channel_id)
                    if channel:
                        logger.info(f"В канале осталось участников: {len(channel.members)}")
                        if len(channel.members) == 1 and channel.members[0].id == bot.user.id:
                            # Остался только бот, можно отключиться
                            logger.info("В канале остался только бот, отключаемся")
                            await music_system.leave_voice_channel()
                        
        except Exception as e:
            logger.error(f"Ошибка обработки изменения голосового состояния: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    # Команды для управления музыкой
    @commands.command(name="music_join")
    @commands.has_permissions(administrator=True)
    async def music_join(ctx):
        """Присоединяется к музыкальному каналу"""
        success = await music_system.join_voice_channel()
        
        embed = discord.Embed(
            title="🎵 Музыкальная система",
            description="Присоединение к голосовому каналу",
            color=0x00ff00 if success else 0xff0000,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📺 Канал",
            value=f"<#{music_system.voice_channel_id}>",
            inline=True
        )
        
        embed.add_field(
            name="🎵 Статус",
            value="✅ Подключен" if success else "❌ Ошибка подключения",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="music_leave")
    @commands.has_permissions(administrator=True)
    async def music_leave(ctx):
        """Покидает музыкальный канал"""
        success = await music_system.leave_voice_channel()
        
        embed = discord.Embed(
            title="🎵 Музыкальная система",
            description="Отключение от голосового канала",
            color=0x00ff00 if success else 0xff0000,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🎵 Статус",
            value="✅ Отключен" if success else "❌ Ошибка отключения",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="music_play")
    @commands.has_permissions(administrator=True)
    async def music_play(ctx):
        """Начинает воспроизведение музыки"""
        await music_system.start_playing()
        
        embed = discord.Embed(
            title="🎵 Музыкальная система",
            description="Воспроизведение музыки",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🎵 Статус",
            value="✅ Воспроизведение начато",
            inline=True
        )
        
        embed.add_field(
            name="📊 Очередь",
            value=f"{len(music_system.music_queue)} треков",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="music_stop")
    @commands.has_permissions(administrator=True)
    async def music_stop(ctx):
        """Останавливает воспроизведение музыки"""
        await music_system.stop_playing()
        
        embed = discord.Embed(
            title="🎵 Музыкальная система",
            description="Остановка воспроизведения",
            color=0xff6b35,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🎵 Статус",
            value="⏹️ Воспроизведение остановлено",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="music_volume")
    @commands.has_permissions(administrator=True)
    async def music_volume(ctx, volume: float):
        """Устанавливает громкость (0.0 - 1.0)"""
        if not 0.0 <= volume <= 1.0:
            embed = discord.Embed(
                title="❌ Ошибка",
                description="Громкость должна быть от 0.0 до 1.0",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            await ctx.send(embed=embed)
            return
        
        await music_system.set_volume(volume)
        
        embed = discord.Embed(
            title="🎵 Музыкальная система",
            description="Установка громкости",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🔊 Громкость",
            value=f"{volume * 100:.0f}%",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="music_loop")
    @commands.has_permissions(administrator=True)
    async def music_loop(ctx):
        """Переключает зацикливание"""
        loop_enabled = await music_system.toggle_loop()
        
        embed = discord.Embed(
            title="🎵 Музыкальная система",
            description="Переключение зацикливания",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🔄 Зацикливание",
            value="✅ Включено" if loop_enabled else "❌ Выключено",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="music_status")
    @commands.has_permissions(administrator=True)
    async def music_status(ctx):
        """Показывает статус музыкальной системы"""
        status = music_system.get_status()
        
        embed = discord.Embed(
            title="🎵 Статус музыкальной системы",
            description="Информация о системе музыки",
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🔗 Подключение",
            value="✅ Подключен" if status['is_connected'] else "❌ Отключен",
            inline=True
        )
        
        embed.add_field(
            name="🎵 Воспроизведение",
            value="✅ Играет" if status['is_playing'] else "⏸️ Остановлено",
            inline=True
        )
        
        embed.add_field(
            name="📊 Очередь",
            value=f"{status['queue_length']} треков",
            inline=True
        )
        
        embed.add_field(
            name="🔊 Громкость",
            value=f"{status['volume'] * 100:.0f}%",
            inline=True
        )
        
        embed.add_field(
            name="🔄 Зацикливание",
            value="✅ Включено" if status['loop_enabled'] else "❌ Выключено",
            inline=True
        )
        
        embed.add_field(
            name="📺 Канал",
            value=f"<#{status['channel_id']}>",
            inline=True
        )
        
        if status['current_track']:
            embed.add_field(
                name="🎼 Текущий трек",
                value=status['current_track'][:50] + "..." if len(status['current_track']) > 50 else status['current_track'],
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="music_debug")
    @commands.has_permissions(administrator=True)
    async def music_debug(ctx):
        """Отладочная информация о музыкальной системе"""
        channel = bot.get_channel(music_system.voice_channel_id)
        
        embed = discord.Embed(
            title="🔧 Отладка музыкальной системы",
            description="Детальная информация для диагностики",
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        # Информация о канале
        if channel:
            embed.add_field(
                name="📺 Канал",
                value=f"**Название:** {channel.name}\n**ID:** {channel.id}\n**Тип:** {channel.type}",
                inline=True
            )
            
            # Права бота
            permissions = channel.permissions_for(channel.guild.me)
            embed.add_field(
                name="🔒 Права бота",
                value=f"**Подключение:** {'✅' if permissions.connect else '❌'}\n**Говорить:** {'✅' if permissions.speak else '❌'}",
                inline=True
            )
            
            # Участники в канале
            embed.add_field(
                name="👥 Участники",
                value=f"**Всего:** {len(channel.members)}\n**Список:** {', '.join([m.name for m in channel.members])}",
                inline=False
            )
        else:
            embed.add_field(
                name="❌ Ошибка",
                value="Канал не найден",
                inline=True
            )
        
        # Статус подключения
        status = music_system.get_status()
        embed.add_field(
            name="🔗 Статус подключения",
            value=f"**Подключен:** {'✅' if status['is_connected'] else '❌'}\n**Воспроизведение:** {'✅' if status['is_playing'] else '❌'}",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    # Добавляем команды к боту
    bot.add_command(music_join)
    bot.add_command(music_leave)
    bot.add_command(music_play)
    bot.add_command(music_stop)
    bot.add_command(music_volume)
    bot.add_command(music_loop)
    bot.add_command(music_status)
    bot.add_command(music_debug) 