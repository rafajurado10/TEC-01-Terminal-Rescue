# Terminal Rescue — Equipo TEC-01

## Descripción

Terminal Rescue recupera el cierre mensual de afiliaciones de una Caja de Compensación Familiar. El sistema procesa los archivos de afiliados, empresas, aportes y beneficiarios para generar información que usa Subsidios. También permite consultar afiliaciones por documento, registra excepciones de calidad y contrasta información con el extracto de Caja Oriente. Este proyecto corrige fallos del entorno recibido durante HackaFESC 2026.

## Integrantes

- Rafael Josué Jurado Cepeda.
- Santiago Serna Contreras.

## Requisitos

Docker Desktop con motor Linux y Docker Compose, conexión para descargar las imágenes, sistema operativo Windows con WSL 2 o Linux, y Git para versionar el proyecto. El ejecutable de Python 3.8 o superior es necesario para ejecutar el validador local; el procesamiento puede ejecutarse con Python 3 desde contenedor.

## Instalación y ejecución

Desde la raíz del repositorio crear la configuración y levantar la solución en el entorno Docker. Una vez iniciados los tres servicios, ejecutar el cierre mensual para generar sus archivos de salida. En Linux:

```bash
cp .env.example .env
docker compose up -d --build
docker compose ps
./run.sh
./validator check
./validator entregables
```

En Windows, crear `.env` con `Copy-Item .env.example .env`. Para ejecutar el cierre con Python sin instalación local, se puede utilizar desde PowerShell: `docker run --rm -v "${PWD}:/app" -w /app python:3.12-slim bash ./run.sh`.

## Configuración

Las variables de `.env.example` y su función son:

- `POSTGRES_DB`: nombre de la base PostgreSQL, por ejemplo `cierre`.
- `POSTGRES_USER`: usuario de PostgreSQL, por ejemplo `cierre`.
- `POSTGRES_PASSWORD`: contraseña de PostgreSQL. Configurar un valor local seguro; no copiarlo a documentos.
- `DATABASE_HOST`: nombre del servicio de base de datos para conexiones entre contenedores; usar `cierre-db`.
- `DATABASE_PORT`: puerto interno de PostgreSQL, normalmente `5432`.
- `DATABASE_NAME`: base que consultan API y worker, por ejemplo `cierre`.
- `DATABASE_USER`: usuario del cliente de base de datos, correspondiente a la cuenta autorizada.
- `DATABASE_PASSWORD`: contraseña del cliente de base; utilizar una variable local y no publicarla.
- `API_PORT`: puerto en el host donde se expone la API, por ejemplo `8081`.
- `WORKER_INTERVAL_SECONDS`: intervalo de conciliación como entero de segundos, por ejemplo `30` sin sufijo de tiempo.

El archivo `.env` debe permanecer fuera del control de versiones y las configuraciones compartibles ir en `.env.example`.

## Arquitectura

La arquitectura consta de tres servicios definidos en `docker-compose.yml`. `cierre-db` ejecuta PostgreSQL y carga los datos de prueba desde `db/init` y `data`. `cierre-api` ofrece consultas HTTP de afiliados y se conecta a `cierre-db` por el nombre de servicio dentro de la red Docker. `cierre-worker` realiza conciliaciones periódicas, también sobre PostgreSQL. El cierre por lotes se ejecuta a través de `run.sh`, `scripts/cierre.sh` y `scripts/cierre.py`, que leen los CSV sin mover los originales y escriben los reportes en `output/`.

## Uso

La API responde a `GET /afiliados/{documento}`. Ejemplo: `curl http://localhost:8081/afiliados/1033111454`. El afiliado encontrado devuelve documento, nombre, estado y empresa; un documento ausente debe responder HTTP 404. Al ejecutar `./run.sh`, se generan cuatro archivos en `output/`: `afiliados_activos.csv`, `excepciones.csv`, `totales.txt` y `top_error.txt`. Los formatos se describen en `RETO.md`.

## Pruebas

Comprobar primero los contenedores mediante `docker compose ps -a`, consultar la API para un documento existente y uno inexistente y revisar `docker compose logs --tail=30 cierre-worker`. Ejecutar `./run.sh` dos veces y comparar el contenido de los archivos para demostrar repetibilidad. Finalmente ejecutar `./validator check` y `./validator entregables` en un entorno Linux configurado con Python y Docker para revisar los requisitos públicos.

## Documentación

- [Informe de incidentes](incident-report.md): diagnósticos y reparaciones.
- [Evidencias](evidence/): salidas de las herramientas de diagnóstico.
- [Registro de uso de IA](AI_USAGE.md): tareas realizadas con ChatGPT y comprobaciones humanas.
- [Guía del kit](KIT.md): instrucciones oficiales del reto.
- [Rúbrica](RUBRICA.md): criterios de evaluación.

## Qué resolvimos

Se corrigió el intervalo inválido del worker, pasando el parámetro a segundos enteros, y el nombre del host PostgreSQL para que la API y el worker puedan conectarse entre contenedores. La API dejó de fallar ante segundos nombres nulos. El cierre heredado fue sustituido por un procesamiento reproducible que contabiliza afiliados, procesa beneficiarios, empresas y aportes, reconoce fechas alternativas, compara datos con Caja Oriente y produce excepciones y reportes. Se comprobaron localmente consultas HTTP y ejecuciones repetidas del cierre.

## Limitaciones y pendientes

La calificación final depende también de casos ocultos del evaluador, los diez archivos reales de evidencia, el registro del repositorio en la plataforma y el pitch público. Se deben validar los resultados y las contribuciones de ambos integrantes antes del cierre oficial.
