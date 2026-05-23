import React, { useState } from 'react';
import { CreditCard, GraduationCap, Heart, PhoneCall, Building2, ChevronDown, ChevronUp } from 'lucide-react';
import logo from '../../assets/logo.png';
import styles from './FaqView.module.css';

export default function FaqView() {
  const [activeFaq, setActiveFaq] = useState(null);

  const toggleFaq = (key) => {
    if (activeFaq === key) {
      setActiveFaq(null);
    } else {
      setActiveFaq(key);
    }
  };

  const categories = [
    {
      id: 'tributario',
      title: 'Trámites Tributarios y Pagos',
      icon: <CreditCard size={20} className={styles.catIcon} />,
      items: [
        {
          q: '¿Cómo puedo pagar el Impuesto Predial?',
          a: 'El portal cuenta con una "Oficina Virtual" donde puedes consultar la liquidación y realizar el pago en línea.'
        },
        {
          q: '¿Cada cuánto se realiza la actualización catastral?',
          a: 'De acuerdo con la Ley 223 de 1995, el municipio debe realizarla en periodos máximos de cinco años.'
        },
        {
          q: '¿Cómo obtengo un certificado de Paz y Salvo?',
          a: 'Se puede gestionar a través del módulo de servicios tributarios en la sede electrónica, previo pago de las obligaciones pendientes.'
        }
      ]
    },
    {
      id: 'educacion',
      title: 'Educación y Empleo',
      icon: <GraduationCap size={20} className={styles.catIcon} />,
      items: [
        {
          q: '¿Cómo accedo a plazas como docente en el municipio?',
          a: 'El ingreso al servicio educativo estatal se realiza mediante concurso de méritos coordinado por la Comisión Nacional del Servicio Civil (CNSC).'
        },
        {
          q: '¿Dónde consulto las ofertas de empleo de la Alcaldía?',
          a: 'En la sección "Trabaje con nosotros" o mediante el portal del Servicio Público de Empleo.'
        }
      ]
    },
    {
      id: 'sociales',
      title: 'Programas Sociales y Salud',
      icon: <Heart size={20} className={styles.catIcon} />,
      items: [
        {
          q: '¿Cómo me inscribo al Programa del Adulto Mayor?',
          a: 'Debes presentar una solicitud escrita dirigida a la coordinación del programa, adjuntando copia de la cédula, recibo de energía y el certificado del Sisbén.'
        },
        {
          q: '¿Cómo consulto mi puntaje del Sisbén?',
          a: 'Aunque el trámite se puede iniciar en la oficina local del Sisbén en la Alcaldía, la consulta de la ficha técnica se hace directamente en el portal nacional del DNP.'
        }
      ]
    },
    {
      id: 'atencion',
      title: 'Atención al Ciudadano',
      icon: <PhoneCall size={20} className={styles.catIcon} />,
      items: [
        {
          q: '¿Cuáles son los canales de atención oficiales?',
          a: (
            <div>
              <p>Los canales de atención oficiales son:</p>
              <ul className={styles.faqList}>
                <li><strong>Dirección:</strong> Carrera 100 # 103A–02.</li>
                <li><strong>Teléfono (PBX):</strong> +57 (604) 8280457.</li>
                <li><strong>Correo para peticiones:</strong> contactenos@apartado.gov.co.</li>
              </ul>
            </div>
          )
        },
        {
          q: '¿Cómo puedo radicar una PQRSDF (Petición, Queja, Reclamo, Sugerencia, Denuncia o Felicitación)?',
          a: 'El sitio dispone de un formulario web específico para el seguimiento de estos requerimientos de manera digital.'
        }
      ]
    },
    {
      id: 'urbanismo',
      title: 'Urbanismo y Planeación',
      icon: <Building2 size={20} className={styles.catIcon} />,
      items: [
        {
          q: '¿Cómo solicito una licencia de construcción o uso de suelo?',
          a: 'Estos trámites se gestionan ante la Secretaría de Planeación. Muchos de los formularios y requisitos (como el certificado de estratificación) están disponibles para descarga en la sección de "Trámites".'
        }
      ]
    }
  ];

  return (
    <div>
      {/* Logo */}
      <div className={styles.logoContainer}>
        <img src={logo} alt="Alcaldía de Apartadó" className={styles.kioskLogo} />
      </div>

      {/* Título */}
      <h2 className={styles.kioskViewTitle}>Preguntas Frecuentes</h2>

      {/* Categorías y acordeones */}
      <div className={styles.faqCategoriesContainer}>
        {categories.map((category) => (
          <div key={category.id} className={styles.faqCategorySection}>
            <h3 className={styles.faqCategoryTitle}>
              {category.icon}
              <span>{category.title}</span>
            </h3>
            <div className={styles.faqQuestionsList}>
              {category.items.map((item, idx) => {
                const key = `${category.id}-${idx}`;
                const isOpen = activeFaq === key;
                return (
                  <div key={idx} className={`${styles.faqItemCard} ${isOpen ? styles.open : ''}`}>
                    <button
                      onClick={() => toggleFaq(key)}
                      className={styles.faqQuestionBtn}
                    >
                      <span className={styles.faqRadioBullet}></span>
                      <span className={styles.faqQuestionText}>{item.q}</span>
                      {isOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                    </button>
                    {isOpen && (
                      <div className={styles.faqAnswerContent}>
                        {item.a}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
