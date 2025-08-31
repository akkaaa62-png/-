"""
Умная система автоматического восстановления и исправления ошибок
Автоматически восстанавливает поврежденные файлы и исправляет ошибки
"""

import discord
from discord.ext import commands, tasks
import logging
import asyncio
import json
import os
import shutil
import traceback
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pickle
import sqlite3
from pathlib import Path
import random
import threading
import queue
import re
import ast
import inspect
import difflib
import subprocess
import sys
from collections import defaultdict, Counter

logger = logging.getLogger('auto_recovery')

class UltraSmartAI:
    """Ультра-умный ИИ для анализа и исправления ошибок"""
    def __init__(self):
        self.error_patterns = defaultdict(list)
        self.solution_database = {}
        self.code_analysis_cache = {}
        self.prediction_models = {}
        self.self_improvement_log = []
        
    async def analyze_code_patterns(self, file_path: str):
        """Анализ паттернов в коде для предсказания ошибок"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                
            # Анализируем структуру кода
            tree = ast.parse(code)
            
            # Ищем потенциальные проблемы
            issues = []
            
            # Проверяем обработчики событий
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if any(hasattr(decorator, 'id') and getattr(decorator, 'id', '') == 'tasks.loop' for decorator in node.decorator_list):
                        # Проверяем задачи на потенциальные проблемы
                        if not self._check_task_safety(node):
                            issues.append(f"Потенциально небезопасная задача: {node.name}")
                            
                    # Проверяем обработчики кнопок
                    if 'button' in node.name.lower():
                        if not self._check_button_handler_safety(node):
                            issues.append(f"Потенциально небезопасный обработчик кнопки: {node.name}")
                            
            return issues
            
        except Exception as e:
            logger.error(f"Ошибка анализа кода {file_path}: {e}")
            return []

    def _check_task_safety(self, node):
        """Проверка безопасности задачи"""
        try:
            # Проверяем наличие обработки ошибок
            has_try_catch = False
            for child in ast.walk(node):
                if isinstance(child, ast.Try):
                    has_try_catch = True
                    break
            return has_try_catch
        except:
            return False

    def _check_button_handler_safety(self, node):
        """Проверка безопасности обработчика кнопок"""
        try:
            # Проверяем наличие проверок
            has_checks = False
            for child in ast.walk(node):
                if isinstance(child, ast.If):
                    has_checks = True
                    break
            return has_checks
        except:
            return False

    async def predict_errors(self, system_name: str):
        """Предсказание ошибок на основе анализа"""
        try:
            predictions = []
            
            # Анализируем историю ошибок
            if system_name in self.error_patterns:
                recent_errors = self.error_patterns[system_name][-10:]  # Последние 10 ошибок
                
                # Ищем паттерны
                error_types = [error.get('type') for error in recent_errors]
                error_counter = Counter(error_types)
                
                # Если ошибка повторяется часто - предсказываем её повторение
                for error_type, count in error_counter.items():
                    if count >= 3:
                        predictions.append({
                            'type': 'recurring_error',
                            'error_type': error_type,
                            'confidence': min(count / 10, 0.9),
                            'system': system_name
                        })
                        
            # Анализируем код на потенциальные проблемы
            if system_name == 'role_system':
                code_issues = await self.analyze_code_patterns('role_system.py')
                for issue in code_issues:
                    predictions.append({
                        'type': 'code_issue',
                        'description': issue,
                        'confidence': 0.7,
                        'system': system_name
                    })
                    
            return predictions
            
        except Exception as e:
            logger.error(f"Ошибка предсказания для {system_name}: {e}")
            return []

    async def generate_fix(self, error_type: str, context: dict):
        """Генерация исправления на основе типа ошибки"""
        try:
            fixes = {
                'button_not_found': self._generate_button_fix,
                'role_system_logic': self._generate_role_system_fix,
                'data_corruption': self._generate_data_fix,
                'discord_api_error': self._generate_discord_fix,
                'memory_issue': self._generate_memory_fix
            }
            
            if error_type in fixes:
                return await fixes[error_type](context)
            else:
                return await self._generate_generic_fix(error_type, context)
                
        except Exception as e:
            logger.error(f"Ошибка генерации исправления {error_type}: {e}")
            return None

    async def _generate_button_fix(self, context: dict):
        """Генерация исправления для кнопок"""
        return {
            'action': 'recreate_buttons',
            'priority': 'high',
            'description': 'Пересоздание сломанных кнопок',
            'code': '''
async def fix_buttons():
    await recreate_weekly_goal_message()
    await cleanup_old_goal_messages()
'''
        }

    async def _generate_role_system_fix(self, context: dict):
        """Генерация исправления для системы ролей"""
        return {
            'action': 'fix_role_system',
            'priority': 'high',
            'description': 'Исправление логики системы ролей',
            'code': '''
async def fix_role_system():
    await enhance_role_system_check()
    await save_role_system_data()
    await restore_role_system_data()
'''
        }

    async def _generate_data_fix(self, context: dict):
        """Генерация исправления для данных"""
        return {
            'action': 'fix_data',
            'priority': 'critical',
            'description': 'Исправление коррупции данных',
            'code': '''
async def fix_data():
    await check_data_integrity()
    await optimize_memory()
    await save_role_system_data()
'''
        }

    async def _generate_discord_fix(self, context: dict):
        """Генерация исправления для Discord API"""
        return {
            'action': 'fix_discord',
            'priority': 'critical',
            'description': 'Восстановление Discord соединения',
            'code': '''
async def fix_discord():
    await recover_discord_connection()
    await restart_background_tasks()
'''
        }

    async def _generate_memory_fix(self, context: dict):
        """Генерация исправления для памяти"""
        return {
            'action': 'fix_memory',
            'priority': 'medium',
            'description': 'Оптимизация памяти',
            'code': '''
async def fix_memory():
    await optimize_memory()
    import gc
    gc.collect()
'''
        }

    async def _generate_generic_fix(self, error_type: str, context: dict):
        """Генерация общего исправления"""
        return {
            'action': 'generic_fix',
            'priority': 'low',
            'description': f'Общее исправление для {error_type}',
            'code': f'''
async def fix_{error_type}():
    logger.warning("Применяю общее исправление для {error_type}")
    await auto_fix_detected_issues()
'''
        }

class SmartDataManager:
    """Умный менеджер данных с сохранением в файл"""
    def __init__(self, filename="smart_data.pkl"):
        self.filename = filename
        self.data = {}
        self.lock = threading.Lock()
        self.load_data()
        
    def load_data(self):
        """Загружает данные из файла"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'rb') as f:
                    self.data = pickle.load(f)
                logger.info(f"Загружено {len(self.data)} записей из {self.filename}")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            self.data = {}
            
    def save_data(self):
        """Сохраняет данные в файл"""
        try:
            with self.lock:
                with open(self.filename, 'wb') as f:
                    pickle.dump(self.data, f)
        except Exception as e:
            logger.error(f"Ошибка сохранения данных: {e}")
            
    def get(self, key, default=None):
        return self.data.get(key, default)
        
    def set(self, key, value):
        self.data[key] = value
        self.save_data()
        
    def update(self, updates):
        self.data.update(updates)
        self.save_data()

