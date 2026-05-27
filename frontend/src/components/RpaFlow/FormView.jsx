import { Search, Layers, ChevronDown, Hash, FileText, Phone, Smartphone, Mail, AtSign, Play, AlertCircle } from 'lucide-react';
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
                <option value="Ficha Catastral">Ficha Catastral (NPN)</option>
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
              <Hash size={16} /> Código / Documento
            </label>
            <div className={styles.inputWrapper}>
              <input
                type="text"
                name="search_value"
                id="search_value"
                required
                placeholder="Ej: 64741384"
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
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
                type="text"
                name="phone"
                id="phone"
                required
                placeholder="Ej: 3001234567"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
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
              />
              <AtSign className="icon-input" size={18} />
            </div>
          </div>
        </div>

        <button type="submit" className={styles.btn} id="submitBtn" disabled={status === 'loading'}>
          <Play size={18} /> Iniciar Generación Automatizada
        </button>
      </form>

      {errorMessage && (
        <div id="errorAlert" className={`${styles.messageBox} ${styles.error}`}>
          <AlertCircle size={18} />
          <span id="errorMessage">{errorMessage}</span>
        </div>
      )}
    </div>
  );
}
