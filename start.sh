#!/bin/bash
#
# Завершение скрипта при любой ошибке
set -e

# Функция обработки ошибок
on_error() {
    echo "Произошла ошибка. Нажмите Enter, чтобы выйти..."
    read
}

# Установка ловушки на ошибки
trap 'on_error' ERR

# Ваш код
echo "Запуск..."

# Exit early on errors
set -eu

# Python buffers stdout. Without this, you won't see what you "print" in the Activity Logs
export PYTHONUNBUFFERED=true

# Install Python 3 virtual env
VIRTUALENV=./venv

if [ ! -d $VIRTUALENV ]; then
  python3 -m venv $VIRTUALENV
fi

# Install pip into virtual environment
if [ ! -f $VIRTUALENV/bin/pip ]; then
  curl --silent --show-error --retry 5 https://bootstrap.pypa.io/pip/3.7/get-pip.py | $VIRTUALENV/bin/python
fi

# Install the requirements
$VIRTUALENV/bin/pip install -r requirements.txt

# Run your glorious application
$VIRTUALENV/bin/python3 server.py

some_command # Если здесь произойдёт ошибка, сработает trap

echo "Скрипт завершён успешно. Нажмите Enter, чтобы выйти..."
read
