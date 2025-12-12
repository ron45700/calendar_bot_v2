Write-Host "🚀 Starting CalendarBot Environment..." -ForegroundColor Green

# Path to Python in venv
$PYTHON = ".\.venv\Scripts\python.exe"

# 1. Start Ngrok (Assuming ngrok is in system PATH)
Write-Host "1. Launching Ngrok (Port 5000)..."
Start-Process powershell -ArgumentList "ngrok http 5000"

# 2. Start Web Server
Write-Host "2. Launching Web Server..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '$PYTHON' server.py"

# 3. Start Telegram Bot
Write-Host "3. Launching Main Bot..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '$PYTHON' main.py"

Write-Host "✅ All services started in new windows!" -ForegroundColor Cyan
