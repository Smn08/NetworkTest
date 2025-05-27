import sys
import os
import signal
import psutil
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QLabel, QLineEdit, QPushButton,
                           QTextEdit, QTabWidget, QGroupBox, QFormLayout,
                           QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox,
                           QMessageBox, QSystemTrayIcon, QMenu, QAction,
                           QSplitter, QTableWidget, QTableWidgetItem, QHeaderView,
                           QProgressBar, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QTimer, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QFontDatabase, QColor
from console import DDoSConsole
import json
from datetime import datetime

class AttackWorker(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    stats_updated = pyqtSignal(dict)
    server_stats = pyqtSignal(dict)  # Новый сигнал для статистики по серверам

    def __init__(self, console, servers, attack_params, attack_type, duration):
        super().__init__()
        self.console = console
        self.servers = servers
        self.attack_params = attack_params
        self.attack_type = attack_type
        self.duration = duration
        self.is_running = True
        self.start_time = None
        self.server_stats_data = {}

    def run(self):
        try:
            self.start_time = datetime.now()
            self.console.execute_attack(self.servers, self.attack_params, 
                                      self.attack_type, self.duration)
            
            # Отправляем статистику каждые 5 секунд
            while self.is_running:
                elapsed = (datetime.now() - self.start_time).total_seconds()
                if elapsed >= self.duration:
                    break
                    
                # Обновляем общую статистику
                stats = {
                    'elapsed': elapsed,
                    'remaining': self.duration - elapsed,
                    'progress': (elapsed / self.duration) * 100
                }
                self.stats_updated.emit(stats)
                self.progress.emit(int(stats['progress']))

                # Обновляем статистику по серверам
                for server in self.servers:
                    if server['status'] == 'online':
                        server_stats = {
                            'name': server['name'],
                            'status': 'running',
                            'progress': int((elapsed / self.duration) * 100),
                            'requests': self.console.get_server_stats(server['host'])
                        }
                        self.server_stats_data[server['name']] = server_stats
                
                self.server_stats.emit(self.server_stats_data)
                self.sleep(5)
                
            self.finished.emit(True, "Атака успешно завершена")
        except Exception as e:
            self.finished.emit(False, str(e))

    def stop(self):
        self.is_running = False
        self.console.stop_attack()  # Добавляем вызов метода остановки атаки в консоли

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.console = DDoSConsole()
        self.attack_worker = None
        self.attack_history = []
        self.init_ui()
        self.setup_tray()
        self.load_settings()
        
        # Устанавливаем обработчик сигналов
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения"""
        self.cleanup_and_exit()

    def cleanup_and_exit(self):
        """Очистка ресурсов и завершение работы"""
        try:
            # Останавливаем все атаки
            if self.attack_worker is not None:
                self.attack_worker.stop()
                self.attack_worker.terminate()
                self.attack_worker.wait()
                self.attack_worker = None

            # Останавливаем таймер
            if hasattr(self, 'stats_timer'):
                self.stats_timer.stop()

            # Сохраняем настройки
            self.save_settings()

            # Очищаем консоль
            if hasattr(self, 'console'):
                self.console.cleanup()

            # Завершаем все дочерние процессы
            current_process = psutil.Process()
            children = current_process.children(recursive=True)
            for child in children:
                try:
                    child.kill()  # Используем kill вместо terminate
                except:
                    pass

            # Принудительно завершаем процесс
            os.kill(os.getpid(), signal.SIGKILL)  # Используем SIGKILL вместо _exit
        except:
            os.kill(os.getpid(), signal.SIGKILL)

    def init_ui(self):
        self.setWindowTitle('Network Testing Tool')
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QPushButton {
                background-color: #0d47a1;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:disabled {
                background-color: #424242;
            }
            QLineEdit, QTextEdit, QSpinBox {
                background-color: #424242;
                color: white;
                border: 1px solid #616161;
                padding: 3px;
            }
            QTabWidget::pane {
                border: 1px solid #616161;
            }
            QTabBar::tab {
                background-color: #424242;
                color: white;
                padding: 5px 10px;
            }
            QTabBar::tab:selected {
                background-color: #0d47a1;
            }
            QGroupBox {
                border: 1px solid #616161;
                margin-top: 10px;
            }
            QGroupBox::title {
                color: white;
            }
            QTableWidget {
                background-color: #424242;
                color: white;
                gridline-color: #616161;
            }
            QHeaderView::section {
                background-color: #0d47a1;
                color: white;
                padding: 5px;
            }
            QProgressBar {
                border: 1px solid #616161;
                border-radius: 3px;
                text-align: center;
                background-color: #424242;
            }
            QProgressBar::chunk {
                background-color: #0d47a1;
            }
            QListWidget {
                background-color: #424242;
                color: white;
                border: 1px solid #616161;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #0d47a1;
            }
        """)

        # Создаем центральный виджет и главный layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Создаем сплиттер для разделения на две части
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Левая панель с вкладками
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        tabs = QTabWidget()
        left_layout.addWidget(tabs)

        # Правая панель с логами и статистикой
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Группа логов
        log_group = QGroupBox("Логи")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        right_layout.addWidget(log_group)
        
        # Группа статистики
        stats_group = QGroupBox("Статистика")
        stats_layout = QVBoxLayout(stats_group)
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(3)
        self.stats_table.setHorizontalHeaderLabels(['Метрика', 'Значение', 'Изменение'])
        stats_layout.addWidget(self.stats_table)
        right_layout.addWidget(stats_group)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 400])

        # Вкладка серверов
        servers_tab = QWidget()
        servers_layout = QVBoxLayout(servers_tab)
        
        # Таблица серверов
        self.servers_table = QTableWidget()
        self.servers_table.setColumnCount(7)  # Добавляем колонку для выбора
        self.servers_table.setHorizontalHeaderLabels(['Выбрать', 'Имя', 'IP', 'Порт', 'Пользователь', 'Статус', 'Задержка'])
        self.servers_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.servers_table.customContextMenuRequested.connect(self.show_server_context_menu)
        servers_layout.addWidget(self.servers_table)

        # Форма добавления сервера
        add_server_group = QGroupBox("Добавить сервер")
        add_server_layout = QVBoxLayout(add_server_group)
        
        form_layout = QHBoxLayout()
        self.server_name_input = QLineEdit()
        self.server_name_input.setPlaceholderText('Имя сервера')
        self.server_ip_input = QLineEdit()
        self.server_ip_input.setPlaceholderText('IP адрес')
        self.server_port_input = QSpinBox()
        self.server_port_input.setRange(1, 65535)
        self.server_port_input.setValue(22)
        self.server_user_input = QLineEdit()
        self.server_user_input.setPlaceholderText('Пользователь')
        self.server_pass_input = QLineEdit()
        self.server_pass_input.setPlaceholderText('Пароль')
        self.server_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addWidget(self.server_name_input)
        form_layout.addWidget(self.server_ip_input)
        form_layout.addWidget(self.server_port_input)
        form_layout.addWidget(self.server_user_input)
        form_layout.addWidget(self.server_pass_input)
        
        add_server_btn = QPushButton('Добавить сервер')
        add_server_btn.clicked.connect(self.add_server)
        
        add_server_layout.addLayout(form_layout)
        add_server_layout.addWidget(add_server_btn)
        
        servers_layout.addWidget(add_server_group)
        tabs.addTab(servers_tab, 'Серверы')

        # Вкладка атак
        attacks_tab = QWidget()
        attacks_layout = QVBoxLayout(attacks_tab)
        
        # Выбор типа атаки
        attack_type_group = QGroupBox("Тип атаки")
        attack_type_layout = QHBoxLayout(attack_type_group)
        
        self.attack_category = QComboBox()
        self.attack_category.addItems(self.console.attack_categories.values())
        self.attack_category.currentIndexChanged.connect(self.update_attack_types)
        
        self.attack_type = QComboBox()
        
        attack_type_layout.addWidget(QLabel('Категория:'))
        attack_type_layout.addWidget(self.attack_category)
        attack_type_layout.addWidget(QLabel('Тип атаки:'))
        attack_type_layout.addWidget(self.attack_type)
        
        attacks_layout.addWidget(attack_type_group)
        
        # Параметры атаки
        attack_params_group = QGroupBox("Параметры атаки")
        attack_params_layout = QVBoxLayout(attack_params_group)
        
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText('Цель атаки (IP или домен)')
        attack_params_layout.addWidget(self.target_input)
        
        params_row = QWidget()
        params_row_layout = QHBoxLayout(params_row)
        
        self.threads_input = QSpinBox()
        self.threads_input.setRange(1, 1000)
        self.threads_input.setValue(100)
        self.threads_input.setPrefix('Потоки: ')
        
        self.duration_input = QSpinBox()
        self.duration_input.setRange(1, 3600)
        self.duration_input.setValue(60)
        self.duration_input.setPrefix('Длительность (сек): ')
        
        self.auto_retry = QCheckBox('Автоматический перезапуск')
        self.auto_retry.setChecked(True)
        
        params_row_layout.addWidget(self.threads_input)
        params_row_layout.addWidget(self.duration_input)
        params_row_layout.addWidget(self.auto_retry)
        
        attack_params_layout.addWidget(params_row)
        attacks_layout.addWidget(attack_params_group)
        
        # Кнопки управления атакой
        attack_controls = QWidget()
        attack_controls_layout = QHBoxLayout(attack_controls)
        
        self.start_attack_btn = QPushButton('Запустить атаку')
        self.start_attack_btn.clicked.connect(self.start_attack)
        self.stop_attack_btn = QPushButton('Остановить атаку')
        self.stop_attack_btn.clicked.connect(self.stop_attack)
        self.stop_attack_btn.setEnabled(False)
        
        attack_controls_layout.addWidget(self.start_attack_btn)
        attack_controls_layout.addWidget(self.stop_attack_btn)
        
        attacks_layout.addWidget(attack_controls)
        
        # Прогресс атаки
        self.attack_progress = QProgressBar()
        attacks_layout.addWidget(self.attack_progress)
        
        tabs.addTab(attacks_tab, 'Атаки')

        # Вкладка мониторинга
        monitoring_tab = QWidget()
        monitoring_layout = QVBoxLayout(monitoring_tab)
        
        # Статистика серверов
        servers_stats_group = QGroupBox("Статистика серверов")
        servers_stats_layout = QVBoxLayout(servers_stats_group)
        self.servers_stats = QTableWidget()
        self.servers_stats.setColumnCount(5)
        self.servers_stats.setHorizontalHeaderLabels(['Сервер', 'Статус', 'Задержка', 'Ошибки', 'Прогресс'])
        servers_stats_layout.addWidget(self.servers_stats)
        monitoring_layout.addWidget(servers_stats_group)
        
        # Статистика атак
        attacks_stats_group = QGroupBox("Статистика атак")
        attacks_stats_layout = QVBoxLayout(attacks_stats_group)
        self.attacks_stats = QTableWidget()
        self.attacks_stats.setColumnCount(6)
        self.attacks_stats.setHorizontalHeaderLabels(['ID', 'Тип', 'Сервер', 'Статус', 'Прогресс', 'Результат'])
        attacks_stats_layout.addWidget(self.attacks_stats)
        monitoring_layout.addWidget(attacks_stats_group)
        
        # История атак
        history_group = QGroupBox("История атак")
        history_layout = QVBoxLayout(history_group)
        self.history_list = QListWidget()
        history_layout.addWidget(self.history_list)
        monitoring_layout.addWidget(history_group)
        
        tabs.addTab(monitoring_tab, 'Мониторинг')

        # Обновляем список серверов
        self.update_servers_list()
        
        # Таймер для обновления статистики
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_server_stats)
        self.stats_timer.setInterval(5000)  # Устанавливаем интервал в 5 секунд
        self.stats_timer.setSingleShot(False)  # Таймер будет повторяться
        self.stats_timer.start()

    def setup_tray(self):
        """Настройка системного трея"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.png"))  # Добавьте иконку в проект
        
        # Создаем меню трея
        tray_menu = QMenu()
        show_action = QAction("Показать", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("Выход", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def load_settings(self):
        """Загрузка настроек"""
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    
                # Загружаем настройки интерфейса
                if 'window' in settings:
                    self.resize(settings['window']['width'], settings['window']['height'])
                    self.move(settings['window']['x'], settings['window']['y'])
                    
                # Загружаем последние использованные параметры
                if 'last_attack' in settings:
                    self.target_input.setText(settings['last_attack']['target'])
                    self.threads_input.setValue(settings['last_attack']['threads'])
                    self.duration_input.setValue(settings['last_attack']['duration'])
                
                # Загружаем историю атак
                if 'attack_history' in settings:
                    self.attack_history = settings['attack_history']
                    self.update_history_list()
        except Exception as e:
            self.log_message(f"Ошибка загрузки настроек: {str(e)}")

    def save_settings(self):
        """Сохранение настроек"""
        try:
            settings = {
                'window': {
                    'width': self.width(),
                    'height': self.height(),
                    'x': self.x(),
                    'y': self.y()
                },
                'last_attack': {
                    'target': self.target_input.text(),
                    'threads': self.threads_input.value(),
                    'duration': self.duration_input.value()
                },
                'attack_history': self.attack_history
            }
            
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            self.log_message(f"Ошибка сохранения настроек: {str(e)}")

    def show_server_context_menu(self, position):
        """Показ контекстного меню для сервера"""
        menu = QMenu()
        check_action = menu.addAction("Проверить статус")
        remove_action = menu.addAction("Удалить")
        
        action = menu.exec(self.servers_table.mapToGlobal(position))
        if action == check_action:
            self.check_selected_server()
        elif action == remove_action:
            self.remove_selected_server()

    def check_selected_server(self):
        """Проверка статуса выбранного сервера"""
        current_row = self.servers_table.currentRow()
        if current_row >= 0:
            server = self.console.servers[current_row]
            self.console.check_server_status(server['host'], server['port'])
            self.update_servers_list()

    def remove_selected_server(self):
        """Удаление выбранного сервера"""
        current_row = self.servers_table.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(self, 'Подтверждение',
                                       'Вы уверены, что хотите удалить этот сервер?',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.console.servers.pop(current_row)
                self.console.save_servers()
                self.update_servers_list()

    def update_servers_list(self):
        """Обновление списка серверов"""
        self.servers_table.setRowCount(0)
        for i, server in enumerate(self.console.servers):
            row = self.servers_table.rowCount()
            self.servers_table.insertRow(row)
            
            # Добавляем чекбокс для выбора сервера
            checkbox = QTableWidgetItem()
            checkbox.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            checkbox.setCheckState(Qt.CheckState.Unchecked)
            self.servers_table.setItem(row, 0, checkbox)
            
            self.servers_table.setItem(row, 1, QTableWidgetItem(server['name']))
            self.servers_table.setItem(row, 2, QTableWidgetItem(server['host']))
            self.servers_table.setItem(row, 3, QTableWidgetItem(str(server['port'])))
            self.servers_table.setItem(row, 4, QTableWidgetItem(server['username']))
            self.servers_table.setItem(row, 5, QTableWidgetItem(server['status']))
            
            # Добавляем задержку, если есть
            if 'stats' in server and 'latency' in server['stats']:
                self.servers_table.setItem(row, 6, QTableWidgetItem(f"{server['stats']['latency']:.2f} мс"))

    def get_selected_servers(self):
        """Получение выбранных серверов"""
        selected_servers = []
        for row in range(self.servers_table.rowCount()):
            if self.servers_table.item(row, 0).checkState() == Qt.CheckState.Checked:
                server = self.console.servers[row]
                if server['status'] == 'online':
                    selected_servers.append(server)
        return selected_servers

    def update_attack_types(self):
        """Обновление списка типов атак"""
        category = str(self.attack_category.currentIndex() + 1)
        self.attack_type.clear()
        self.attack_type.addItems(self.console.attack_types[category].values())

    def add_server(self):
        """Добавление нового сервера"""
        name = self.server_name_input.text()
        ip = self.server_ip_input.text()
        port = self.server_port_input.value()
        username = self.server_user_input.text()
        password = self.server_pass_input.text()

        if not all([name, ip, username, password]):
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля')
            return

        server = {
            'name': name,
            'host': ip,
            'port': port,
            'username': username,
            'password': password,
            'status': 'offline'
        }

        self.console.servers.append(server)
        self.console.save_servers()
        self.update_servers_list()

        # Очищаем поля ввода
        self.server_name_input.clear()
        self.server_ip_input.clear()
        self.server_port_input.setValue(22)
        self.server_user_input.clear()
        self.server_pass_input.clear()

    def start_attack(self):
        """Запуск атаки"""
        selected_servers = self.get_selected_servers()
        if not selected_servers:
            QMessageBox.warning(self, 'Ошибка', 'Выберите хотя бы один сервер')
            return

        target = self.target_input.text()
        if not target:
            QMessageBox.warning(self, 'Ошибка', 'Укажите цель атаки')
            return

        category = str(self.attack_category.currentIndex() + 1)
        attack_type = str(self.attack_type.currentIndex() + 1)
        attack_id = f"{category}_{attack_type}"

        attack_params = {
            'target': target,
            'threads': str(self.threads_input.value()),
            'timeout': '5'
        }

        duration = self.duration_input.value()

        # Запускаем атаку в отдельном потоке
        self.attack_worker = AttackWorker(
            self.console,
            selected_servers,
            attack_params,
            attack_id,
            duration
        )
        self.attack_worker.progress.connect(self.update_progress)
        self.attack_worker.status.connect(self.update_status)
        self.attack_worker.finished.connect(self.attack_finished)
        self.attack_worker.stats_updated.connect(self.update_attack_stats)
        self.attack_worker.server_stats.connect(self.update_server_stats)
        self.attack_worker.start()

        self.start_attack_btn.setEnabled(False)
        self.stop_attack_btn.setEnabled(True)
        self.attack_progress.setValue(0)
        
        # Добавляем атаку в историю
        attack_info = {
            'id': attack_id,
            'target': target,
            'servers': [s['name'] for s in selected_servers],
            'start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'running'
        }
        self.attack_history.append(attack_info)
        self.update_history_list()
        
        # Сохраняем настройки
        self.save_settings()

    def stop_attack(self):
        """Остановка атаки"""
        if self.attack_worker is not None:
            self.attack_worker.stop()
            self.attack_worker.terminate()
            self.attack_worker.wait()
            self.attack_worker = None
            self.attack_finished(False, "Атака остановлена пользователем")

    def update_progress(self, value):
        """Обновление прогресса атаки"""
        self.attack_progress.setValue(value)

    def update_status(self, status):
        """Обновление статуса атаки"""
        self.log_message(status)

    def update_attack_stats(self):
        """Обновление статистики атак"""
        try:
            if not self.isVisible():  # Проверяем, видимо ли окно
                return

            self.attacks_stats.setRowCount(0)
            for attack in self.console.attack_monitor.attacks:
                row = self.attacks_stats.rowCount()
                self.attacks_stats.insertRow(row)
                self.attacks_stats.setItem(row, 0, QTableWidgetItem(attack['id']))
                self.attacks_stats.setItem(row, 1, QTableWidgetItem(attack['type']))
                self.attacks_stats.setItem(row, 2, QTableWidgetItem(attack['server']))
                self.attacks_stats.setItem(row, 3, QTableWidgetItem(attack['status']))
                self.attacks_stats.setItem(row, 4, QTableWidgetItem(f"{attack['progress']}%"))
                self.attacks_stats.setItem(row, 5, QTableWidgetItem(attack.get('result', '')))
        except Exception as e:
            print(f"Error in update_attack_stats: {e}")

    def update_server_stats(self):
        """Обновление статистики серверов"""
        try:
            if not self.isVisible():  # Проверяем, видимо ли окно
                return

            self.servers_stats.setRowCount(0)
            for server_name, server_stats in self.console.server_stats.items():
                row = self.servers_stats.rowCount()
                self.servers_stats.insertRow(row)
                
                self.servers_stats.setItem(row, 0, QTableWidgetItem(server_name))
                self.servers_stats.setItem(row, 1, QTableWidgetItem(server_stats['status']))
                
                # Добавляем задержку
                if 'latency' in server_stats:
                    latency = server_stats['latency']
                    self.servers_stats.setItem(row, 2, QTableWidgetItem(f"{latency:.2f} мс"))
                
                # Добавляем ошибки
                if 'errors' in server_stats:
                    errors = server_stats['errors']
                    self.servers_stats.setItem(row, 3, QTableWidgetItem(f"{errors}"))
                
                # Добавляем прогресс-бар
                progress = QProgressBar()
                progress.setValue(server_stats.get('progress', 0))
                self.servers_stats.setCellWidget(row, 4, progress)
        except Exception as e:
            print(f"Error updating stats: {e}")

    def update_history_list(self):
        """Обновление списка истории атак"""
        self.history_list.clear()
        for attack in reversed(self.attack_history):
            item = QListWidgetItem(
                f"[{attack['start_time']}] {attack['id']} -> {attack['target']} "
                f"({', '.join(attack['servers'])}) - {attack['status']}"
            )
            if attack['status'] == 'running':
                item.setForeground(QColor('#4CAF50'))  # Зеленый для активных
            elif attack['status'] == 'completed':
                item.setForeground(QColor('#2196F3'))  # Синий для завершенных
            else:
                item.setForeground(QColor('#F44336'))  # Красный для ошибок
            self.history_list.addItem(item)

    def attack_finished(self, success, message):
        """Обработка завершения атаки"""
        self.start_attack_btn.setEnabled(True)
        self.stop_attack_btn.setEnabled(False)
        self.attack_progress.setValue(100 if success else 0)
        self.log_message(message)
        
        # Обновляем статус в истории
        if self.attack_history:
            self.attack_history[-1]['status'] = 'completed' if success else 'failed'
            self.update_history_list()
        
        # Автоматический перезапуск
        if success and self.auto_retry.isChecked():
            self.start_attack()

    def log_message(self, message):
        """Добавление сообщения в лог"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        reply = QMessageBox.question(self, 'Подтверждение',
                                   'Вы уверены, что хотите выйти?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.cleanup_and_exit()
        else:
            event.ignore()

    def update_stats(self):
        """Обновление статистики"""
        try:
            if not self.isVisible():  # Проверяем, видимо ли окно
                return

            if self.attack_worker is not None and self.attack_worker.isRunning():
                self.console.update_server_status(silent=True)
                self.update_servers_list()
                self.update_attack_stats()
        except Exception as e:
            print(f"Error in update_stats: {e}")

    def showEvent(self, event):
        """Обработчик показа окна"""
        super().showEvent(event)
        # Запускаем таймер только когда окно видимо
        if hasattr(self, 'stats_timer'):
            self.stats_timer.start()

    def hideEvent(self, event):
        """Обработчик скрытия окна"""
        super().hideEvent(event)
        # Останавливаем таймер когда окно скрыто
        if hasattr(self, 'stats_timer'):
            self.stats_timer.stop()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    
    # Устанавливаем обработчик для корректного завершения
    app.aboutToQuit.connect(window.cleanup_and_exit)
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 