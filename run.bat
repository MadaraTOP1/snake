@echo off
SETLOCAL

REM Путь к виртуальному окружению
SET VENV_DIR=venv

REM Проверка наличия Python в PATH
python --version >nul 2>&1
IF ERRORLEVEL 1 (
  echo Ошибка: Python не найден в PATH. Установите Python 3.8+ и добавьте его в системный PATH.
  pause
  exit /b 1
)

REM Создать venv, если его нет
IF NOT EXIST "%VENV_DIR%\Scripts\activate.bat" (
  echo Виртуальное окружение не найдено — создаю "%VENV_DIR%"...
  python -m venv "%VENV_DIR%"
  IF ERRORLEVEL 1 (
    echo Ошибка: не удалось создать виртуальное окружение.
    pause
    exit /b 1
  )
)

REM Активировать venv
call "%VENV_DIR%\Scripts\activate.bat"
IF ERRORLEVEL 1 (
  echo Ошибка: не удалось активировать виртуальное окружение.
  pause
  exit /b 1
)

REM Обновить pip и установить зависимости если requirements.txt есть
python -m pip install --upgrade pip
IF EXIST requirements.txt (
  echo Установка зависимостей из requirements.txt...
  pip install -r requirements.txt
  IF ERRORLEVEL 1 (
    echo Предупреждение: проблемы при установке зависимостей. Проверьте requirements.txt.
    REM Продолжаем попытку запустить игру
  )
)

REM Запуск игры
IF EXIST snake_game.py (
  echo Запуск snake_game.py...
  python snake_game.py
) ELSE (
  echo Ошибка: файл snake_game.py не найден в текущей папке.
  pause
)

REM Деактивация окружения (опционально)
REM deactivate

ENDLOCAL
