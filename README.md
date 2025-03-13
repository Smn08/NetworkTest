# Web Testing Console

Консольное приложение для управления DDoS атаками с поддержкой множества серверов и различных типов атак.

## Возможности

- Управление множеством серверов
- Шифрование конфигураций серверов
- Поддержка различных типов атак
- Логирование всех действий
- Тестовые атаки для проверки доступности целей

## Типы атак

### Тестовые атаки (категория 5)
1. TCP Test (5_3) - проверка доступности TCP порта
   - Параметры: `--port`, `--timeout`, `--threads`, `--test_duration`
   - Пример: `python attack.py 5_3 1.1.1.1 --port 80 --timeout 5 --threads 1 --test_duration 10`

2. HTTP Test (5_4) - проверка доступности HTTP сервера
   - Параметры: `--port`, `--timeout`, `--threads`, `--test_duration`
   - Пример: `python attack.py 5_4 1.1.1.1 --port 80 --timeout 5 --threads 1 --test_duration 10`

3. DNS Test (5_5) - проверка работы DNS сервера
   - Параметры: `--port`, `--timeout`, `--threads`, `--test_duration`
   - Пример: `python attack.py 5_5 1.1.1.1 --port 53 --timeout 5 --threads 1 --test_duration 10`

### Флуд атаки (категория 1)
1. UDP Flood (1_1)
2. TCP SYN Flood (1_2)
3. HTTP Flood (1_3)
4. ICMP Flood (1_4)
5. TCP ACK Flood (1_10)
6. TCP RST Flood (1_11)
7. TCP Window Flood (1_12)
8. TCP Fragment Flood (1_13)
9. TCP XMAS Flood (1_14)
10. TCP NULL Flood (1_15)
11. TCP FIN Flood (1_16)

### Амплификация атаки (категория 2)
1. DNS Amplification (2_1)
2. NTP Amplification (2_2)
3. Memcached Amplification (2_3)
4. SSDP Amplification (2_4)

### Медленные атаки (категория 3)
1. Slowloris (3_1)

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

3. Настройте серверы в файле `servers.json`:
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
python ddos_console.py
```

2. Выберите тип атаки и введите параметры
3. Выберите серверы для атаки
4. Дождитесь завершения атаки

## Безопасность

- Все пароли серверов шифруются
- Логи сохраняются в директории `logs/`
- Поддерживается SSL/TLS для безопасного соединения

## Требования

- Python 3.6+
- Linux/Unix серверы для атак
- Доступ к интернету

## Лицензия

MIT License