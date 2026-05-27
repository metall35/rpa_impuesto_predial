import { ShieldCheck } from 'lucide-react';
import logo from '../../assets/logo.png';
import styles from './GuiaPasoPasoView.module.css';

export default function GuiaPasoPasoView() {
  return (
    <div>

      <div className={styles.logoContainer}>
        <img src={logo} alt="Alcaldía de Apartadó" className={styles.kioskLogo} />
      </div>

      <h2 className={styles.kioskViewTitle}>GUÍA PASO A PASO</h2>
      <h3 className={styles.kioskViewSubtitleAccent}>PAGO DE IMPUESTO PREDIAL</h3>

      <div className={styles.stepsGrid}>
        <div className={styles.stepCard}>
          <div className={styles.stepNumber}>1</div>
          <div className={styles.stepContent}>
            <h4>Sitio Web</h4>
            <p>
              Ingresa al sitio web oficial de la Alcaldía de Apartadó desde cualquier dispositivo.
            </p>
          </div>
        </div>

        <div className={styles.stepCard}>
          <div className={styles.stepNumber}>2</div>
          <div className={styles.stepContent}>
            <h4>Localiza el Trámite</h4>
            <p>
              Busca la opción <strong className={styles.textHighlight}>"Impuesto Predial"</strong> en la sección de "Trámites y Servicios".
            </p>
          </div>
        </div>

        <div className={styles.stepCard}>
          <div className={styles.stepNumber}>3</div>
          <div className={styles.stepContent}>
            <h4>Identificación</h4>
            <p>
              Selecciona si deseas buscar por código predial o número de cuenta para iniciar.
            </p>
          </div>
        </div>

        <div className={styles.stepCard}>
          <div className={styles.stepNumber}>4</div>
          <div className={styles.stepContent}>
            <h4>Pago Electrónico</h4>
            <p>
              Finaliza tu trámite pagando de forma segura en línea usando el botón de <strong className={styles.textHighlight}>PSE</strong>.
            </p>
          </div>
        </div>
      </div>

      <div className={styles.kioskAlertBanner}>
        <ShieldCheck size={28} className={styles.bannerIcon} />
        <div className={styles.bannerText}>
          <strong>Trámite Seguro</strong>
          <p>Contribuir al desarrollo de Apartadó es más fácil y rápido desde nuestros canales digitales.</p>
        </div>
      </div>
    </div>
  );
}
