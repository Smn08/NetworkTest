# Web Testing Console

Консольное приложение для управления Web тестированием с поддержкой множества серверов и различных типов тестов.

## Возможности

- Управление множеством серверов
- Шифрование конфигураций серверов
- Поддержка различных типов тестов
- Логирование всех действий
- Тесты для проверки доступности целей

## Типы тестов

### 1. Флуд тесты
1. UDP Flood (1_1)
   - Отправка UDP пакетов с случайным размером данных
   - Случайный интервал между пакетами
   - Фрагментация пакетов
   - Параметры: `--port`, `--threads`, `--duration`

2. TCP SYN Flood (1_2)
   - Отправка TCP SYN пакетов
   - Случайный размер окна
   - Случайный TTL
   - Случайный тип сервиса
   - Параметры: `--port`, `--threads`, `--duration`

3. HTTP Flood (1_3)
   - Отправка HTTP запросов
   - Различные HTTP методы (GET, POST, HEAD и др.)
   - Случайные пути запросов
   - Реалистичные заголовки
   - Параметры: `--port`, `--threads`, `--duration`

4. ICMP Flood (1_4)
   - Отправка ICMP пакетов
   - Различные типы ICMP
   - Случайный размер данных
   - Случайный интервал
   - Параметры: `--threads`, `--duration`

### 2. Амплификация тесты
1. DNS Amplification (2_1)
   - Отправка DNS запросов типа ANY
   - Использование открытых DNS серверов
   - Параметры: `--port`, `--threads`, `--duration`

2. NTP Amplification (2_2)
   - Отправка NTP запросов типа monlist
   - Использование открытых NTP серверов
   - Параметры: `--port`, `--threads`, `--duration`

3. Memcached Amplification (2_3)
   - Отправка Memcached запросов
   - Использование открытых Memcached серверов
   - Параметры: `--port`, `--threads`, `--duration`

4. SSDP Amplification (2_4)
   - Отправка SSDP M-SEARCH запросов
   - Использование открытых SSDP серверов
   - Параметры: `--port`, `--threads`, `--duration`

### 3. Медленные тесты
1. Slowloris (3_1)
   - Медленное открытие HTTP соединений
   - Случайное количество сокетов
   - Настраиваемые таймауты
   - Параметры: `--port`, `--sockets`, `--timeout`, `--duration`

### 4. TCP тесты
1. TCP ACK Flood (4_1)
   - Отправка TCP ACK пакетов
   - Случайный размер окна
   - Случайный TTL
   - Параметры: `--port`, `--threads`, `--duration`

2. TCP RST Flood (4_2)
   - Отправка TCP RST пакетов
   - Случайный размер окна
   - Случайный TTL
   - Параметры: `--port`, `--threads`, `--duration`

3. TCP Window Flood (4_3)
   - Отправка TCP пакетов с большим размером окна
   - Случайный TTL
   - Параметры: `--port`, `--threads`, `--duration`

4. TCP Fragment Flood (4_4)
   - Отправка фрагментированных TCP пакетов
   - Случайный размер фрагментов
   - Случайные флаги фрагментации
   - Параметры: `--port`, `--threads`, `--duration`

5. TCP XMAS Flood (4_5)
   - Отправка TCP пакетов с установленными всеми флагами
   - Случайный размер окна
   - Случайный TTL
   - Параметры: `--port`, `--threads`, `--duration`

6. TCP NULL Flood (4_6)
   - Отправка TCP пакетов без флагов
   - Случайный размер окна
   - Случайный TTL
   - Параметры: `--port`, `--threads`, `--duration`

7. TCP FIN Flood (4_7)
   - Отправка TCP FIN пакетов
   - Случайный размер окна
   - Случайный TTL
   - Параметры: `--port`, `--threads`, `--duration`

### 5. Тестовые тесты
1. TCP Test (5_1)
   - Проверка доступности TCP порта
   - Параметры: `--port`, `--timeout`, `--threads`, `--test_duration`

2. HTTP Test (5_2)
   - Проверка доступности HTTP сервера
   - Параметры: `--port`, `--timeout`, `--threads`, `--test_duration`

3. DNS Test (5_3)
   - Проверка работы DNS сервера
   - Параметры: `--port`, `--timeout`, `--threads`, `--test_duration`

### 6. HTTP/HTTPS тесты
1. HTTP GET Flood (6_1)
   - Отправка HTTP GET запросов
   - Случайные пути и параметры
   - Параметры: `--port`, `--threads`, `--duration`

2. HTTP POST Flood (6_2)
   - Отправка HTTP POST запросов
   - Случайные данные в теле запроса
   - Параметры: `--port`, `--threads`, `--duration`

3. HTTPS Flood (6_3)
   - Отправка HTTPS запросов
   - Поддержка SSL/TLS
   - Параметры: `--port`, `--threads`, `--duration`

### 7. DNS тесты
1. DNS Query Flood (7_1)
   - Отправка DNS запросов
   - Различные типы запросов
   - Параметры: `--port`, `--threads`, `--duration`

2. DNS Response Flood (7_2)
   - Отправка DNS ответов
   - Случайные записи
   - Параметры: `--port`, `--threads`, `--duration`

### 8. Специальные тесты
1. Slow Read (8_1)
   - Медленное чтение HTTP ответов
   - Настраиваемые таймауты
   - Параметры: `--port`, `--timeout`, `--duration`

2. Slow POST (8_2)
   - Медленная отправка POST данных
   - Случайные размеры данных
   - Параметры: `--port`, `--timeout`, `--duration`

### 9. VoIP тесты
1. SIP Flood (9_1)
   - Отправка SIP запросов
   - Различные SIP методы
   - Параметры: `--port`, `--threads`, `--duration`

2. RTP Flood (9_2)
   - Отправка RTP пакетов
   - Случайные аудио данные
   - Параметры: `--port`, `--threads`, `--duration`

### 10. WiFi тесты
1. Deauth Flood (10_1)
   - Отправка deauth пакетов
   - Случайные MAC адреса
   - Параметры: `--interface`, `--duration`

2. Beacon Flood (10_2)
   - Отправка beacon пакетов
   - Случайные SSID
   - Параметры: `--interface`, `--duration`

### 11. Сетевые протоколы
1. ARP Flood (11_1)
   - Отправка ARP пакетов
   - Случайные MAC адреса
   - Параметры: `--interface`, `--duration`

2. DHCP Flood (11_2)
   - Отправка DHCP запросов
   - Случайные MAC адреса
   - Параметры: `--interface`, `--duration`

### 12. DoS тесты
1. Resource Exhaustion (12_1)
   - Исчерпание ресурсов системы
   - Открытие множества соединений
   - Параметры: `--port`, `--threads`, `--duration`

2. Process Kill (12_2)
   - Завершение процессов
   - Случайные сигналы
   - Параметры: `--process`, `--duration`

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/ddos-console.git
cd ddos-console
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Настройте серверы в файле `servers_template.json`:
```json
{
    "servers": [
        {
            "name": "server1",
            "ip": "1.2.3.4",
            "username": "user",
            "password": "encrypted_password"
        }
    ]
}
```

## Использование

1. Запустите консоль:
```bash
python console.py
```

2. Выберите тип теста и введите параметры
3. Выберите серверы для тестирования
4. Дождитесь завершения теста

## Безопасность

- Все пароли серверов шифруются
- Логи сохраняются в директории `logs/`
- Поддерживается SSL/TLS для безопасного соединения

## Требования

- Python 3.6+
- Linux/Unix серверы для тестирования
- Доступ к интернету