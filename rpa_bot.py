import os
import time
from dotenv import load_dotenv
from twocaptcha import TwoCaptcha
# pyrefly: ignore [missing-import]
from playwright.sync_api import sync_playwright
import qrcode
import io
import base64

# Cargar variables de entorno del archivo .env
load_dotenv()

def imprimir_archivo(ruta_archivo):
    """Envia el archivo a la impresora predeterminada en Windows."""
    try:
        # Esto usa la asociación predeterminada de Windows para imprimir el archivo PDF
        # os.startfile(ruta_archivo, "print")
        print(f"Impresión automática temporalmente desactivada. Archivo guardado en: {ruta_archivo}")
    except Exception as e:
        print(f"Error al intentar imprimir: {e}")

def run_rpa(search_type, search_value, phone, email):
    # Configurar resolvedor de 2Captcha
    api_key = os.getenv("TWOCAPTCHA_API_KEY")
    if not api_key:
        print("ADVERTENCIA: No se encontró la API Key de 2Captcha en el archivo .env")
        solver = None
    else:
        solver = TwoCaptcha(api_key)
    
    with sync_playwright() as p:
        # Para depuración local, podrías cambiar headless=False y resolver el captcha a mano.
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        try:
            print("Navegando al portal...")
            # Usamos wait_until="domcontentloaded" para evitar quedar bloqueados por assets externos lentos
            page.goto("https://oficinavirtual.apartado-antioquia.gov.co/Predial/Index", wait_until="domcontentloaded", timeout=60000)
            
            # Esperar a que la opción de búsqueda esté visible antes de interactuar
            page.get_by_text(search_type, exact=True).wait_for(state="visible", timeout=15000)

            # 1. Seleccionar tipo de búsqueda (Ficha Catastral, Número Cuenta, Propietario)
            # Intentamos hacer clic en el texto del label o radio button
            page.get_by_text(search_type, exact=True).click()
            
            # 2. Escribir el código a buscar.
            # Como no tenemos el ID exacto del input, usamos un selector genérico para el input de texto visible ahí.
            # Normalmente estos inputs tienen class="form-control" o están bajo una sección específica.
            page.locator('input[type="text"]').first.fill(search_value)

            if solver:
                print("Resolviendo reCAPTCHA con 2Captcha...")
                try:
                    # Extraer sitekey dinámicamente o usar la por defecto
                    sitekey_element = page.locator(".g-recaptcha")
                    if sitekey_element.count() > 0:
                        sitekey = sitekey_element.get_attribute("data-sitekey")
                    else:
                        sitekey = "6LcfN70UAAAAADa89KIZRMMo8CWSXPrOVsElAZd_"
                    
                    print(f"Sitekey detectada: {sitekey}")
                    print("Enviando captcha a 2Captcha (puede tomar de 15 a 30 segundos)...")
                    
                    result = solver.recaptcha(
                        sitekey=sitekey,
                        url=page.url
                    )
                    token = result['code']
                    print("¡Captcha resuelto exitosamente por 2Captcha!")
                    
                    # Inyectar el token en el text area de respuesta de recaptcha
                    page.evaluate(f'document.getElementById("g-recaptcha-response").innerHTML = "{token}";')
                    page.evaluate(f'document.getElementById("g-recaptcha-response").value = "{token}";')
                    
                    # También inyectamos en cualquier campo con name "g-recaptcha-response"
                    page.evaluate(f'document.getElementsByName("g-recaptcha-response")[0].value = "{token}";')
                    
                    # Esperar 1 segundo para asegurar la inyección antes de enviar
                    time.sleep(1)
                except Exception as e:
                    raise Exception(f"Error al resolver el captcha a través de 2Captcha: {e}")
            else:
                print("Intentando hacer clic en el reCAPTCHA de forma manual/física...")
                try:
                    # El reCAPTCHA siempre está en un iframe
                    recaptcha_iframe = page.frame_locator("iframe[title*='reCAPTCHA']")
                    recaptcha_iframe.locator(".recaptcha-checkbox-border").click(timeout=5000)
                    # Damos unos segundos para ver si nos da el check verde automático
                    time.sleep(3)
                except Exception as e:
                    print("No se pudo interactuar con el reCAPTCHA o no apareció:", e)
            
            # 3. Clic en Buscar
            page.get_by_role("button", name="Buscar").click()

            # Esperar a que cargue la siguiente página (Ventana de Atención) o aparezca un error
            print("Esperando respuesta del portal...")
            try:
                locator_exito = page.locator("text=Ventanilla de Atención")
                locator_error = page.locator("text=No se encontró el valor de búsqueda")
                locator_info = page.locator("text=Información")
                
                # Combinar con OR
                locator_espera = locator_exito.or_(locator_error).or_(locator_info)
                locator_espera.wait_for(state="visible", timeout=15000)
            except Exception as e:
                raise Exception("Tiempo de espera agotado esperando la respuesta del portal.")
            
            # Si se muestra un cuadro de diálogo de error de búsqueda
            if locator_error.count() > 0 and locator_error.first.is_visible():
                error_text = locator_error.first.inner_text()
                print(f"Error detectado en el portal: {error_text}")
                # Intentar hacer clic en el botón OK de la modal para cerrarla
                try:
                    page.get_by_role("button", name="OK").click(timeout=3000)
                except Exception as click_err:
                    print(f"No se pudo cerrar la modal de error: {click_err}")
                return {"status": "error", "message": f"Error del portal: {error_text}"}

            # 4. Pantalla de información general (Imagen 2) -> Clic en Generar Factura
            print("Cargó información del predio. Generando factura...")
            page.screenshot(path="debug_pantalla_2.png") # Guardamos captura por si falla
            # Seleccionamos cualquier elemento (sea input, span, div, a o button) que tenga exactamente el texto/valor "Generar Factura"
            page.locator("text='Generar Factura'").first.click()

            # 5. Modal de Período de Generación (Imagen 3)
            print("Modal de periodo detectado. Confirmando generación...")
            try:
                # Esperar a que la modal sea visible buscando su título
                page.locator("text=Seleccione el Período de Generación").wait_for(state="visible", timeout=15000)
            except Exception as e:
                raise Exception("No apareció la modal de selección de período.")
            
            # Buscar el botón "Generar Factura" dentro de la modal (admite Bootstrap y DevExtreme dxPopup)
            btn_generar_modal = page.locator(".modal-dialog, .modal-content, .dx-overlay-content, .dx-popup-content, [role='dialog']").locator("text=Generar Factura").first
            btn_generar_modal.wait_for(state="visible", timeout=10000)
            btn_generar_modal.click()

            # Esperar a que la modal se cierre por completo
            try:
                page.locator(".dx-overlay-content, .dx-popup-content, [role='dialog']").wait_for(state="hidden", timeout=10000)
            except:
                pass
            
            # Esperar a que desaparezca cualquier panel de carga de DevExtreme (.dx-loadpanel)
            print("Esperando a que terminen de cargar los elementos de la página (dx-loadpanel)...")
            try:
                page.locator(".dx-loadpanel:visible, .dx-loadpanel-content:visible").first.wait_for(state="hidden", timeout=15000)
            except Exception as le:
                print(f"Advertencia al esperar el panel de carga: {le}")
            
            # Espera de seguridad adicional para que la vista se actualice completamente
            print("Esperando 3 segundos adicionales para estabilización de la vista...")
            time.sleep(3)
            
            # 5.5. Clic en "Generar Factura" en la página principal para avanzar a la pantalla de contacto (Imagen 4)
            print("Haciendo clic en 'Generar Factura' de la página principal para avanzar...")
            btn_generar_principal = page.locator("text=Generar Factura").first
            btn_generar_principal.wait_for(state="visible", timeout=10000)
            btn_generar_principal.click()

            # 6. Pantalla final de regenerar/imprimir (Imagen 4)
            print("Esperando a que la pantalla de impresión ('Imprimir Factura') sea visible...")
            try:
                # Esperar a que el botón "Imprimir Factura" esté visible
                page.locator("text=Imprimir Factura").wait_for(state="visible", timeout=8000)
            except Exception:
                print("No apareció el botón 'Imprimir Factura'. Es posible que el clic anterior no se haya registrado. Reintentando...")
                try:
                    # Tomar captura para depurar
                    page.screenshot(path="reintento_generar_factura.png")
                except:
                    pass
                # Reintentar hacer clic en el botón principal
                btn_generar_principal.click()
                page.locator("text=Imprimir Factura").wait_for(state="visible", timeout=15000)
            # Esperar a que los datos de la factura se carguen dinámicamente desde el portal
            print("Esperando a que se carguen los datos de la factura (números, vigencia, total)...")
            factura_cargada = False
            for attempt in range(40):
                try:
                    inputs = page.locator("input")
                    count = inputs.count()
                    for i in range(count):
                        val = inputs.nth(i).input_value()
                        # Si algún input contiene un signo de pesos ($) o un número de factura largo, ya cargó la info
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
            
            print("Llenando datos de contacto...")
            # Asegurar que los campos estén visibles antes de escribir
            page.get_by_label("Teléfono").wait_for(state="visible", timeout=5000)
            page.get_by_label("Teléfono").fill(phone)
            page.get_by_label("Correo Electrónico").wait_for(state="visible", timeout=5000)
            page.get_by_label("Correo Electrónico").fill(email)

            # Descargando factura...
            print("Descargando factura...")
            # Monitorear tanto el evento de descarga estándar como la apertura de nuevas pestañas (popups)
            download_obj = None
            popup_page = None
            
            def on_download(d):
                nonlocal download_obj
                download_obj = d
                print(f"Evento de descarga detectado por Playwright: {d.suggested_filename}")
                
            def on_popup(p):
                nonlocal popup_page
                popup_page = p
                print(f"Evento de popup detectado por Playwright: {p.url}")
                
            page.on("download", on_download)
            context.on("page", on_popup)
            
            # Asegurar que el botón sea visible y clickeable
            btn_imprimir = page.locator("text='Imprimir Factura'").first
            btn_imprimir.wait_for(state="visible", timeout=10000)
            
            # Guardamos captura antes de dar clic
            try:
                page.screenshot(path="antes_de_imprimir.png")
            except:
                pass

            # Esperar a que aparezca la modal de Éxito con el botón de Descargar Recibo (con reintentos de clic)
            print("Esperando a que aparezca el botón 'Descargar recibo' en el popup de Éxito...")
            btn_descargar = page.locator("text='Descargar recibo'").first
            
            exito_modal_visible = False
            for retry in range(3):
                print(f"Haciendo clic en el botón 'Imprimir Factura' (Intento {retry + 1})...")
                try:
                    btn_imprimir.click()
                except Exception as click_err:
                    print(f"Error al hacer clic en Imprimir Factura: {click_err}")
                
                # Esperamos a ver si aparece el botón 'Descargar recibo'
                try:
                    btn_descargar.wait_for(state="visible", timeout=6000)
                    exito_modal_visible = True
                    break
                except Exception:
                    print("No apareció el botón 'Descargar recibo' aún. Reintentando...")
            
            if not exito_modal_visible:
                # Guardamos captura final en caso de error
                try:
                    page.screenshot(path="error_imprimir_factura.png")
                except:
                    pass
                raise Exception("No apareció el popup de éxito con el botón 'Descargar recibo' después de varios intentos.")

            # --- NUEVO FLUJO DE ORDEN (Descargar la factura primero, bloqueando redirecciones, y luego pagar) ---
            
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
            print("Haciendo clic en el botón 'Descargar recibo'...")
            btn_descargar.click()

            # Esperar hasta 40 segundos a que ocurra uno de los dos eventos de descarga/popup
            print("Esperando descarga o popup del PDF (hasta 40 segundos)...")
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
            
            # Remover el interceptor de rutas
            try:
                page.unroute("**/*", intercept_redirects)
            except Exception as e:
                print(f"Advertencia al remover interceptor: {e}")
            
            if not file_saved:
                raise Exception("No se detectó descarga ni apertura de PDF después de hacer clic en Imprimir Factura.")

            # Imprimir el archivo (local/servidor)
            imprimir_archivo(file_path)
            
            # 3. Remover la modal de éxito de PDF (SweetAlert) para revelar la página de fondo y el botón de pago
            print("Removiendo la modal de éxito de PDF para interactuar con la página de fondo...")
            page.evaluate("""
                const swal = document.querySelector('.swal2-container');
                if (swal) {
                    swal.remove();
                }
                document.body.classList.remove('swal2-shown', 'swal2-height-auto');
                document.documentElement.classList.remove('swal2-shown', 'swal2-height-auto');
            """)
            
            # 4. Capturar el enlace de pago en línea (PSE) y generar el QR
            payment_url = None
            payment_qr = None
            print("Intentando capturar enlace de pago en línea (PSE)...")
            try:
                btn_pagar = page.locator("text='Pagar en Línea'").first
                btn_pagar.wait_for(state="visible", timeout=10000)
                
                with page.expect_popup(timeout=20000) as popup_info:
                    btn_pagar.click()
                
                payment_popup = popup_info.value
                # Esperar a que la URL de pago cambie de about:blank o se cargue
                for _ in range(20):
                    if payment_popup.url and payment_popup.url != "about:blank":
                        break
                    page.wait_for_timeout(500)
                payment_url = payment_popup.url
                print(f"URL de pago en línea capturada: {payment_url}")
                payment_popup.close()
                
                # Cerrar la modal SweetAlert de pago que se genera tras el clic para dejar el DOM limpio
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

        except Exception as e:
            try:
                page.screenshot(path="error_pantalla.png")
                print("Captura de pantalla de error guardada en error_pantalla.png")
            except Exception as se:
                print(f"No se pudo guardar captura de pantalla: {se}")
            print(f"Error durante el proceso RPA: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            browser.close()
