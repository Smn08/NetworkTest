#!/bin/bash

# Проверяем наличие необходимых утилит
command -v hping3 >/dev/null 2>&1 || { echo "{\"error\": \"hping3 не установлен\", \"details\": \"Установите его командой: apt-get install hping3\"}"; exit 1; }

# Получаем параметры
TARGET=$1
PORT=$2
DURATION=$3
THREADS=$4

# Проверяем параметры
if [ -z "$TARGET" ] || [ -z "$PORT" ] || [ -z "$DURATION" ] || [ -z "$THREADS" ]; then
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

# Функция для отправки TCP ACK пакетов
send_tcp_ack_packets() {
    local target=$1
    local port=$2
    local duration=$3
    local thread_id=$4
    local start_time=$(date +%s)
    local packets_sent=0
    local errors=0
    
    while [ $(($(date +%s) - start_time)) -lt $duration ]; do
        if hping3 -A -p $port $target > /dev/null 2>&1; then
            packets_sent=$((packets_sent + 1))
        else
            errors=$((errors + 1))
        fi
    done
    
    echo "{\"thread_id\": $thread_id, \"packets_sent\": $packets_sent, \"errors\": $errors, \"duration\": $duration}"
}

# Создаем временный файл для результатов
TEMP_FILE=$(mktemp)

# Запускаем тест в указанном количестве потоков
for ((i=0; i<THREADS; i++)); do
    send_tcp_ack_packets "$TARGET" "$PORT" "$DURATION" "$i" >> "$TEMP_FILE" &
    pids[$i]=$!
done

# Ждем завершения всех потоков
for pid in "${pids[@]}"; do
    wait $pid
done

# Собираем результаты в JSON массив
echo "{\"test_info\": {\"target\": \"$TARGET\", \"port\": $PORT, \"duration\": $DURATION, \"threads\": $THREADS}, \"results\": ["
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