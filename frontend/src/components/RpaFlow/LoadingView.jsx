import styles from './RpaFlow.module.css';

export default function LoadingView({ activeStep }) {
  const stepsText = {
    1: 'Iniciando proceso...',
    2: 'Buscando factura...',
    3: 'Generando factura...',
    4: 'Generando link de pago...',
    5: 'Finalizado'
  };

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
    <div id="loadingView">
      <div className={styles.loadingContainer}>
        
        <div className={styles.spinnerOuter}>
          <div className={styles.spinnerInner}></div>
        </div>

        <div className={styles.kioskLoadingHeader}>
          <h3 className={styles.kioskLoadingTitle}>Automatización en Progreso</h3>
          <p className={styles.kioskLoadingSubtitle}>
            El sistema está realizando la consulta de manera inteligente en el portal de la alcaldía.
          </p>
        </div>

        <div className={styles.kioskProgressContainer}>
          <div className={styles.kioskProgressLabelRow}>
            <span className={styles.kioskProgressStatus}>{currentStatus}</span>
            <span className={styles.kioskProgressPercentage}>{percentage}%</span>
          </div>
          
          <div className={styles.kioskProgressTrack}>
            <div 
              className={styles.kioskProgressFill} 
              style={{ width: `${percentage}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
}
