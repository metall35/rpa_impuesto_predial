import os
import time
import urllib.request
import json
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from playwright.sync_api import sync_playwright
import qrcode
import io
import base64

# archivo .env
load_dotenv()


def close_session_objects(session_data):
    """Helper tool to close playwright browser context and stop playwright instance safely."""
    try:
        if "page" in session_data and session_data["page"]:
            try:
                session_data["page"].close()
            except:
                pass
        if "context" in session_data and session_data["context"]:
            try:
                session_data["context"].close()
            except:
                pass
    except Exception as e:
        print(f"Error al cerrar los objetos de la sesión Playwright: {e}")

def complete_invoice_generation(page, context, search_value, phone, email):
    """Helper to complete the invoice generation after selecting/landing on a single predio."""
    print("Cargó información del predio. Generando factura...")
    _t_fase0 = time.time()
    print(f"[TIMING] Inicio complete_invoice_generation t0={_t_fase0:.2f}")
    # Esperar a que el shader (overlay de carga) del DevExpress desaparezca antes de hacer clic
    try:
        page.locator(".dx-overlay-shader").first.wait_for(state="hidden", timeout=10000)
    except:
        pass
        
    try:
        # Usar visible=true para asegurarnos de no hacer force click en un span o botón oculto
        page.locator("text='Generar Factura'").locator("visible=true").first.click()
    except Exception as e:
        print(f"Error al hacer clic inicial en Generar Factura: {e}")

    try:
        page.locator("text=Seleccione el Período de Generación").wait_for(state="visible", timeout=15000)
    except Exception as e:
        raise Exception("No apareció la modal de selección de período.")
    
    btn_generar_modal = page.locator(".modal-dialog, .modal-content, .dx-overlay-content, .dx-popup-content, [role='dialog']").locator("text=Generar Factura").first
    btn_generar_modal.wait_for(state="visible", timeout=10000)
    btn_generar_modal.click()

    # CUT 4: timeouts recortados (solo aceleran detección de fallo; el camino feliz sale al ocultarse
    # el elemento). El loadpanel (generación AJAX pesada, load-bearing) se mantiene en 15000.
    try:
        page.locator(".dx-overlay-content, .dx-popup-content, [role='dialog']").wait_for(state="hidden", timeout=5000)
    except:
        pass

    try:
        page.locator(".dx-loadpanel:visible, .dx-loadpanel-content:visible").first.wait_for(state="hidden", timeout=15000)
    except Exception as le:
        print(f"Advertencia al esperar el panel de carga: {le}")

    # Esperar a que el overlay/shader de DevExpress quede oculto (señal real de "render listo").
    try:
        page.locator(".dx-overlay-shader").first.wait_for(state="hidden", timeout=5000)
    except:
        pass

    # PASO A: "Generar Factura" principal -> aparece "Imprimir Factura".
    # LÓGICA FIEL AL ORIGINAL: si "Generar Factura" sigue visible se hace UN clic y se ESPERA
    # PACIENTEMENTE a que aparezca "Imprimir Factura" (wait_for retorna apenas aparece -> rápido en
    # el camino feliz). NO se reclica durante la generación en curso. Solo un reintento si tras una
    # espera amplia no apareció. Bugs corregidos: locator de texto válido y variable siempre definida.
    _t_A = time.time()
    btn_generar_principal = page.locator("text='Generar Factura'").locator("visible=true").first
    btn_imprimir = page.locator("text='Imprimir Factura'").first

    # Settle: esperar a que el overlay/shader de DevExpress quede oculto (sale rápido si no hay) y un
    # pad para que se adjunte el handler del botón antes del clic forzado (reemplaza el sleep de 3s).
    try:
        page.locator(".dx-overlay-shader").first.wait_for(state="hidden", timeout=8000)
    except:
        pass
    page.wait_for_timeout(1000)

    try:
        if btn_generar_principal.is_visible():
            btn_generar_principal.click(force=True)
    except Exception as e:
        print(f"Advertencia al hacer clic en 'Generar Factura' principal: {e}")

    btn_imprimir_visible = False
    try:
        btn_imprimir.wait_for(state="visible", timeout=20000)
        btn_imprimir_visible = True
    except Exception:
        print("'Imprimir Factura' no apareció aún. Reintentando clic en 'Generar Factura'...")
        try:
            if btn_generar_principal.is_visible():
                btn_generar_principal.click(force=True)
        except Exception as e:
            print(f"No se pudo reintentar el clic en 'Generar Factura': {e}")
        try:
            btn_imprimir.wait_for(state="visible", timeout=20000)
            btn_imprimir_visible = True
        except Exception:
            pass
    print(f"[TIMING] Paso A (Generar->Imprimir): {time.time() - _t_A:.2f}s")
    if not btn_imprimir_visible:
        raise Exception("No apareció el botón 'Imprimir Factura' tras intentar 'Generar Factura'.")
        
    print("Esperando a que se carguen los datos...")
    try:
        # Espera nativa revisando específicamente el símbolo $ para evitar el falso positivo con la cédula en la caja de búsqueda.
        page.wait_for_function("""
            () => {
                const inputs = Array.from(document.querySelectorAll('input'));
                return inputs.some(input => input.value.includes('$'));
            }
        """, timeout=20000)
        print("¡Datos de factura detectados!")
    except Exception as e:
        print("Advertencia: No se detectaron datos de la factura cargados, procediendo de todos modos...")
    
    #llena telefono y correo
    page.get_by_label("Teléfono").wait_for(state="visible", timeout=5000)
    page.get_by_label("Teléfono").fill(phone)
    page.get_by_label("Correo Electrónico").wait_for(state="visible", timeout=5000)
    page.get_by_label("Correo Electrónico").fill(email)

    print("Descargando factura...")
    download_obj = None
    popup_page = None
    
    def on_download(d):
        nonlocal download_obj
        download_obj = d
        print(f"Evento de descarga detectado: {d.suggested_filename}")
        
    def on_popup(p):
        nonlocal popup_page
        popup_page = p
        print(f"Evento de popup detectado por Playwright: {p.url}")
        
    page.on("download", on_download)
    context.on("page", on_popup)

    # PASO B: "Imprimir Factura" -> aparece "Descargar recibo". LÓGICA FIEL AL ORIGINAL: bucle de
    # hasta 3 intentos, cada uno con UN clic y espera PACIENTE de "Descargar recibo" (sin reclicar a
    # mitad de la operación). Única optimización: el settle previo al clic es por evento (overlay
    # oculto) en vez del sleep fijo de 500ms. El wait_for_function de '$' + el fill de Teléfono/Correo
    # ya confirmaron arriba que la UI está lista, por eso no se reañade el settle redundante previo.
    _t_B = time.time()
    btn_imprimir = page.locator("text='Imprimir Factura'").first
    try:
        btn_imprimir.wait_for(state="visible", timeout=10000)
    except Exception:
        # Fallback en caso de que aún diga Generar Factura en alguna vista
        btn_imprimir = page.locator("text='Generar Factura'").nth(1)

    btn_descargar = page.locator("text='Descargar recibo'").first

    exito_modal_visible = False
    for retry in range(3):
        print(f"Haciendo clic en el botón de factura (Intento {retry + 1})...")
        try:
            btn_imprimir.scroll_into_view_if_needed()
            # Settle por evento en vez de sleep fijo de 500ms: sale de inmediato si no hay overlay.
            try:
                page.locator(".dx-overlay-shader").first.wait_for(state="hidden", timeout=3000)
            except:
                pass
            btn_imprimir.click(force=True)
        except Exception as click_err:
            print(f"Error al hacer clic en el botón de factura: {click_err}")

        try:
            btn_descargar.wait_for(state="visible", timeout=10000)
            exito_modal_visible = True
            break
        except Exception:
            print("No apareció el botón 'Descargar recibo' aún. Reintentando...")
    print(f"[TIMING] Paso B (Imprimir->Descargar): {time.time() - _t_B:.2f}s")
    if not exito_modal_visible:
        raise Exception("No apareció el popup de éxito con el botón 'Descargar recibo' después de varios intentos.")

    # 1. Definir interceptor de rutas para bloquear la redirección automática a la segunda página durante la descarga
    def intercept_redirects(route):
        if route.request.is_navigation_request() and "/Predial/Index" in route.request.url:
            print(f"Interceptada y bloqueada redirección automática a: {route.request.url}")
            route.abort()
        else:
            route.continue_()

    # Registrar la ruta en la página
    page.route("**/*", intercept_redirects)
    
    # 2. Hacer clic en el botón Descargar Recibo para iniciar la descarga del PDF
    btn_descargar.click()

    # CUT 3: comprobación al INICIO del bucle (no perder el primer tick si la descarga es instantánea).
    # El bucle es dirigido por evento (on_download/on_popup); el techo es solo tope de seguridad.
    _t_dl = time.time()
    for _ in range(150):
        if download_obj or popup_page:
            break
        page.wait_for_timeout(100)
    print(f"[TIMING] Espera descarga PDF: {time.time() - _t_dl:.2f}s")
    
    descargas_dir = os.path.join(os.getcwd(), "facturas_descargadas")
    os.makedirs(descargas_dir, exist_ok=True)
    
    file_saved = False
    file_path = None
    filename = None
    
    # Caso A: Descarga estándar iniciada por el navegador
    if download_obj:
        file_path = os.path.join(descargas_dir, download_obj.suggested_filename)
        download_obj.save_as(file_path)
        filename = os.path.basename(file_path)
        print(f"Factura descargada exitosamente en: {file_path}")
        file_saved = True
    
    # Caso B: Se abrió una nueva pestaña con el PDF
    elif popup_page:
        print(f"Se detectó nueva pestaña con el PDF: {popup_page.url}")
        popup_page.wait_for_load_state("load")
        
        # Nombre de archivo basado en el código
        filename = f"factura_predial_{search_value}.pdf"
        file_path = os.path.join(descargas_dir, filename)
        
        # Descargar los bytes utilizando el contexto de navegación existente (mantiene las cookies de sesión)
        try:
            response = context.request.get(popup_page.url)
            with open(file_path, "wb") as f:
                f.write(response.body())
            print(f"Factura descargada exitosamente desde nueva pestaña en: {file_path}")
            file_saved = True
        except Exception as req_err:
            raise Exception(f"No se pudo descargar el PDF de la nueva pestaña: {req_err}")
    
    try:
        page.unroute("**/*", intercept_redirects)
    except Exception as e:
        print(f"Advertencia al remover interceptor: {e}")
    
    if not file_saved:
        raise Exception("No se detectó descarga ni apertura de PDF después de hacer clic en Imprimir Factura.")

    page.evaluate("""
        const swal = document.querySelector('.swal2-container');
        if (swal) {
            swal.remove();
        }
        document.body.classList.remove('swal2-shown', 'swal2-height-auto');
        document.documentElement.classList.remove('swal2-shown', 'swal2-height-auto');
    """)
    
    # 4. Capturar el enlace generar el QR
    payment_url = None
    payment_qr = None
    try:
        btn_pagar = page.locator("text='Pagar en Línea'").first
        btn_pagar.wait_for(state="visible", timeout=10000)
        
        with page.expect_popup(timeout=20000) as popup_info:
            btn_pagar.click()
        
        payment_popup = popup_info.value
        # CUT 2: granularidad 100ms (la URL real suele aparecer en ~100-300ms), techo ~5s.
        for _ in range(50):
            if payment_popup.url and payment_popup.url != "about:blank":
                break
            page.wait_for_timeout(100)
        payment_url = payment_popup.url
        print(f"URL de pago en línea capturada: {payment_url}")
        payment_popup.close()
        
        page.evaluate("""
            const swal = document.querySelector('.swal2-container');
            if (swal) {
                swal.remove();
            }
            document.body.classList.remove('swal2-shown', 'swal2-height-auto');
            document.documentElement.classList.remove('swal2-shown', 'swal2-height-auto');
        """)
        
        if payment_url and payment_url != "about:blank":
            # Generar el código QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(payment_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            payment_qr = f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"
            print("QR de pago generado exitosamente.")
    except Exception as pay_err:
        print(f"Advertencia: No se pudo capturar el enlace de pago en línea o generar el QR: {pay_err}")

    print(f"[TIMING] TOTAL complete_invoice_generation: {time.time() - _t_fase0:.2f}s")
    return {
        "status": "success",
        "message": "Factura descargada exitosamente.",
        "file": file_path,
        "filename": filename,
        "payment_url": payment_url,
        "payment_qr": payment_qr
    }

