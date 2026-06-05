# Contexto del Proyecto: RPA Impuesto Predial (Apartadó)

Este documento sirve para mantener el contexto de los avances y optimizaciones del bot RPA. Puedes leer este archivo en el futuro para retomar rápidamente el trabajo.

## Estado Actual y Tecnologías
- **Backend:** Python con FastAPI.
- **RPA:** Playwright en modo sincrónico (`sync_playwright`) manejando Chromium.
- **Frontend:** React + Vite.
- **Resolución de Captcha:** Migrado de 2Captcha a **CapMonster** (API directa vía `urllib.request` sin dependencias externas).

## Optimizaciones Implementadas (Última Sesión)
Se atacó directamente el problema de los altos tiempos de respuesta y consumo de recursos.
1. **Reemplazo a CapMonster**: Eliminación de la dependencia `2captcha-python`. Integración nativa que maneja el ReCAPTCHA v2 de la página usando la variable `CAPMONSTER_API_KEY` del archivo `.env`.
2. **Browser Pooling (Singleton)**: En lugar de instanciar un navegador pesado (Chromium) en cada petición a `/api/generar_factura`, ahora existe un hilo global (`global_rpa_thread`) en `app.py`. Este hilo arranca Chromium una sola vez y lo mantiene vivo, creando únicamente un nuevo `context` y `page` por petición.
3. **Bloqueo de Recursos Nativos**: Se configuró `page.route` para abortar la descarga de imágenes, media y fuentes, reduciendo el ancho de banda y el tiempo de renderizado de la página oficial.
4. **Refinamiento de Esperas Nativas**: Se eliminaron los bucles manuales de Python (`time.sleep`) y se cambiaron por `page.wait_for_function`. Esto permite saber en milisegundos cuándo el portal carga los datos buscando un símbolo `$`, reduciendo los reintentos fallidos a la hora de hacer clics y minimizando tiempos muertos.

## Próximos Pasos (Pendientes)
El código ya fue commiteado. Lo siguiente a trabajar es continuar optimizando la "Fase 2" (cuando el usuario ya seleccionó el predio o se carga el predio único).

**Ideas a explorar:**
- **Bypass de Modales y Clics Físicos:** El código actual simula un humano haciendo clic en *"Imprimir Factura"*, *"Descargar Recibo"* y *"Pagar en Línea"*. Al interactuar visualmente, hay pausas o fallos si la página se queda congelada.
- **El Objetivo:** Usar Playwright para interceptar o leer los atributos ocultos (ej. funciones JS `_doPostBack` o enlaces `/DownloadPDF`) de manera que el bot haga directamente una petición HTTP de descarga del PDF de la factura y extraiga la URL de pago sin tener que forzar clics en la interfaz, saltándose la renderización de las animaciones del portal.
