
import { QrCode, Clock } from 'lucide-react';
import styles from './RpaFlow.module.css';

export default function QrPaymentCard({ paymentUrl, paymentQr }) {
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
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: '1.4' }}>
          Puedes pagar de forma segura escaneando este código QR desde tu celular o haciendo clic en el enlace PSE de la factura.
        </p>
        <div className={styles.qrTimerBadge}>
          <Clock size={14} />
          <span>El pago y el código QR solo están disponibles por 10 minutos.</span>
        </div>
      </div>
    </div>
  );
}
