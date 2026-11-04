"""
core/modules/__init__.py — Rumix Modules Gateway.
Ищет *.py в этой папке, регистрирует их как API-маршруты.
Новый модуль = новый файл. Код шлюза не меняется.

Контракт:
    GET  /api/m/<name>  — состояние
    POST /api/m/<name>  — действие, JSON-тело
    GET  /api/modules   — каталог (сломанные модули видны честно, ok:false)
    каждый вызов → ~/rumix/agents/evidence.jsonl (9 полей карты v3)

Статусы и уверенность — строго словарь карты v3:
    status: full / partial / unavailable / error
    confidence: high / medium / low
"""
import glob
import importlib
import importlib.util
import json
import os
import re
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional

MODULES_DIR = os.path.dirname(os.path.abspath(__file__))
_loaded_modules: Dict[str, Any] = {}
_broken_modules: Dict[str, str] = {}


@dataclass
class ModuleResult:
    data: Any
    status: str = "full"
    confidence: str = "high"
    limitations: list = None
    code: int = 200
    raw_ref: Optional[str] = None
    conflict: bool = False

    def __post_init__(self):
        if self.limitations is None:
            self.limitations = []
        # Код важнее забытого status: 400 не может быть "full".
        if self.code >= 400 and self.status == "full":
            self.status = {400: "partial", 404: "partial", 405: "partial",
                           503: "unavailable"}.get(self.code, "error")


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

    def _help(self):
        """help_text из module(); если пусто — первая строка docstring."""
        if self.help:
            return self.help
        for fn in (self.get_handler, self.post_handler):
            doc = ((getattr(fn, "__doc__", "") or "").strip().split("\n")[0]) if fn else ""
            if doc:
                return doc
        return ""

    def to_dict(self):
        return {
            "name": self.name,
            "title": self.title,
            "icon": self.icon,
            "ok": True,
            "has_action": self.post_handler is not None,
            "help": self._help(),
        }


def module(name: str, title: str, icon: str = "📦", help_text: str = "") -> Module:
    if not re.match(r"^[a-z][a-z0-9_]*$", name):
        raise ValueError(f"Имя модуля '{name}' неверно. Только [a-z0-9_].")
    m = Module(name, title, icon, help_text)
    _loaded_modules[name] = m
    return m


def discover():
    """Сканирует папку и импортирует все модули. Сломанные — в _broken_modules."""
    _loaded_modules.clear()
    _broken_modules.clear()
    for filepath in sorted(glob.glob(os.path.join(MODULES_DIR, "*.py"))):
        fname = os.path.basename(filepath)
        if fname.startswith("__"):
            continue
        mod_name = fname[:-3]
        full = f"core.modules.{mod_name}"
        try:
            # reload: повторный mount не должен обнулять каталог из-за кэша импортов
            if full in sys.modules:
                importlib.reload(sys.modules[full])
            else:
                importlib.import_module(full)
        except Exception as e:
            _broken_modules[mod_name] = f"{type(e).__name__}: {e}"
            # модуль мог успеть зарегистрироваться до падения — чтобы не было
            # двух записей в каталоге, убираем недострой
            _loaded_modules.pop(mod_name, None)
            print(f"❌ Модуль {mod_name} не загрузился: {e}")


# ---------------------------------------------------------------- улики (v3)
_EVIDENCE_CLS = None


def _evidence_cls():
    """EvidenceBuffer по пути к файлу: одноимённый pip-пакет 'agents' не мешает."""
    global _EVIDENCE_CLS
    if _EVIDENCE_CLS is None:
        p = Path(MODULES_DIR).parents[1] / "agents" / "runtime" / "evidence_buffer.py"
        spec = importlib.util.spec_from_file_location("_rumix_evidence", p)
        if spec is None or spec.loader is None:
            raise ImportError(f"нет evidence_buffer: {p}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _EVIDENCE_CLS = mod.EvidenceBuffer
    return _EVIDENCE_CLS


def _record(name, method, res):
    """Каждый вызов — строка в журнале. Сбой записи не ломает API."""
    try:
        _evidence_cls()().record(
            source=f"m/{name}",
            test=f"{method} /api/m/{name}",
            result=json.dumps(res.data, ensure_ascii=False, default=str)[:300],
            status=res.status,
            confidence=res.confidence,
            limitations=res.limitations,
            raw_ref=res.raw_ref,
            conflict=res.conflict,
        )
    except Exception as e:
        print(f"[modules] evidence пропущена для {name}: {e}")


def mount(app):
    """Подключает модули к Flask-приложению. Идемпотентно."""
    from flask import jsonify, request

    if getattr(app, "_modules_mounted", False):
        return _loaded_modules
    app._modules_mounted = True

    discover()

    def payload(name, method, res):
        _record(name, method, res)
        resp = jsonify({
            "ok": res.code < 400,
            "status": res.status,
            "confidence": res.confidence,
            "data": res.data,
            "limitations": res.limitations,
            "raw_ref": res.raw_ref,
        })
        resp.status_code = res.code
        return resp

    @app.route("/api/modules", methods=["GET"])
    def list_modules():
        mods = [m.to_dict() for m in _loaded_modules.values()]
        for name, err in sorted(_broken_modules.items()):
            mods.append({"name": name, "title": "не загрузился", "icon": "⚠️",
                         "ok": False, "has_action": False, "error": err})
        return jsonify({"ok": True, "modules": mods})

    def make_handler(mod):
        def handler():
            name = mod.name
            method = request.method
            fn = mod.get_handler if method == "GET" else mod.post_handler
            if fn is None:
                return payload(name, method, ModuleResult(
                    {"error": f"у модуля '{name}' нет действия {method}"},
                    status="partial", code=405))
            try:
                if method == "GET":
                    res = fn()
                else:
                    data = request.get_json(silent=True)
                    if not isinstance(data, dict):
                        return payload(name, method, ModuleResult(
                            {"error": "нужен JSON-объект в теле"},
                            status="partial", code=400))
                    res = fn(data)
            except Exception as e:
                traceback.print_exc()
                return payload(name, method, ModuleResult(
                    {"error": str(e)}, status="error", confidence="high", code=500))
            if not isinstance(res, ModuleResult):
                res = ModuleResult(res)
            return payload(name, method, res)
        return handler

    for name, mod in _loaded_modules.items():
        # Один маршрут на модуль: метод различается внутри handler.
        # Отсутствующий метод отвечает JSON-ом, а не HTML-ом Flask.
        app.add_url_rule(f"/api/m/{name}", f"mod_{name}",
                         make_handler(mod), methods=["GET", "POST"])

    total = len(_loaded_modules)
    broken = f", сломано: {len(_broken_modules)}" if _broken_modules else ""
    print(f"✅ Шлюз модулей запущен. Найдено: {total}{broken}")
    return _loaded_modules