def solve_captcha_worker(api_key, sitekey, page_url):
    """Resuelve el captcha en segundo plano para no bloquear a Playwright"""
    print("Enviando captcha a CAPSOLVER en segundo plano...")
    try:
        task_payload = {
            "clientKey": api_key,
            "task": {
                "type": "ReCaptchaV2TaskProxyLess",
                "websiteURL": page_url,
                "websiteKey": sitekey
            }
        }
        
        req = urllib.request.Request("https://api.capsolver.com/createTask", data=json.dumps(task_payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=20) as response:
            res = json.loads(response.read().decode('utf-8'))
            task_id = res.get("taskId")

        token = None
        # Capsolver nunca resuelve al instante: pequeña espera inicial (antes el primer poll
        # esperaba 5s en seco). Luego se sondea cada 3s, esperando al FINAL del bucle para no
        # malgastar tiempo tras detectar el token. Presupuesto: 2 + 38*3 = 116s de sleeps,
        # cómodamente por debajo del captcha_future.result(timeout=125) que lo consume.
        time.sleep(2)
        for _ in range(38):
            result_payload = {"clientKey": api_key, "taskId": task_id}
            req2 = urllib.request.Request("https://api.capsolver.com/getTaskResult", data=json.dumps(result_payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
            try:
                with urllib.request.urlopen(req2, timeout=20) as response2:
                    res2 = json.loads(response2.read().decode('utf-8'))
                    status = res2.get("status")
                    if status == "ready":
                        token = res2.get("solution").get("gRecaptchaResponse")
                        break
            except Exception as poll_err:
                # Un poll lento/fallido no debe matar todo el solve: reintentar en la siguiente vuelta.
                print(f"Advertencia en poll de CAPSOLVER, reintentando: {poll_err}")
            time.sleep(3)
        return token
    except Exception as e:
        print(f"Error en worker de CAPSOLVER: {e}")
        return None

def run_rpa_start(browser, search_type, search_value, phone, email):
    """Phase 1: Start playwright, solve captcha, submit search, check for multiple predios."""
    import threading
    import concurrent.futures
    print(f"THREAD DEBUG [start]: Running in {threading.current_thread().name} (ID: {threading.current_thread().ident})")
    api_key = os.getenv("CAPSOLVER_API_KEY")
    if not api_key:
        print("ADVERTENCIA: No se encontró la API Key de CAPSOLVER en el archivo .env")
    
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    session_data = {
        "context": context,
        "page": page,
        "timestamp": time.time()
    }

    try:
        captcha_future = None
        executor = None
        target_url = "https://oficinavirtual.apartado-antioquia.gov.co/Predial/Index"
        
        if api_key:
            # Iniciamos el worker de capsolver concurrentemente con la navegación
            sitekey_estatica = "6LcfN70UAAAAADa89KIZRMMo8CWSXPrOVsElAZd_"
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            captcha_future = executor.submit(solve_captcha_worker, api_key, sitekey_estatica, target_url)

        print("Navegando al portal...")
        
        def intercept_resources(route):
            # No bloquear stylesheet porque DevExpress rompe sus modals (calcula posiciones con JS basado en CSS)
            if route.request.resource_type in ["image", "media", "font"]:
                route.abort()
            else:
                route.continue_()
                
        page.route("**/*", intercept_resources)
        page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        
        # Mapear tipos comunes al nombre del radio button en Apartadó
        search_type_mapped = search_type
        if search_type in ["Documento", "Cédula", "Cedula"]:
            search_type_mapped = "Propietario"
            
        page.get_by_text(search_type_mapped, exact=True).first.wait_for(state="visible", timeout=40000)
        page.get_by_text(search_type_mapped, exact=True).first.click()
        
        page.locator('input[type="text"]').first.fill(search_value)

        # captcha
        if api_key and captcha_future:
            print("Esperando resolución concurrente del reCAPTCHA...")
            token = captcha_future.result(timeout=125)
            
            if token:
                print("¡Captcha resuelto exitosamente por CAPSOLVER!")
                try:
                    # Esperar a que el textarea del captcha se agregue al DOM
                    try:
                        page.wait_for_selector("#g-recaptcha-response", state="attached", timeout=15000)
                    except:
                        pass
                        
                    # Inyectar el token en la página de forma segura
                    page.evaluate(f'''
                        var el = document.getElementById("g-recaptcha-response");
                        if (el) {{
                            el.innerHTML = "{token}";
                            el.value = "{token}";
                        }}
                        var els = document.getElementsByName("g-recaptcha-response");
                        if (els.length > 0) {{
                            els[0].value = "{token}";
                        }}
                    ''')
                    
                    # Sobrescribir grecaptcha.getResponse para que la validación del cliente pase
                    page.evaluate(f'''
                        if (typeof grecaptcha !== "undefined") {{
                            grecaptcha.getResponse = function() {{ return "{token}"; }};
                        }} else {{
                            window.grecaptcha = {{
                                getResponse: function() {{ return "{token}"; }}
                            }};
                        }}
                    ''')
                    # La inyección vía page.evaluate es síncrona en Playwright sync-mode: los valores
                    # ya quedan en el DOM/JS al retornar. Solo un margen mínimo (antes era 1s) por si un
                    # bundle tardío de reCAPTCHA re-inicializa grecaptcha y sobreescribe el override.
                    page.wait_for_timeout(200)
                except Exception as e:
                    raise Exception(f"Error al inyectar el token resuelto: {e}")
            else:
                raise Exception("El worker de CAPSOLVER retornó None o falló.")
        else:
            print("Intentando hacer clic en el reCAPTCHA de forma manual/física...")
            try:
                recaptcha_iframe = page.frame_locator("iframe[title*='reCAPTCHA']")
                recaptcha_iframe.locator(".recaptcha-checkbox-border").click(timeout=5000)
                # Esperar a que el checkbox quede marcado (aria-checked="true") en lugar de un sleep
                # fijo de 3s. El atributo está en el div padre .recaptcha-checkbox, no en el -border.
                # Si no se marca (desafío de imagen / red lenta) se continúa igual que antes.
                try:
                    recaptcha_iframe.locator('.recaptcha-checkbox[aria-checked="true"]').wait_for(state="visible", timeout=5000)
                except Exception as wait_err:
                    print("El reCAPTCHA no se marcó dentro del tiempo esperado, continuando:", wait_err)
            except Exception as e:
                print("No se pudo interactuar con el reCAPTCHA o no apareció:", e)
        
        page.get_by_role("button", name="Buscar").click()

        print("Esperando respuesta del portal...")
        try:
            locator_generar = page.locator("text='Generar Factura'")
            locator_multiples = page.locator("text=Seleccione un predio para continuar con el proceso")
            locator_error = page.locator("text=No se encontró el valor de búsqueda")
            
            # Bucle de espera inteligente para evitar falsos positivos
            for _ in range(180):
                if locator_generar.first.is_visible():
                    print("Se detectó botón 'Generar Factura' (predio único).")
                    break
                elif locator_multiples.first.is_visible() or "/SeleccionPredio" in page.url:
                    print("Se detectó pantalla de múltiples predios.")
                    break
                elif locator_error.first.is_visible():
                    print("Se detectó error en la búsqueda.")
                    break
                page.wait_for_timeout(500)
            else:
                raise Exception("Tiempo de espera agotado sin detectar respuesta del portal.")
        except Exception as e:
            raise Exception(f"Error esperando respuesta del portal: {e}")
        
        # 1. Caso: Múltiples predios encontrados
        if "/SeleccionPredio" in page.url or (locator_multiples.count() > 0 and locator_multiples.first.is_visible()):
            print("Se detectaron múltiples predios asociados. Extrayendo tabla para enviar al frontend...")
            
            # Esperar a que las filas de datos de DevExpress estén visibles
            try:
                page.wait_for_selector(".dx-data-row", state="visible", timeout=20000)
                # En vez de un margen fijo de 1000ms: esperar a que el conteo de filas se estabilice.
                # DevExpress puede agregar filas de forma asíncrona tras pintar la primera; resolvemos
                # en cuanto dos lecturas consecutivas coinciden (~200ms típico), con tope de ~3s.
                # Protege mejor la red lenta que el sleep fijo y evita extraer una tabla incompleta.
                try:
                    page.locator(".dx-overlay-shader").first.wait_for(state="hidden", timeout=3000)
                except:
                    pass
                prev_count = -1
                for _ in range(30):  # máx ~3s
                    count = page.locator(".dx-data-row").count()
                    if count > 0 and count == prev_count:
                        break
                    prev_count = count
                    page.wait_for_timeout(100)
            except Exception as e:
                print(f"Advertencia al esperar las filas del grid (.dx-data-row): {e}")
            
            try:
                page.screenshot(path="debug_multiple_predios.png")
            except Exception:
                pass
            
            # Ejecutar script en el navegador para extraer la tabla
            table_data = page.evaluate("""() => {
                // Buscar encabezados en toda la página
                const headers = [];
                const headerCells = document.querySelectorAll('.dx-header-row td, .dx-datagrid-headers td, th');
                headerCells.forEach(cell => {
                    headers.push(cell.innerText.trim());
                });
                
                // Encabezados fallback basados en la vista de Apartado si no se encuentran
                if (headers.length === 0) {
                    headers.push("Numero cuenta", "Numero ficha", "Matricula", "Avaluo", "Direccion", "Deuda actual", "Cedula Catastral", "Estrato", "Destino economico");
                }
                
                const rows = [];
                // Obtener todas las filas de datos
                const rowElements = document.querySelectorAll('.dx-data-row');
                rowElements.forEach((row, index) => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length > 0) {
                        const rowData = {};
                        cells.forEach((cell, cellIndex) => {
                            const headerName = headers[cellIndex] || `col_${cellIndex}`;
                            rowData[headerName] = cell.innerText.trim();
                        });
                        rows.push({
                            index: index,
                            data: rowData
                        });
                    }
                });
                return rows;
            }""")
            
            return {
                "status": "multiple_predios",
                "predios": table_data,
                "session_data": session_data
            }

        # 2. Caso: Error de búsqueda
        if locator_error.count() > 0 and locator_error.first.is_visible():
            error_text = locator_error.first.inner_text()
            print(f"Error detectado en el portal: {error_text}")
            try:
                page.get_by_role("button", name="OK").click(timeout=3000)
            except Exception as click_err:
                print(f"No se pudo cerrar la modal de error: {click_err}")
            close_session_objects(session_data)
            return {"status": "error", "message": f"Error del portal: {error_text}"}

        # 3. Caso: Predio único (flujo regular)
        result = complete_invoice_generation(page, context, search_value, phone, email)
        close_session_objects(session_data)
        return result

    except Exception as e:
        try:
            page.screenshot(path="error_pantalla.png", full_page=True)
            print("Captura de pantalla de error guardada en error_pantalla.png")
        except Exception as se:
            print(f"No se pudo guardar captura de pantalla: {se}")
        print(f"Error durante el proceso RPA: {e}")
        close_session_objects(session_data)
        return {"status": "error", "message": str(e)}
    finally:
        # Cerrar el executor del captcha sin bloquear (wait=False): evita fugar un hilo por
        # cada petición. wait=False retorna de inmediato; el worker termina cuando acabe su poll.
        if executor is not None:
            executor.shutdown(wait=False)

def run_rpa_continue(session_data, predio_index, search_value, phone, email):
    """Phase 2: Use existing browser context to click on selected row and complete generation."""
    import threading
    print(f"THREAD DEBUG [continue]: Running in {threading.current_thread().name} (ID: {threading.current_thread().ident})")
    page = session_data["page"]
    context = session_data["context"]
    
    # Reset timestamp to avoid cleanup while running
    session_data["timestamp"] = time.time()

    try:
        print(f"Seleccionando predio {predio_index} en la tabla...")
        # Hacer clic en la fila correspondiente (específicamente en el primer td de la fila de datos)
        row_locator = page.locator(".dx-data-row").nth(predio_index)
        row_locator.locator("td").first.click()
        
        # Dar un momento para la selección
        page.wait_for_timeout(500)
        
        # Clic en Continuar
        btn_continuar = page.locator("#btnContinue").first
        btn_continuar.wait_for(state="visible", timeout=10000)
        btn_continuar.click()
        
        # Esperar a que cargue la Ventanilla de Atención
        # page.locator("text=Ventanilla de Atención").wait_for(state="visible", timeout=20000)
        
        # Ejecutar generación de factura
        result = complete_invoice_generation(page, context, search_value, phone, email)
        close_session_objects(session_data)
        return result
        
    except Exception as e:
        try:
            page.screenshot(path="error_pantalla_continue.png")
            print("Captura de pantalla de error guardada en error_pantalla_continue.png")
        except Exception as se:
            print(f"No se pudo guardar captura de pantalla: {se}")
        print(f"Error durante la continuación del proceso RPA: {e}")
        close_session_objects(session_data)
        return {"status": "error", "message": str(e)}

def run_rpa(search_type, search_value, phone, email):
    """Backwards compatible function running synchronous single-run flow."""
    res = run_rpa_start(search_type, search_value, phone, email)
    if res.get("status") == "multiple_predios":
        # If it hits multiple predios in backwards compatible mode, just select the first one and close
        session_data = res["session_data"]
        result = run_rpa_continue(session_data, 0, search_value, phone, email)
        return result
    return res
