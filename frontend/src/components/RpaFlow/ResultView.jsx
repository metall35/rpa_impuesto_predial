import React from 'react';
import { CheckCircle2, ArrowLeft, Server } from 'lucide-react';
import QrPaymentCard from './QrPaymentCard';
import styles from './RpaFlow.module.css';

export default function ResultView({
  result,
  isPrintingServer,
  reset,
  printLocal,
  printServer
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
              className={`${styles.btn} ${styles.btnSuccess}`}
              id="printServerBtn"
              onClick={printServer}
              disabled={isPrintingServer}
            >
              {isPrintingServer ? (
                <>
                  <span
                    style={{
                      border: '2px solid #fff',
                      borderTop: '2px solid transparent',
                      borderRadius: '50%',
                      width: '14px',
                      height: '14px',
                      display: 'inline-block',
                      animation: `${styles.rotate} 1s linear infinite`,
                      marginRight: '6px',
                    }}
                  ></span>
                  Imprimiendo...
                </>
              ) : (
                <>
                  <Server size={16} /> Imprimir
                </>
              )}
            </button>
          </div>
        </div>

        {/* QR de Pago en Línea */}
        <QrPaymentCard paymentUrl={result.paymentUrl} paymentQr={result.paymentQr} />

        <div className={styles.pdfFrameContainer}>
          <iframe id="pdfViewer" src={result.pdfUrl} title="Visor de Factura Predial"></iframe>
        </div>
      </div>
    </div>
  );
}
