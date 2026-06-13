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

## Corrección de Errores de Primera Ejecución y Reducción de Tiempos (Sesión de Optimización)
Se atacaron dos frentes: bugs intermitentes en la primera ejecución y los tiempos de respuesta altos.

### Bugs de primera ejecución corregidos (`rpa_bot.py`, `complete_invoice_generation`)
1. **Selector Playwright inválido:** El locator `page.locator("text='Imprimir Factura', text='Generar Factura'")` no es sintaxis válida (Playwright **no** une dos motores `text=` con coma). Se reemplazó por un único locator de texto válido sobre `'Generar Factura'`.
2. **`NameError` en reintento:** `btn_generar_principal` se usaba en el bloque de reintento aunque solo se asignaba dentro de un `try` que podía fallar antes. Ahora se define **antes** del `try` (siempre existe) y el reintento de clic va envuelto en su propio `try/except`.

### Reducción de tiempos (esperas por evento en vez de sleeps fijos)
- **Polling de CAPSOLVER (`solve_captcha_worker`):** el `time.sleep(5)` estaba al **inicio** del bucle (5s muertos antes del primer poll). Ahora: espera inicial de 2s, sondeo cada 3s con el `sleep` al **final** (retorna de inmediato al detectar el token), y `timeout=20` en las llamadas `urlopen` para que un poll colgado no bloquee. Presupuesto 2 + 38·3 = 116s, por debajo del `captcha_future.result(timeout=125)`.
- **Sleeps fijos reemplazados** por esperas sobre `.dx-overlay-shader` / `.dx-loadpanel` ocultos (la señal real de "render listo" de DevExpress) + un pad mínimo: los dos `wait_for_timeout(3000)`, el `wait_for_timeout(500)` previo al click forzado, el `time.sleep(1)` tras inyectar el token (→ `wait_for_timeout(200)`) y el `time.sleep(3)` del fallback manual de reCAPTCHA (→ espera de `aria-checked="true"`).
- **Margen tras `.dx-data-row`:** el `wait_for_timeout(1000)` fijo se cambió por una **estabilización de conteo de filas** (dos lecturas consecutivas iguales, ~200ms típico, tope ~3s). Más rápido en el caso común y más robusto en red lenta, sin reintroducir el bug de "predios vacíos".

### Hygiene / fugas
- **Fuga de `ThreadPoolExecutor`:** se creaba uno por petición sin cerrarlo nunca. Ahora se cierra con `executor.shutdown(wait=False)` en un `finally` de `run_rpa_start` (no bloquea; el worker termina al acabar su poll actual).
- **Flags de arranque de Chromium (`app.py`):** se añadieron flags seguros de footprint/quietud y anti-throttling de timers (NO se tocó CSS ni nada que afecte el cálculo de layout de DevExpress). `--disable-gpu` va aislado y comentado como la primera línea a quitar si apareciera algún mis-click de modal.

**Nota crítica conservada:** se sigue **sin bloquear** `stylesheet`, se mantiene el *browser pooling* global, y todas las esperas sobre overlays/loadpanels/`.dx-data-row` de DevExpress siguen siendo load-bearing.

## Producción y máquina de estados de clic (Sesión 2)

### Arranque para producción (`app.py`)
- **Doble Chromium eliminado:** `python app.py` cargaba el módulo dos veces (`__main__` + el import `"app:app"` de uvicorn), lanzando DOS navegadores. Solución: `global_rpa_thread` ya **no** se crea a nivel de módulo, sino dentro del `lifespan` (que solo corre en el proceso que sirve la app) → un único Chromium.
- `@app.on_event("startup")` (deprecado) → `lifespan` con apagado limpio (`global_rpa_thread.stop()`).
- `reload` configurable por env `RELOAD` (default **False** en prod), + `HOST`/`PORT`. Un solo worker obligatorio (browser global + `active_sessions` en memoria).
- CORS por env `ALLOWED_ORIGINS` (wildcard sin credenciales). Path traversal corregido en `/api/imprimir_factura` (`os.path.basename` + validación de directorio).

### Clics frágiles de DevExpress (`rpa_bot.py`) — espera paciente, fiel al original
Los pasos **Generar Factura → Imprimir Factura** (Paso A) y **Imprimir Factura → Descargar recibo** (Paso B) sufren una carrera: tras el re-render de DevExpress, `click(force=True)` puede disparar antes de que el handler esté adjunto → clic perdido.

**Lección aprendida (importante):** se intentó una "máquina de estados por detección de spinner" (reclicar cuando no se detecta un `.dx-loadpanel`/`.dx-overlay-shader` en ~2s). FALLÓ: este portal usa modales **SweetAlert2** (`swal2`), no necesariamente loadpanels de DevExpress en esa transición, así que la señal de spinner no existía → reclicaba "Generar Factura" a mitad de la generación → "Imprimir Factura" nunca se estabilizaba. **Se revirtió.**

**Enfoque final (el que funciona):** mantener la LÓGICA ORIGINAL — UN clic y **espera paciente** del botón objetivo con `wait_for` (que retorna *apenas aparece*, así que ya es rápido en el camino feliz), **sin reclicar a mitad de la operación**. Solo un reintento si tras una espera amplia (20s Paso A / 3 intentos Paso B) no apareció. La optimización real está en:
- Reemplazar los `sleep` ciegos de settle (3000ms / 500ms) por esperas por evento de `.dx-overlay-shader` oculto + un pad pequeño (1000ms en Paso A).
- Corregir los bugs (locator de texto válido; variable siempre definida → sin NameError).
- Instrumentación `[TIMING]` por fase (Paso A, Paso B, descarga, total) para ver tiempos reales en una sola corrida.

**Regla de oro:** NO reclicar agresivamente en pasos de DevExpress; `wait_for` paciente = rápido (sale al aparecer) + estable (no interfiere con AJAX en curso). No asumir que hay un spinner `.dx-*`; el portal mezcla SweetAlert2.
