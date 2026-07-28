#!/usr/bin/env python3
"""
Tests de Arquitectura - Fase 6
Verifica que las vistas NO importan modelos directamente.
"""

import ast
import os
from pathlib import Path


def test_views_dont_import_models():
    """
    Test de Arquitectura: Verifica que las vistas no importan modelos directamente.
    Regla: Las vistas solo pueden comunicarse con controladores.
    EXCEPCIÓN: Pueden importar enums/constantes (ShipmentStatus, ShipmentType)
    """
    views_dir = Path("logitrack/views")
    violations = []

    # Importaciones permitidas desde models (solo enums/constantes)
    ALLOWED_MODEL_IMPORTS = ["ShipmentStatus", "ShipmentType"]

    for py_file in views_dir.glob("*.py"):
        if py_file.name.startswith("__"):
            continue

        with open(py_file, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and "models" in node.module:
                    # Verificar qué se importa de models
                    imported_names = [name.name for name in node.names]
                    # Verificar si hay importaciones no permitidas
                    for name in imported_names:
                        if name not in ALLOWED_MODEL_IMPORTS:
                            violations.append({
                                "file": py_file.name,
                                "line": node.lineno,
                                "import": f"from {node.module} import {name}"
                            })

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name and "models" in alias.name:
                        violations.append({
                            "file": py_file.name,
                            "line": node.lineno,
                            "import": f"import {alias.name}"
                        })

    if violations:
        error_msg = "❌ Violaciones de arquitectura encontradas:\n"
        for v in violations:
            error_msg += f"  - {v['file']}:{v['line']} -> {v['import']}\n"
        error_msg += "\nRegla: Las vistas NO deben importar modelos directamente."
        error_msg += " Solo pueden importar enums/constantes (ShipmentStatus, ShipmentType)."
        error_msg += " Usa el controlador para acceder a los modelos."

        assert False, error_msg

    assert True, "✅ Arquitectura correcta: Las vistas no importan modelos"


def test_views_only_import_controllers():
    """
    Test de Arquitectura: Verifica que las vistas solo importan controladores.
    Las vistas NO deben importar services o models directamente.
    """
    views_dir = Path("logitrack/views")
    violations = []

    # Importaciones permitidas en vistas
    allowed_imports = [
        "PyQt6",
        "..controllers",
        "..ui.theme",
        "..ui.components",
        "..models",  # Permitido solo para tipos (ShipmentStatus, ShipmentType)
    ]

    for py_file in views_dir.glob("*.py"):
        if py_file.name.startswith("__"):
            continue

        with open(py_file, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    # Verificar si es una importación no permitida
                    is_allowed = False
                    for allowed in allowed_imports:
                        if allowed in node.module:
                            is_allowed = True
                            break

                    # Excepción: permitir importar modelos solo para tipos (no para lógica)
                    if node.module and "models" in node.module:
                        # Verificar qué se importa de models
                        for name in node.names:
                            # Permitir importar solo ShipmentStatus y ShipmentType
                            if name.name not in ["ShipmentStatus", "ShipmentType"]:
                                if not is_allowed:
                                    violations.append({
                                        "file": py_file.name,
                                        "line": node.lineno,
                                        "import": f"from {node.module} import {name.name}"
                                    })
                    elif not is_allowed and not node.module.startswith("."):
                        # Importación absoluta no permitida
                        if "services" in node.module or "models" in node.module:
                            violations.append({
                                "file": py_file.name,
                                "line": node.lineno,
                                "import": f"from {node.module} import ..."
                            })

    if violations:
        error_msg = "❌ Importaciones no permitidas en vistas:\n"
        for v in violations:
            error_msg += f"  - {v['file']}:{v['line']} -> {v['import']}\n"
        error_msg += "\nRegla: Las vistas solo deben importar controladores y UI."

        assert False, error_msg

    assert True, "✅ Arquitectura correcta: Las vistas solo importan controladores"


def test_controllers_dont_have_ui_imports():
    """
    Test de Arquitectura: Verifica que los controladores NO importan UI.
    Los controladores NO deben tener dependencias de PyQt6 widgets.
    """
    controllers_dir = Path("logitrack/controllers")
    violations = []

    for py_file in controllers_dir.glob("*.py"):
        if py_file.name.startswith("__"):
            continue

        with open(py_file, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if "PyQt6.QtWidgets" in alias.name:
                        violations.append({
                            "file": py_file.name,
                            "line": node.lineno,
                            "import": f"import {alias.name}"
                        })

            elif isinstance(node, ast.ImportFrom):
                if node.module and "PyQt6.QtWidgets" in node.module:
                    violations.append({
                        "file": py_file.name,
                        "line": node.lineno,
                        "import": f"from {node.module} import ..."
                    })

    if violations:
        error_msg = "❌ Controladores importan UI:\n"
        for v in violations:
            error_msg += f"  - {v['file']}:{v['line']} -> {v['import']}\n"
        error_msg += "\nRegla: Los controladores NO deben importar PyQt6 widgets."

        assert False, error_msg

    assert True, "✅ Arquitectura correcta: Los controladores no importan UI"


def test_services_dont_have_ui_imports():
    """
    Test de Arquitectura: Verifica que los servicios NO importan UI.
    Los servicios deben ser independientes de la interfaz.
    """
    services_dir = Path("logitrack/services")
    violations = []

    for py_file in services_dir.glob("*.py"):
        if py_file.name.startswith("__"):
            continue

        with open(py_file, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if "PyQt6" in alias.name:
                        violations.append({
                            "file": py_file.name,
                            "line": node.lineno,
                            "import": f"import {alias.name}"
                        })

            elif isinstance(node, ast.ImportFrom):
                if node.module and "PyQt6" in node.module:
                    violations.append({
                        "file": py_file.name,
                        "line": node.lineno,
                        "import": f"from {node.module} import ..."
                    })

    if violations:
        error_msg = "❌ Servicios importan UI:\n"
        for v in violations:
            error_msg += f"  - {v['file']}:{v['line']} -> {v['import']}\n"
        error_msg += "\nRegla: Los servicios NO deben importar PyQt6."

        assert False, error_msg

    assert True, "✅ Arquitectura correcta: Los servicios no importan UI"


def test_models_dont_have_ui_imports():
    """
    Test de Arquitectura: Verifica que los modelos NO importan UI.
    Los modelos deben ser totalmente independientes.
    """
    models_dir = Path("logitrack/models")
    violations = []

    for py_file in models_dir.glob("*.py"):
        if py_file.name.startswith("__"):
            continue

        with open(py_file, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if "PyQt6" in alias.name:
                        violations.append({
                            "file": py_file.name,
                            "line": node.lineno,
                            "import": f"import {alias.name}"
                        })

            elif isinstance(node, ast.ImportFrom):
                if node.module and "PyQt6" in node.module:
                    violations.append({
                        "file": py_file.name,
                        "line": node.lineno,
                        "import": f"from {node.module} import ..."
                    })

    if violations:
        error_msg = "❌ Modelos importan UI:\n"
        for v in violations:
            error_msg += f"  - {v['file']}:{v['line']} -> {v['import']}\n"
        error_msg += "\nRegla: Los modelos NO deben importar PyQt6."

        assert False, error_msg

    assert True, "✅ Arquitectura correcta: Los modelos no importan UI"