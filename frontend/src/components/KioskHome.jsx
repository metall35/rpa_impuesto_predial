import React from 'react';
import { Calendar, ListOrdered, FileText, HelpCircle, Headset } from 'lucide-react';
import logo from '../assets/logo.png';
import styles from './KioskHome.module.css';

export default function KioskHome({ setView }) {
  return (
    <div className="text-center">
      {/* Logo de la Alcaldía */}
      <div className={styles.logoContainer}>
        <img src={logo} alt="Alcaldía de Apartadó" className={styles.kioskLogo} />
      </div>

      {/* Título de Bienvenida */}
      <h2 className={styles.kioskWelcomeTitle}>
        ¡Bienvenido a tu Centro de Ayuda de Trámites y Servicios!
      </h2>
      <p className={styles.kioskWelcomeSubtitle}>
        Estamos aquí para guiarte. ¿Qué gestión necesitas realizar hoy?
      </p>

      {/* Grid de 4 Botones principales */}
      <div className={styles.kioskGrid}>
        <button 
          onClick={() => setView('fechas_de_pago')} 
          className={styles.kioskCardBtn}
          id="btn-fechas-pago"
        >
          <Calendar className={styles.kioskCardIcon} size={48} />
          <span>Fechas de Pago</span>
        </button>

        <button 
          onClick={() => setView('guia_paso_a_paso')} 
          className={styles.kioskCardBtn}
          id="btn-guia-paso"
        >
          <ListOrdered className={styles.kioskCardIcon} size={48} />
          <span>Guía Paso a Paso</span>
        </button>

        <button 
          onClick={() => setView('copia_de_factura')} 
          className={styles.kioskCardBtn}
          id="btn-copia-factura"
        >
          <FileText className={styles.kioskCardIcon} size={48} />
          <span>Copia de tu factura</span>
        </button>

        <button 
          onClick={() => setView('preguntas_frecuentes')} 
          className={styles.kioskCardBtn}
          id="btn-preguntas-frecuentes"
        >
          <HelpCircle className={styles.kioskCardIcon} size={48} />
          <span>Preguntas frecuentes</span>
        </button>
      </div>

      {/* Botón de Asistencia Inferior */}
      <button 
        onClick={() => setView('asistencia')} 
        className={styles.kioskAssistBtn}
        id="btn-necesitas-asistencia"
      >
        <Headset size={24} />
        <span>¿Necesitas asistencia?</span>
      </button>
    </div>
  );
}
