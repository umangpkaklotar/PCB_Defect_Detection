$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$certificateDirectory = Join-Path $projectRoot "certs"
$certificatePath = Join-Path $certificateDirectory "pcb-dev-cert.pem"
$keyPath = Join-Path $certificateDirectory "pcb-dev-key.pem"
$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Get-Command mkcert -ErrorAction SilentlyContinue)) {
    throw "mkcert is required. Install it first, then run: mkcert -install"
}

if (-not (Test-Path $pythonPath)) {
    throw "Python virtual environment not found at $pythonPath"
}

$lanAddress = Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object {
        $_.IPAddress -ne "127.0.0.1" -and
        $_.IPAddress -notlike "169.254.*" -and
        $_.PrefixOrigin -ne "WellKnown"
    } |
    Select-Object -First 1 -ExpandProperty IPAddress

if (-not $lanAddress) {
    throw "Could not find a LAN IPv4 address for this PC."
}

New-Item -ItemType Directory -Force -Path $certificateDirectory | Out-Null

if (-not (Test-Path $certificatePath) -or -not (Test-Path $keyPath)) {
    & mkcert -install
    & mkcert `
        -cert-file $certificatePath `
        -key-file $keyPath `
        localhost 127.0.0.1 $lanAddress
}

Write-Host "PC URL:    https://localhost:8443/"
Write-Host "Phone URL: https://$lanAddress`:8443/"
Write-Host "Keep the PC and phone on the same Wi-Fi network."
Write-Host "Allow the Python/Uvicorn firewall prompt if Windows displays one."

Push-Location $projectRoot
try {
    & $pythonPath -m uvicorn backend.main:app `
        --reload `
        --host 0.0.0.0 `
        --port 8443 `
        --ssl-certfile $certificatePath `
        --ssl-keyfile $keyPath
}
finally {
    Pop-Location
}
