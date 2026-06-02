import os
import time
from dotenv import load_dotenv
from twocaptcha import TwoCaptcha
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
        if "browser" in session_data and session_data["browser"]:
            try:
                session_data["browser"].close()
            except:
                pass
        if "playwright" in session_data and session_data["playwright"]:
            try:
                session_data["playwright"].stop()
            except:
                pass
    except Exception as e:
        print(f"Error al cerrar los objetos de la sesión Playwright: {e}")

def complete_invoice_generation(page, context, search_value, phone, email):
    """Helper to complete the invoice generation after selecting/landing on a single predio."""
    print("Cargó información del predio. Generando factura...")
    page.locator("text='Generar Factura'").first.click()

    try:
        page.locator("text=Seleccione el Período de Generación").wait_for(state="visible", timeout=15000)
    except Exception as e:
        raise Exception("No apareció la modal de selección de período.")
    
    btn_generar_modal = page.locator(".modal-dialog, .modal-content, .dx-overlay-content, .dx-popup-content, [role='dialog']").locator("text=Generar Factura").first
    btn_generar_modal.wait_for(state="visible", timeout=10000)
    btn_generar_modal.click()

    try:
        page.locator(".dx-overlay-content, .dx-popup-content, [role='dialog']").wait_for(state="hidden", timeout=10000)
    except:
        pass
    
    try:
        page.locator(".dx-loadpanel:visible, .dx-loadpanel-content:visible").first.wait_for(state="hidden", timeout=15000)
    except Exception as le:
        print(f"Advertencia al esperar el panel de carga: {le}")
    
    # Espera a que cargue
    print("Esperando 3 segundos...")
    time.sleep(3)
    
    btn_generar_principal = page.locator("text=Generar Factura").first
    btn_generar_principal.wait_for(state="visible", timeout=10000)
    btn_generar_principal.click()

    try:
        page.locator("text=Imprimir Factura").wait_for(state="visible", timeout=8000)
    except Exception:
        print("No apareció el botón 'Imprimir Factura'. Es posible que el clic anterior no se haya registrado. Reintentando...")
        btn_generar_principal.click()
        page.locator("text=Imprimir Factura").wait_for(state="visible", timeout=15000)
        
    print("Esperando a que se carguen los datos...")
    factura_cargada = False
    for attempt in range(40):
        try:
            inputs = page.locator("input")
            count = inputs.count()
            for i in range(count):
                val = inputs.nth(i).input_value()
                # comprueba si hay datos
                if "$" in val or (val.isdigit() and len(val) >= 5):
                    print(f"¡Datos de factura detectados! Valor encontrado: {val}")
                    factura_cargada = True
                    break
        except Exception as e:
            print(f"Error al leer inputs: {e}")
        if factura_cargada:
            break
        page.wait_for_timeout(500)
    
    if not factura_cargada:
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
    
    # Asegurar que el botón sea visible y clickeable
    btn_imprimir = page.locator("text='Imprimir Factura'").first
    btn_imprimir.wait_for(state="visible", timeout=10000)

    # Esperar a que aparezca la modal de Éxito con el botón
    btn_descargar = page.locator("text='Descargar recibo'").first
    
    exito_modal_visible = False
    for retry in range(3):
        print(f"Haciendo clic en el botón 'Imprimir Factura' (Intento {retry + 1})...")
        try:
            btn_imprimir.click()
        except Exception as click_err:
            print(f"Error al hacer clic en Imprimir Factura: {click_err}")
        
        try:
            btn_descargar.wait_for(state="visible", timeout=6000)
            exito_modal_visible = True
            break
        except Exception:
            print("No apareció el botón 'Descargar recibo' aún. Reintentando...")
    
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

    for _ in range(80):
        page.wait_for_timeout(500)
        if download_obj or popup_page:
            break
    
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
        for _ in range(20):
            if payment_popup.url and payment_popup.url != "about:blank":
                break
            page.wait_for_timeout(500)
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

    return {
        "status": "success", 
        "message": "Factura descargada exitosamente.", 
        "file": file_path,
        "filename": filename,
        "payment_url": payment_url,
        "payment_qr": payment_qr
    }

def run_rpa_start(search_type, search_value, phone, email):
    """Phase 1: Start playwright, solve captcha, submit search, check for multiple predios."""
    api_key = os.getenv("TWOCAPTCHA_API_KEY")
    if not api_key:
        print("ADVERTENCIA: No se encontró la API Key de 2Captcha en el archivo .env")
        solver = None
    else:
        solver = TwoCaptcha(api_key)
    
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    session_data = {
        "playwright": p,
        "browser": browser,
        "context": context,
        "page": page,
        "timestamp": time.time()
    }

    try:
        print("Navegando al portal...")
        page.goto("https://oficinavirtual.apartado-antioquia.gov.co/Predial/Index", wait_until="domcontentloaded", timeout=60000)
        
        page.get_by_text(search_type, exact=True).wait_for(state="visible", timeout=15000)
        page.get_by_text(search_type, exact=True).click()
        
        page.locator('input[type="text"]').first.fill(search_value)

        # captcha
        if solver:
            print("Resolviendo reCAPTCHA con 2Captcha...")
            try:
                sitekey_element = page.locator(".g-recaptcha")
                if sitekey_element.count() > 0:
                    sitekey = sitekey_element.get_attribute("data-sitekey")
                else:
                    sitekey = "6LcfN70UAAAAADa89KIZRMMo8CWSXPrOVsElAZd_"
                
                print(f"Sitekey detectada: {sitekey}")
                print("Enviando captcha a 2Captcha...")
                
                result = solver.recaptcha(
                    sitekey=sitekey,
                    url=page.url
                )
                token = result['code']
                print("¡Captcha resuelto exitosamente por 2Captcha!")
                
                page.evaluate(f'document.getElementById("g-recaptcha-response").innerHTML = "{token}";')
                page.evaluate(f'document.getElementById("g-recaptcha-response").value = "{token}";')
                page.evaluate(f'document.getElementsByName("g-recaptcha-response")[0].value = "{token}";')
                time.sleep(1)
            except Exception as e:
                raise Exception(f"Error al resolver el captcha a través de 2Captcha: {e}")
        else:
            print("Intentando hacer clic en el reCAPTCHA de forma manual/física...")
            try:
                recaptcha_iframe = page.frame_locator("iframe[title*='reCAPTCHA']")
                recaptcha_iframe.locator(".recaptcha-checkbox-border").click(timeout=5000)
                time.sleep(3)
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
                page.locator(".dx-data-row").first.wait_for(state="visible", timeout=15000)
            except Exception as e:
                print(f"Advertencia al esperar las filas del grid: {e}")
            
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
            page.screenshot(path="error_pantalla.png")
            print("Captura de pantalla de error guardada en error_pantalla.png")
        except Exception as se:
            print(f"No se pudo guardar captura de pantalla: {se}")
        print(f"Error durante el proceso RPA: {e}")
        close_session_objects(session_data)
        return {"status": "error", "message": str(e)}

def run_rpa_continue(session_data, predio_index, search_value, phone, email):
    """Phase 2: Use existing browser context to click on selected row and complete generation."""
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
        page.locator("text=Ventanilla de Atención").wait_for(state="visible", timeout=20000)
        
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
