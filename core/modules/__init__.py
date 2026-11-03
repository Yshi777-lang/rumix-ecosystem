"""
core/modules/__init__.py — Rumix Modules Gateway.
Ищет *.py в этой папке, регистрирует их как API-маршруты.
Новый модуль = новый файл. Код шлюза не меняется.
"""
import os
import re
import glob
import importlib
import traceback
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, Callable

MODULES_DIR = os.path.dirname(os.path.abspath(__file__))
_loaded_modules: Dict[str, Any] = {}

@dataclass
class ModuleResult:
    data: Any
    status: str = "ok"
    confidence: str = "high"
    limitations: list = None
    code: int = 200

    def __post_init__(self):
        if self.limitations is None:
            self.limitations = []

class Module:
    def __init__(self, name: str, title: str, icon: str = "📦", help_text: str = ""):
        self.name = name
        self.title = title
        self.icon = icon
        self.help = help_text
        self.get_handler: Optional[Callable] = None
        self.post_handler: Optional[Callable] = None

    def get(self, f: Callable):
        self.get_handler = f
        return f

    def post(self, f: Callable):
        self.post_handler = f
        return f

    def to_dict(self):
        return {
            "name": self.name,
            "title": self.title,
            "icon": self.icon,
            "ok": True,
            "has_action": self.post_handler is not None,
            "help": self.help
        }

def module(name: str, title: str, icon: str = "📦", help_text: str = "") -> Module:
    if not re.match(r"^[a-z][a-z0-9_]*$", name):
        raise ValueError(f"Имя модуля '{name}' неверно. Только [a-z0-9_].")
    m = Module(name, title, icon, help_text)
    _loaded_modules[name] = m
    return m

def discover():
    """Сканирует папку и импортирует все модули."""
    _loaded_modules.clear()
    for filepath in glob.glob(os.path.join(MODULES_DIR, "*.py")):
        fname = os.path.basename(filepath)
        if fname.startswith("__"):
            continue
        mod_name = fname[:-3]
        try:
            importlib.import_module(f"core.modules.{mod_name}")
        except Exception as e:
            print(f"❌ Ошибка загрузки модуля {mod_name}: {e}")
            traceback.print_exc()

def mount(app):
    """Подключает модули к Flask-приложению."""
    from flask import jsonify, request
    
    # 1. Сканируем папку при старте
    discover()

    # 2. Каталог всех модулей
    @app.route("/api/modules", methods=["GET"])
    def list_modules():
        mods = [m.to_dict() for m in _loaded_modules.values()]
        return jsonify({"ok": True, "modules": mods})

    # 3. Динамические маршруты для каждого модуля
    for name, mod in _loaded_modules.items():
        def make_get_handler(m):
            def handler():
                try:
                    res = m.get_handler()
                    if isinstance(res, ModuleResult):
                        resp = jsonify({"ok": res.code == 200, "status": res.status, "data": res.data, "confidence": res.confidence, "limitations": res.limitations})
                        resp.status_code = res.code
                        return resp
                    return jsonify({"ok": True, "data": res})
                except Exception as e:
                    return jsonify({"ok": False, "error": str(e)}), 500
            return handler

        def make_post_handler(m):
            def handler():
                try:
                    data = request.get_json() or {}
                    res = m.post_handler(data)
                    if isinstance(res, ModuleResult):
                        resp = jsonify({"ok": res.code == 200, "status": res.status, "data": res.data, "confidence": res.confidence, "limitations": res.limitations})
                        resp.status_code = res.code
                        return resp
                    return jsonify({"ok": True, "data": res})
                except Exception as e:
                    return jsonify({"ok": False, "error": str(e)}), 500
            return handler

        if mod.get_handler:
            app.add_url_rule(f"/api/m/{name}", f"mod_{name}_get", make_get_handler(mod), methods=["GET"])
        if mod.post_handler:
            app.add_url_rule(f"/api/m/{name}", f"mod_{name}_post", make_post_handler(mod), methods=["POST"])

    print(f"✅ Шлюз модулей запущен. Найдено: {len(_loaded_modules)}")
