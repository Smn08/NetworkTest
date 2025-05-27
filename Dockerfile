# Используем Ubuntu как базовый образ
FROM ubuntu:22.04

# Установка переменных окружения
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=host.docker.internal:0.0
ENV QT_X11_NO_MITSHM=1
ENV QT_DEBUG_PLUGINS=1
ENV QT_STYLE_OVERRIDE=Fusion
ENV QT_QPA_PLATFORM=xcb

# Устанавливаем Python и необходимые системные зависимости
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    python3-pyqt5 \
    python3-pyqt5.qtwebengine \
    x11-apps \
    # X11 библиотеки
    libglib2.0-0 \
    libx11-6 \
    libxcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libxkbcommon0 \
    # Дополнительные библиотеки для Qt
    libxext6 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libsm6 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libnss3 \
    libcups2 \
    libxss1 \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем директорию для логов
RUN mkdir -p logs

# Создаем непривилегированного пользователя
RUN useradd -m -s /bin/bash appuser
RUN chown -R appuser:appuser /app
USER appuser

# Запускаем bash вместо GUI
CMD ["/bin/bash"] 