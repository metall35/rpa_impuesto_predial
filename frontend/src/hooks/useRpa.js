import { useState, useRef } from 'react';

export const useRpa = () => {
  const [searchType, setSearchType] = useState('Propietario');
  const [searchValue, setSearchValue] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  
  const [status, setStatus] = useState('idle'); // 'idle' | 'loading' | 'success' | 'error' | 'multiple_predios'
  const [errorMessage, setErrorMessage] = useState('');
  const [activeStep, setActiveStep] = useState(1);
  const [result, setResult] = useState(null); // { filename, pdfUrl, paymentUrl, paymentQr }
  
  // Estados para selección de múltiples predios
  const [prediosList, setPrediosList] = useState([]);
  const [sessionId, setSessionId] = useState('');
  const [selectedPredioIndex, setSelectedPredioIndex] = useState(null);

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
    
    timeoutsRef.current = [t2, t3, t4];
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    
    setStatus('loading');
    setErrorMessage('');
    setResult(null);
    setPrediosList([]);
    setSessionId('');
    setSelectedPredioIndex(null);
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

      if (response.ok) {
        if (data.status === 'multiple_predios') {
          setPrediosList(data.predios);
          setSessionId(data.session_id);
          setStatus('multiple_predios');
        } else if (data.status === 'success') {
          setResult({
            filename: data.filename,
            pdfUrl: `/facturas/${data.filename}`,
            paymentUrl: data.payment_url,
            paymentQr: data.payment_qr,
          });
          setActiveStep(5);
          await new Promise((resolve) => setTimeout(resolve, 1200));
          setStatus('success');
        } else {
          setErrorMessage('Ocurrió un error inesperado durante el trámite.');
          setStatus('error');
        }
      } else {
        setErrorMessage('Ocurrió un error inesperado durante el trámite.');
        setStatus('error');
      }
    } catch (err) {
      clearProgressTimeouts();
      setErrorMessage('Error de red o conexión al intentar conectar con el servidor.');
      setStatus('error');
    }
  };

  const handleSelectPredio = async (index) => {
    setStatus('loading');
    setErrorMessage('');
    setSelectedPredioIndex(index);
    startProgressSimulation();

    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('index', index);
    formData.append('phone', phone);
    formData.append('email', email);

    try {
      const response = await fetch('/api/seleccionar_predio', {
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
        setActiveStep(5);
        await new Promise((resolve) => setTimeout(resolve, 1200));
        setStatus('success');
      } else {
        setErrorMessage('Ocurrió un error inesperado al seleccionar el predio.');
        setStatus('error');
      }
    } catch (err) {
      clearProgressTimeouts();
      setErrorMessage('Error de red al intentar conectar con el servidor, por favor vuelva a intentarlo.');
      setStatus('error');
    }
  };

  const reset = () => {
    setStatus('idle');
    setErrorMessage('');
    setResult(null);
    setPrediosList([]);
    setSessionId('');
    setSelectedPredioIndex(null);
    clearProgressTimeouts();
    setSearchType('Propietario');
    setSearchValue('');
    setPhone('');
    setEmail('');
  };

  const printLocal = () => {
    if (!result?.pdfUrl) return;
    const iframe = document.getElementById('pdfViewer');
    if (iframe) {
      try {
        iframe.contentWindow.focus();
        iframe.contentWindow.print();
      } catch (err) {
        const printWindow = window.open(result.pdfUrl, '_blank');
        if (printWindow) {
          printWindow.focus();
          printWindow.print();
        }
      }
    } else {
      const printWindow = window.open(result.pdfUrl, '_blank');
      if (printWindow) {
        printWindow.focus();
        printWindow.print();
      }
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
    prediosList,
    sessionId,
    selectedPredioIndex,
    handleSubmit,
    handleSelectPredio,
    reset,
    printLocal,
  };
};
