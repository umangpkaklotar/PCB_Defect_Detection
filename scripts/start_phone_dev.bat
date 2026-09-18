@echo off
setlocal

cd /d "%~dp0.."
set "PYTHON=.venv\Scripts\python.exe"
set "CERT_DIR=certs"
set "CERT_FILE=%CERT_DIR%\pcb-dev-cert.pem"
set "KEY_FILE=%CERT_DIR%\pcb-dev-key.pem"

if not exist "%PYTHON%" (
    echo Python virtual environment not found at %PYTHON%.
    exit /b 1
)

where mkcert >nul 2>nul
if errorlevel 1 (
    echo mkcert is required. Install it, then run: mkcert -install
    exit /b 1
)

for /f "delims=" %%I in ('"%PYTHON%" -c "import socket; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0]); s.close()"') do set "LAN_IP=%%I"

if not defined LAN_IP (
    echo Could not find this PC's LAN IP address.
    exit /b 1
)

if not exist "%CERT_DIR%" mkdir "%CERT_DIR%"

if not exist "%CERT_FILE%" (
    echo Creating local HTTPS certificate for %LAN_IP%...
    mkcert -install
    mkcert -cert-file "%CERT_FILE%" -key-file "%KEY_FILE%" localhost 127.0.0.1 %LAN_IP%
    if errorlevel 1 exit /b 1
)

echo.
echo PC URL:    https://localhost:8443/
echo Phone URL: https://%LAN_IP%:8443/
echo Keep the PC and phone on the same Wi-Fi network.
echo Allow the Python firewall prompt if Windows displays one.
echo.

"%PYTHON%" -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8443 --ssl-certfile "%CERT_FILE%" --ssl-keyfile "%KEY_FILE%"