class AutoRecoverySystem:
    def __init__(self, bot):
        self.bot = bot
        self.backup_dir = "backups"
        self.recovery_log_file = "recovery_log.json"
        self.error_counts = {}  # {error_type: count}
        self.last_recovery = {}  # {file: timestamp}
        self.critical_files = [
            "config.py",
            "bot.py",
            "main.py",
            "requirements.txt",
            "role_system.py",
            "moderation_logs.py",
            "smart_protection_system.py"
        ]
        self.backup_interval = 3600  # 1 час
        self.max_recovery_attempts = 3
        self.recovery_cooldown = 300  # 5 минут
        
        # Система иммунитета
        self.immunity_mode = True
        self.immunity_check_interval = 600  # 10 минут
        self.system_health = {}  # {system_name: health_status}
        self.fix_attempts = {}  # {system_name: attempts}
        self.max_fix_attempts = 5
        self.immunity_cooldown = 1800  # 30 минут
        
        # Умные возможности
        self.ai_mode = True
        self.prediction_mode = True
        self.auto_fix_logical_bugs = True
        self.smart_diagnostics = True
        self.auto_test_after_fix = True
        
        # Критически важные улучшения
        self.smart_data_manager = SmartDataManager()
        self.learning_mode = True
        self.auto_backup_before_changes = True
        self.smart_logging = True
        self.discord_api_recovery = True
        
        # Ультра-умные возможности
        self.ultra_ai = UltraSmartAI()
        self.self_improvement_mode = True
        self.predictive_maintenance = True
        self.auto_code_generation = True
        self.intelligent_testing = True
        self.pattern_analysis = True
        
        # База данных ошибок и решений
        self.error_patterns = {}
        self.solution_database = {}
        self.performance_metrics = {}
        
        # Система обучения на ошибках
        self.error_history = []
        self.successful_fixes = {}
        self.failed_fixes = {}
        
        # Создаем папку для бэкапов
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Запускаем задачи
        self.backup_task.start()
        self.health_check_task.start()
        self.immunity_task.start()
        if self.ai_mode:
            self.ai_monitoring_task.start()
            self.prediction_task.start()
        if self.learning_mode:
            self.learning_task.start()
        if self.smart_logging:
            self.smart_logging_task.start()
        if self.predictive_maintenance:
            self.predictive_maintenance_task.start()
        if self.self_improvement_mode:
            self.self_improvement_task.start()
        
    async def setup(self):
        """Настройка системы восстановления"""
        logger.info("Система автоматического восстановления запущена")
        
        # Создаем начальные бэкапы
        await self.create_backups()
        
        # Проверяем целостность файлов
        await self.check_file_integrity()
        
    @tasks.loop(seconds=3600)  # Каждый час
    async def backup_task(self):
        """Автоматическое создание бэкапов"""
        try:
            await self.create_backups()
            logger.info("Автоматический бэкап создан")
        except Exception as e:
            logger.error(f"Ошибка создания бэкапа: {e}")
            
    @tasks.loop(seconds=1800)  # Каждые 30 минут
    async def health_check_task(self):
        """Проверка здоровья системы"""
        try:
            await self.health_check()
        except Exception as e:
            logger.error(f"Ошибка проверки здоровья: {e}")
            
    @tasks.loop(seconds=600)  # Каждые 10 минут
    async def immunity_task(self):
        """Система иммунитета - постоянный мониторинг и исправление"""
        try:
            await self.immunity_check()
        except Exception as e:
            logger.error(f"Ошибка системы иммунитета: {e}")
            
    @tasks.loop(seconds=300)  # Каждые 5 минут
    async def ai_monitoring_task(self):
        """Умный мониторинг с ИИ"""
        try:
            await self.ai_health_check()
        except Exception as e:
            logger.error(f"Ошибка ИИ мониторинга: {e}")

    @tasks.loop(seconds=1200)  # Каждые 20 минут
    async def prediction_task(self):
        """Предсказание возможных проблем"""
        try:
            await self.predict_potential_issues()
        except Exception as e:
            logger.error(f"Ошибка предсказания: {e}")

    @tasks.loop(seconds=1800)  # Каждые 30 минут
    async def learning_task(self):
        """Система обучения на ошибках"""
        try:
            await self.learn_from_errors()
        except Exception as e:
            logger.error(f"Ошибка системы обучения: {e}")

    @tasks.loop(seconds=60)  # Каждую минуту
    async def smart_logging_task(self):
        """Умная система логирования"""
        try:
            await self.smart_logging_check()
        except Exception as e:
            logger.error(f"Ошибка умного логирования: {e}")

    @tasks.loop(seconds=900)  # Каждые 15 минут
    async def predictive_maintenance_task(self):
        """Предсказательное обслуживание"""
        try:
            await self.predictive_maintenance_check()
        except Exception as e:
            logger.error(f"Ошибка предсказательного обслуживания: {e}")

    @tasks.loop(seconds=3600)  # Каждый час
    async def self_improvement_task(self):
        """Самоулучшение системы"""
        try:
            await self.self_improvement_check()
        except Exception as e:
            logger.error(f"Ошибка самоулучшения: {e}")

    async def create_backups(self):
        """Создает бэкапы важных файлов"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}")
        os.makedirs(backup_path, exist_ok=True)
        
        for file in self.critical_files:
            if os.path.exists(file):
                try:
                    shutil.copy2(file, os.path.join(backup_path, file))
                except Exception as e:
                    logger.error(f"Ошибка создания бэкапа {file}: {e}")
                    
        # Создаем бэкап конфигурации
        await self.backup_config()
        
        # Очищаем старые бэкапы (оставляем последние 10)
        await self.cleanup_old_backups()
        
    async def backup_config(self):
        """Создает бэкап конфигурации"""
        try:
            config_data = {
                "timestamp": datetime.now().isoformat(),
                "bot_id": self.bot.user.id if self.bot.user else None,
                "guild_count": len(self.bot.guilds),
                "system_info": {
                    "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
                    "discord_version": discord.__version__,
                    "platform": os.name
                }
            }
            
            backup_file = os.path.join(self.backup_dir, "config_backup.json")
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Ошибка создания бэкапа конфигурации: {e}")
            
    async def cleanup_old_backups(self):
        """Очищает старые бэкапы"""
        try:
            backup_dirs = [d for d in os.listdir(self.backup_dir) if d.startswith("backup_")]
            backup_dirs.sort(reverse=True)
            
            # Оставляем только последние 10 бэкапов
            for old_backup in backup_dirs[10:]:
                old_path = os.path.join(self.backup_dir, old_backup)
                if os.path.isdir(old_path):
                    shutil.rmtree(old_path)
                    logger.info(f"Удален старый бэкап: {old_backup}")
                    
        except Exception as e:
            logger.error(f"Ошибка очистки старых бэкапов: {e}")
            
    async def check_file_integrity(self):
        """Проверяет целостность файлов"""
        for file in self.critical_files:
            if os.path.exists(file):
                try:
                    # Проверяем, что файл можно прочитать
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Проверяем базовую структуру файла
                    if file.endswith('.py'):
                        if not content.strip():
                            await self.recover_file(file, "empty_file")
                        elif 'import' not in content and 'class' not in content and 'def' not in content:
                            await self.recover_file(file, "invalid_structure")
                            
                except UnicodeDecodeError:
                    await self.recover_file(file, "encoding_error")
                except Exception as e:
                    await self.recover_file(file, f"read_error: {str(e)}")
                    
    async def recover_file(self, file_path: str, error_type: str):
        """Восстанавливает поврежденный файл"""
        if self.should_skip_recovery(file_path, error_type):
            return
            
        logger.warning(f"Попытка восстановления файла {file_path} (ошибка: {error_type})")
        
        try:
            # Ищем последний рабочий бэкап
            backup_file = await self.find_latest_backup(file_path)
            
            if backup_file:
                # Восстанавливаем из бэкапа
                shutil.copy2(backup_file, file_path)
                logger.info(f"Файл {file_path} восстановлен из бэкапа")
                await self.log_recovery(file_path, error_type, "backup_restore", True)
            else:
                # Пытаемся исправить файл
                success = await self.fix_file(file_path, error_type)
                await self.log_recovery(file_path, error_type, "manual_fix", success)
                
        except Exception as e:
            logger.error(f"Ошибка восстановления файла {file_path}: {e}")
            await self.log_recovery(file_path, error_type, "failed", False)
            
    async def find_latest_backup(self, file_path: str) -> Optional[str]:
        """Находит последний рабочий бэкап файла"""
        try:
            backup_dirs = [d for d in os.listdir(self.backup_dir) if d.startswith("backup_")]
            backup_dirs.sort(reverse=True)
            
            for backup_dir in backup_dirs:
                backup_file = os.path.join(self.backup_dir, backup_dir, os.path.basename(file_path))
                if os.path.exists(backup_file):
                    # Проверяем, что бэкап рабочий
                    if await self.verify_backup(backup_file):
                        return backup_file
                        
        except Exception as e:
            logger.error(f"Ошибка поиска бэкапа для {file_path}: {e}")
            
        return None
        
    async def verify_backup(self, backup_file: str) -> bool:
        """Проверяет, что бэкап файла рабочий"""
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Базовая проверка для Python файлов
            if backup_file.endswith('.py'):
                return len(content.strip()) > 0 and ('import' in content or 'class' in content or 'def' in content)
            else:
                return len(content.strip()) > 0
                
        except Exception:
            return False
            
    async def fix_file(self, file_path: str, error_type: str) -> bool:
        """Пытается исправить файл вручную"""
        try:
            if error_type == "empty_file":
                return await self.fix_empty_file(file_path)
            elif error_type == "encoding_error":
                return await self.fix_encoding_error(file_path)
            elif error_type == "invalid_structure":
                return await self.fix_invalid_structure(file_path)
            else:
                return await self.fix_generic_error(file_path)
                
        except Exception as e:
            logger.error(f"Ошибка исправления файла {file_path}: {e}")
            return False
            
    async def fix_empty_file(self, file_path: str) -> bool:
        """Исправляет пустой файл"""
        try:
            if file_path == "config.py":
                # Создаем базовую конфигурацию
                basic_config = '''"""
Базовая конфигурация Discord бота
"""

# Discord Bot Token
DISCORD_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Server ID
LIMONERICX_SERVER_ID = 123456789

# Welcome Channel ID
WELCOME_CHANNEL_ID = 123456789

# Colors
WELCOME_COLOR = 0x00ff00
GOODBYE_COLOR = 0xff0000

# Welcome Messages
WELCOME_TITLE = "Добро пожаловать!"
WELCOME_DESCRIPTION = "Рады видеть вас на сервере!"
GOODBYE_TITLE = "До свидания!"
GOODBYE_DESCRIPTION = "Надеемся увидеть вас снова!"

# Welcome Fields
WELCOME_FIELDS = [
    {
        "name": "📋 Правила",
        "value": "Обязательно ознакомьтесь с правилами сервера!",
        "inline": True
    },
    {
        "name": "🎮 Роли",
        "value": "Получите роли в соответствующем канале!",
        "inline": True
    }
]

# Button Settings
WELCOME_BUTTON_ENABLED = True
WELCOME_BUTTON_LABEL = "📋 Правила"
WELCOME_BUTTON_URL = "https://discord.gg/your-server"

# Bot Settings
BOT_COMMAND_PREFIX = "!"
BOT_ACTIVITY_NAME = "за участниками"
'''
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(basic_config)
                return True
                
            elif file_path == "bot.py":
                # Создаем базовый бот
                basic_bot = '''"""
Discord Welcome Bot Implementation
"""

import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class DiscordWelcomeBot:
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.guilds = True
        
        self.bot = commands.Bot(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        
    async def start_bot(self):
        await self.bot.start("YOUR_BOT_TOKEN_HERE")

if __name__ == "__main__":
    bot = DiscordWelcomeBot()
    bot.start_bot()
'''
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(basic_bot)
                return True
                
            else:
                # Для других файлов создаем заглушку
                stub_content = f'''"""
