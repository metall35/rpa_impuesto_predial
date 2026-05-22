import React from 'react';

export default function LoadingView({ activeStep }) {
  // Mapeo de pasos a textos requeridos por el usuario
  const stepsText = {
    1: 'Iniciando proceso...',
    2: 'Buscando factura...',
    3: 'Generando factura...',
    4: 'Generando link de pago...',
    5: 'Finalizado'
  };

  // Porcentaje de progreso para cada paso
  const progressPercentage = {
    1: 20,
    2: 45,
    3: 70,
    4: 90,
    5: 100
  };

  const currentStatus = stepsText[activeStep] || 'Procesando...';
  const percentage = progressPercentage[activeStep] || 10;

  return (
    <div id="loadingView" className="view active">
      <div className="loading-container">
        {/* Spinner animado superior */}
        <div className="spinner-outer">
          <div className="spinner-inner"></div>
        </div>

        {/* Textos de Estado */}
        <div className="kiosk-loading-header">
          <h3 className="kiosk-loading-title">Automatización en Progreso</h3>
          <p className="kiosk-loading-subtitle">
            El sistema está realizando la consulta de manera inteligente en el portal de la alcaldía.
          </p>
        </div>

        {/* Contenedor de la barra de progreso */}
        <div className="kiosk-progress-container">
          <div className="kiosk-progress-label-row">
            <span className="kiosk-progress-status">{currentStatus}</span>
            <span className="kiosk-progress-percentage">{percentage}%</span>
          </div>
          
          <div className="kiosk-progress-track">
            <div 
              className="kiosk-progress-fill" 
              style={{ width: `${percentage}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
}
