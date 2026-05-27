
import { CheckCircle2, ArrowLeft } from 'lucide-react';
import QrPaymentCard from './QrPaymentCard';
import styles from './RpaFlow.module.css';

export default function ResultView({
  result,
  reset
}) {
  if (!result) return null;

  return (
    <div id="resultView">
      <div className={styles.resultContainer}>
        <div className={styles.resultHeader}>
          <div className={styles.resultTitle}>
            <CheckCircle2 size={28} style={{ color: 'var(--success)' }} />
            <div>
              <h3 style={{ fontSize: '1.25rem', fontFamily: 'Outfit', color: 'var(--text-main)' }}>
                Factura Generada Correctamente
              </h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 'normal' }} id="resultFilenameText">
                Archivo: {result.filename}
              </p>
            </div>
          </div>
          <div className={styles.resultActions}>
            <button className={`${styles.btn} ${styles.btnSecondary}`} id="backBtn" onClick={reset}>
              <ArrowLeft size={16} /> Nueva Consulta
            </button>
          </div>
        </div>

        <QrPaymentCard paymentUrl={result.paymentUrl} paymentQr={result.paymentQr} />

        <div className={styles.pdfFrameContainer}>
          <iframe id="pdfViewer" src={result.pdfUrl} title="Visor de Factura Predial"></iframe>
        </div>
      </div>
    </div>
  );
}
