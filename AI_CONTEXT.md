# Contexto del Proyecto: RPA Impuesto Predial (Apartadó)

Este documento sirve para mantener el contexto de los avances y optimizaciones del bot RPA. Puedes leer este archivo en el futuro para retomar rápidamente el trabajo.

## Estado Actual y Tecnologías
- **Backend:** Python con FastAPI.
- **RPA:** Playwright en modo sincrónico (`sync_playwright`) manejando Chromium.
- **Frontend:** React + Vite.
- **Resolución de Captcha:** Migrado de 2Captcha a **CapMonster** (API directa vía `urllib.request` sin dependencias externas).

## Optimizaciones Implementadas (Última Sesión)
Se atacó directamente el problema de los altos tiempos de respuesta, consumo de recursos en servidor y fugas de memoria.
1. **Reemplazo a CAPSOLVER (Concurrente)**: Se reemplazó 2Captcha/Capmonster por la API directa de Capsolver (ProxyLess). Ahora el captcha se resuelve en un hilo secundario (`ThreadPoolExecutor`) al mismo tiempo que Playwright navega hacia la URL principal, traslapando tiempos muertos de carga.
2. **Browser Pooling Global**: Se resolvió la fuga de memoria de Chromium modificando `RpaThread` en `app.py`. Ahora Playwright y Chromium se instancian *una sola vez* al arrancar el servidor. Para cada petición, se abre un `Context` y `Page` ligero que se cierra siempre mediante `close_session_objects()`, conservando intacto el `Browser` raíz.
3. **Bloqueo de Recursos Nativos Ajustado**: Se configuró `page.route` para abortar la descarga de imágenes, media y fuentes, reduciendo el ancho de banda. *Nota Crítica:* **Nunca** se deben bloquear los `stylesheet` (CSS), ya que el portal oficial usa DevExpress y depende del CSS para calcular posiciones; bloquearlo provoca que los clics fallen al no mostrarse los modals correctamente.
4. **Rescate de Hooks y Frontend Build**: Se restauró exitosamente `useRpa.js` desde commits anteriores, reparando errores del frontend, y se generó un nuevo build en la carpeta `dist`.

## Próximos Pasos (Pendientes)
El código ya fue commiteado. Lo siguiente a trabajar es continuar optimizando la "Fase 2" (cuando el usuario ya seleccionó el predio o se carga el predio único).

**Ideas a explorar:**
- **Bypass de Modales y Clics Físicos:** El código actual simula un humano haciendo clic en *"Imprimir Factura"*, *"Descargar Recibo"* y *"Pagar en Línea"*. Al interactuar visualmente, hay pausas o fallos si la página se queda congelada.
- **El Objetivo:** Usar Playwright para interceptar o leer los atributos ocultos (ej. funciones JS `_doPostBack` o enlaces `/DownloadPDF`) de manera que el bot haga directamente una petición HTTP de descarga del PDF de la factura y extraiga la URL de pago sin tener que forzar clics en la interfaz, saltándose la renderización de las animaciones del portal.

## Optimizaciones de Sincronización (Solución de Múltiples Predios Vacíos)
Se identificó y corrigió un problema donde el frontend recibía la respuesta de `"predios": []` a pesar de que el portal oficial mostraba varios resultados. 
1. **Espera Inteligente de Filas AJAX:** El scraper se modificó para esperar explícitamente el selector `.dx-data-row` con `page.wait_for_selector` (hasta 20 segundos) en vez de usar un `page.wait_for_timeout(3000)` arbitrario, lo que garantiza que los datos asíncronos de la tabla DevExpress siempre se extraigan una vez que el DOM los renderice, incluso con red lenta.
2. **Mapeo de Tipos de Búsqueda:** Se incluyó un mapeo de los términos `"Documento"` y `"Cédula"` (enviados desde el frontend) a `"Propietario"`, que es el label exacto del *radio button* que existe en el HTML del portal de Apartadó. Esto previene los Timeouts de Playwright al momento de localizar la opción a seleccionar.
