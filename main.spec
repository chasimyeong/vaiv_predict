# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import os
import importlib

a = Analysis(['Dpredict_RestAPI_v0.3.py'],
             pathex=['C:\\Users\\daumsoft\\Jupyter Notebook\\daumsoft\\LH Digital Twin Develop\\딥러닝_통합_API\\Dpredict'],
             binaries=[],
             datas=[(os.path.join(os.path.dirname(importlib.import_module('tensorflow').__file__),
                                  "lite/experimental/microfrontend/python/ops/_audio_microfrontend_op.so"),
                     "tensorflow/lite/experimental/microfrontend/python/ops/"),
                     ("models", "models/"),
                     ("models/weights", "models/weights/")
                     ],
             hiddenimports=["tensorflow.python.keras.engine.base_layer_v1"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Dpredict_RestAPI_v0.3',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Dpredict_RestAPI_v0.3')