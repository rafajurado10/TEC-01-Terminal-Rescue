# Uso de inteligencia artificial

## Uso 1
- Herramienta: ChatGPT.
- Para qué se usó: diagnosticar los errores de configuración del worker y la conexión entre contenedores.
- Prompt principal (resumido): "El worker falla con WORKER_INTERVAL_SECONDS=30s y no resuelve cierre-database: ¿qué debemos corregir?".
- Qué produjo: explicación de los errores CIE-1107 y CIE-2210 y pasos de cambio de las variables del entorno.
- Qué modificó o corrigió el equipo: Rafa editó .env y .env.example, recreó los contenedores y comprobó la conciliación mediante los logs reales de Docker.

## Uso 2
- Herramienta: ChatGPT.
- Para qué se usó: identificar la causa de un HTTP 500 al consultar un afiliado con el segundo nombre ausente.
- Prompt principal (resumido): "GET /afiliados/1033111454 devuelve 500, ¿qué línea de app.py provoca la falla?".
- Qué produjo: una expresión Python para unir partes no vacías del nombre evitando concatenar valores None.
- Qué modificó o corrigió el equipo: Rafa reemplazó la línea de armado del nombre, reconstruyó cierre-api y verificó que la misma consulta respondiera 200 OK.

## Uso 3
- Herramienta: ChatGPT.
- Para qué se usó: proponer una reparación reproducible del cierre mensual sobre archivos CSV reales del kit.
- Prompt principal (resumido): "Repara run.sh y el cierre para generar activos, excepciones, totales y error frecuente de forma repetible".
- Qué produjo: una propuesta de scripts Bash y Python para procesar empresas, aportes, beneficiarios, fechas y cruce Caja Oriente.
- Qué modificó o corrigió el equipo: Rafa incorporó los scripts a su repositorio, probó el procesamiento con Docker y ejecutó run.sh para comprobar los conteos y la salida.
