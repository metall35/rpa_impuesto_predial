import { FileText, BookOpen, FileCheck, Lightbulb } from 'lucide-react';
import logo from '../../assets/logo.png';
import styles from './AsistenciaView.module.css';

export default function AsistenciaView() {
  return (
    <div className={styles.asistenciaContainer}>
      {/* Logo */}
      <div className={styles.logoContainer}>
        <img src={logo} alt="Alcaldía de Apartadó" className={styles.kioskLogo} />
      </div>

      {/* Header Section */}
      <div className={styles.headerSection}>
        <h2 className={styles.kioskViewTitle}>
          ¿Cómo consultar y pagar tu Impuesto Predial?
        </h2>
        <p className={styles.kioskViewSubtitle}>
          Si tienes una propiedad en el municipio de Apartadó y necesitas descargar tu recibo o pagar tu Impuesto Predial en línea, el proceso es muy sencillo. Solo sigue estos pasos:
        </p>
      </div>

      {/* Two Column Layout to prevent scroll */}
      <div className={styles.asistenciaContentRow}>
        {/* Left Column: Main Step */}
        <div className={styles.asistenciaLeftCol}>
          <div className={styles.mainStepCard}>
            <div className={styles.stepHeader}>
              <div className={styles.stepNumber}>1</div>
              <h3>Ten a la mano tu Ficha Catastral</h3>
            </div>
            <p className={styles.stepDescription}>
              Vas a necesitar el número de identificación de tu inmueble (Ficha o Cédula Catastral).
            </p>

            {/* Tip Box */}
            <div className={styles.tipBox}>
              <Lightbulb className={styles.tipIcon} size={18} />
              <div className={styles.tipContent}>
                <strong>Consejo útil:</strong> Si no sabes cuál es, búscala en un recibo de años anteriores o en las escrituras.
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Where to find it list */}
        <div className={styles.asistenciaRightCol}>
          <div className={styles.placesCard}>
            <h3>¿Dónde encontrar tu Cédula o Ficha Catastral?</h3>
            
            <div className={styles.placesList}>
              {/* Item 1 */}
              <div className={styles.placeItem}>
                <div className={styles.placeIconWrapper}>
                  <FileText size={18} />
                </div>
                <div className={styles.placeText}>
                  <strong>Recibos anteriores:</strong> Busca "Referencia Catastral", "Cédula Catastral", "No. de Ficha" o "CHIP".
                </div>
              </div>

              {/* Item 2 */}
              <div className={styles.placeItem}>
                <div className={styles.placeIconWrapper}>
                  <FileCheck size={18} />
                </div>
                <div className={styles.placeText}>
                  <strong>Certificado de Tradición:</strong> Justo debajo de la Matrícula Inmobiliaria.
                </div>
              </div>

              {/* Item 3 */}
              <div className={styles.placeItem}>
                <div className={styles.placeIconWrapper}>
                  <BookOpen size={18} />
                </div>
                <div className={styles.placeText}>
                  <strong>Escritura Pública:</strong> Busca en las primeras páginas (descripción física y linderos).
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
