
import { CheckCircle2, ArrowLeft, Printer } from 'lucide-react';
import QrPaymentCard from './QrPaymentCard';
import styles from './RpaFlow.module.css';

export default function ResultView({
  result,
  reset,
  printLocal
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
            <button
              onClick={printLocal}
              className={`${styles.btn} ${styles.btnPrimaryHeader}`}
              id="printBtn"
            >
              <Printer size={16} /> Imprimir Factura
            </button>
          </div>
        </div>

        <div className={styles.resultContentRow}>
          <div className={styles.resultLeftCol}>
            <QrPaymentCard paymentUrl={result.paymentUrl} paymentQr={result.paymentQr} />
          </div>
          <div className={styles.resultRightCol}>
            <div className={styles.pdfFrameContainer}>
              <iframe id="pdfViewer" src={`${result.pdfUrl}#toolbar=0&navpanes=0`} title="Visor de Factura Predial"></iframe>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
