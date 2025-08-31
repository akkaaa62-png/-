
"""
Красивая система верификации с цветными кнопками в ЛС для Discord бота
"""

import discord
from discord.ext import commands
import logging
import json
import os
import random
from datetime import datetime
from config import LIMONERICX_SERVER_ID

logger = logging.getLogger('verification')

class BeautifulVerificationSystem:
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = LIMONERICX_SERVER_ID
        self.verification_channel_id = 1383490270850584707  # Канал верификации
        self.verified_role_id = 1375794448650342521  # Роль после верификации

        # База данных верифицированных пользователей и капч
        self.verified_users_file = "verified_users.json"
        self.verified_users = self.load_verified_users()
        self.pending_verifications = {}  # Временное хранение капч

        # Настройки цветных кнопок
        self.button_colors = [
            {"name": "🔴 Красная", "emoji": "🔴", "style": discord.ButtonStyle.danger},
            {"name": "🟠 Оранжевая", "emoji": "🟠", "style": discord.ButtonStyle.secondary},
            {"name": "🟡 Желтая", "emoji": "🟡", "style": discord.ButtonStyle.secondary},
            {"name": "🟢 Зеленая", "emoji": "🟢", "style": discord.ButtonStyle.success},
            {"name": "🔵 Синяя", "emoji": "🔵", "style": discord.ButtonStyle.primary},
            {"name": "🟣 Фиолетовая", "emoji": "🟣", "style": discord.ButtonStyle.secondary},
            {"name": "⚫ Черная", "emoji": "⚫", "style": discord.ButtonStyle.secondary},
            {"name": "⚪ Белая", "emoji": "⚪", "style": discord.ButtonStyle.secondary},
            {"name": "🟤 Коричневая", "emoji": "🟤", "style": discord.ButtonStyle.secondary},
            {"name": "🔸 Розовая", "emoji": "🔸", "style": discord.ButtonStyle.secondary},
            {"name": "💎 Алмазная", "emoji": "💎", "style": discord.ButtonStyle.secondary},
            {"name": "⭐ Золотая", "emoji": "⭐", "style": discord.ButtonStyle.secondary},
            {"name": "🌟 Серебряная", "emoji": "🌟", "style": discord.ButtonStyle.secondary},
            {"name": "✨ Радужная", "emoji": "✨", "style": discord.ButtonStyle.secondary},
            {"name": "🔥 Огненная", "emoji": "🔥", "style": discord.ButtonStyle.secondary},
            {"name": "❄️ Ледяная", "emoji": "❄️", "style": discord.ButtonStyle.secondary},
            {"name": "⚡ Молниевая", "emoji": "⚡", "style": discord.ButtonStyle.secondary},
            {"name": "🌙 Лунная", "emoji": "🌙", "style": discord.ButtonStyle.secondary},
            {"name": "☀️ Солнечная", "emoji": "☀️", "style": discord.ButtonStyle.secondary},
            {"name": "🎯 Цель", "emoji": "🎯", "style": discord.ButtonStyle.secondary}
        ]

    def load_verified_users(self):
        """Загрузка списка верифицированных пользователей"""
        try:
            if os.path.exists(self.verified_users_file):
                with open(self.verified_users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_verified_users(self):
        """Сохранение списка верифицированных пользователей"""
        try:
            with open(self.verified_users_file, 'w', encoding='utf-8') as f:
                json.dump(self.verified_users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения верифицированных пользователей: {e}")

    def generate_color_captcha(self):
        """Генерация капчи с цветными кнопками"""
        # Выбираем 3 случайные кнопки в правильном порядке
        correct_sequence = random.sample(range(20), 3)
        
        return {
            'correct_sequence': correct_sequence,
            'current_step': 0,
            'user_sequence': []
        }

    async def start_verification(self, user):
        """Начало процесса верификации через ЛС"""
        try:
            # Проверяем, не верифицирован ли уже пользователь
            guild = self.bot.get_guild(self.guild_id)
            if not guild:
                return False, "Сервер не найден"

            member = guild.get_member(user.id)
            if not member:
                return False, "Вы не найдены на сервере"

            role = guild.get_role(self.verified_role_id)
            if role in member.roles:
                return False, "Вы уже верифицированы!"

            # Генерируем капчу с цветными кнопками
            captcha_data = self.generate_color_captcha()
            self.pending_verifications[user.id] = captcha_data

            # Отправляем красивое сообщение с инструкциями
            embed = discord.Embed(
                title="🌈 Цветная верификация Limonericx",
                description="**🎨 Добро пожаловать в уникальную систему верификации!**\n\n✨ Для получения роли участника необходимо пройти тест на внимательность",
                color=0x9932cc
            )
            
            # Показываем правильную последовательность
            sequence_text = ""
            for i, button_index in enumerate(captcha_data['correct_sequence']):
                button = self.button_colors[button_index]
                sequence_text += f"{i+1}️⃣ **{button['name']}** {button['emoji']}\n"
            
            embed.add_field(
                name="🎯 **Правильная последовательность:**",
                value=sequence_text,
                inline=False
            )
            
            embed.add_field(
                name="📝 **Как пройти:**",
                value="1️⃣ Запомните последовательность выше\n2️⃣ Нажмите кнопки **В ТОЧНОМ ПОРЯДКЕ**\n3️⃣ Получите роль участника!\n\n⚠️ **Один неверный клик = начать заново!**",
                inline=False
            )
            
            embed.add_field(
                name="⏰ **Важно:**",
                value="• У вас есть **10 минут** на прохождение\n• Порядок нажатий **критически важен**\n• При ошибке нажмите кнопку на сервере заново\n• Всего кнопок: **20**, правильных: **3**",
                inline=False
            )
            
            embed.set_footer(
                text="🛡️ Система безопасности Limonericx • Защита от ботов",
                icon_url=guild.icon.url if guild.icon else None
            )
            
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/845287707838963742.png")

            # Создаем view с 20 цветными кнопками
            view = ColorCaptchaView(self, user.id)
            
            try:
                await user.send(embed=embed, view=view)
                logger.info(f"Отправлена цветная капча пользователю {user.name}")
                return True, "Цветная капча отправлена в ЛС!"
            except discord.Forbidden:
                return False, "Не удалось отправить ЛС. Откройте личные сообщения!"

        except Exception as e:
            logger.error(f"Ошибка при начале верификации {user}: {e}")
            return False, f"Ошибка: {str(e)}"

    async def check_button_press(self, user_id, button_index):
        """Проверка нажатия кнопки"""
        if user_id not in self.pending_verifications:
            return False, "Верификация не найдена. Начните заново."

        captcha_data = self.pending_verifications[user_id]
        current_step = captcha_data['current_step']
        correct_sequence = captcha_data['correct_sequence']

        # Проверяем правильность кнопки
        if button_index == correct_sequence[current_step]:
            # Правильная кнопка!
            captcha_data['user_sequence'].append(button_index)
            captcha_data['current_step'] += 1
            
            if captcha_data['current_step'] >= len(correct_sequence):
                # Все кнопки нажаты правильно!
                return True, "verification_complete"
            else:
                # Переходим к следующему шагу
                step_num = captcha_data['current_step'] + 1
                next_button = self.button_colors[correct_sequence[captcha_data['current_step']]]
                return True, f"step_{step_num}_{next_button['name']}"
        else:
            # Неправильная кнопка
            wrong_button = self.button_colors[button_index]
            correct_button = self.button_colors[correct_sequence[current_step]]
            return False, f"Неверно! Нажали: {wrong_button['name']}, нужно было: {correct_button['name']}"

    async def complete_verification(self, user):
        """Завершение верификации и выдача роли"""
        try:
            guild = self.bot.get_guild(self.guild_id)
            member = guild.get_member(user.id)
            role = guild.get_role(self.verified_role_id)

            await member.add_roles(role, reason="Прошел цветную верификацию")

            # Записываем в базу
            self.verified_users[str(user.id)] = {
                'username': str(user),
                'verified_at': datetime.now().isoformat(),
                'account_created': user.created_at.isoformat(),
                'verification_method': 'color_buttons'
            }
            self.save_verified_users()

            # Удаляем из pending
            if user.id in self.pending_verifications:
                del self.pending_verifications[user.id]

            # Отправляем красивое сообщение об успехе
            embed = discord.Embed(
                title="🎉 Поздравляем!",
                description="**🌈 Цветная верификация успешно пройдена!**\n\n✨ Добро пожаловать в наше сообщество Limonericx!",
                color=0x00ff00
            )
            
            embed.add_field(
                name="🎯 Что получили:",
                value="• ✅ Роль участника\n• 🗨️ Доступ ко всем каналам\n• 🎮 Возможность играть на сервере\n• 🎊 Участие в мероприятиях\n• 🏆 Прохождение уникальной верификации!",
                inline=False
            )
            
            embed.add_field(
                name="🚀 Что дальше:",
                value="• 📚 Изучите правила сервера\n• 👥 Познакомьтесь с участниками\n• 💬 Начните общение в чатах\n• 🎮 Присоединяйтесь к играм\n• 🌟 Наслаждайтесь общением!",
                inline=False
            )
            
            embed.set_footer(
                text=f"🛡️ Верифицирован через цветные кнопки • {datetime.now().strftime('%d.%m.%Y в %H:%M')}",
                icon_url=guild.icon.url if guild.icon else None
            )
            
            embed.set_thumbnail(url=user.display_avatar.url)

            await user.send(embed=embed)
            
            logger.info(f"Пользователь {user} успешно верифицирован через цветные кнопки")
            return True

        except Exception as e:
            logger.error(f"Ошибка при завершении верификации {user}: {e}")
            return False


class ColorCaptchaView(discord.ui.View):
    """View с 20 цветными кнопками для верификации"""
    
    def __init__(self, verification_system, user_id):
        super().__init__(timeout=600)  # 10 минут
        self.verification_system = verification_system
        self.user_id = user_id
        
        # Создаем 20 кнопок
        for i, button_info in enumerate(verification_system.button_colors):
            button = ColorButton(
                style=button_info['style'],
                emoji=button_info['emoji'],
                custom_id=f"color_button_{i}",
                row=i // 5  # Распределяем по рядам (5 кнопок в ряду)
            )
            button.button_index = i
            button.verification_system = verification_system
            button.user_id = user_id
            self.add_item(button)


class ColorButton(discord.ui.Button):
    """Цветная кнопка для верификации"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.button_index = None
        self.verification_system = None
        self.user_id = None
    
    async def callback(self, interaction: discord.Interaction):
        try:
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Это не ваша верификация!", ephemeral=True)
                return
            success, message = await self.verification_system.check_button_press(
                self.user_id, self.button_index
            )
            if success:
                if message == "verification_complete":
                    # Верификация завершена успешно!
                    user = interaction.user
                    complete_success = await self.verification_system.complete_verification(user)
                    
                    if complete_success:
                        # Отключаем все кнопки
                        for item in self.view.children:
                            item.disabled = True
                        
                        embed = discord.Embed(
                            title="🎉 Успех!",
                            description="**Поздравляем! Все кнопки нажаты правильно!**\n\n✅ Роль участника получена!\n🎊 Добро пожаловать в Limonericx!",
                            color=0x00ff00
                        )
                        
                        try:
                            if not interaction.response.is_done():
                                await interaction.response.edit_message(embed=embed, view=self.view)
                            else:
                                await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, view=self.view)
                        except discord.errors.InteractionResponded:
                            await interaction.followup.send("✅ Верификация завершена успешно!", ephemeral=True)
                        
                        # Удаляем пользователя из pending
                        if user.id in self.verification_system.pending_verifications:
                            del self.verification_system.pending_verifications[user.id]
                    else:
                        try:
                            if not interaction.response.is_done():
                                await interaction.response.send_message("❌ Ошибка при выдаче роли", ephemeral=True)
                            else:
                                await interaction.followup.send("❌ Ошибка при выдаче роли", ephemeral=True)
                        except:
                            pass
            elif message.startswith("step_"):
                # Правильный шаг, показываем прогресс
                parts = message.split("_", 2)
                step_num = parts[1]
                next_button_name = parts[2]
                
                embed = discord.Embed(
                    title=f"✅ Шаг {step_num}/3 пройден!",
                    description=f"**Отлично!** Теперь нажмите: **{next_button_name}**",
                    color=0x00ff00
                )
                
                # Показываем прогресс
                progress_text = ""
                captcha_data = self.verification_system.pending_verifications[self.user_id]
                for i, button_index in enumerate(captcha_data['correct_sequence']):
                    button = self.verification_system.button_colors[button_index]
                    if i < captcha_data['current_step']:
                        progress_text += f"✅ {button['name']} {button['emoji']}\n"
                    elif i == captcha_data['current_step']:
                        progress_text += f"👉 **{button['name']}** {button['emoji']} ← **СЛЕДУЮЩАЯ**\n"
                    else:
                        progress_text += f"⏳ {button['name']} {button['emoji']}\n"
                
                embed.add_field(
                    name="📋 Прогресс:",
                    value=progress_text,
                    inline=False
                )
                
                try:
                    if not interaction.response.is_done():
                        await interaction.response.edit_message(embed=embed, view=self.view)
                    else:
                        await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, view=self.view)
                except discord.errors.InteractionResponded:
                    await interaction.followup.send("✅ Шаг пройден! Следуйте инструкциям.", ephemeral=True)
            else:
                try:
                    if not interaction.response.is_done():
                        await interaction.response.send_message(f"✅ {message}", ephemeral=True)
                    else:
                        await interaction.followup.send(f"✅ {message}", ephemeral=True)
                except:
                    pass
        except Exception as e:
            # Ошибка - неправильная кнопка или другая ошибка
            embed = discord.Embed(
                title="❌ Неправильно!",
                description=f"**{message}**\n\n🔄 Начните верификацию заново на сервере.",
                color=0xff0000
            )
            # Отключаем все кнопки
            for item in self.view.children:
                item.disabled = True
            # Удаляем из pending verifications
            if self.user_id in self.verification_system.pending_verifications:
                del self.verification_system.pending_verifications[self.user_id]
            try:
                if not interaction.response.is_done():
                    await interaction.response.edit_message(embed=embed, view=self.view)
                else:
                    await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, view=self.view)
            except discord.errors.InteractionResponded:
                await interaction.followup.send("❌ Неправильно! Начните верификацию заново.", ephemeral=True)
            except Exception:
                pass
            logger.error(f"Ошибка в кнопке верификации: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ Произошла ошибка", ephemeral=True)
                else:
                    await interaction.followup.send("❌ Произошла ошибка", ephemeral=True)
            except:
                pass
            return


class BeautifulVerificationView(discord.ui.View):
    def __init__(self, verification_system):
        super().__init__(timeout=None)
        self.verification_system = verification_system

    @discord.ui.button(label='🌈 Пройти цветную верификацию', style=discord.ButtonStyle.primary, emoji='🎨')
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Кнопка для начала верификации"""
        user = interaction.user

        await interaction.response.defer(ephemeral=True)

        try:
            success, message = await self.verification_system.start_verification(user)

            if success:
                embed = discord.Embed(
                    title="📨 Проверьте ЛС!",
                    description=f"**{user.mention}**, вам отправлена цветная капча в личные сообщения!\n\n🌈 Проверьте ЛС и следуйте инструкциям для получения роли.",
                    color=0x9932cc
                )
                embed.add_field(
                    name="📱 Не получили сообщение?",
                    value="• Проверьте настройки приватности\n• Разрешите сообщения от участников сервера\n• Попробуйте еще раз через минуту",
                    inline=False
                )
                embed.add_field(
                    name="🎯 Особенности верификации:",
                    value="• 20 цветных кнопок на выбор\n• Нужно нажать 3 правильные\n• Порядок критически важен\n• Одна ошибка = начать заново",
                    inline=False
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(
                    title="❌ Ошибка",
                    description=message,
                    color=0xff0000
                )
                await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Ошибка в кнопке верификации: {e}")
            await interaction.followup.send(
                "❌ Произошла ошибка. Попробуйте еще раз или обратитесь к администрации.",
                ephemeral=True
            )


async def setup_verification_system(bot):
    """Настройка красивой системы верификации"""
    try:
        verification_system = BeautifulVerificationSystem(bot)
        bot.verification_system = verification_system

        verification_channel = bot.get_channel(verification_system.verification_channel_id)
        if not verification_channel:
            logger.error(f"Канал верификации не найден: {verification_system.verification_channel_id}")
            return

        # Красивое главное сообщение
        embed = discord.Embed(
            title="🌈 Цветная система верификации Limonericx",
            description="**✨ Добро пожаловать на сервер Limonericx!** 🎨\n\n🔒 Для получения доступа ко всем каналам пройдите уникальную цветную верификацию!",
            color=0x9932cc
        )

        embed.add_field(
            name="🎯 **Что вы получите:**",
            value="```🎨 Полный доступ к серверу\n💬 Общение во всех каналах  \n🎮 Игра на Minecraft сервере\n🎊 Участие в мероприятиях\n🏆 Уникальный опыт верификации\n🌈 Статус прошедшего цветной тест```",
            inline=False
        )

        embed.add_field(
            name="🌈 **Цветная верификация:**",
            value="```🎨 20 разноцветных кнопок\n🎯 Нужно нажать 3 правильные\n📋 В строго определенном порядке\n⚡ Один неверный клик = начать заново\n🧠 Тест на внимательность и память```",
            inline=False
        )

        embed.add_field(
            name="🎮 **Процесс прохождения:**",
            value="```🔹 Нажмите кнопку ниже\n🔹 Проверьте личные сообщения\n🔹 Запомните последовательность цветов\n🔹 Нажмите кнопки в правильном порядке\n🔹 Получите роль участника!```",
            inline=False
        )

        embed.add_field(
            name="📋 **Правила сервера:**",
            value="```🤝 Уважайте других участников\n🚫 Запрещен спам и флуд\n⚡ Соблюдайте правила чата\n🛡️ Слушайтесь администрацию\n🎨 Наслаждайтесь творчеством!```",
            inline=False
        )

        embed.add_field(
            name="🆘 **Нужна помощь?**",
            value="Если возникли проблемы с цветной верификацией, обратитесь к <@&1376222106760773836> в тикетах технической поддержки.",
            inline=False
        )

        embed.set_footer(
            text="🌈 Защищено цветной системой безопасности • Нажмите кнопку для начала",
            icon_url=bot.user.display_avatar.url
        )

        embed.set_image(url="https://media.discordapp.net/attachments/1234567890/1234567890/verification_banner.gif")
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/845287707838963742.png")

        view = BeautifulVerificationView(verification_system)

        # Очищаем канал и отправляем новое сообщение
        try:
            await verification_channel.purge(limit=100)
        except:
            pass

        await verification_channel.send(embed=embed, view=view)

        logger.info("Красивая система верификации с цветными кнопками настроена")

    except Exception as e:
        logger.error(f"Ошибка при настройке системы верификации: {e}")
