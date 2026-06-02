import { useState } from 'react';
import { ChevronRight, Check } from 'lucide-react';
import styles from './RpaFlow.module.css';

export default function PrediosSelectorView({ predios, onSelect, onCancel }) {
  const [selectedIndex, setSelectedIndex] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedIndex !== null) {
      onSelect(selectedIndex);
    }
  };

  return (
    <div className={styles.prediosContainer}>
      <h3 className={styles.prediosTitle}>Múltiples Predios Encontrados</h3>
      <p className={styles.prediosSubtitle}>
        Su consulta está asociada a más de un predio en la Alcaldía de Apartadó. Por favor, seleccione el predio que desea pagar:
      </p>

      <div className={styles.prediosTableWrapper}>
        <table className={styles.prediosTable}>
          <thead>
            <tr>
              <th style={{ width: '70px', textAlign: 'center' }}>Selección</th>
              <th>Número Cuenta</th>
              <th>Dirección</th>
              <th>Cédula Catastral</th>
              <th>Deuda Actual</th>
              <th>Matrícula</th>
            </tr>
          </thead>
          <tbody>
            {predios.map((item) => {
              const isSelected = selectedIndex === item.index;
              const data = item.data;
              
              // Mapeo flexible de llaves para evitar problemas de acentos o espacios
              const numCuenta = data["Número cuenta"] || data["Numero cuenta"] || data["Numero_cuenta"] || Object.values(data)[0] || "";
              const direccion = data["Dirección"] || data["Direccion"] || "";
              const cedulaCatastral = data["Cedula Catastral"] || data["Cédula Catastral"] || data["Cedula_Catastral"] || "";
              const deudaActual = data["Deuda actual"] || data["Deuda_actual"] || "";
              const matricula = data["Matricula"] || data["Matrícula"] || "";

              return (
                <tr 
                  key={item.index}
                  onClick={() => setSelectedIndex(item.index)}
                  className={`${styles.predioRow} ${isSelected ? styles.predioRowSelected : ''}`}
                >
                  <td className={styles.selectCell}>
                    <div className={`${styles.radioCircle} ${isSelected ? styles.radioCircleActive : ''}`}>
                      {isSelected && <Check size={12} />}
                    </div>
                  </td>
                  <td className={styles.boldCell}>{numCuenta}</td>
                  <td>{direccion}</td>
                  <td className={styles.mutedCell}>{cedulaCatastral}</td>
                  <td className={styles.deudaCell}>{deudaActual}</td>
                  <td>{matricula}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className={styles.prediosActions}>
        <button 
          type="button" 
          onClick={onCancel} 
          className={`${styles.btn} ${styles.btnSecondary}`}
          id="btn-cancel-predios"
        >
          Volver atrás
        </button>
        
        <button 
          type="button"
          onClick={handleSubmit}
          disabled={selectedIndex === null}
          className={styles.btn}
          id="btn-confirmar-predio"
          style={{ width: 'auto', marginTop: 0 }}
        >
          <span>Continuar con el proceso</span>
          <ChevronRight size={18} />
        </button>
      </div>
    </div>
  );
}
