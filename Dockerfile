# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /usr/src/app

# Копируем файлы зависимостей
COPY requirements.txt ./

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем все файлы проекта
COPY . .

# Определяем команду для запуска бота
#CMD ["python3", "main.py"]