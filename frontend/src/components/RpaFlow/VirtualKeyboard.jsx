import { useState } from 'react';
import { createPortal } from 'react-dom';
import { Delete, Check, ArrowUp, X, RotateCcw } from 'lucide-react';
import styles from './RpaFlow.module.css';

export default function VirtualKeyboard({
  activeInputName,
  value,
  onChange,
  onClose,
  layoutType = 'alphanumeric' // 'alphanumeric' | 'numeric'
}) {
  const [isUpper, setIsUpper] = useState(false);

  const handleKeyClick = (key) => {
    if (key === 'space') {
      onChange(value + ' ');
    } else if (key === 'backspace') {
      onChange(value.slice(0, -1));
    } else if (key === 'clear') {
      onChange('');
    } else if (key === '.com') {
      onChange(value + '.com');
    } else if (key === '@') {
      onChange(value + '@');
    } else if (key === 'shift') {
      setIsUpper(!isUpper);
    } else {
      onChange(value + (isUpper ? key.toUpperCase() : key.toLowerCase()));
    }
  };

  const alphanumericRows = [
    ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
    ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'ñ'],
    ['shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', '-', '_', 'backspace'],
    ['@', 'space', '.', '.com', 'clear']
  ];

  const numericRows = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['clear', '0', 'backspace']
  ];

  const rows = layoutType === 'numeric' ? numericRows : alphanumericRows;

  // Formato amigable del nombre del input
  const getInputLabel = () => {
    switch (activeInputName) {
      case 'search_value':
        return 'No. de Predial';
      case 'phone':
        return 'Teléfono Móvil';
      case 'email':
        return 'Correo Electrónico';
      default:
        return 'Entrada';
    }
  };

  return createPortal(
    <div id="virtualKeyboardContainer" className={styles.keyboardOverlay} onClick={onClose}>
      <div className={styles.keyboardContainer} onClick={(e) => e.stopPropagation()}>
        {/* Header del teclado */}
        <div className={styles.keyboardHeader}>
          <div className={styles.keyboardHeaderLeft}>
            <span className={styles.keyboardInputBadge}>{getInputLabel()}</span>
            <span className={styles.keyboardCurrentValue}>
              {value || <span className={styles.keyboardPlaceholder}>Escriba aquí...</span>}
            </span>
          </div>
          <div className={styles.keyboardHeaderActions}>
            <button
              type="button"
              className={styles.keyboardCloseBtn}
              onClick={onClose}
              title="Cerrar teclado"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Teclas */}
        <div className={styles.keyboardLayout}>
          {rows.map((row, rowIndex) => (
            <div key={rowIndex} className={styles.keyboardRow}>
              {row.map((key) => {
                let keyContent = key;
                let extraClass = '';

                if (key === 'shift') {
                  keyContent = <ArrowUp size={22} className={isUpper ? styles.shiftActive : ''} />;
                  extraClass = styles.keyShift;
                } else if (key === 'backspace') {
                  keyContent = <Delete size={22} />;
                  extraClass = styles.keyBackspace;
                } else if (key === 'clear') {
                  keyContent = <RotateCcw size={20} />;
                  extraClass = styles.keyClear;
                } else if (key === 'space') {
                  keyContent = 'Espacio';
                  extraClass = styles.keySpace;
                } else if (key === '.com') {
                  keyContent = '.com';
                  extraClass = styles.keyCom;
                } else {
                  keyContent = isUpper ? key.toUpperCase() : key;
                }

                return (
                  <button
                    key={key}
                    type="button"
                    className={`${styles.keyboardKey} ${extraClass}`}
                    onClick={() => handleKeyClick(key)}
                  >
                    {keyContent}
                  </button>
                );
              })}
            </div>
          ))}
          {/* Fila de acción principal en el teclado */}
          <div className={styles.keyboardRow}>
            <button
              type="button"
              className={styles.keyAccept}
              onClick={onClose}
            >
              <Check size={20} /> Aceptar y Continuar
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
}

