import { useState } from 'react';
import { Search, Layers, ChevronDown, Hash, FileText, Phone, Smartphone, Mail, AtSign, Play, AlertCircle } from 'lucide-react';
import VirtualKeyboard from './VirtualKeyboard';
import styles from './RpaFlow.module.css';

export default function FormView({
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
  handleSubmit
}) {
  const [activeInputName, setActiveInputName] = useState(null);

  return (
    <div id="formView">
      <form onSubmit={handleSubmit}>
        <div className={styles.formGrid}>
          <div className={styles.formGroup}>
            <label htmlFor="search_type">
              <Search size={16} /> Tipo de Búsqueda
            </label>
            <div className={styles.inputWrapper}>
              <select
                name="search_type"
                id="search_type"
                required
                value={searchType}
                onChange={(e) => setSearchType(e.target.value)}
              >
                <option value="Propietario">Propietario (Cédula/NIT)</option>
                <option value="Ficha Catastral">Ficha Catastral</option>
                <option value="Número Cuenta">Número de Cuenta</option>
              </select>
              <Layers className="icon-input" size={18} />
              <div className={styles.selectArrow}>
                <ChevronDown size={16} />
              </div>
            </div>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="search_value">
              <Hash size={16} /> No. de Predial
            </label>
            <div className={styles.inputWrapper}>
              <input
                type="text"
                name="search_value"
                id="search_value"
                required
                placeholder="Ej: 10XXXXXXXX"
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                onFocus={() => setActiveInputName('search_value')}
                onClick={() => setActiveInputName('search_value')}
                inputMode="none"
              />
              <FileText className="icon-input" size={18} />
            </div>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="phone">
              <Phone size={16} /> Teléfono Móvil
            </label>
            <div className={styles.inputWrapper}>
              <input
                type="tel"
                name="phone"
                id="phone"
                required
                placeholder="Ej: 3001234567"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                onFocus={() => setActiveInputName('phone')}
                onClick={() => setActiveInputName('phone')}
                inputMode="none"
              />
              <Smartphone className="icon-input" size={18} />
            </div>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="email">
              <Mail size={16} /> Correo Electrónico
            </label>
            <div className={styles.inputWrapper}>
              <input
                type="email"
                name="email"
                id="email"
                required
                placeholder="Ej: contribuyente@correo.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onFocus={() => setActiveInputName('email')}
                onClick={() => setActiveInputName('email')}
                inputMode="none"
              />
              <AtSign className="icon-input" size={18} />
            </div>
          </div>
        </div>

        <button type="submit" className={styles.btn} id="submitBtn" disabled={status === 'loading'}>
          <Play size={18} /> Buscar Factura
        </button>
      </form>

      {errorMessage && (
        <div id="errorAlert" className={`${styles.messageBox} ${styles.error}`}>
          <AlertCircle size={18} />
          <span id="errorMessage">{errorMessage}</span>
        </div>
      )}

      {activeInputName && (
        <VirtualKeyboard
          activeInputName={activeInputName}
          value={
            activeInputName === 'search_value'
              ? searchValue
              : activeInputName === 'phone'
              ? phone
              : activeInputName === 'email'
              ? email
              : ''
          }
          onChange={
            activeInputName === 'search_value'
              ? setSearchValue
              : activeInputName === 'phone'
              ? setPhone
              : activeInputName === 'email'
              ? setEmail
              : () => {}
          }
          onClose={() => setActiveInputName(null)}
          layoutType={activeInputName === 'phone' ? 'numeric' : 'alphanumeric'}
        />
      )}
    </div>
  );
}

