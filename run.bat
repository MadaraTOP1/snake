@echo off
SETLOCAL

SET VENV_DIR=venv

python --version >nul 2>&1
IF ERRORLEVEL 1 (
  echo Ошибка: Python не найден в PATH. Установите Python 3.8+.
  pause
  exit /b 1
)

IF NOT EXIST "%VENV_DIR%\Scripts\activate.bat" (
  echo Виртуальное окружение не найдено — создаю "%VENV_DIR%"...
  python -m venv "%VENV_DIR%"
  IF ERRORLEVEL 1 (
    echo Ошибка: не удалось создать виртуальное окружение.
    pause
    exit /b 1
  )
)

call "%VENV_DIR%\Scripts\activate.bat"
IF ERRORLEVEL 1 (
  echo Ошибка: не удалось активировать виртуальное окружение.
  pause
  exit /b 1
)

python -m pip install --upgrade pip
IF EXIST requirements.txt (
  echo Установка зависимостей...
  pip install -r requirements.txt
  IF ERRORLEVEL 1 (
    echo Предупреждение: проблемы при установке зависимостей.
  )
)

IF EXIST snake_game.py (
  echo Запуск snake_game.py...
  python snake_game.py
) ELSE (
  echo Ошибка: файл snake_game.py не найден в текущей папке.
  pause
)

ENDLOCAL
