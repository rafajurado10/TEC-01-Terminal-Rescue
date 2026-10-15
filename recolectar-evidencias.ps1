# Ejecutar en PowerShell desde la raiz del repositorio TEC-01-Terminal-Rescue.
# Este script recoge SALIDAS REALES del equipo: no rellena resultados inventados.
$ErrorActionPreference = 'Continue'
New-Item -ItemType Directory -Force -Path 'evidence' | Out-Null
function Evidence([string]$File, [string]$Description, [scriptblock]$Action) {
  $p = Join-Path 'evidence' $File
  @("Comprobacion: $Description", "Fecha local: $(Get-Date -Format s)", '--- SALIDA DE LA TERMINAL ---') | Set-Content -Path $p -Encoding utf8
  try { & $Action 2>&1 | Out-String -Width 240 | Add-Content -Path $p -Encoding utf8 }
  catch { "ERROR EJECUCION: $_" | Add-Content -Path $p -Encoding utf8 }
}
Evidence '01-worker.txt' 'docker compose logs del worker y estado actual' { docker compose ps -a; docker compose logs --tail=30 cierre-worker }
Evidence '02-conexion.txt' 'docker compose: conexión worker PostgreSQL' { docker compose ps -a; docker compose logs --tail=30 cierre-worker }
Evidence '03-api.txt' 'curl consulta real y codigo HTTP' { curl.exe -i http://localhost:8081/afiliados/1033111454 }
Evidence '04-cierre.txt' 'ejecucion del cierre a través de run.sh' { docker run --rm -v "${PWD}:/app" -w /app python:3.12-slim bash ./run.sh }
Evidence '05-duplicados.txt' 'excepciones de documentos duplicados' { Import-Csv .\output\excepciones.csv | Where-Object { $_.tipo -eq 'DUPLICADO' } | Format-Table -AutoSize | Out-String -Width 240 }
Evidence '06-empresa-codigos.txt' 'excepciones de empresa y codigos invalidos' { Import-Csv .\output\excepciones.csv | Where-Object { $_.tipo -in @('SIN_EMPRESA','CODIGO_INVALIDO') } | Format-Table -AutoSize | Out-String -Width 240 }
Evidence '07-beneficiarios.txt' 'beneficiarios huerfanos del cierre' { Import-Csv .\output\excepciones.csv | Where-Object { $_.tipo -eq 'BENEFICIARIO_HUERFANO' } | Format-Table -AutoSize | Out-String -Width 240 }
Evidence '08-fechas.txt' 'fechas invalidas del cierre' { Import-Csv .\output\excepciones.csv | Where-Object { $_.tipo -eq 'FECHA_INVALIDA' } | Format-Table -AutoSize | Out-String -Width 240 }
Evidence '09-cruce.txt' 'cruce con Caja Oriente, inconsistencias' { Import-Csv .\output\excepciones.csv | Where-Object { $_.tipo -eq 'CRUCE_NO_COINCIDE' } | Format-Table -AutoSize | Out-String -Width 240 }
Evidence '10-totales-repetibilidad.txt' 'hoja control, totales y hashes de dos ejecuciones sucesivas' {
  Get-Content .\control\hoja_control.csv
  Get-Content .\output\totales.txt
  $files = @('.\output\afiliados_activos.csv','.\output\excepciones.csv','.\output\totales.txt','.\output\top_error.txt')
  $before = @($files | ForEach-Object { (Get-FileHash $_ -Algorithm SHA256).Hash })
  'PRIMERA EJECUCION: ' + ($before -join ', ')
  docker run --rm -v "${PWD}:/app" -w /app python:3.12-slim bash ./run.sh
  $after = @($files | ForEach-Object { (Get-FileHash $_ -Algorithm SHA256).Hash })
  'SEGUNDA EJECUCION: ' + ($after -join ', ')
  'ARCHIVOS IDENTICOS: ' + [string](-not [bool](Compare-Object $before $after))
}
Write-Host 'Evidencias reales generadas en evidence/. Revisalas antes de subirlas.'
