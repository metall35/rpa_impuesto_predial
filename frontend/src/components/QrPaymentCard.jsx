import React from 'react';
import { QrCode, Clock } from 'lucide-react';

export default function QrPaymentCard({ paymentUrl, paymentQr }) {
  if (!paymentUrl || !paymentQr) return null;

  return (
    <div id="qrPaymentContainer" className="qr-payment-card">
      <div className="qr-image-wrapper">
        <img id="qrImage" src={paymentQr} alt="QR de Pago" />
      </div>
      <div className="qr-info-section">
        <div className="qr-title-row">
          <QrCode size={20} />
          <h4>Escanea y paga en línea</h4>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: '1.4' }}>
          Puedes pagar de forma segura escaneando este código QR desde tu celular.
        </p>
        <div className="qr-timer-badge">
          <Clock size={14} />
          <span>El pago y el código QR solo están disponibles por 10 minutos.</span>
        </div>
      </div>
    </div>
  );
}
