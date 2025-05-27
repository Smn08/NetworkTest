# Создаем форму
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$form = New-Object System.Windows.Forms.Form
$form.Text = "Network Testing Tool Launcher"
$form.Size = New-Object System.Drawing.Size(400,200)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false
$form.MinimizeBox = $false

# Создаем элементы управления
$label = New-Object System.Windows.Forms.Label
$label.Location = New-Object System.Drawing.Point(10,20)
$label.Size = New-Object System.Drawing.Size(360,20)
$label.Text = "Инициализация..."
$label.TextAlign = [System.Drawing.ContentAlignment]::MiddleCenter
$form.Controls.Add($label)

$progressBar = New-Object System.Windows.Forms.ProgressBar
$progressBar.Location = New-Object System.Drawing.Point(10,50)
$progressBar.Size = New-Object System.Drawing.Size(360,20)
$form.Controls.Add($progressBar)

$percentLabel = New-Object System.Windows.Forms.Label
$percentLabel.Location = New-Object System.Drawing.Point(10,80)
$percentLabel.Size = New-Object System.Drawing.Size(360,20)
$percentLabel.Text = "0%"
$percentLabel.TextAlign = [System.Drawing.ContentAlignment]::MiddleCenter
$form.Controls.Add($percentLabel)

# Функция обновления прогресса
function Update-Progress {
    param(
        [int]$Value,
        [string]$Status
    )
    $progressBar.Value = $Value
    $label.Text = $Status
    $percentLabel.Text = "$Value%"
    [System.Windows.Forms.Application]::DoEvents()
}

# Основной процесс
$form.Add_Shown({
    try {
        # Проверяем наличие docker-compose
        Update-Progress -Value 10 -Status "Проверка docker-compose..."
        if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
            throw "docker-compose не найден"
        }

        # Проверяем наличие необходимых файлов
        Update-Progress -Value 20 -Status "Проверка файлов..."
        if (-not (Test-Path "..\docker\docker-compose.yml")) {
            throw "docker-compose.yml не найден"
        }
        if (-not (Test-Path "..\docker\Dockerfile")) {
            throw "Dockerfile не найден"
        }
        if (-not (Test-Path "..\src\gui.py")) {
            throw "gui.py не найден"
        }

        # Запускаем контейнер
        Update-Progress -Value 30 -Status "Запуск контейнера..."
        Set-Location "..\docker"
        docker-compose up -d
        if ($LASTEXITCODE -ne 0) {
            throw "Ошибка запуска контейнера"
        }

        # Ждем запуска контейнера
        Update-Progress -Value 50 -Status "Ожидание запуска контейнера..."
        Start-Sleep -Seconds 5

        # Запускаем GUI
        Update-Progress -Value 70 -Status "Запуск графического интерфейса..."
        docker exec -e DISPLAY=host.docker.internal:0.0 network-test python3 /app/src/gui.py
        if ($LASTEXITCODE -ne 0) {
            throw "Ошибка запуска GUI"
        }

        # Завершение
        Update-Progress -Value 100 -Status "Готово!"
        Start-Sleep -Seconds 1
        $form.Close()
    }
    catch {
        $label.Text = "Ошибка: $_"
        $label.ForeColor = [System.Drawing.Color]::Red
        Start-Sleep -Seconds 5
        $form.Close()
    }
})

# Показываем форму
$form.ShowDialog() 