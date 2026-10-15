# Informe de incidentes — Terminal Rescue

Diagnósticos basados en el código original del kit y comprobaciones del equipo. Las evidencias deben regenerarse en el computador donde se ejecutó la solución.

## Incidente 1
- **Síntoma:** El contenedor cierre-worker terminaba al iniciar por una variable de intervalo inválida.
- **Diagnóstico:** El log CIE-1107 mostraba WORKER_INTERVAL_SECONDS=30s, aunque el programa esperaba un número entero.
- **Comandos:** `docker compose ps -a` y `docker compose logs --tail=50 cierre-worker`
- **Solución:** Se sustituyó 30s por 30 en .env.example y en la configuración local, y se recreó el worker.
- **Evidencia:** evidence/01-worker.txt

## Incidente 2
- **Síntoma:** El worker seguía activo pero no podía consultar la base PostgreSQL.
- **Diagnóstico:** El log CIE-2210 indicaba que el nombre cierre-database no existía en la red; el servicio definido se llama cierre-db.
- **Comandos:** `docker compose logs --tail=30 cierre-worker` y `docker compose ps -a`
- **Solución:** Se configuró DATABASE_HOST=cierre-db y se recrearon cierre-api y cierre-worker para leer el host correcto.
- **Evidencia:** evidence/02-conexion.txt

## Incidente 3
- **Síntoma:** Una consulta HTTP del afiliado con nombre intermedio vacío respondía error interno 500.
- **Diagnóstico:** La concatenación directa en app.py no aceptaba los valores nulos devueltos por PostgreSQL.
- **Comandos:** `curl -i http://localhost:8081/afiliados/1033111454` y `docker compose logs cierre-api`
- **Solución:** Se construyó el nombre uniendo solamente campos con texto y la misma consulta pasó a HTTP 200.
- **Evidencia:** evidence/03-api.txt

## Incidente 4
- **Síntoma:** El proceso heredado de cierre no encontraba la carpeta de entrada de afiliados.
- **Diagnóstico:** El script original buscaba /opt/cierre/entrada en lugar de utilizar los CSV incluidos bajo data/ del proyecto.
- **Comandos:** `find data -name "*.csv"` y `docker run --rm python:3.12-slim bash ./run.sh`
- **Solución:** Se hizo que cierre.sh invoque el procesador Python con rutas relativas al repositorio, sin mover archivos de entrada.
- **Evidencia:** evidence/04-cierre.txt

## Incidente 5
- **Síntoma:** El maestro de afiliados contenía documentos repetidos que podían distorsionar los conteos.
- **Diagnóstico:** Un archivo de excepciones permite identificar documentos con tipo DUPLICADO sin incluir doblemente el afiliado principal.
- **Comandos:** `sort data/AFI_MAE.csv | uniq -d` y `grep DUPLICADO output/excepciones.csv`
- **Solución:** El procesamiento conserva una sola fila por documento y reporta explícitamente cada documento repetido.
- **Evidencia:** evidence/05-duplicados.txt

## Incidente 6
- **Síntoma:** Había afiliados con referencias a empresas ausentes o estados fuera del catálogo esperado.
- **Diagnóstico:** Al comparar cod_emp con EMPRESA.csv y el campo EST_AFI con A/I se detectan SIN_EMPRESA y CODIGO_INVALIDO.
- **Comandos:** `grep SIN_EMPRESA output/excepciones.csv` y `grep CODIGO_INVALIDO output/excepciones.csv`
- **Solución:** El cierre evita contabilizar como activos válidos los registros inválidos y genera excepciones explicativas.
- **Evidencia:** evidence/06-empresa-codigos.txt

## Incidente 7
- **Síntoma:** El archivo de beneficiarios contenía referencias a afiliados que no estaban en el maestro.
- **Diagnóstico:** El cruce entre AFI_BEN.csv y los documentos únicos de AFI_MAE.csv identifica BENEFICIARIO_HUERFANO.
- **Comandos:** `awk -F, "NR>1 {print $1}" data/AFI_BEN.csv` y `grep BENEFICIARIO_HUERFANO output/excepciones.csv`
- **Solución:** Se calcularon los beneficiarios por afiliado real y se documentaron las referencias huérfanas.
- **Evidencia:** evidence/07-beneficiarios.txt

## Incidente 8
- **Síntoma:** Las fechas de afiliación no venían siempre con el mismo formato de origen.
- **Diagnóstico:** Se inspeccionaron fechas alternativas y aquellas imposibles se registraron como FECHA_INVALIDA en excepciones.csv.
- **Comandos:** `grep FECHA_INVALIDA output/excepciones.csv` y `wc -l output/excepciones.csv`
- **Solución:** Se implementó normalización de fechas conocidas sin descartar silenciosamente registros con fecha inválida.
- **Evidencia:** evidence/08-fechas.txt

## Incidente 9
- **Síntoma:** El extracto externo de Caja Oriente tenía columnas y estados diferentes al sistema local.
- **Diagnóstico:** Se normalizaron documentos con ceros iniciales y se mapearon VIGENTE y RETIRADO antes de contrastar estados.
- **Comandos:** `grep CRUCE_NO_COINCIDE output/excepciones.csv` y `sort output/excepciones.csv`
- **Solución:** Se informan los cruces ausentes o inconsistentes en CRUCE_NO_COINCIDE, preservando el encabezado del archivo de activos.
- **Evidencia:** evidence/09-cruce.txt

## Incidente 10
- **Síntoma:** El script heredado dejaba totales incompletos y no podía repetirse después de mover los CSV.
- **Diagnóstico:** La hoja de control demanda 1500 afiliados únicos, 1194 activos y 274 inactivos; el original también alteraba entradas.
- **Comandos:** `docker run --rm python:3.12-slim bash ./run.sh`, `wc -l output/afiliados_activos.csv` y `chmod +x run.sh`
- **Solución:** El cierre ahora genera totales.txt y otros tres reportes desde entradas conservadas para producir resultados repetibles.
- **Evidencia:** evidence/10-totales-repetibilidad.txt
