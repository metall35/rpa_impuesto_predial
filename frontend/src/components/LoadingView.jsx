import React from 'react';

export default function LoadingView({ activeStep }) {
  const steps = [
    { id: 1, text: 'Inicializando bot y cargando el portal municipal' },
    { id: 2, text: 'Resolviendo desafío reCAPTCHA v2 (2Captcha)' },
    { id: 3, text: 'Consultando información del predio e impuestos' },
    { id: 4, text: 'Generando y validando liquidación predial' },
    { id: 5, text: 'Descargando recibo oficial en formato PDF y capturando enlace de pago' },
  ];

  const getStepClass = (stepId) => {
    if (stepId < activeStep) return 'status-step completed';
    if (stepId === activeStep) return 'status-step active';
    return 'status-step';
  };

  return (
    <div id="loadingView" className="view active">
      <div className="loading-container">
        <div className="spinner-outer">
          <div className="spinner-inner"></div>
        </div>
        <div>
          <h3 style={{ fontSize: '1.4rem', fontFamily: 'Outfit', marginBottom: '8px' }}>
            Automatización en Progreso
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            Estamos navegando y resolviendo el trámite en el portal de la alcaldía.
          </p>
        </div>

        <div className="status-timeline">
          {steps.map((step) => (
            <div key={step.id} className={getStepClass(step.id)} id={`step${step.id}`}>
              <div className="step-icon">{step.id}</div>
              <span className="step-text">{step.text}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
