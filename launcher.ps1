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
$label.Location = New-Object System.Drawing.Point(20,20)
$label.Size = New-Object System.Drawing.Size(360,20)
$label.Text = "Initializing..."
$label.TextAlign = [System.Drawing.ContentAlignment]::MiddleCenter
$form.Controls.Add($label)

$progressBar = New-Object System.Windows.Forms.ProgressBar
$progressBar.Location = New-Object System.Drawing.Point(20,50)
$progressBar.Size = New-Object System.Drawing.Size(360,30)
$progressBar.Style = "Continuous"
$form.Controls.Add($progressBar)

$percentLabel = New-Object System.Windows.Forms.Label
$percentLabel.Location = New-Object System.Drawing.Point(20,90)
$percentLabel.Size = New-Object System.Drawing.Size(360,20)
$percentLabel.Text = "0%"
$percentLabel.TextAlign = [System.Drawing.ContentAlignment]::MiddleCenter
$form.Controls.Add($percentLabel)

# Функция обновления прогресса
function Update-Progress {
    param($value, $status)
    $progressBar.Value = $value
    $percentLabel.Text = "$value%"
    $label.Text = $status
    [System.Windows.Forms.Application]::DoEvents()
}

# Основной процесс
$form.Add_Shown({
    try {
        # Проверяем Docker
        Update-Progress 10 "Checking Docker..."
        $dockerCheck = docker ps 2>&1
        if ($LASTEXITCODE -ne 0) {
            Update-Progress 100 "Error: Docker is not running!"
            Start-Sleep -Seconds 2
            $form.Close()
            return
        }

        # Проверяем docker-compose
        Update-Progress 20 "Checking docker-compose..."
        $composeCheck = docker-compose version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Update-Progress 100 "Error: docker-compose not found!"
            Start-Sleep -Seconds 2
            $form.Close()
            return
        }

        # Проверяем наличие необходимых файлов
        Update-Progress 30 "Checking files..."
        if (-not (Test-Path "docker-compose.yml")) {
            Update-Progress 100 "Error: docker-compose.yml not found!"
            Start-Sleep -Seconds 2
            $form.Close()
            return
        }

        # Проверяем, не запущен ли уже контейнер
        Update-Progress 40 "Checking container status..."
        $containerCheck = docker ps --filter "name=network-test" --format "{{.Names}}"
        if ($containerCheck -eq "network-test") {
            Update-Progress 50 "Stopping existing container..."
            docker-compose down
            Start-Sleep -Seconds 2
        }

        # Запускаем контейнер
        Update-Progress 60 "Starting Docker container..."
        $containerStart = docker-compose up -d 2>&1
        if ($LASTEXITCODE -ne 0) {
            Update-Progress 100 "Error: Failed to start container!"
            Start-Sleep -Seconds 2
            $form.Close()
            return
        }

        # Ждем запуска контейнера
        Update-Progress 70 "Waiting for container to start..."
        Start-Sleep -Seconds 5

        # Запускаем GUI
        Update-Progress 80 "Starting GUI..."
        $form.Close()
        
        # Запускаем GUI напрямую через docker exec
        $process = Start-Process "cmd.exe" -ArgumentList "/c docker exec -e DISPLAY=host.docker.internal:0.0 network-test python3 gui.py" -NoNewWindow -PassThru -Wait
        
        # Останавливаем контейнер после закрытия GUI
        docker-compose down
    }
    catch {
        Update-Progress 100 "Error: $($_.Exception.Message)"
        Start-Sleep -Seconds 2
        $form.Close()
    }
})

# Показываем форму
$form.ShowDialog() 