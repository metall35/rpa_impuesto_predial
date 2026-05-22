import { useState, useRef } from 'react';

export const useRpa = () => {
  const [searchType, setSearchType] = useState('Propietario');
  const [searchValue, setSearchValue] = useState('64741384');
  const [phone, setPhone] = useState('3001234567');
  const [email, setEmail] = useState('test@example.com');
  
  const [status, setStatus] = useState('idle'); // 'idle' | 'loading' | 'success' | 'error'
  const [errorMessage, setErrorMessage] = useState('');
  const [activeStep, setActiveStep] = useState(1);
  const [result, setResult] = useState(null); // { filename, pdfUrl, paymentUrl, paymentQr }
  const [isPrintingServer, setIsPrintingServer] = useState(false);

  const timeoutsRef = useRef([]);

  const clearProgressTimeouts = () => {
    timeoutsRef.current.forEach(clearTimeout);
    timeoutsRef.current = [];
  };

  const startProgressSimulation = () => {
    clearProgressTimeouts();
    setActiveStep(1);
    
    const t2 = setTimeout(() => setActiveStep(2), 8000);
    const t3 = setTimeout(() => setActiveStep(3), 35000);
    const t4 = setTimeout(() => setActiveStep(4), 50000);
    const t5 = setTimeout(() => setActiveStep(5), 70000);
    
    timeoutsRef.current = [t2, t3, t4, t5];
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    
    setStatus('loading');
    setErrorMessage('');
    setResult(null);
    startProgressSimulation();

    const formData = new FormData();
    formData.append('search_type', searchType);
    formData.append('search_value', searchValue);
    formData.append('phone', phone);
    formData.append('email', email);

    try {
      const response = await fetch('/api/generar_factura', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      clearProgressTimeouts();

      if (response.ok && data.status === 'success') {
        setResult({
          filename: data.filename,
          pdfUrl: `/facturas/${data.filename}`,
          paymentUrl: data.payment_url,
          paymentQr: data.payment_qr,
        });
        setStatus('success');
      } else {
        setErrorMessage(data.message || 'Ocurrió un error inesperado durante el trámite.');
        setStatus('error');
      }
    } catch (err) {
      clearProgressTimeouts();
      setErrorMessage('Error de red o conexión al intentar conectar con el servidor.');
      setStatus('error');
    }
  };

  const reset = () => {
    setStatus('idle');
    setErrorMessage('');
    setResult(null);
    clearProgressTimeouts();
  };

  const printLocal = () => {
    if (!result?.pdfUrl) return;
    const printWindow = window.open(result.pdfUrl, '_blank');
    if (printWindow) {
      printWindow.focus();
    } else {
      alert('Por favor, permita las ventanas emergentes para visualizar e imprimir la factura.');
    }
  };

  const printServer = async () => {
    if (!result?.filename) return;
    setIsPrintingServer(true);

    try {
      const formData = new FormData();
      formData.append('filename', result.filename);

      const response = await fetch('/api/imprimir_factura', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (response.ok) {
        alert(`Éxito: ${data.message}`);
      } else {
        alert(`Error al imprimir en servidor: ${data.message}`);
      }
    } catch (err) {
      alert('Error de red al intentar imprimir en el servidor.');
    } finally {
      setIsPrintingServer(false);
    }
  };

  return {
    searchType,
    setSearchType,
    searchValue,
    setSearchValue,
    phone,
    setPhone,
    email,
    setEmail,
    status,
    errorMessage,
    activeStep,
    result,
    isPrintingServer,
    handleSubmit,
    reset,
    printLocal,
    printServer,
  };
};
