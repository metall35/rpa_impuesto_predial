import React from 'react';
import { ShieldCheck } from 'lucide-react';
import logo from '../assets/logo.png';

export default function GuiaPasoPasoView() {
  return (
    <div className="guia-paso-view">
      {/* Logo */}
      <div className="logo-container">
        <img src={logo} alt="Alcaldía de Apartadó" className="kiosk-logo" />
      </div>

      {/* Título */}
      <h2 className="kiosk-view-title font-bold">GUÍA PASO A PASO</h2>
      <h3 className="kiosk-view-subtitle-accent">PAGO DE IMPUESTO PREDIAL</h3>

      {/* Cuadrícula 2x2 de Pasos */}
      <div className="steps-grid">
        <div className="step-card">
          <div className="step-number">1</div>
          <div className="step-content">
            <h4>Sitio Web</h4>
            <p>
              Ingresa al sitio web oficial de la Alcaldía de Apartadó desde cualquier dispositivo.
            </p>
          </div>
        </div>

        <div className="step-card">
          <div className="step-number">2</div>
          <div className="step-content">
            <h4>Localiza el Trámite</h4>
            <p>
              Busca la opción <strong className="text-highlight">"Impuesto Predial"</strong> en la sección de "Trámites y Servicios".
            </p>
          </div>
        </div>

        <div className="step-card">
          <div className="step-number">3</div>
          <div className="step-content">
            <h4>Identificación</h4>
            <p>
              Selecciona si deseas buscar por código predial o número de cuenta para iniciar.
            </p>
          </div>
        </div>

        <div className="step-card">
          <div className="step-number">4</div>
          <div className="step-content">
            <h4>Pago Electrónico</h4>
            <p>
              Finaliza tu trámite pagando de forma segura en línea usando el botón de <strong className="text-highlight">PSE</strong>.
            </p>
          </div>
        </div>
      </div>

      {/* Banner de Trámite Seguro */}
      <div className="kiosk-alert-banner success border-left-green">
        <ShieldCheck size={28} className="banner-icon text-green" />
        <div className="banner-text">
          <strong>Trámite Seguro</strong>
          <p>Contribuir al desarrollo de Apartadó es más fácil y rápido desde nuestros canales digitales.</p>
        </div>
      </div>
    </div>
  );
}
