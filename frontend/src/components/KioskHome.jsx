import React from 'react';
import { Calendar, ListOrdered, FileText, HelpCircle, Headset } from 'lucide-react';
import logo from '../assets/logo.png';

export default function KioskHome({ setView }) {
  return (
    <div className="kiosk-home text-center">
      {/* Logo de la Alcaldía */}
      <div className="logo-container">
        <img src={logo} alt="Alcaldía de Apartadó" className="kiosk-logo" />
      </div>

      {/* Título de Bienvenida */}
      <h2 className="kiosk-welcome-title">
        ¡Bienvenido a tu Centro de Ayuda de Trámites y Servicios!
      </h2>
      <p className="kiosk-welcome-subtitle">
        Estamos aquí para guiarte. ¿Qué gestión necesitas realizar hoy?
      </p>

      {/* Grid de 4 Botones principales */}
      <div className="kiosk-grid">
        <button 
          onClick={() => setView('fechas_de_pago')} 
          className="kiosk-card-btn"
          id="btn-fechas-pago"
        >
          <Calendar className="kiosk-card-icon" size={48} />
          <span>Fechas de Pago</span>
        </button>

        <button 
          onClick={() => setView('guia_paso_a_paso')} 
          className="kiosk-card-btn"
          id="btn-guia-paso"
        >
          <ListOrdered className="kiosk-card-icon" size={48} />
          <span>Guía Paso a Paso</span>
        </button>

        <button 
          onClick={() => setView('copia_de_factura')} 
          className="kiosk-card-btn"
          id="btn-copia-factura"
        >
          <FileText className="kiosk-card-icon" size={48} />
          <span>Copia de tu factura</span>
        </button>

        <button 
          onClick={() => setView('preguntas_frecuentes')} 
          className="kiosk-card-btn"
          id="btn-preguntas-frecuentes"
        >
          <HelpCircle className="kiosk-card-icon" size={48} />
          <span>Preguntas frecuentes</span>
        </button>
      </div>

      {/* Botón de Asistencia Inferior */}
      <button 
        onClick={() => setView('asistencia')} 
        className="kiosk-assist-btn"
        id="btn-necesitas-asistencia"
      >
        <Headset size={24} />
        <span>¿Necesitas asistencia?</span>
      </button>
    </div>
  );
}
