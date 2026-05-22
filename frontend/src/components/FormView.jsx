import React from 'react';
import { Search, Layers, ChevronDown, Hash, FileText, Phone, Smartphone, Mail, AtSign, Play, AlertCircle } from 'lucide-react';

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
    <div id="formView" className="view active">
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="search_type">
              <Search className="icon-label" size={16} /> Tipo de Búsqueda
            </label>
            <div className="input-wrapper">
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
              <div className="select-arrow">
                <ChevronDown size={16} />
              </div>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="search_value">
              <Hash className="icon-label" size={16} /> Código / Documento
            </label>
            <div className="input-wrapper">
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

          <div className="form-group">
            <label htmlFor="phone">
              <Phone className="icon-label" size={16} /> Teléfono Móvil
            </label>
            <div className="input-wrapper">
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

          <div className="form-group">
            <label htmlFor="email">
              <Mail className="icon-label" size={16} /> Correo Electrónico
            </label>
            <div className="input-wrapper">
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

        <button type="submit" className="btn" id="submitBtn" disabled={status === 'loading'}>
          <Play size={18} /> Iniciar Generación Automatizada
        </button>
      </form>

      {errorMessage && (
        <div id="errorAlert" className="message-box error">
          <AlertCircle size={18} />
          <span id="errorMessage">{errorMessage}</span>
        </div>
      )}
    </div>
  );
}
