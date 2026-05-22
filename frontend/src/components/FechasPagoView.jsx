import React from 'react';
import { Info } from 'lucide-react';
import logo from '../assets/logo.png';

export default function FechasPagoView() {
  return (
    <div className="fechas-pago-view">
      {/* Logo */}
      <div className="logo-container">
        <img src={logo} alt="Alcaldía de Apartadó" className="kiosk-logo" />
      </div>

      {/* Título */}
      <h2 className="kiosk-view-title">Fechas importantes 2026</h2>
      <p className="kiosk-view-subtitle">
        Consulte el calendario tributario oficial para el municipio de Apartadó. Manténgase al día con sus obligaciones para evitar recargos y contribuir al progreso de nuestra ciudad.
      </p>

      {/* Tabla de fechas */}
      <div className="table-responsive">
        <table className="kiosk-table">
          <thead>
            <tr>
              <th>Trimestre</th>
              <th>Fecha Límite (2026)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Primer Trimestre</td>
              <td className="date-highlight">31 de Marzo</td>
            </tr>
            <tr>
              <td>Segundo Trimestre</td>
              <td className="date-highlight">30 de Junio</td>
            </tr>
            <tr>
              <td>Tercero Trimestre</td>
              <td className="date-highlight">30 de Septiembre</td>
            </tr>
            <tr>
              <td>Cuarto Trimestre</td>
              <td className="date-highlight">24 de Diciembre</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Banner Informativo */}
      <div className="kiosk-alert-banner success">
        <Info size={24} className="banner-icon" />
        <p>
          Recuerde que el pago oportuno permite financiar obras de infraestructura y programas sociales en Apartadó.
        </p>
      </div>
    </div>
  );
}
