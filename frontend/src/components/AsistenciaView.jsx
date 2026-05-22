import React, { useState } from 'react';
import { User, Home, Phone, MessageSquare, CheckCircle } from 'lucide-react';
import logo from '../assets/logo.png';

export default function AsistenciaView() {
  const [nombre, setNombre] = useState('');
  const [idPredio, setIdPredio] = useState('');
  const [telefono, setTelefono] = useState('');
  const [comentarios, setComentarios] = useState('');
  const [aceptoPolitica, setAceptoPolitica] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!aceptoPolitica) {
      alert('Debe aceptar la Política de Tratamiento de Datos Personales para continuar.');
      return;
    }
    // No tiene integración por requerimiento:
    setSubmitted(true);
  };

  return (
    <div className="asistencia-view">
      {/* Logo */}
      <div className="logo-container">
        <img src={logo} alt="Alcaldía de Apartadó" className="kiosk-logo" />
      </div>

      {/* Título */}
      <h2 className="kiosk-view-title font-semibold text-green-header">
        ¿Necesitas asistencia con tu pago?
      </h2>

      {submitted ? (
        <div className="kiosk-success-submission animate-fade-in text-center">
          <CheckCircle size={64} className="text-green mx-auto mb-4" />
          <h3>¡Información enviada con éxito!</h3>
          <p>
            Hemos registrado tus datos. Un asesor de la Alcaldía de Apartadó se pondrá en contacto al teléfono proporcionado en breve.
          </p>
          <button 
            onClick={() => {
              setSubmitted(false);
              setNombre('');
              setIdPredio('');
              setTelefono('');
              setComentarios('');
              setAceptoPolitica(false);
            }} 
            className="btn btn-success mt-4"
          >
            Enviar otra consulta
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="kiosk-form">
          <div className="form-grid">
            {/* Nombre Completo */}
            <div className="form-group">
              <label htmlFor="nombre">
                <User size={16} /> Nombre completo
              </label>
              <div className="input-wrapper">
                <input
                  type="text"
                  id="nombre"
                  name="nombre"
                  required
                  placeholder="Ingrese su nombre completo"
                  value={nombre}
                  onChange={(e) => setNombre(e.target.value)}
                />
                <User className="icon-input" size={18} />
              </div>
            </div>

            {/* ID del Predio */}
            <div className="form-group">
              <label htmlFor="idPredio">
                <Home size={16} /> ID del predio
              </label>
              <div className="input-wrapper">
                <input
                  type="text"
                  id="idPredio"
                  name="idPredio"
                  required
                  placeholder="Ingrese el número o ID del predio"
                  value={idPredio}
                  onChange={(e) => setIdPredio(e.target.value)}
                />
                <Home className="icon-input" size={18} />
              </div>
            </div>

            {/* Teléfono */}
            <div className="form-group">
              <label htmlFor="telefono">
                <Phone size={16} /> Teléfono de contacto
              </label>
              <div className="input-wrapper">
                <input
                  type="text"
                  id="telefono"
                  name="telefono"
                  required
                  placeholder="Ingrese su número telefónico"
                  value={telefono}
                  onChange={(e) => setTelefono(e.target.value)}
                />
                <Phone className="icon-input" size={18} />
              </div>
            </div>

            {/* Comentarios */}
            <div className="form-group full-width-field">
              <label htmlFor="comentarios">
                <MessageSquare size={16} /> Comentarios
              </label>
              <div className="input-wrapper">
                <textarea
                  id="comentarios"
                  name="comentarios"
                  required
                  rows="4"
                  placeholder="Escriba su consulta o comentarios aquí..."
                  value={comentarios}
                  onChange={(e) => setComentarios(e.target.value)}
                />
                <MessageSquare className="icon-input-textarea" size={18} />
              </div>
            </div>
          </div>

          {/* Checkbox de Privacidad */}
          <div className="kiosk-checkbox-group">
            <label className="checkbox-container">
              <input
                type="checkbox"
                required
                checked={aceptoPolitica}
                onChange={(e) => setAceptoPolitica(e.target.checked)}
              />
              <span className="checkmark"></span>
              <span className="checkbox-text">
                <strong>Acepto Política de Tratamiento de Datos Personales</strong>
                <br />
                Al enviar este formulario, autorizo el tratamiento de mis datos personales conforme a la Ley 1581 de 2012 y demás normas vigentes, con el propósito de recibir asistencia relacionada con trámites y pagos en línea ante la Alcaldía de Apartadó. Para más información <a href="#policy" onClick={(e) => { e.preventDefault(); alert('Conforme a la Ley 1581 de 2012, sus datos personales serán custodiados y utilizados únicamente para responder a su solicitud de asistencia.'); }} className="text-link">clic aquí</a>
              </span>
            </label>
          </div>

          {/* Botón de Enviar */}
          <div className="form-submit-container">
            <button type="submit" className="kiosk-submit-btn">
              ENVIAR INFORMACIÓN
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
