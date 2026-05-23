import React, { useState } from 'react';
import { ArrowLeft, HelpCircle } from 'lucide-react';
import logo from './assets/logo.png';
import KioskHome from './components/KioskHome';
import FechasPagoView from './components/FechasPagoView';
import GuiaPasoPasoView from './components/GuiaPasoPasoView';
import FaqView from './components/FaqView';
import AsistenciaView from './components/AsistenciaView';
import FormView from './components/FormView';
import LoadingView from './components/LoadingView';
import ResultView from './components/ResultView';
import { useRpa } from './hooks/useRpa';
import styles from './App.module.css';

function App() {
  const [view, setView] = useState('home'); // 'home' | 'fechas_de_pago' | 'guia_paso_a_paso' | 'copia_de_factura' | 'preguntas_frecuentes' | 'asistencia'
  const rpa = useRpa();

  // Función para manejar el regreso al Home o restaurar el RPA
  const handleBack = () => {
    if (view === 'copia_de_factura' && rpa.status !== 'idle') {
      // Si está en carga o éxito, primero resetear el bot
      rpa.reset();
    } else {
      setView('home');
    }
  };

  return (
    <div className={styles.kioskContainer}>
      <main className={styles.kioskCard}>
        {/* Vista: Inicio / Home */}
        {view === 'home' && <KioskHome setView={setView} />}

        {/* Vista: Fechas de Pago */}
        {view === 'fechas_de_pago' && <FechasPagoView />}

        {/* Vista: Guía Paso a Paso */}
        {view === 'guia_paso_a_paso' && <GuiaPasoPasoView />}

        {/* Vista: Preguntas Frecuentes */}
        {view === 'preguntas_frecuentes' && <FaqView />}

        {/* Vista: Asistencia */}
        {view === 'asistencia' && <AsistenciaView />}

        {/* Vista: Copia de Factura (Flujo RPA) */}
        {view === 'copia_de_factura' && (
          <div className="copia-factura-wrapper">
            {(rpa.status === 'idle' || rpa.status === 'error') && (
              <>
                <div className="logo-container">
                  <img src={logo} alt="Alcaldía de Apartadó" className="kiosk-logo" />
                </div>
                <h2 className="kiosk-view-title font-semibold">Copia de tu factura</h2>
                <p className="kiosk-view-subtitle">
                  Ingrese la información requerida por el sistema para consultar, generar y descargar su factura del Impuesto Predial.
                </p>
                <FormView
                  searchType={rpa.searchType}
                  setSearchType={rpa.setSearchType}
                  searchValue={rpa.searchValue}
                  setSearchValue={rpa.setSearchValue}
                  phone={rpa.phone}
                  setPhone={rpa.setPhone}
                  email={rpa.email}
                  setEmail={rpa.setEmail}
                  status={rpa.status}
                  errorMessage={rpa.errorMessage}
                  handleSubmit={rpa.handleSubmit}
                />
              </>
            )}

            {rpa.status === 'loading' && (
              <LoadingView activeStep={rpa.activeStep} />
            )}

            {rpa.status === 'success' && (
              <ResultView
                result={rpa.result}
                isPrintingServer={rpa.isPrintingServer}
                reset={rpa.reset}
                printLocal={rpa.printLocal}
                printServer={rpa.printServer}
              />
            )}
          </div>
        )}
      </main>

      {/* Botones de navegación flotantes (visibles en cualquier vista interna) */}
      {view !== 'home' && (
        <div className={styles.kioskNavigationFloaters}>
          <button 
            onClick={handleBack} 
            className={styles.kioskFloatBackBtn} 
            title="Volver al menú principal"
            id="kiosk-back-btn"
          >
            <ArrowLeft size={28} />
          </button>
          
          <button 
            onClick={() => setView('asistencia')} 
            className={styles.kioskFloatHelpBtn} 
            title="Solicitar asistencia"
            id="kiosk-help-btn"
          >
            <HelpCircle size={28} />
          </button>
        </div>
      )}
    </div>
  );
}

export default App;

