"""
Запуск игры из EXE с правильной рабочей директорией.
"""
import sys
import os

# Setup working directory
if hasattr(sys, 'frozen'):
    app_dir = os.path.dirname(sys.executable)
else:
    app_dir = os.path.dirname(os.path.abspath(__file__))

os.chdir(app_dir)

# Run the GUI
try:
    from gui_main import main
    main()
except Exception as e:
    import traceback
    traceback.print_exc()
