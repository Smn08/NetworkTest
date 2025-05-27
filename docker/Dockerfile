FROM ubuntu:20.04

# Установка Python и необходимых пакетов
RUN apt-get update && apt-get install -y \
    python3.8 \
    python3-pip \
    python3-dev \
    mesa-utils \
    mesa-va-drivers \
    mesa-vdpau-drivers \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libglu1-mesa \
    libglu1-mesa-dev \
    libgl1-mesa-dev \
    libgl1 \
    libgl1-mesa-swx11 \
    libgl1-mesa-swrast \
    x11-apps \
    x11-utils \
    x11-xserver-utils \
    xauth \
    xvfb \
    libx11-dev \
    libx11-xcb-dev \
    libxcb1-dev \
    libxcb-glx0-dev \
    libxcb-icccm4-dev \
    libxcb-image0-dev \
    libxcb-keysyms1-dev \
    libxcb-randr0-dev \
    libxcb-render-util0-dev \
    libxcb-shape0-dev \
    libxcb-sync-dev \
    libxcb-xfixes0-dev \
    libxcb-xinerama0-dev \
    libxcb-xkb-dev \
    libxkbcommon-x11-dev \
    gcc \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY src/requirements.txt .

# Установка зависимостей Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY src/ /app/src/
COPY config/ /app/config/

# Установка переменных окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV QT_DEBUG_PLUGINS=1
ENV QT_X11_NO_MITSHM=1
ENV QT_STYLE_OVERRIDE=Fusion
ENV QT_QPA_PLATFORM=xcb
ENV LIBGL_ALWAYS_INDIRECT=1
ENV DISPLAY=host.docker.internal:0.0
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:/usr/lib:/usr/local/lib:${LD_LIBRARY_PATH}

# Создание символических ссылок для библиотек OpenGL
RUN ln -sf /usr/lib/x86_64-linux-gnu/libGL.so.1 /usr/lib/libGL.so.1 && \
    ln -sf /usr/lib/x86_64-linux-gnu/libGL.so /usr/lib/libGL.so && \
    ln -sf /usr/lib/x86_64-linux-gnu/libGLESv2.so.2 /usr/lib/libGLESv2.so.2 && \
    ln -sf /usr/lib/x86_64-linux-gnu/libGLESv2.so /usr/lib/libGLESv2.so && \
    ln -sf /usr/lib/x86_64-linux-gnu/libEGL.so.1 /usr/lib/libEGL.so.1 && \
    ln -sf /usr/lib/x86_64-linux-gnu/libEGL.so /usr/lib/libEGL.so

# Обновление кэша библиотек
RUN ldconfig

# Запуск приложения
CMD ["python3", "src/gui.py"] 