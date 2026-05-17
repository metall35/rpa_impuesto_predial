import os
import time
# pyrefly: ignore [missing-import]
from playwright.sync_api import sync_playwright

def imprimir_archivo(ruta_archivo):
    """Envia el archivo a la impresora predeterminada en Windows."""
    try:
        # Esto usa la asociación predeterminada de Windows para imprimir el archivo PDF
        os.startfile(ruta_archivo, "print")
        print(f"Enviado a imprimir: {ruta_archivo}")
    except Exception as e:
        print(f"Error al intentar imprimir: {e}")

def run_rpa(search_type, search_value, phone, email):
    # Notas importantes sobre reCAPTCHA:
    # Como solicitaste que corra 100% por detrás (headless), el reCAPTCHA bloqueará el proceso
    # a menos que el portal tenga seguridad baja o uses un servicio como 2Captcha/Anti-captcha.
    # Si el portal exige reCAPTCHA, la ejecución en 'headless=True' fallará en la primera pantalla.
    
    with sync_playwright() as p:
        # Para depuración local, podrías cambiar headless=False y resolver el captcha a mano.
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        try:
            print("Navegando al portal...")
            page.goto("https://oficinavirtual.apartado-antioquia.gov.co/Predial/Index")

            # 1. Seleccionar tipo de búsqueda (Ficha Catastral, Número Cuenta, Propietario)
            # Intentamos hacer clic en el texto del label o radio button
            page.get_by_text(search_type, exact=True).click()
            
            # 2. Escribir el código a buscar.
            # Como no tenemos el ID exacto del input, usamos un selector genérico para el input de texto visible ahí.
            # Normalmente estos inputs tienen class="form-control" o están bajo una sección específica.
            page.locator('input[type="text"]').first.fill(search_value)

            print("Intentando hacer clic en el reCAPTCHA...")
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

            # Esperar a que cargue la siguiente página (Ventana de Atención)
            # Cambiamos el texto a 'Ventanilla de Atención' para no confundir con las instrucciones
            page.wait_for_selector("text='Ventanilla de Atención'", timeout=15000)
            
            # 4. Pantalla de información general (Imagen 2) -> Clic en Generar Factura
            print("Cargó información del predio. Generando factura...")
            page.screenshot(path="debug_pantalla_2.png") # Guardamos captura por si falla
            # Seleccionamos cualquier elemento (sea input, span, div, a o button) que tenga exactamente el texto/valor "Generar Factura"
            page.locator("text='Generar Factura'").first.click()

            # 5. Modal de Período de Generación (Imagen 3)
            # Como indicaste, dejamos el periodo predeterminado (el último) y solo damos "Generar Factura" de nuevo
            print("Modal de periodo detectado. Confirmando generación...")
            page.wait_for_selector(".modal-content text='Generar Factura', .modal-dialog text='Generar Factura', text='Generar Factura'", timeout=15000)
            # Al abrirse la modal, usualmente el último botón visible de generar factura es el de la modal
            page.locator("text='Generar Factura'").last.click()

            # 6. Pantalla final de regenerar/imprimir (Imagen 4)
            page.wait_for_selector("text=Imprimir Factura", timeout=15000)
            
            print("Llenando datos de contacto...")
            # Como los labels dicen "Teléfono *" y "Correo Electrónico *", usamos sus placeholders o un selector aproximado
            # Playwright permite ubicar inputs según el texto cercano (label)
            page.get_by_label("Teléfono").fill(phone)
            page.get_by_label("Correo Electrónico").fill(email)

            print("Descargando factura...")
            # Interceptamos la descarga del PDF
            with page.expect_download() as download_info:
                page.locator("text='Imprimir Factura'").first.click()
            
            download = download_info.value
            
            # Guardamos el archivo en la carpeta actual
            descargas_dir = os.path.join(os.getcwd(), "facturas_descargadas")
            os.makedirs(descargas_dir, exist_ok=True)
            
            file_path = os.path.join(descargas_dir, download.suggested_filename)
            download.save_as(file_path)
            
            print(f"Factura descargada exitosamente en: {file_path}")

            # 7. Imprimir automáticamente
            imprimir_archivo(file_path)

            return {"status": "success", "message": "Factura descargada e impresa correctamente.", "file": file_path}

        except Exception as e:
            print(f"Error durante el proceso RPA: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            browser.close()
