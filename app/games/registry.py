# app/games/registry.py
import os
import importlib
import pkgutil

# Импортируем BaseGame для проверки типов
from games.base.base_game import BaseGame

class GameRegistry:
    """Реестр всех доступных игр"""
    
    _games = {}
    
    @classmethod
    def register_game(cls, game_class):
        """Регистрация игры"""
        game_name = game_class.GAME_NAME.lower()
        cls._games[game_name] = game_class
        print(f"Игра '{game_class.GAME_NAME}' зарегистрирована")
        
    @classmethod
    def get_game_class(cls, game_name):
        """Получение класса игры по имени"""
        return cls._games.get(game_name.lower())
        
    @classmethod
    def get_all_games(cls):
        """Получение всех зарегистрированных игр"""
        return {name: cls.get_game_info(name) for name in cls._games}
        
    @classmethod
    def get_game_info(cls, game_name):
        """Получение информации об игре"""
        game_class = cls.get_game_class(game_name)
        if game_class:
            return game_class.get_game_info()
        return None
        
    @classmethod
    def auto_discover_games(cls):
        """Автоматическое обнаружение и регистрация игр"""
        games_package = "games"
        
        try:
            # Импортируем пакет games
            games_module = importlib.import_module(games_package)
            print(f"Просмотр пакета: {games_module.__path__}")
            
            # Проходим по всем подмодулям пакета games
            for importer, modname, ispkg in pkgutil.iter_modules(games_module.__path__):
                print(f"Найден модуль: {modname}, ispkg: {ispkg}")
                if ispkg and modname not in ['base', 'registry']:
                    try:
                        print(f"Попытка загрузки игры: {modname}")
                        # Импортируем модуль игры
                        game_module = importlib.import_module(f"{games_package}.{modname}")
                        print(f"Модуль {modname} импортирован")
                        
                        # Проверяем, есть ли в модуле класс Game
                        if hasattr(game_module, 'Game'):
                            game_class = getattr(game_module, 'Game')
                            if isinstance(game_class, type) and issubclass(game_class, BaseGame):
                                cls.register_game(game_class)
                            else:
                                print(f"Класс Game в {modname} не является подклассом BaseGame")
                        else:
                            # Ищем любой класс, который наследуется от BaseGame
                            for attr_name in dir(game_module):
                                attr = getattr(game_module, attr_name)
                                if (isinstance(attr, type) and 
                                    issubclass(attr, BaseGame) and
                                    attr.__module__ == game_module.__name__):
                                    cls.register_game(attr)
                                    break
                            else:
                                print(f"В модуле {modname} не найден класс игры")
                                
                    except Exception as e:
                        print(f"Ошибка при загрузке игры из модуля {modname}: {e}")
                        import traceback
                        traceback.print_exc()
                        
        except Exception as e:
            print(f"Ошибка при автоматическом обнаружении игр: {e}")
            import traceback
            traceback.print_exc()

# Автоматическое обнаружение игр при импорте модуля
GameRegistry.auto_discover_games()