import React from 'react';
import { CheckCircle2, ArrowLeft, Download, Printer, Server } from 'lucide-react';
import QrPaymentCard from './QrPaymentCard';

export default function ResultView({
  result,
  isPrintingServer,
  reset,
  printLocal,
  printServer
}) {
  if (!result) return null;

  return (
    <div id="resultView" className="view active">
      <div className="result-container">
        <div className="result-header">
          <div className="result-title">
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
          <div className="result-actions">
            <button className="btn btn-secondary" id="backBtn" onClick={reset}>
              <ArrowLeft size={16} /> Nueva Consulta
            </button>
            <button
              className="btn btn-success"
              id="printServerBtn"
              onClick={printServer}
              disabled={isPrintingServer}
            >
              {isPrintingServer ? (
                <>
                  <span
                    className="spinner-tiny"
                    style={{
                      border: '2px solid #fff',
                      borderTop: '2px solid transparent',
                      borderRadius: '50%',
                      width: '14px',
                      height: '14px',
                      display: 'inline-block',
                      animation: 'spin 1s linear infinite',
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

        <div className="pdf-frame-container">
          <iframe id="pdfViewer" src={result.pdfUrl} title="Visor de Factura Predial"></iframe>
        </div>
      </div>
    </div>
  );
}
