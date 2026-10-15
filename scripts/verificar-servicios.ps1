# Verificacion de servicios - Terminal Rescue
# Script de diagnostico para Windows

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

Write-Host "=== TERMINAL RESCUE ==="
Write-Host "Verificando servicios..."

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker no esta instalado o disponible."
    exit 1
}

docker compose ps

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No se pudo consultar Docker Compose."
    exit 1
}

Write-Host "Verificando API..."

try {
    $respuesta = Invoke-RestMethod -Uri "http://localhost:8081/health" -TimeoutSec 5
    $respuesta | ConvertTo-Json -Compress

    if ($respuesta.status -ne "UP") {
        Write-Host "ERROR: La API no reporta estado UP."
        exit 1
    }

    Write-Host "API funcionando correctamente."
}
catch {
    Write-Host "ERROR: No se pudo consultar la API."
    exit 1
}