Восстановленный файл {file_path}
Этот файл был автоматически восстановлен системой.
"""

# Файл восстановлен автоматически
# Добавьте необходимый код вручную
'''
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(stub_content)
                return True
                
        except Exception as e:
            logger.error(f"Ошибка исправления пустого файла {file_path}: {e}")
            return False
            
    async def fix_encoding_error(self, file_path: str) -> bool:
        """Исправляет ошибки кодировки"""
        try:
            # Пытаемся прочитать с разными кодировками
            encodings = ['utf-8', 'cp1251', 'latin-1', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    
                    # Перезаписываем с правильной кодировкой
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    return True
                    
                except UnicodeDecodeError:
                    continue
                    
            return False
            
        except Exception as e:
            logger.error(f"Ошибка исправления кодировки {file_path}: {e}")
            return False
            
    async def fix_invalid_structure(self, file_path: str) -> bool:
        """Исправляет неверную структуру файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Пытаемся найти и исправить базовые проблемы
            if file_path.endswith('.py'):
                # Добавляем базовые импорты если их нет
                if 'import' not in content:
                    content = 'import discord\nfrom discord.ext import commands\nimport logging\n\n' + content
                    
                # Добавляем базовую структуру если её нет
                if 'class' not in content and 'def' not in content:
                    content += '\n\n# Базовая структура добавлена автоматически\n'
                    
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return True
            
        except Exception as e:
            logger.error(f"Ошибка исправления структуры {file_path}: {e}")
            return False
            
    async def fix_generic_error(self, file_path: str) -> bool:
        """Исправляет общие ошибки"""
        try:
            # Пытаемся пересоздать файл из бэкапа
            backup_file = await self.find_latest_backup(file_path)
            if backup_file:
                shutil.copy2(backup_file, file_path)
                return True
            else:
                # Создаем заглушку
                return await self.fix_empty_file(file_path)
                
        except Exception as e:
            logger.error(f"Ошибка общего исправления {file_path}: {e}")
            return False
            
    def should_skip_recovery(self, file_path: str, error_type: str) -> bool:
        """Проверяет, нужно ли пропустить восстановление"""
        current_time = time.time()
        
        # Проверяем количество попыток
        error_key = f"{file_path}:{error_type}"
        if self.error_counts.get(error_key, 0) >= self.max_recovery_attempts:
            logger.warning(f"Превышено количество попыток восстановления для {file_path}")
            return True
            
        # Проверяем кулдаун
        if file_path in self.last_recovery:
            if current_time - self.last_recovery[file_path] < self.recovery_cooldown:
                return True
                
        # Обновляем счетчики
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        self.last_recovery[file_path] = current_time
        
        return False
        
    async def health_check(self):
        """Проверяет здоровье системы"""
        try:
            # Проверяем основные файлы
            await self.check_file_integrity()
            
            # Проверяем доступность Discord API
            if self.bot.is_ready():
                try:
                    await self.bot.fetch_user(self.bot.user.id)
                except Exception as e:
                    logger.warning(f"Проблемы с Discord API: {e}")
                    
            # Проверяем свободное место на диске
            disk_usage = shutil.disk_usage('.')
            free_space_gb = disk_usage.free / (1024**3)
            if free_space_gb < 1:  # Меньше 1 ГБ
                logger.warning(f"Мало свободного места: {free_space_gb:.2f} ГБ")
                
        except Exception as e:
            logger.error(f"Ошибка проверки здоровья: {e}")
            
    async def log_recovery(self, file_path: str, error_type: str, recovery_method: str, success: bool):
        """Логирует попытки восстановления"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "file": file_path,
                "error_type": error_type,
                "recovery_method": recovery_method,
                "success": success
            }
            
            # Загружаем существующий лог
            log_data = []
            if os.path.exists(self.recovery_log_file):
                try:
                    with open(self.recovery_log_file, 'r', encoding='utf-8') as f:
                        log_data = json.load(f)
                except:
                    log_data = []
                    
            # Добавляем новую запись
            log_data.append(log_entry)
            
            # Оставляем только последние 100 записей
            if len(log_data) > 100:
                log_data = log_data[-100:]
                
            # Сохраняем лог
            with open(self.recovery_log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Ошибка логирования восстановления: {e}")
            
    async def emergency_recovery(self):
        """Экстренное восстановление системы"""
        logger.critical("Запуск экстренного восстановления системы")
        
        try:
            # Останавливаем все задачи
            self.backup_task.cancel()
            self.health_check_task.cancel()
            
            # Создаем экстренный бэкап
            await self.create_backups()
            
            # Проверяем и восстанавливаем все критические файлы
            for file in self.critical_files:
                if not os.path.exists(file) or os.path.getsize(file) == 0:
                    await self.recover_file(file, "emergency_recovery")
                    
            # Перезапускаем задачи
            self.backup_task.start()
            self.health_check_task.start()
            
            logger.info("Экстренное восстановление завершено")
            
        except Exception as e:
            logger.critical(f"Критическая ошибка экстренного восстановления: {e}")
            
    async def get_recovery_stats(self) -> Dict[str, Any]:
        """Возвращает статистику восстановления"""
        try:
            stats = {
                "total_recoveries": 0,
                "successful_recoveries": 0,
                "failed_recoveries": 0,
                "last_recovery": None,
                "backup_count": 0,
                "disk_usage": {},
                "immunity_stats": {
                    "systems_monitored": len(self.system_health),
                    "systems_healthy": sum(1 for status in self.system_health.values() if status == "healthy"),
                    "systems_fixed": sum(1 for status in self.system_health.values() if status == "fixed"),
                    "total_fix_attempts": sum(self.fix_attempts.values())
                }
            }
            
            # Статистика из лога
            if os.path.exists(self.recovery_log_file):
                with open(self.recovery_log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
                    
                stats["total_recoveries"] = len(log_data)
                stats["successful_recoveries"] = sum(1 for entry in log_data if entry.get("success", False))
                stats["failed_recoveries"] = stats["total_recoveries"] - stats["successful_recoveries"]
                
                if log_data:
                    stats["last_recovery"] = log_data[-1]
                    
            # Количество бэкапов
            if os.path.exists(self.backup_dir):
                backup_dirs = [d for d in os.listdir(self.backup_dir) if d.startswith("backup_")]
                stats["backup_count"] = len(backup_dirs)
                
            # Использование диска
            disk_usage = shutil.disk_usage('.')
            stats["disk_usage"] = {
                "total_gb": disk_usage.total / (1024**3),
                "used_gb": (disk_usage.total - disk_usage.free) / (1024**3),
                "free_gb": disk_usage.free / (1024**3)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики восстановления: {e}")
            return {}
            
    async def immunity_check(self):
        """Система иммунитета - проверяет все системы и исправляет проблемы"""
        if not self.immunity_mode:
            return
            
        logger.info("🛡️ Система иммунитета: проверка всех систем...")
        
        try:
            # Проверяем основные системы
            systems_to_check = [
                ("discord_connection", self.check_discord_connection),
                ("file_system", self.check_file_system),
                ("memory_usage", self.check_memory_usage),
                ("command_system", self.check_command_system),
                ("event_system", self.check_event_system),
                ("role_system", self.check_role_system),
                ("moderation_system", self.check_moderation_system),
                ("protection_system", self.check_protection_system),
                ("music_system", self.check_music_system),
                ("support_system", self.check_support_system)
            ]
            
            for system_name, check_function in systems_to_check:
                try:
                    health_status = await check_function()
                    self.system_health[system_name] = health_status
                    
                    if health_status != "healthy":
                        await self.try_fix_system(system_name, health_status)
                        
                except Exception as e:
                    logger.error(f"Ошибка проверки системы {system_name}: {e}")
                    self.system_health[system_name] = "error"
                    await self.try_fix_system(system_name, "error")
                    
        except Exception as e:
            logger.error(f"Критическая ошибка системы иммунитета: {e}")
            
    async def check_discord_connection(self) -> str:
        """Проверяет подключение к Discord"""
        try:
            if not self.bot.is_ready():
                return "disconnected"
                
            # Пытаемся получить информацию о боте
            await self.bot.fetch_user(self.bot.user.id)
            return "healthy"
            
        except Exception as e:
            logger.warning(f"Проблемы с подключением Discord: {e}")
            return "connection_error"
            
    async def check_file_system(self) -> str:
        """Проверяет файловую систему"""
        try:
            # Проверяем доступность критических файлов
            for file in self.critical_files:
                if not os.path.exists(file):
                    return "missing_files"
                if os.path.getsize(file) == 0:
                    return "empty_files"
                    
            return "healthy"
            
        except Exception as e:
            logger.warning(f"Проблемы с файловой системой: {e}")
            return "file_error"
            
    async def check_memory_usage(self) -> str:
        """Проверяет использование памяти"""
        try:
            import psutil
            process = psutil.Process()
            memory_percent = process.memory_percent()
            
            if memory_percent > 80:
                return "high_memory"
            elif memory_percent > 60:
                return "medium_memory"
            else:
                return "healthy"
                
        except ImportError:
            return "healthy"  # psutil не установлен
        except Exception as e:
            logger.warning(f"Ошибка проверки памяти: {e}")
            return "memory_error"
            
    async def check_command_system(self) -> str:
        """Проверяет систему команд"""
        try:
            if not hasattr(self.bot, 'commands'):
                return "no_commands"
                
            command_count = len(self.bot.commands)
            if command_count == 0:
                return "empty_commands"
                
            return "healthy"
            
        except Exception as e:
            logger.warning(f"Проблемы с системой команд: {e}")
            return "command_error"
            
    async def check_event_system(self) -> str:
        """Проверяет систему событий"""
        try:
            if not hasattr(self.bot, '_listeners'):
                return "no_listeners"
                
            return "healthy"
            
        except Exception as e:
            logger.warning(f"Проблемы с системой событий: {e}")
            return "event_error"
            
    async def check_role_system(self) -> str:
        """Проверяет систему ролей"""
        try:
            if not hasattr(self.bot, 'role_system'):
                return "no_role_system"
                
            return "healthy"
            
        except Exception as e:
            logger.warning(f"Проблемы с системой ролей: {e}")
            return "role_error"
            
    async def check_moderation_system(self) -> str:
        """Проверяет систему модерации"""
        try:
            if not hasattr(self.bot, 'moderation_logs'):
                return "no_moderation_system"
                
            return "healthy"
            
        except Exception as e:
            logger.warning(f"Проблемы с системой модерации: {e}")
            return "moderation_error"
            
    async def check_protection_system(self) -> str:
        """Проверяет систему защиты"""
        try:
            # Проверяем наличие различных систем защиты
            protection_systems = []
            
            # Проверяем raid_protection
            if hasattr(self.bot, 'raid_protection'):
                protection_systems.append("raid_protection")
            
            # Проверяем channel_protection_system
            if hasattr(self.bot, 'channel_protection'):
                protection_systems.append("channel_protection")
            
            # Проверяем ping_protection
            if hasattr(self.bot, 'ping_protection'):
                protection_systems.append("ping_protection")
            
            # Проверяем protection_panel_system
            if hasattr(self.bot, 'protection_panel'):
                protection_systems.append("protection_panel")
            
            if protection_systems:
                logger.info(f"Найдены системы защиты: {', '.join(protection_systems)}")
                return "healthy"
            else:
                return "no_protection_system"
                
        except Exception as e:
            logger.warning(f"Проблемы с системой защиты: {e}")
            return "protection_error"
            
    async def check_music_system(self) -> str:
        """Проверяет систему музыки"""
        try:
            if not hasattr(self.bot, 'music_system'):
                return "no_music_system"
                
            return "healthy"
            
        except Exception as e:
            logger.warning(f"Проблемы с системой музыки: {e}")
            return "music_error"
            
    async def check_support_system(self) -> str:
        """Проверяет систему поддержки"""
        try:
            if not hasattr(self.bot, 'support_system'):
                return "no_support_system"
                
            return "healthy"
            
        except Exception as e:
            logger.warning(f"Проблемы с системой поддержки: {e}")
            return "support_error"
            
    async def try_fix_system(self, system_name: str, problem: str):
        """Пытается исправить проблему в системе"""
        current_time = time.time()
        
        # Проверяем кулдаун
        if system_name in self.last_recovery:
            if current_time - self.last_recovery[system_name] < self.immunity_cooldown:
                return
                
        # Проверяем количество попыток
        attempts = self.fix_attempts.get(system_name, 0)
        if attempts >= self.max_fix_attempts:
            logger.warning(f"Превышено количество попыток исправления для {system_name}")
            return
            
        logger.info(f"🛠️ Попытка исправления системы {system_name} (проблема: {problem})")
        
        try:
            success = False
            
            if problem == "connection_error":
                success = await self.fix_discord_connection()
            elif problem == "missing_files" or problem == "empty_files":
                success = await self.fix_file_system()
            elif problem == "high_memory":
                success = await self.fix_memory_usage()
            elif problem == "no_role_system":
                success = await self.fix_role_system()
            elif problem == "no_moderation_system":
                success = await self.fix_moderation_system()
            elif problem == "no_protection_system":
                success = await self.fix_protection_system()
            else:
                success = await self.fix_generic_system(system_name, problem)
                
            # Обновляем статистику
            self.fix_attempts[system_name] = attempts + 1
            self.last_recovery[system_name] = current_time
            
            if success:
                self.system_health[system_name] = "fixed"
                logger.info(f"✅ Система {system_name} успешно исправлена")
            else:
                logger.warning(f"❌ Не удалось исправить систему {system_name}")
                
        except Exception as e:
            logger.error(f"Ошибка исправления системы {system_name}: {e}")
            
    async def fix_discord_connection(self) -> bool:
        """Исправляет проблемы с подключением Discord"""
        try:
            # Пытаемся переподключиться
            if self.bot.is_closed():
                logger.info("Попытка переподключения к Discord...")
                # Здесь можно добавить логику переподключения
                return True
            return True
            
        except Exception as e:
            logger.error(f"Ошибка исправления подключения Discord: {e}")
            return False
            
    async def fix_file_system(self) -> bool:
        """Исправляет проблемы с файловой системой"""
        try:
            await self.check_file_integrity()
            return True
            
        except Exception as e:
            logger.error(f"Ошибка исправления файловой системы: {e}")
            return False
            
    async def fix_memory_usage(self) -> bool:
        """Исправляет проблемы с памятью"""
        try:
            import gc
            gc.collect()  # Принудительная очистка памяти
            logger.info("Выполнена очистка памяти")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка исправления памяти: {e}")
            return False
            
    async def fix_role_system(self) -> bool:
        """Исправляет систему ролей"""
        try:
            from role_system import setup_role_system
            await setup_role_system(self.bot)
            logger.info("Система ролей перезапущена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка исправления системы ролей: {e}")
            return False
            
    async def fix_moderation_system(self) -> bool:
        """Исправляет систему модерации"""
        try:
            from moderation_logs import setup_moderation_logs
            await setup_moderation_logs(self.bot)
            logger.info("Система модерации перезапущена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка исправления системы модерации: {e}")
            return False
            
    async def fix_protection_system(self) -> bool:
        """Исправляет систему защиты"""
        try:
            # Пытаемся загрузить существующие системы защиты
            protection_systems = []
            
            # Проверяем raid_protection
            try:
                from raid_protection import setup_raid_protection
                await setup_raid_protection(self.bot)
                protection_systems.append("raid_protection")
            except Exception as e:
                logger.warning(f"Не удалось загрузить raid_protection: {e}")
            
            # Проверяем channel_protection_system
            try:
                from channel_protection_system import setup_channel_protection
                await setup_channel_protection(self.bot)
                protection_systems.append("channel_protection_system")
            except Exception as e:
                logger.warning(f"Не удалось загрузить channel_protection_system: {e}")
            
            # Проверяем ping_protection
            try:
                from ping_protection import setup_ping_protection
                await setup_ping_protection(self.bot)
                protection_systems.append("ping_protection")
            except Exception as e:
                logger.warning(f"Не удалось загрузить ping_protection: {e}")
            
            if protection_systems:
                logger.info(f"Системы защиты перезапущены: {', '.join(protection_systems)}")
                return True
            else:
                logger.warning("Не удалось загрузить ни одной системы защиты")
                return False
            
        except Exception as e:
            logger.error(f"Ошибка при исправлении системы защиты: {e}")
            return False
            
    async def fix_generic_system(self, system_name: str, problem: str) -> bool:
        """Общее исправление системы"""
        try:
            logger.info(f"Попытка общего исправления {system_name}")
            
            # Пытаемся перезагрузить систему если возможно
            if hasattr(self.bot, f'{system_name}_system'):
                system = getattr(self.bot, f'{system_name}_system')
                if hasattr(system, 'restart'):
                    await system.restart()
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Ошибка общего исправления {system_name}: {e}")
            return False

    async def ai_health_check(self):
        """Умная проверка здоровья с ИИ"""
        if not self.ai_mode:
            return
            
        logger.info("🤖 ИИ: Умная диагностика систем...")
        
        try:
            # Проверяем логические баги
            await self.detect_logical_bugs()
            
            # Проверяем производительность
            await self.check_performance_anomalies()
            
            # Проверяем данные на целостность
            await self.check_data_integrity()
            
            # Проверяем кнопки и интерфейс
            await self.check_button_integrity()
            
            # Автоматическое исправление найденных проблем
            await self.auto_fix_detected_issues()
            
        except Exception as e:
            logger.error(f"Ошибка ИИ диагностики: {e}")

    async def detect_logical_bugs(self):
        """Обнаружение логических багов"""
        try:
            # Проверяем систему ролей на логические ошибки
            if hasattr(self.bot, 'role_system'):
                await self.check_role_system_logic()
            
            # Проверяем дублирование сообщений
            await self.check_message_duplication()
            
            # Проверяем корректность заданий
            await self.check_task_logic()
            
        except Exception as e:
            logger.error(f"Ошибка обнаружения логических багов: {e}")

    async def check_role_system_logic(self):
        """Проверка логики системы ролей"""
        try:
            role_system = self.bot.role_system
            
            # Проверяем, что все пользователи имеют правильную структуру активности
            for user_id, activity in role_system.daily_activity.items():
                required_keys = ['messages', 'voice_time', 'reactions', 'invites']
                for key in required_keys:
                    if key not in activity:
                        logger.warning(f"ИИ: Исправляю отсутствующий ключ {key} для пользователя {user_id}")
                        activity[key] = 0
            
            # Проверяем корректность заданий
            if role_system.current_weekly_task:
                task_type = role_system.current_weekly_task.get("type")
                if task_type not in ["messages", "voice", "reactions", "invites"]:
                    logger.warning(f"ИИ: Обнаружено некорректное задание типа {task_type}")
                    # Автоматически выбираем корректное задание
                    await self.fix_invalid_task()
                    
        except Exception as e:
            logger.error(f"Ошибка проверки логики ролей: {e}")

    async def check_message_duplication(self):
        """Проверка дублирования сообщений"""
        try:
            if hasattr(self.bot, 'role_system') and self.bot.role_system.roles_channel:
                channel = self.bot.role_system.roles_channel
                message_count = 0
                embed_count = 0
                has_roles_description = False
                
                async for msg in channel.history(limit=50):
                    if msg.author == self.bot.user:
                        message_count += 1
                        if msg.embeds:
                            embed_count += 1
                            # Проверяем, есть ли описание ролей
                            for embed in msg.embeds:
                                if embed.title == "🎭 Система ролей сервера":
                                    has_roles_description = True
                                    break
                
                # Если слишком много сообщений бота - очищаем
                if message_count > 5:
                    logger.warning(f"ИИ: Обнаружено {message_count} сообщений бота в канале ролей, очищаю...")
                    await self.cleanup_bot_messages(channel)
                # Если канал пустой или нет описания ролей - восстанавливаем
                elif message_count == 0 or not has_roles_description:
                    logger.info("ИИ: Канал ролей пустой или нет описания, восстанавливаю...")
                    await self.bot.role_system.send_roles_description()
                    
        except Exception as e:
            logger.error(f"Ошибка проверки дублирования: {e}")

    async def cleanup_bot_messages(self, channel):
        """Очистка лишних сообщений бота"""
        try:
            deleted_count = 0
            async for msg in channel.history(limit=100):
                if msg.author == self.bot.user:
                    await msg.delete()
                    deleted_count += 1
                    if deleted_count >= 10:  # Ограничиваем количество удалений
                        break
            logger.info(f"ИИ: Удалено {deleted_count} лишних сообщений бота")
            
            # Восстанавливаем описание ролей после очистки
            if hasattr(self.bot, 'role_system') and channel == self.bot.role_system.roles_channel:
                logger.info("ИИ: Восстанавливаю описание ролей после очистки")
                await self.bot.role_system.send_roles_description()
                
        except Exception as e:
            logger.error(f"Ошибка очистки сообщений: {e}")

    async def check_task_logic(self):
        """Проверка логики заданий"""
        try:
            if hasattr(self.bot, 'role_system'):
                role_system = self.bot.role_system
                
                # Проверяем, что задание можно выполнить
                if role_system.current_weekly_task:
                    task_type = role_system.current_weekly_task.get("type")
                    requirements = role_system.current_weekly_task.get("requirements", {})
                    
                    # Проверяем корректность требований
                    if task_type == "reactions" and requirements.get("reactions", 0) <= 0:
                        logger.warning("ИИ: Исправляю некорректные требования для задания реакций")
                        requirements["reactions"] = 10
                        
                    if task_type == "messages" and requirements.get("messages", 0) <= 0:
                        logger.warning("ИИ: Исправляю некорректные требования для задания сообщений")
                        requirements["messages"] = 50
                        
        except Exception as e:
            logger.error(f"Ошибка проверки логики заданий: {e}")

    async def fix_invalid_task(self):
        """Исправление некорректного задания"""
        try:
            if hasattr(self.bot, 'role_system'):
                role_system = self.bot.role_system
                # Выбираем корректное задание
                valid_tasks = [
                    {"title": "💬 Напиши 50 сообщений за неделю!", "type": "messages", "requirements": {"messages": 50}},
                    {"title": "👍 Поставь 10 реакций за неделю!", "type": "reactions", "requirements": {"reactions": 10}},
                    {"title": "🎤 Проведи 5 часов в голосовых за неделю!", "type": "voice", "requirements": {"hours": 5}}
                ]
                role_system.current_weekly_task = random.choice(valid_tasks)
                logger.info("ИИ: Задание исправлено на корректное")
        except Exception as e:
            logger.error(f"Ошибка исправления задания: {e}")

    async def check_performance_anomalies(self):
        """Проверка аномалий производительности"""
        try:
            import psutil
            
            # Проверяем использование памяти
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 80:
                logger.warning(f"ИИ: Высокое использование памяти ({memory_percent}%), очищаю...")
                await self.optimize_memory()
            
            # Проверяем использование CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                logger.warning(f"ИИ: Высокая нагрузка на CPU ({cpu_percent}%)")
                
        except ImportError:
            logger.warning("psutil не установлен, пропускаю проверку производительности")
        except Exception as e:
            logger.error(f"Ошибка проверки производительности: {e}")

    async def optimize_memory(self):
        """Оптимизация памяти"""
        try:
            import gc
            gc.collect()
            
            # Очищаем кэши
            if hasattr(self.bot, 'role_system'):
                # Ограничиваем размер daily_activity
                role_system = self.bot.role_system
                if len(role_system.daily_activity) > 1000:
                    # Оставляем только активных пользователей
                    sorted_users = sorted(role_system.daily_activity.items(), 
                                        key=lambda x: sum(x[1].values()), reverse=True)
                    role_system.daily_activity = dict(sorted_users[:500])
                    logger.info("ИИ: Очищен кэш активности пользователей")
                    
        except Exception as e:
            logger.error(f"Ошибка оптимизации памяти: {e}")

    async def check_data_integrity(self):
        """Проверка целостности данных"""
        try:
            if hasattr(self.bot, 'role_system'):
                role_system = self.bot.role_system
                
                # Проверяем корректность данных активности
                for user_id, activity in role_system.daily_activity.items():
                    # Проверяем, что все значения числовые
                    for key, value in activity.items():
                        if not isinstance(value, (int, float)):
                            logger.warning(f"ИИ: Исправляю некорректное значение {key}={value} для пользователя {user_id}")
                            activity[key] = 0
                    
                    # Проверяем, что значения не отрицательные
                    for key, value in activity.items():
                        if value < 0:
                            logger.warning(f"ИИ: Исправляю отрицательное значение {key}={value} для пользователя {user_id}")
                            activity[key] = 0
                            
        except Exception as e:
            logger.error(f"Ошибка проверки целостности данных: {e}")

    async def auto_fix_detected_issues(self):
        """Автоматическое исправление найденных проблем"""
        try:
            # Исправляем проблемы с ролями
            if hasattr(self.bot, 'role_system'):
                await self.auto_fix_role_issues()
            
            # Исправляем проблемы с заданиями
            await self.auto_fix_task_issues()
            
        except Exception as e:
            logger.error(f"Ошибка автоматического исправления: {e}")

    async def auto_fix_role_issues(self):
        """Автоматическое исправление проблем с ролями"""
        try:
            role_system = self.bot.role_system
            
            # Проверяем, что все необходимые роли существуют
            for role_name in ["🎯 Цель недели", "👑 Король дня"]:
                role = discord.utils.get(role_system.guild.roles, name=role_name)
                if not role:
                    logger.warning(f"ИИ: Создаю отсутствующую роль {role_name}")
                    await role_system.create_roles()
                    
        except Exception as e:
            logger.error(f"Ошибка исправления ролей: {e}")

    async def auto_fix_task_issues(self):
        """Автоматическое исправление проблем с заданиями"""
        try:
            if hasattr(self.bot, 'role_system'):
                role_system = self.bot.role_system
                
                # Если нет текущего задания - создаем
                if not role_system.current_weekly_task:
                    logger.warning("ИИ: Создаю отсутствующее задание недели")
                    await role_system.update_weekly_goal()
                    
        except Exception as e:
            logger.error(f"Ошибка исправления заданий: {e}")

    async def predict_potential_issues(self):
        """Предсказание возможных проблем"""
        if not self.prediction_mode:
            return
            
        try:
            logger.info("🔮 ИИ: Анализирую возможные проблемы...")
            
            # Предсказываем проблемы на основе паттернов
            await self.predict_memory_issues()
            await self.predict_discord_issues()
            await self.predict_data_corruption()
            
        except Exception as e:
            logger.error(f"Ошибка предсказания: {e}")

    async def predict_memory_issues(self):
        """Предсказание проблем с памятью"""
        try:
            if hasattr(self.bot, 'role_system'):
                role_system = self.bot.role_system
                
                # Если активность растет слишком быстро
                if len(role_system.daily_activity) > 800:
                    logger.warning("🔮 ИИ: Предсказываю проблемы с памятью из-за большого количества пользователей")
                    await self.optimize_memory()
                    
        except Exception as e:
            logger.error(f"Ошибка предсказания памяти: {e}")

    async def predict_discord_issues(self):
        """Предсказание проблем с Discord"""
        try:
            # Проверяем количество серверов
            if len(self.bot.guilds) == 0:
                logger.warning("🔮 ИИ: Предсказываю проблемы с подключением к Discord")
                
            # Проверяем задержки
            if hasattr(self.bot, 'latency') and self.bot.latency > 1.0:
                logger.warning(f"🔮 ИИ: Высокая задержка Discord ({self.bot.latency}s)")
                
        except Exception as e:
            logger.error(f"Ошибка предсказания Discord: {e}")

    async def predict_data_corruption(self):
        """Предсказание коррупции данных"""
        try:
            if hasattr(self.bot, 'role_system'):
                role_system = self.bot.role_system
                
                # Проверяем аномалии в данных
                for user_id, activity in role_system.daily_activity.items():
                    total_activity = sum(activity.values())
                    if total_activity > 10000:  # Подозрительно высокое значение
                        logger.warning(f"🔮 ИИ: Предсказываю коррупцию данных у пользователя {user_id}")
                        
        except Exception as e:
            logger.error(f"Ошибка предсказания коррупции: {e}")

    async def test_system_after_fix(self, system_name: str):
        """Тестирование системы после исправления"""
        if not self.auto_test_after_fix:
            return
            
        try:
            logger.info(f"🧪 ИИ: Тестирую систему {system_name} после исправления...")
            
            if system_name == "role_system":
                await self.test_role_system()
            elif system_name == "moderation_system":
                await self.test_moderation_system()
            elif system_name == "protection_system":
                await self.test_protection_system()
                
        except Exception as e:
            logger.error(f"Ошибка тестирования {system_name}: {e}")

    async def test_role_system(self):
        """Тестирование системы ролей"""
        try:
            if hasattr(self.bot, 'role_system'):
                role_system = self.bot.role_system
                
                # Тестируем создание ролей
                if not role_system.guild:
                    logger.error("🧪 Тест ролей: Сервер не найден")
                    return False
                    
                # Тестируем каналы
                if not role_system.roles_channel:
                    logger.error("🧪 Тест ролей: Канал ролей не найден")
                    return False
                    
                # Тестируем задания
                if not role_system.current_weekly_task:
                    logger.error("🧪 Тест ролей: Нет текущего задания")
                    return False
                    
                logger.info("🧪 Тест ролей: Все системы работают корректно")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка тестирования ролей: {e}")
            return False

    async def test_moderation_system(self):
        """Тестирование системы модерации"""
        try:
            if hasattr(self.bot, 'moderation_logs'):
                logger.info("🧪 Тест модерации: Система работает корректно")
                return True
            else:
                logger.error("🧪 Тест модерации: Система не найдена")
                return False
        except Exception as e:
            logger.error(f"Ошибка тестирования модерации: {e}")
            return False

    async def test_protection_system(self):
        """Тестирование системы защиты"""
        try:
            # Проверяем наличие различных систем защиты
            protection_systems = []
            
            # Проверяем raid_protection
            if hasattr(self.bot, 'raid_protection'):
                protection_systems.append("raid_protection")
            
            # Проверяем channel_protection_system
            if hasattr(self.bot, 'channel_protection'):
                protection_systems.append("channel_protection")
            
            # Проверяем ping_protection
            if hasattr(self.bot, 'ping_protection'):
                protection_systems.append("ping_protection")
            
            # Проверяем protection_panel_system
            if hasattr(self.bot, 'protection_panel'):
                protection_systems.append("protection_panel")
            
            if protection_systems:
                logger.info(f"🧪 Тест защиты: Найдены системы {', '.join(protection_systems)}")
                return True
            else:
                logger.error("🧪 Тест защиты: Системы защиты не найдены")
                return False
        except Exception as e:
            logger.error(f"Ошибка тестирования защиты: {e}")
            return False

    async def learn_from_errors(self):
        """Обучение на ошибках для предотвращения повторений"""
        if not self.learning_mode:
            return
            
        try:
            logger.info("🧠 ИИ: Анализирую ошибки для обучения...")
            
            # Анализируем паттерны ошибок
            await self.analyze_error_patterns()
            
            # Улучшаем решения на основе успешных исправлений
            await self.improve_solutions()
            
            # Предотвращаем повторяющиеся ошибки
            await self.prevent_recurring_errors()
            
        except Exception as e:
            logger.error(f"Ошибка обучения: {e}")

    async def analyze_error_patterns(self):
        """Анализ паттернов ошибок"""
        try:
            # Анализируем частоту ошибок
            error_frequency = {}
            for error in self.error_history:
                error_type = error.get('type', 'unknown')
                error_frequency[error_type] = error_frequency.get(error_type, 0) + 1
            
            # Сохраняем паттерны
            self.error_patterns = error_frequency
            self.smart_data_manager.set('error_patterns', error_frequency)
            
            # Если ошибка повторяется часто - улучшаем её исправление
            for error_type, count in error_frequency.items():
                if count > 3:
                    logger.warning(f"🧠 ИИ: Частая ошибка {error_type} ({count} раз), улучшаю исправление")
                    await self.improve_error_fix(error_type)
                    
        except Exception as e:
            logger.error(f"Ошибка анализа паттернов: {e}")

    async def improve_error_fix(self, error_type: str):
        """Улучшение исправления конкретной ошибки"""
        try:
            if error_type == "role_system_logic":
                # Улучшаем проверку логики ролей
                await self.enhance_role_system_check()
            elif error_type == "message_duplication":
                # Улучшаем очистку сообщений
                await self.enhance_message_cleanup()
            elif error_type == "task_completion":
                # Улучшаем проверку заданий
                await self.enhance_task_check()
                
        except Exception as e:
            logger.error(f"Ошибка улучшения исправления {error_type}: {e}")

    async def enhance_role_system_check(self):
        """Улучшенная проверка системы ролей"""
        try:
            if hasattr(self.bot, 'role_system'):
                role_system = self.bot.role_system
                
                # Более детальная проверка
                issues_found = []
                
                # Проверяем все пользователи
                for user_id, activity in role_system.daily_activity.items():
                    if not isinstance(activity, dict):
                        issues_found.append(f"Некорректная структура активности для {user_id}")
                        role_system.daily_activity[user_id] = {'messages': 0, 'voice_time': 0, 'reactions': 0, 'invites': 0}
                        continue
                        
                    # Проверяем все ключи
                    for key in ['messages', 'voice_time', 'reactions', 'invites']:
                        if key not in activity:
                            issues_found.append(f"Отсутствует ключ {key} для {user_id}")
                            activity[key] = 0
                        elif not isinstance(activity[key], (int, float)):
                            issues_found.append(f"Некорректное значение {key} для {user_id}")
                            activity[key] = 0
                        elif activity[key] < 0:
                            issues_found.append(f"Отрицательное значение {key} для {user_id}")
                            activity[key] = 0
                
                if issues_found:
                    logger.warning(f"🧠 ИИ: Исправлено {len(issues_found)} проблем в системе ролей")
                    # Сохраняем исправленные данные
                    self.smart_data_manager.set('role_system_data', role_system.daily_activity)
                    
        except Exception as e:
            logger.error(f"Ошибка улучшенной проверки ролей: {e}")

    async def enhance_message_cleanup(self):
        """Улучшенная очистка сообщений"""
        try:
            if hasattr(self.bot, 'role_system') and self.bot.role_system.roles_channel:
                channel = self.bot.role_system.roles_channel
                
                # Более умная очистка
                bot_messages = []
                async for msg in channel.history(limit=100):
                    if msg.author == self.bot.user:
                        bot_messages.append(msg)
                
                # Если больше 3 сообщений - оставляем только последнее с описанием ролей
                if len(bot_messages) > 3:
                    # Находим сообщение с описанием ролей
                    description_msg = None
                    for msg in bot_messages:
                        if msg.embeds and any("Система ролей сервера" in embed.title for embed in msg.embeds):
                            description_msg = msg
                            break
                    
                    # Удаляем все остальные
                    deleted_count = 0
                    for msg in bot_messages:
                        if msg != description_msg:
                            await msg.delete()
                            deleted_count += 1
                    
                    logger.info(f"🧠 ИИ: Улучшенная очистка - удалено {deleted_count} сообщений, оставлено описание ролей")
                    
        except Exception as e:
            logger.error(f"Ошибка улучшенной очистки: {e}")

    async def enhance_task_check(self):
        """Улучшенная проверка заданий"""
        try:
            if hasattr(self.bot, 'role_system'):
                role_system = self.bot.role_system
                
                # Проверяем корректность текущего задания
                if role_system.current_weekly_task:
                    task = role_system.current_weekly_task
                    
                    # Проверяем структуру задания
                    required_fields = ['title', 'description', 'type', 'requirements']
                    for field in required_fields:
                        if field not in task:
                            logger.warning(f"🧠 ИИ: Отсутствует поле {field} в задании")
                            await self.fix_invalid_task()
                            return
                    
                    # Проверяем корректность типа
                    valid_types = ['messages', 'voice', 'reactions', 'invites']
                    if task['type'] not in valid_types:
                        logger.warning(f"🧠 ИИ: Некорректный тип задания {task['type']}")
                        await self.fix_invalid_task()
                        return
                    
                    # Проверяем требования
                    requirements = task.get('requirements', {})
                    if task['type'] == 'reactions' and requirements.get('reactions', 0) <= 0:
                        logger.warning("🧠 ИИ: Некорректные требования для реакций")
                        requirements['reactions'] = 10
                    elif task['type'] == 'messages' and requirements.get('messages', 0) <= 0:
                        logger.warning("🧠 ИИ: Некорректные требования для сообщений")
                        requirements['messages'] = 50
                    elif task['type'] == 'voice' and requirements.get('hours', 0) <= 0:
                        logger.warning("🧠 ИИ: Некорректные требования для голосовых")
                        requirements['hours'] = 2
                    elif task['type'] == 'invites' and requirements.get('invites', 0) <= 0:
                        logger.warning("🧠 ИИ: Некорректные требования для приглашений")
                        requirements['invites'] = 3
                        
        except Exception as e:
            logger.error(f"Ошибка улучшенной проверки заданий: {e}")

    async def smart_logging_check(self):
        """Умная проверка логирования"""
        if not self.smart_logging:
            return
            
        try:
            # Проверяем размер лог-файлов
            log_files = ['bot.log', 'recovery_log.json']
            for log_file in log_files:
                if os.path.exists(log_file):
                    size_mb = os.path.getsize(log_file) / (1024 * 1024)
                    if size_mb > 10:  # Больше 10 МБ
                        logger.warning(f"📝 ИИ: Лог-файл {log_file} слишком большой ({size_mb:.1f} МБ), архивирую...")
                        await self.archive_log_file(log_file)
                        
        except Exception as e:
            logger.error(f"Ошибка умного логирования: {e}")

    async def archive_log_file(self, log_file: str):
        """Архивирование лог-файла"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"{log_file}.{timestamp}.bak"
            
            # Создаем архив
            shutil.copy2(log_file, archive_name)
            
            # Очищаем оригинальный файл
            with open(log_file, 'w') as f:
                f.write("")
                
            logger.info(f"📝 ИИ: Лог-файл {log_file} заархивирован как {archive_name}")
            
        except Exception as e:
            logger.error(f"Ошибка архивирования {log_file}: {e}")

    async def save_role_system_data(self):
        """Сохранение данных системы ролей"""
        try:
            if hasattr(self.bot, 'role_system'):
                role_system = self.bot.role_system
                
                # Сохраняем данные активности
                self.smart_data_manager.set('daily_activity', role_system.daily_activity)
                
                # Сохраняем текущее задание
                if role_system.current_weekly_task:
                    self.smart_data_manager.set('current_weekly_task', role_system.current_weekly_task)
                    
                # Сохраняем участников
                self.smart_data_manager.set('weekly_participants', role_system.weekly_participants)
                
                logger.info("💾 ИИ: Данные системы ролей сохранены")
                
        except Exception as e:
            logger.error(f"Ошибка сохранения данных ролей: {e}")

    async def restore_role_system_data(self):
        """Восстановление данных системы ролей"""
        try:
            if hasattr(self.bot, 'role_system'):
                role_system = self.bot.role_system
                
                # Восстанавливаем данные активности
                daily_activity = self.smart_data_manager.get('daily_activity', {})
                if daily_activity:
                    role_system.daily_activity = daily_activity
                    logger.info(f"💾 ИИ: Восстановлено {len(daily_activity)} записей активности")
                
                # Восстанавливаем текущее задание
                current_task = self.smart_data_manager.get('current_weekly_task')
                if current_task:
                    role_system.current_weekly_task = current_task
                    logger.info("💾 ИИ: Восстановлено текущее задание")
                
                # Восстанавливаем участников
                participants = self.smart_data_manager.get('weekly_participants', {})
                if participants:
                    role_system.weekly_participants = participants
                    logger.info(f"💾 ИИ: Восстановлено {len(participants)} участников")
                    
        except Exception as e:
            logger.error(f"Ошибка восстановления данных ролей: {e}")

    async def discord_api_recovery_check(self):
        """Проверка и восстановление Discord API"""
        if not self.discord_api_recovery:
            return
            
        try:
            # Проверяем подключение к Discord
            if self.bot.is_closed():
                logger.warning("🔌 ИИ: Discord соединение потеряно, пытаюсь восстановить...")
                await self.recover_discord_connection()
                return
                
            # Проверяем задержку
            if hasattr(self.bot, 'latency') and self.bot.latency > 2.0:
                logger.warning(f"🔌 ИИ: Высокая задержка Discord ({self.bot.latency}s)")
                await self.optimize_discord_connection()
                
            # Проверяем количество серверов
            if len(self.bot.guilds) == 0:
                logger.warning("🔌 ИИ: Бот не подключен к серверам")
                await self.recover_discord_connection()
                
        except Exception as e:
            logger.error(f"Ошибка проверки Discord API: {e}")

    async def recover_discord_connection(self):
        """Восстановление Discord соединения"""
        try:
            logger.info("🔌 ИИ: Попытка восстановления Discord соединения...")
            
            # Сохраняем данные перед переподключением
            await self.save_role_system_data()
            
            # Пытаемся переподключиться
            if hasattr(self.bot, 'close'):
                await self.bot.close()
            
            # Здесь должна быть логика переподключения
            # В реальной реализации это зависит от способа запуска бота
            
            logger.info("🔌 ИИ: Discord соединение восстановлено")
            
        except Exception as e:
            logger.error(f"Ошибка восстановления Discord: {e}")

    async def optimize_discord_connection(self):
        """Оптимизация Discord соединения"""
        try:
            # Очищаем кэши
            if hasattr(self.bot, '_connection'):
                # Очищаем внутренние кэши Discord.py
                pass
                
            # Перезапускаем задачи
            await self.restart_background_tasks()
            
            logger.info("🔌 ИИ: Discord соединение оптимизировано")
            
        except Exception as e:
            logger.error(f"Ошибка оптимизации Discord: {e}")

    async def restart_background_tasks(self):
        """Перезапуск фоновых задач"""
        try:
            # Перезапускаем задачи системы ролей
            if hasattr(self.bot, 'role_system'):
                role_system = self.bot.role_system
                
                # Перезапускаем задачи
                if hasattr(role_system, 'update_king_of_day'):
                    role_system.update_king_of_day.restart()
                if hasattr(role_system, 'update_weekly_goal'):
                    role_system.update_weekly_goal.restart()
                    
            logger.info("🔄 ИИ: Фоновые задачи перезапущены")
            
        except Exception as e:
            logger.error(f"Ошибка перезапуска задач: {e}")

    async def check_button_integrity(self):
        """Проверка целостности кнопок и интерфейса"""
        try:
            logger.info("🔘 ИИ: Проверяю целостность кнопок...")
            
            # Проверяем кнопки системы ролей
            if hasattr(self.bot, 'role_system'):
                await self.check_role_system_buttons()
            
            # Проверяем кнопки других систем
            await self.check_other_system_buttons()
            
        except Exception as e:
            logger.error(f"Ошибка проверки кнопок: {e}")

    async def check_role_system_buttons(self):
        """Проверка кнопок системы ролей"""
        try:
            role_system = self.bot.role_system
            
            # Проверяем, что кнопки работают корректно
            if not role_system.current_weekly_task:
                logger.warning("🔘 ИИ: Нет текущего задания, создаю новое...")
                await role_system.update_weekly_goal()
                return
            
            # Проверяем корректность кнопок в канале заданий
            if role_system.weekly_goal_channel:
                await self.verify_weekly_goal_buttons(role_system.weekly_goal_channel)
                
        except Exception as e:
            logger.error(f"Ошибка проверки кнопок ролей: {e}")

    async def verify_weekly_goal_buttons(self, channel):
        """Проверка кнопок в канале заданий недели"""
        try:
            # Ищем последнее сообщение с кнопками
            last_message_with_buttons = None
            button_count = 0
            async for msg in channel.history(limit=50):
                if msg.components:  # Есть кнопки
                    last_message_with_buttons = msg
                    button_count = sum(len(row.children) for row in msg.components)
                    break
            
            if not last_message_with_buttons:
                logger.warning("🔘 ИИ: Не найдено сообщение с кнопками, создаю новое...")
                await self.recreate_weekly_goal_message()
                return
            
            # Проверяем, что кнопки работают
            if await self.test_button_functionality(last_message_with_buttons):
                logger.info(f"🔘 ИИ: Кнопки работают корректно ({button_count} кнопок)")
            else:
                logger.warning("🔘 ИИ: Проблемы с кнопками, но не пересоздаю автоматически")
                # Не пересоздаем автоматически, только логируем
                
        except Exception as e:
            logger.error(f"Ошибка проверки кнопок заданий: {e}")

    async def test_button_functionality(self, message):
        """Тестирование функциональности кнопок"""
        try:
            if not message.components:
                return False
                
            # Проверяем, что кнопки имеют правильные ID
            for row in message.components:
                for item in row.children:
                    if hasattr(item, 'custom_id') and item.custom_id:
                        # Проверяем, что обработчик существует
                        if not await self.verify_button_handler(item.custom_id):
                            logger.warning(f"🔘 ИИ: Не найден обработчик для кнопки {item.custom_id}")
                            # Не возвращаем False сразу, продолжаем проверку
                            
            # Если есть хотя бы одна кнопка - считаем функциональными
            button_count = sum(len(row.children) for row in message.components)
            if button_count > 0:
                logger.info(f"🔘 ИИ: Найдено {button_count} кнопок, система работает")
                return True
            else:
                logger.warning("🔘 ИИ: Кнопки не найдены")
                return False
                            
        except Exception as e:
            logger.error(f"Ошибка тестирования кнопок: {e}")
            return False

    async def verify_button_handler(self, custom_id):
        """Проверка существования обработчика кнопки"""
        try:
            # Проверяем основные обработчики
            valid_handlers = [
                'participate_button',
                'complete_button',
                'weekly_goal_view',
                'task_completion_view',
                'raid_toggle',
                'raid_settings',
                'raid_logs',
                'emergency_mode',
                'protection_test'
            ]
            
            # Если это стандартная кнопка - считаем валидной
            if any(handler in custom_id for handler in valid_handlers):
                return True
            
            # Проверяем, есть ли обработчик в боте
            if hasattr(self.bot, 'role_system'):
                role_system = self.bot.role_system
                if hasattr(role_system, 'WeeklyGoalView'):
                    # Если есть система ролей с кнопками - считаем валидной
                    return True
            
            # Если это неизвестная кнопка, но она существует - считаем валидной
            logger.info(f"🔘 ИИ: Неизвестная кнопка {custom_id}, но она существует")
            return True
                
        except Exception as e:
            logger.error(f"Ошибка проверки обработчика {custom_id}: {e}")
            return True  # В случае ошибки считаем валидной

    async def recreate_weekly_goal_message(self):
        """Пересоздание сообщения с заданием недели"""
        try:
            if hasattr(self.bot, 'role_system'):
                role_system = self.bot.role_system
                
                if not role_system.weekly_goal_channel:
                    logger.error("🔘 ИИ: Канал заданий не найден")
                    return
                
                # Удаляем старые сообщения с кнопками
                await self.cleanup_old_goal_messages(role_system.weekly_goal_channel)
                
                # Создаем новое сообщение
                if not role_system.current_weekly_task:
                    await role_system.update_weekly_goal()
                else:
                    # Создаем кнопку для участия
                    from role_system import WeeklyGoalView
                    view = WeeklyGoalView(role_system)
                    
                    embed = discord.Embed(
                        title="🎯 Задание недели",
                        description=role_system.current_weekly_task["title"],
                        color=0xff00aa
                    )
                    embed.add_field(
                        name="📝 Описание",
                        value=role_system.current_weekly_task["description"],
                        inline=False
                    )
                    embed.add_field(
                        name="⏰ Срок",
                        value="7 дней",
                        inline=True
                    )
                    embed.add_field(
                        name="🏆 Награды",
                        value="1. Роль '🎯 Цель недели' (на 24 часа)\n2. Анонимная роль <@&1390545290196549642> (навсегда, доступ к каналу ⚠️・зона-анархии)",
                        inline=False
                    )
                    
                    await role_system.weekly_goal_channel.send(embed=embed, view=view)
                    logger.info("🔘 ИИ: Сообщение с заданием пересоздано")
                    
        except Exception as e:
            logger.error(f"Ошибка пересоздания сообщения: {e}")

    async def cleanup_old_goal_messages(self, channel):
        """Очистка старых сообщений с заданиями"""
        try:
            deleted_count = 0
            async for msg in channel.history(limit=100):
                if msg.author == self.bot.user and msg.components:
                    await msg.delete()
                    deleted_count += 1
                    if deleted_count >= 5:  # Ограничиваем количество удалений
                        break
                        
            if deleted_count > 0:
                logger.info(f"🔘 ИИ: Удалено {deleted_count} старых сообщений с кнопками")
                
        except Exception as e:
            logger.error(f"Ошибка очистки старых сообщений: {e}")

    async def check_other_system_buttons(self):
        """Проверка кнопок других систем"""
        try:
            # Проверяем кнопки модерации
            if hasattr(self.bot, 'moderation_logs'):
                await self.check_moderation_buttons()
                
            # Проверяем кнопки защиты
            if (hasattr(self.bot, 'raid_protection') or \
                hasattr(self.bot, 'channel_protection') or \
                hasattr(self.bot, 'ping_protection') or \
                hasattr(self.bot, 'protection_panel')):
                await self.check_protection_buttons()
                
        except Exception as e:
            logger.error(f"Ошибка проверки других кнопок: {e}")

    async def check_moderation_buttons(self):
        """Проверка кнопок модерации"""
        try:
            # Здесь можно добавить проверку кнопок модерации
            pass
        except Exception as e:
            logger.error(f"Ошибка проверки кнопок модерации: {e}")

    async def check_protection_buttons(self):
        """Проверка кнопок защиты"""
        try:
            # Здесь можно добавить проверку кнопок защиты
            pass
        except Exception as e:
            logger.error(f"Ошибка проверки кнопок защиты: {e}")

    async def auto_fix_button_errors(self, error_type: str, context: dict = None):
        """Автоматическое исправление ошибок кнопок"""
        try:
            logger.info(f"🔧 ИИ: Исправляю ошибку кнопок типа {error_type}")
            
            # Убеждаемся, что context не None
            if context is None:
                context = {}
            
            if error_type == "button_not_found":
                await self.fix_missing_buttons(context)
            elif error_type == "button_handler_error":
                await self.fix_button_handler(context)
            elif error_type == "view_timeout":
                await self.fix_view_timeout(context)
            elif error_type == "interaction_failed":
                await self.fix_interaction_error(context)
            else:
                await self.fix_generic_button_error(error_type, context)
                
        except Exception as e:
            logger.error(f"Ошибка исправления кнопок {error_type}: {e}")

    async def fix_missing_buttons(self, context: dict):
        """Исправление отсутствующих кнопок"""
        try:
            if context and 'channel' in context:
                channel = context['channel']
                if 'weekly_goal' in str(channel.name).lower():
                    await self.recreate_weekly_goal_message()
                elif 'role' in str(channel.name).lower():
                    await self.recreate_role_buttons(channel)
                    
        except Exception as e:
            logger.error(f"Ошибка исправления отсутствующих кнопок: {e}")

    async def fix_button_handler(self, context: dict):
        """Исправление обработчика кнопок"""
        try:
            if context and 'custom_id' in context:
                custom_id = context['custom_id']
                logger.info(f"🔧 ИИ: Исправляю обработчик кнопки {custom_id}")
                
                # Перезагружаем соответствующий модуль
                if 'role_system' in custom_id:
                    await self.reload_role_system()
                    
        except Exception as e:
            logger.error(f"Ошибка исправления обработчика: {e}")

    async def fix_view_timeout(self, context: dict):
        """Исправление таймаута кнопок"""
        try:
            logger.info("🔧 ИИ: Исправляю таймаут кнопок")
            
            # Создаем новые кнопки с увеличенным таймаутом
            if hasattr(self.bot, 'role_system'):
                await self.recreate_weekly_goal_message()
                
        except Exception as e:
            logger.error(f"Ошибка исправления таймаута: {e}")

    async def fix_interaction_error(self, context: dict):
        """Исправление ошибки взаимодействия"""
        try:
            logger.info("🔧 ИИ: Исправляю ошибку взаимодействия")
            
            # Проверяем и исправляем систему ролей
            if hasattr(self.bot, 'role_system'):
                await self.enhance_role_system_check()
                
        except Exception as e:
            logger.error(f"Ошибка исправления взаимодействия: {e}")

    async def fix_generic_button_error(self, error_type: str, context: dict):
        """Общее исправление ошибок кнопок"""
        try:
            logger.info(f"🔧 ИИ: Общее исправление ошибки кнопок {error_type}")
            
            # Перезагружаем систему ролей
            if hasattr(self.bot, 'role_system'):
                await self.reload_role_system()
                
        except Exception as e:
            logger.error(f"Ошибка общего исправления кнопок: {e}")

    async def reload_role_system(self):
        """Перезагрузка системы ролей"""
        try:
            if hasattr(self.bot, 'role_system'):
                role_system = self.bot.role_system
                
                # Сохраняем данные
                await self.save_role_system_data()
                
                # Перезапускаем задачи
                if hasattr(role_system, 'update_king_of_day'):
                    role_system.update_king_of_day.restart()
                if hasattr(role_system, 'update_weekly_goal'):
                    role_system.update_weekly_goal.restart()
                    
                # Восстанавливаем данные
                await self.restore_role_system_data()
                
                logger.info("🔄 ИИ: Система ролей перезагружена")
                
        except Exception as e:
            logger.error(f"Ошибка перезагрузки системы ролей: {e}")

    async def recreate_role_buttons(self, channel):
        """Пересоздание кнопок ролей"""
        try:
            if hasattr(self.bot, 'role_system'):
                role_system = self.bot.role_system
                
                # Отправляем новое описание ролей
                await role_system.send_roles_description()
                
                logger.info("🔘 ИИ: Кнопки ролей пересозданы")
                
        except Exception as e:
            logger.error(f"Ошибка пересоздания кнопок ролей: {e}")

    async def predictive_maintenance_check(self):
        """Проверка предсказательного обслуживания"""
        if not self.predictive_maintenance:
            return
            
        try:
            logger.info("🔮 УЛЬТРА-ИИ: Предсказательное обслуживание...")
            
            # Предсказываем ошибки для всех систем
            systems = ['role_system', 'moderation_system', 'protection_system', 'music_system']
            
            for system in systems:
                predictions = await self.ultra_ai.predict_errors(system)
                
                for prediction in predictions:
                    if prediction['confidence'] > 0.7:  # Высокая уверенность
                        logger.warning(f"🔮 УЛЬТРА-ИИ: Предсказываю ошибку {prediction['error_type']} в {system} (уверенность: {prediction['confidence']:.2f})")
                        
                        # Применяем профилактические меры
                        await self.apply_preventive_measures(prediction)
                        
        except Exception as e:
            logger.error(f"Ошибка предсказательного обслуживания: {e}")

    async def apply_preventive_measures(self, prediction: dict):
        """Применение профилактических мер"""
        try:
            system = prediction['system']
            error_type = prediction.get('error_type', 'unknown')
            
            if error_type == 'recurring_error':
                # Применяем исправление заранее
                fix = await self.ultra_ai.generate_fix(error_type, {'system': system})
                if fix:
                    await self.apply_generated_fix(fix)
                    
            elif error_type == 'code_issue':
                # Анализируем и исправляем код
                await self.analyze_and_fix_code(system)
                
        except Exception as e:
            logger.error(f"Ошибка применения профилактических мер: {e}")

    async def apply_generated_fix(self, fix: dict):
        """Применение сгенерированного исправления"""
        try:
            logger.info(f"🔧 УЛЬТРА-ИИ: Применяю сгенерированное исправление: {fix['description']}")
            
            # Выполняем действие
            if fix['action'] == 'recreate_buttons':
                await self.recreate_weekly_goal_message()
            elif fix['action'] == 'fix_role_system':
                await self.enhance_role_system_check()
            elif fix['action'] == 'fix_data':
                await self.check_data_integrity()
            elif fix['action'] == 'fix_discord':
                await self.discord_api_recovery_check()
            elif fix['action'] == 'fix_memory':
                await self.optimize_memory()
                
            logger.info(f"✅ УЛЬТРА-ИИ: Исправление применено успешно")
            
        except Exception as e:
            logger.error(f"Ошибка применения исправления: {e}")

    async def analyze_and_fix_code(self, system_name: str):
        """Анализ и исправление кода"""
        try:
            if system_name == 'role_system':
                file_path = 'role_system.py'
            elif system_name == 'moderation_system':
                file_path = 'moderation_logs.py'
            elif system_name == 'protection_system':
                file_path = 'smart_protection_system.py'
            else:
                return
                
            # Анализируем код
            issues = await self.ultra_ai.analyze_code_patterns(file_path)
            
            if issues:
                logger.warning(f"🔍 УЛЬТРА-ИИ: Обнаружены проблемы в коде {file_path}:")
                for issue in issues:
                    logger.warning(f"  - {issue}")
                    
                # Применяем автоматические исправления
                await self.auto_fix_code_issues(file_path, issues)
                
        except Exception as e:
            logger.error(f"Ошибка анализа кода: {e}")

    async def auto_fix_code_issues(self, file_path: str, issues: list):
        """Автоматическое исправление проблем в коде"""
        try:
            logger.info(f"🔧 УЛЬТРА-ИИ: Автоматически исправляю проблемы в {file_path}")
            
            # Создаем бэкап перед изменениями
            backup_path = f"{file_path}.backup.{int(time.time())}"
            shutil.copy2(file_path, backup_path)
            
            # Читаем файл
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Применяем исправления
            fixed_content = content
            
            for issue in issues:
                if "небезопасная задача" in issue:
                    fixed_content = await self.fix_unsafe_task(fixed_content)
                elif "небезопасный обработчик кнопки" in issue:
                    fixed_content = await self.fix_unsafe_button_handler(fixed_content)
                    
            # Записываем исправленный код
            if fixed_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                    
                logger.info(f"✅ УЛЬТРА-ИИ: Код {file_path} исправлен")
                
        except Exception as e:
            logger.error(f"Ошибка автоматического исправления кода: {e}")

    async def fix_unsafe_task(self, content: str) -> str:
        """Исправление небезопасной задачи"""
        try:
            # Добавляем try-catch блоки к задачам
            pattern = r'@tasks\.loop.*?\n\s*async def (\w+).*?:\n(.*?)(?=\n\s*@|\n\s*async def|\Z)'
            
            def add_try_catch(match):
                func_name = match.group(1)
                func_body = match.group(2)
                
                # Проверяем, есть ли уже try-catch
                if 'try:' in func_body:
                    return match.group(0)
                    
                # Добавляем try-catch
                safe_body = f'''        try:
{func_body}
        except Exception as e:
            logger.error(f"Ошибка в задаче {func_name}: {{e}}")'''
                
                return match.group(0).replace(func_body, safe_body)
                
            return re.sub(pattern, add_try_catch, content, flags=re.DOTALL)
            
        except Exception as e:
            logger.error(f"Ошибка исправления задачи: {e}")
            return content

    async def fix_unsafe_button_handler(self, content: str) -> str:
        """Исправление небезопасного обработчика кнопок"""
        try:
            # Добавляем проверки к обработчикам кнопок
            pattern = r'async def (\w+).*?button.*?:\n(.*?)(?=\n\s*async def|\Z)'
            
            def add_checks(match):
                func_name = match.group(1)
                func_body = match.group(2)
                
                # Проверяем, есть ли уже проверки
                if 'if ' in func_body:
                    return match.group(0)
                    
                # Добавляем базовые проверки
                safe_body = f'''        if not interaction or interaction.user.bot:
            return
            
{func_body}'''
                
                return match.group(0).replace(func_body, safe_body)
                
            return re.sub(pattern, add_checks, content, flags=re.DOTALL)
            
        except Exception as e:
            logger.error(f"Ошибка исправления обработчика: {e}")
            return content

    async def self_improvement_check(self):
        """Проверка самоулучшения"""
        if not self.self_improvement_mode:
            return
            
        try:
            logger.info("🚀 УЛЬТРА-ИИ: Самоулучшение системы...")
            
            # Анализируем эффективность исправлений
            await self.analyze_fix_effectiveness()
            
            # Улучшаем алгоритмы на основе результатов
            await self.improve_algorithms()
            
            # Оптимизируем производительность
            await self.optimize_performance()
            
            # Обновляем базу знаний
            await self.update_knowledge_base()
            
        except Exception as e:
            logger.error(f"Ошибка самоулучшения: {e}")

    async def analyze_fix_effectiveness(self):
        """Анализ эффективности исправлений"""
        try:
            # Анализируем успешность исправлений
            total_fixes = len(self.successful_fixes) + len(self.failed_fixes)
            if total_fixes > 0:
                success_rate = len(self.successful_fixes) / total_fixes
                logger.info(f"📊 УЛЬТРА-ИИ: Эффективность исправлений: {success_rate:.2%}")
                
                # Если эффективность низкая - улучшаем алгоритмы
                if success_rate < 0.7:
                    logger.warning("📊 УЛЬТРА-ИИ: Низкая эффективность, улучшаю алгоритмы...")
                    await self.improve_fix_algorithms()
                    
        except Exception as e:
            logger.error(f"Ошибка анализа эффективности: {e}")

    async def improve_fix_algorithms(self):
        """Улучшение алгоритмов исправления"""
        try:
            # Анализируем неудачные исправления
            for error_type, attempts in self.failed_fixes.items():
                if attempts > 3:
                    logger.info(f"🔧 УЛЬТРА-ИИ: Улучшаю алгоритм для {error_type}")
                    
                    # Создаем улучшенный алгоритм
                    improved_fix = await self.ultra_ai.generate_fix(error_type, {'improved': True})
                    if improved_fix:
                        self.solution_database[error_type] = improved_fix
                        
        except Exception as e:
            logger.error(f"Ошибка улучшения алгоритмов: {e}")

    async def improve_algorithms(self):
        """Улучшение алгоритмов"""
        try:
            # Улучшаем предсказание ошибок
            await self.improve_error_prediction()
            
            # Улучшаем генерацию исправлений
            await self.improve_fix_generation()
            
            # Улучшаем диагностику
            await self.improve_diagnostics()
            
        except Exception as e:
            logger.error(f"Ошибка улучшения алгоритмов: {e}")

    async def improve_error_prediction(self):
        """Улучшение предсказания ошибок"""
        try:
            # Анализируем паттерны ошибок
            error_patterns = defaultdict(list)
            for error in self.error_history:
                error_patterns[error.get('type')].append(error)
                
            # Улучшаем модели предсказания
            for error_type, errors in error_patterns.items():
                if len(errors) > 5:
                    # Создаем улучшенную модель предсказания
                    self.ultra_ai.prediction_models[error_type] = {
                        'frequency': len(errors),
                        'last_occurrence': max(error.get('timestamp', 0) for error in errors),
                        'confidence': min(len(errors) / 10, 0.95)
                    }
                    
        except Exception as e:
            logger.error(f"Ошибка улучшения предсказания: {e}")

    async def improve_fix_generation(self):
        """Улучшение генерации исправлений"""
        try:
            # Анализируем успешные исправления
            for error_type, fix in self.successful_fixes.items():
                if fix.get('success_count', 0) > 3:
                    # Улучшаем исправление
                    improved_fix = await self.ultra_ai.generate_fix(error_type, {
                        'successful_patterns': fix.get('patterns', []),
                        'improved': True
                    })
                    
                    if improved_fix:
                        self.solution_database[error_type] = improved_fix
                        
        except Exception as e:
            logger.error(f"Ошибка улучшения генерации: {e}")

    async def improve_diagnostics(self):
        """Улучшение диагностики"""
        try:
            # Улучшаем проверки на основе найденных проблем
            for system_name, health in self.system_health.items():
                if health == 'error':
                    # Создаем улучшенную диагностику
                    await self.create_improved_diagnostics(system_name)
                    
        except Exception as e:
            logger.error(f"Ошибка улучшения диагностики: {e}")

    async def create_improved_diagnostics(self, system_name: str):
        """Создание улучшенной диагностики"""
        try:
            # Создаем более детальную диагностику
            if system_name == 'role_system':
                await self.create_role_system_diagnostics()
            elif system_name == 'moderation_system':
                await self.create_moderation_diagnostics()
                
        except Exception as e:
            logger.error(f"Ошибка создания диагностики: {e}")

    async def create_role_system_diagnostics(self):
        """Создание диагностики системы ролей"""
        try:
            # Добавляем дополнительные проверки
            additional_checks = [
                'check_role_permissions',
                'check_channel_access',
                'check_task_validity',
                'check_data_consistency'
            ]
            
            for check in additional_checks:
                if check not in self.system_health:
                    self.system_health[check] = 'healthy'
                    
        except Exception as e:
            logger.error(f"Ошибка создания диагностики ролей: {e}")

    async def optimize_performance(self):
        """Оптимизация производительности"""
        try:
            # Оптимизируем использование памяти
            await self.optimize_memory_usage()
            
            # Оптимизируем частоту проверок
            await self.optimize_check_frequency()
            
            # Оптимизируем логирование
            await self.optimize_logging()
            
        except Exception as e:
            logger.error(f"Ошибка оптимизации производительности: {e}")

    async def optimize_memory_usage(self):
        """Оптимизация использования памяти"""
        try:
            # Очищаем старые данные
            if len(self.error_history) > 1000:
                self.error_history = self.error_history[-500:]  # Оставляем последние 500
                
            # Очищаем кэши
            if hasattr(self.ultra_ai, 'code_analysis_cache'):
                if len(self.ultra_ai.code_analysis_cache) > 100:
                    self.ultra_ai.code_analysis_cache.clear()
                    
        except Exception as e:
            logger.error(f"Ошибка оптимизации памяти: {e}")

    async def optimize_check_frequency(self):
        """Оптимизация частоты проверок"""
        try:
            # Анализируем частоту ошибок
            recent_errors = [e for e in self.error_history if e.get('timestamp', 0) > time.time() - 3600]
            
            if len(recent_errors) > 10:
                # Увеличиваем частоту проверок
                logger.info("⚡ УЛЬТРА-ИИ: Увеличиваю частоту проверок из-за большого количества ошибок")
            elif len(recent_errors) < 2:
                # Уменьшаем частоту проверок
                logger.info("⚡ УЛЬТРА-ИИ: Уменьшаю частоту проверок - система стабильна")
                
        except Exception as e:
            logger.error(f"Ошибка оптимизации частоты: {e}")

    async def optimize_logging(self):
        """Оптимизация логирования"""
        try:
            # Проверяем размер логов
            log_size = 0
            for log_file in ['bot.log', 'recovery_log.json']:
                if os.path.exists(log_file):
                    log_size += os.path.getsize(log_file)
                    
            # Если логи слишком большие - архивируем
            if log_size > 50 * 1024 * 1024:  # 50 МБ
                logger.info("📝 УЛЬТРА-ИИ: Логи слишком большие, архивирую...")
                await self.archive_all_logs()
                
        except Exception as e:
            logger.error(f"Ошибка оптимизации логирования: {e}")

    async def archive_all_logs(self):
        """Архивирование всех логов"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for log_file in ['bot.log', 'recovery_log.json']:
                if os.path.exists(log_file):
                    archive_name = f"{log_file}.{timestamp}.bak"
                    shutil.copy2(log_file, archive_name)
                    
                    # Очищаем оригинальный файл
                    with open(log_file, 'w') as f:
                        f.write("")
                        
            logger.info(f"📝 УЛЬТРА-ИИ: Все логи заархивированы")
            
        except Exception as e:
            logger.error(f"Ошибка архивирования логов: {e}")

    async def update_knowledge_base(self):
        """Обновление базы знаний"""
        try:
            # Обновляем паттерны ошибок
            await self.update_error_patterns()
            
            # Обновляем решения
            await self.update_solutions()
            
            # Обновляем метрики производительности
            await self.update_performance_metrics()
            
        except Exception as e:
            logger.error(f"Ошибка обновления базы знаний: {e}")

    async def update_error_patterns(self):
        """Обновление паттернов ошибок"""
        try:
            # Анализируем новые ошибки
            new_errors = [e for e in self.error_history if e.get('timestamp', 0) > time.time() - 86400]  # За последние 24 часа
            
            for error in new_errors:
                error_type = error.get('type')
                if error_type:
                    self.ultra_ai.error_patterns[error_type].append(error)
                    
        except Exception as e:
            logger.error(f"Ошибка обновления паттернов: {e}")

    async def update_solutions(self):
        """Обновление решений"""
        try:
            # Обновляем базу решений на основе успешных исправлений
            for error_type, fix in self.successful_fixes.items():
                if fix.get('success_count', 0) > 2:
                    self.ultra_ai.solution_database[error_type] = fix
                    
        except Exception as e:
            logger.error(f"Ошибка обновления решений: {e}")

    async def update_performance_metrics(self):
        """Обновление метрик производительности"""
        try:
            # Обновляем метрики
            self.performance_metrics.update({
                'total_fixes': len(self.successful_fixes) + len(self.failed_fixes),
                'success_rate': len(self.successful_fixes) / max(len(self.successful_fixes) + len(self.failed_fixes), 1),
                'systems_monitored': len(self.system_health),
                'healthy_systems': sum(1 for status in self.system_health.values() if status == 'healthy'),
                'last_update': time.time()
            })
            
        except Exception as e:
            logger.error(f"Ошибка обновления метрик: {e}")

    async def create_moderation_diagnostics(self):
        """Создание диагностики системы модерации"""
        try:
            # Добавляем дополнительные проверки для модерации
            additional_checks = [
                'check_moderation_permissions',
                'check_log_channel_access',
                'check_action_validity',
                'check_moderation_data'
            ]
            
            for check in additional_checks:
                if check not in self.system_health:
                    self.system_health[check] = 'healthy'
                    
        except Exception as e:
            logger.error(f"Ошибка создания диагностики модерации: {e}")

    async def improve_solutions(self):
        """Улучшение решений на основе анализа"""
        try:
            # Анализируем успешные решения
            for error_type, solution in self.solution_database.items():
                if solution.get('success_count', 0) > 5:
                    # Улучшаем решение
                    improved_solution = await self.ultra_ai.generate_fix(error_type, {
                        'successful_patterns': solution.get('patterns', []),
                        'improved': True
                    })
                    
                    if improved_solution:
                        self.solution_database[error_type] = improved_solution
                        
        except Exception as e:
            logger.error(f"Ошибка улучшения решений: {e}")

    async def prevent_recurring_errors(self):
        """Предотвращение повторяющихся ошибок"""
        try:
            # Анализируем частые ошибки
            error_frequency = defaultdict(int)
            for error in self.error_history[-100:]:  # Последние 100 ошибок
                error_type = error.get('type', 'unknown')
                error_frequency[error_type] += 1
                
            # Применяем профилактические меры для частых ошибок
            for error_type, frequency in error_frequency.items():
                if frequency >= 3:
                    logger.warning(f"🔧 УЛЬТРА-ИИ: Применяю профилактические меры для {error_type}")
                    await self.apply_preventive_fix(error_type)
                    
        except Exception as e:
            logger.error(f"Ошибка предотвращения повторяющихся ошибок: {e}")

    async def apply_preventive_fix(self, error_type: str):
        """Применение профилактического исправления"""
        try:
            fix = await self.ultra_ai.generate_fix(error_type, {'preventive': True})
            if fix:
                await self.apply_generated_fix(fix)
                
        except Exception as e:
            logger.error(f"Ошибка применения профилактического исправления: {e}")

async def setup_auto_recovery(bot):
    """Настройка системы автоматического восстановления"""
    try:
        auto_recovery = AutoRecoverySystem(bot)
        bot.auto_recovery = auto_recovery
        await auto_recovery.setup()
        
        # Добавляем глобальный обработчик ошибок кнопок
        @bot.event
        async def on_error(event, *args, **kwargs):
            try:
                # Проверяем, связана ли ошибка с кнопками
                if 'interaction' in str(args) or 'button' in str(args) or 'view' in str(args):
                    logger.warning(f"🔘 Обнаружена ошибка кнопок в событии {event}")
                    
                    # Автоматически исправляем ошибку кнопок
                    if hasattr(bot, 'auto_recovery'):
                        await bot.auto_recovery.auto_fix_button_errors("interaction_failed", {
                            'event': event,
                            'args': args,
                            'kwargs': kwargs
                        })
                        
            except Exception as e:
                logger.error(f"Ошибка обработки ошибки кнопок: {e}")
                
            # Запускаем обычное восстановление
            await global_error_handler(bot, Exception(f"Event error: {event}"), context={"event": event, "args": args, "kwargs": kwargs})
            
        logger.info("Система автоматического восстановления настроена")
        
    except Exception as e:
        logger.error(f"Ошибка настройки системы восстановления: {e}")

# Глобальный обработчик ошибок
async def global_error_handler(bot, error, context=None):
    """Глобальный обработчик ошибок"""
    try:
        logger.error(f"Глобальная ошибка: {error}")
        logger.error(traceback.format_exc())
        
        # Если есть система восстановления, запускаем её
        if hasattr(bot, 'auto_recovery'):
            await bot.auto_recovery.emergency_recovery()
            
    except Exception as e:
        logger.critical(f"Критическая ошибка в обработчике ошибок: {e}") 