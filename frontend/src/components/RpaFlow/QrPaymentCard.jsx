
import { useState, useEffect } from 'react';
import { QrCode, Clock, CreditCard, X } from 'lucide-react';
import styles from './RpaFlow.module.css';

export default function QrPaymentCard({ paymentUrl, paymentQr }) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    if (isModalOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isModalOpen]);

  if (!paymentUrl || !paymentQr) return null;

  return (
    <div id="qrPaymentContainer" className={styles.qrPaymentCard}>
      <div className={styles.qrImageWrapper}>
        <img id="qrImage" src={paymentQr} alt="QR de Pago" />
      </div>
      <div className={styles.qrInfoSection}>
        <div className={styles.qrTitleRow}>
          <QrCode size={20} />
          <h4>Escanea y paga en línea</h4>
        </div>
        <p className={styles.qrInstructionsText}>
          Puedes pagar de forma segura escaneando este código QR desde tu celular.
        </p>
        <div className={styles.qrTimerBadge}>
          <Clock size={14} />
          <span>El pago y el código QR solo están disponibles por 10 minutos.</span>
        </div>
        <button
          id="openPaymentModalBtn"
          className={styles.paymentButton}
          onClick={() => setIsModalOpen(true)}
        >
          <CreditCard size={18} />
          <span>Pagar en este dispositivo</span>
        </button>
      </div>

      {isModalOpen && (
        <div className={styles.modalOverlay} onClick={() => setIsModalOpen(false)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h3>Pasarela de Pago</h3>
              <button 
                className={styles.modalCloseButton} 
                onClick={() => setIsModalOpen(false)}
                aria-label="Cerrar modal"
              >
                <X size={20} />
              </button>
            </div>
            <div className={styles.modalBody}>
              <iframe
                id="paymentIframe"
                src={paymentUrl}
                title="Pasarela de Pago"
                className={styles.paymentIframe}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

