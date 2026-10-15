\# Informe de diagnóstico de servicios — Terminal Rescue



\*Responsable:\* Santiago Serna Contreras



\*Proyecto:\* TEC-01 — Terminal Rescue



\*Institución:\* FESC



\## 1. Objetivo



Documentar la ejecución del script de diagnóstico de Terminal Rescue desde un segundo computador, identificando el estado de Docker y la disponibilidad de la API.



\## 2. Prueba realizada



Se ejecutó el script scripts/verificar-servicios.ps1 desde PowerShell.



El procedimiento permitió consultar Docker Compose e intentar verificar el endpoint de salud de la API.



\## 3. Resultados obtenidos



\- Docker Compose respondió a la consulta de servicios.

\- No aparecieron contenedores activos en la salida mostrada.

\- La consulta de la API devolvió el mensaje: "ERROR: No se pudo consultar la API".



\## 4. Diagnóstico



El resultado indica que la API no estaba disponible desde el computador utilizado para la prueba.



Una posible causa es que los servicios de Terminal Rescue no estuvieran iniciados en ese entorno.



Este resultado no demuestra un defecto del código de la aplicación, sino que identifica una condición local que requiere revisión.



\## 5. Procedimiento recomendado



Verificar que Docker Desktop esté funcionando e iniciar los servicios mediante docker compose up -d --build.



Posteriormente, ejecutar nuevamente el script de diagnóstico y revisar sus resultados.



\## 6. Conclusión



El diagnóstico permitió documentar el comportamiento del sistema cuando la API no está disponible y establecer un procedimiento para comprobar su recuperación.



Esta contribución complementa la documentación técnica y las herramientas de diagnóstico de Terminal Rescue.

