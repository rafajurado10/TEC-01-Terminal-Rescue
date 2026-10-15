\# Guía de verificación de Terminal Rescue



\*Responsable:\* Santiago Serna Contreras  

\*Proyecto:\* TEC-01 - Terminal Rescue  

\*Institución:\* FESC



\## 1. Objetivo



Documentar el procedimiento para comprobar el funcionamiento del sistema Terminal Rescue, incluyendo la base de datos PostgreSQL, la API de consultas y el worker de conciliación.



\## 2. Verificación de Docker



Con Docker Desktop iniciado, abrir PowerShell desde la carpeta principal del proyecto y ejecutar:



docker compose up -d --build

docker compose ps



Comprobar que los servicios de PostgreSQL, API y worker estén funcionando correctamente.



\## 3. Verificación de la API



Ejecutar los siguientes comandos:



curl.exe http://localhost:8081/health



curl.exe -i http://localhost:8081/afiliados/1033111454



La primera consulta debe confirmar que la API funciona. La segunda debe devolver una respuesta JSON válida con la información del afiliado de prueba.



\## 4. Verificación del worker



Ejecutar:



docker compose logs --tail=30 cierre-worker



Revisar los registros para comprobar que el worker realiza la conciliación sin errores de conexión.



\## 5. Verificación del cierre mensual



Ejecutar desde la raíz del proyecto:



docker run --rm -v "${PWD}:/app" -w /app python:3.12-slim python scripts/cierre.py



Comprobar que se generen los archivos de resultados correspondientes y revisar los totales y las excepciones.



\## 6. Seguridad



No publicar contraseñas, tokens de acceso ni archivos .env que contengan información privada.



\## 7. Conclusión



Esta guía permite repetir las comprobaciones esenciales de Terminal Rescue y facilitar el diagnóstico de posibles fallos de los servicios.

