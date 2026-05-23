import React from 'react';
import { Info } from 'lucide-react';
import logo from '../../assets/logo.png';
import styles from './FechasPagoView.module.css';

export default function FechasPagoView() {
  return (
    <div>
      {/* Logo */}
      <div className={styles.logoContainer}>
        <img src={logo} alt="Alcaldía de Apartadó" className={styles.kioskLogo} />
      </div>

      {/* Título */}
      <h2 className={styles.kioskViewTitle}>Fechas importantes 2026</h2>
      <p className={styles.kioskViewSubtitle}>
        Consulte el calendario tributario oficial para el municipio de Apartadó. Manténgase al día con sus obligaciones para evitar recargos y contribuir al progreso de nuestra ciudad.
      </p>

      {/* Tabla de fechas */}
      <div className={styles.tableResponsive}>
        <table className={styles.kioskTable}>
          <thead>
            <tr>
              <th>Trimestre</th>
              <th>Fecha Límite (2026)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Primer Trimestre</td>
              <td className={styles.dateHighlight}>31 de Marzo</td>
            </tr>
            <tr>
              <td>Segundo Trimestre</td>
              <td className={styles.dateHighlight}>30 de Junio</td>
            </tr>
            <tr>
              <td>Tercero Trimestre</td>
              <td className={styles.dateHighlight}>30 de Septiembre</td>
            </tr>
            <tr>
              <td>Cuarto Trimestre</td>
              <td className={styles.dateHighlight}>24 de Diciembre</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Banner Informativo */}
      <div className={styles.kioskAlertBanner}>
        <Info size={24} className={styles.bannerIcon} />
        <p>
          Recuerde que el pago oportuno permite financiar obras de infraestructura y programas sociales en Apartadó.
        </p>
      </div>
    </div>
  );
}
