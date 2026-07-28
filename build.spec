# -*- mode: python ; coding: utf-8 -*-

"""
LogiTrack Desktop - Archivo de especificación de PyInstaller
"""

import sys
import os
from pathlib import Path

# ============================================================
# CONFIGURACIÓN
# ============================================================

APP_NAME = "LogiTrackDesktop"

# ============================================================
# RECOLECCIÓN DE DATOS
# ============================================================

def collect_data_files():
    """Recopila archivos de datos necesarios"""
    datas = []
    
    # Incluir TODO el paquete logitrack
    if Path('logitrack').exists():
        datas.append(('logitrack', 'logitrack'))
    
    # Incluir recursos si existen
    if Path('resources').exists():
        datas.append(('resources', 'resources'))
    
    return datas

# ============================================================
# IMPORTACIONES OCULTAS
# ============================================================

hiddenimports = [
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'sqlite3',
    'json',
    'datetime',
    'pathlib',
    'typing',
    'dataclasses',
    'enum',
    'random',
    'time',
]

# ============================================================
# ANÁLISIS
# ============================================================

a = Analysis(
    ['logitrack/__main__.py'],
    pathex=[],
    binaries=[],
    datas=collect_data_files(),
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# ============================================================
# PYZ
# ============================================================

pyz = PYZ(a.pure)

# ============================================================
# EXE
# ============================================================

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico' if Path('resources/icon.ico').exists() else None,
)

# ============================================================
# COLLECT
# ============================================================

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=f'{APP_NAME}',
)