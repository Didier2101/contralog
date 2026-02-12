/**
 * CONTRATO DETALLE - Nubeware Colombia
 * Timeline moderno, español colombiano, datos reales
 * Actualizado: Sin Lucide, Sin Swal, Sin target blank
 */

const NubewareContratoDetalle = {
    
    init: function() {
        this.loadContractDetails();
    },

    getUrlParams: function() {
        const urlParams = new URLSearchParams(window.location.search);
        return {
            codigo: urlParams.get('codigo'),
            tipo: urlParams.get('tipo')
        };
    },

    validateParams: function(params) {
        return params.codigo && params.tipo;
    },

    formatDate: function(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('es-CO', { 
            day: '2-digit', 
            month: 'long', 
            year: 'numeric' 
        });
    },

    formatDateShort: function(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('es-CO', { 
            day: '2-digit', 
            month: 'short', 
            year: 'numeric' 
        });
    },

    getEstadoClass: function(estado) {
        return estado?.toLowerCase() || '';
    },

    getDocumentIcon: function(tipoDocumento) {
        const tipo = tipoDocumento?.toLowerCase() || '';
        if (tipo.includes('poliza')) return '🛡️';
        if (tipo.includes('salarios')) return '🏥';
        if (tipo.includes('contrato')) return '✍️';
        return '📄';
    },

    renderContract: function(contrato, tipo) {
        const documentos = contrato.documentos || [];
        
        // Meses para el calendario
        const meses = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'];
        const mesActual = new Date().getMonth();
        const anoActual = new Date().getFullYear();
        
        let calendarioHtml = '';
        meses.forEach((mes, index) => {
            let clase = 'enterprise-calendar-month';
            if (index === mesActual) clase += ' current';
            if (index === 1) clase += ' active'; 
            
            calendarioHtml += `
                <div class="${clase}">
                    <span>${mes}</span>
                    ${index === mesActual ? '<span class="enterprise-calendar-marker"></span>' : ''}
                </div>
            `;
        });

        return `
            <!-- BREADCRUMB - RUTA DESDE DASHBOARD -->
            <div class="enterprise-breadcrumb">
                <a href="dashboard.html">Dashboard</a>
                <span style="font-size: 0.7rem; margin: 0 5px;">></span>
                <a href="dashboard.html#contratos">Contratos</a>
                <span style="font-size: 0.7rem; margin: 0 5px;">></span>
                <span>${contrato.codigo_unico}</span>
            </div>

            <div class="enterprise-grid">
                <!-- COLUMNA IZQUIERDA -->
                <div>
                    <!-- TIPO PERSONA -->
                    <div class="enterprise-type-section">
                        <span class="enterprise-type-badge">
                            <span style="margin-right: 5px;">${tipo === 'juridico' ? '🏢' : '👤'}</span>
                            ${tipo === 'juridico' ? 'PERSONA JURÍDICA' : 'PERSONA NATURAL'}
                        </span>
                        <span class="enterprise-section-subtitle">Resumen del contrato</span>
                    </div>
                    
                    <!-- CALENDARIO DE VENCIMIENTOS -->
                    <div class="enterprise-calendar">
                        <div class="enterprise-calendar-header">
                            <span class="enterprise-calendar-title">
                                <span style="margin-right: 5px;">🔔</span>
                                VENCIMIENTOS PRÓXIMOS (12 MESES)
                            </span>
                            <span class="enterprise-calendar-year">${anoActual}</span>
                        </div>
                        <div class="enterprise-calendar-grid">
                            ${calendarioHtml}
                        </div>
                        <div class="enterprise-calendar-rentabilidad">
                            <span style="margin-right: 5px; color: var(--nubeware-success);">📈</span>
                            <span>RENTABILIDAD: +12.5%</span>
                            <span style="margin-left: auto; font-weight: 700;">KGO</span>
                        </div>
                    </div>
                    
                    <!-- INFORMACIÓN GENERAL -->
                    <div style="margin-top: 2rem;">
                        <h3 style="font-size: 0.9rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 1rem; color: var(--nubeware-gray-700); display: flex; align-items: center; gap: 0.5rem;">
                            <span style="color: var(--nubeware-primary);">ℹ️</span>
                            INFORMACIÓN GENERAL
                        </h3>
                        
                        <div class="enterprise-info-grid">
                            <div class="enterprise-info-item">
                                <span class="enterprise-info-label">
                                    <span style="font-size: 0.7rem; margin-right: 5px;">📅</span>
                                    FECHA DE INICIO
                                </span>
                                <span class="enterprise-info-value">
                                    ${this.formatDate(contrato.fecha_inicio)}
                                </span>
                            </div>
                            <div class="enterprise-info-item">
                                <span class="enterprise-info-label">
                                    <span style="font-size: 0.7rem; margin-right: 5px;">✅</span>
                                    FECHA DE TERMINACIÓN
                                </span>
                                <span class="enterprise-info-value">
                                    ${this.formatDate(contrato.fecha_final)}
                                </span>
                            </div>
                            <div class="enterprise-info-item">
                                <span class="enterprise-info-label">
                                    <span style="font-size: 0.7rem; margin-right: 5px;">👤</span>
                                    RESPONSABLE
                                </span>
                                <span class="enterprise-info-value">
                                    ${contrato.creador_nombre?.charAt(0).toUpperCase() || 'D'}
                                </span>
                                <span class="enterprise-info-subvalue">
                                    ${contrato.creador_nombre || 'Didier Guerrero'}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- COLUMNA DERECHA -->
                <div>
                    <!-- ESTADO DEL CONTRATO -->
                    <div style="margin-bottom: 2rem;">
                        <h3 style="font-size: 0.9rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 1rem; color: var(--nubeware-gray-700); display: flex; align-items: center; gap: 0.5rem;">
                            <span style="color: var(--nubeware-primary);">⚙️</span>
                            ESTADO DEL CONTRATO
                        </h3>
                        
                        <div class="enterprise-timeline-moderno">
                            <div class="enterprise-timeline-item-moderno">
                                <div class="enterprise-timeline-icon active">
                                    <span>✓</span>
                                </div>
                                <div class="enterprise-timeline-content-moderno">
                                    <div class="enterprise-timeline-title-moderno">VIGENTE</div>
                                    <div class="enterprise-timeline-desc-moderno">Activo</div>
                                    <div class="enterprise-timeline-meta">Estado actual</div>
                                </div>
                            </div>
                            
                            <div class="enterprise-timeline-item-moderno">
                                <div class="enterprise-timeline-icon warning">
                                    <span>⏳</span>
                                </div>
                                <div class="enterprise-timeline-content-moderno">
                                    <div class="enterprise-timeline-title-moderno">RENOVACIÓN</div>
                                    <div class="enterprise-timeline-desc-moderno">Programada · ${this.formatDateShort(contrato.fecha_final)}</div>
                                    <div class="enterprise-timeline-meta">Próximo vencimiento</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- DOCUMENTOS ASOCIADOS -->
                    <div style="margin-bottom: 2rem;">
                        <h3 style="font-size: 0.9rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 1rem; color: var(--nubeware-gray-700); display: flex; align-items: center; gap: 0.5rem;">
                            <span>📂</span>
                            DOCUMENTOS ASOCIADOS
                            <span style="margin-left: auto; font-size: 0.7rem; background: var(--nubeware-gray-100); padding: 0.2rem 0.6rem; border: var(--border-nubeware);">
                                ${documentos.length}
                            </span>
                        </h3>
                        
                        ${documentos.length > 0 ? `
                            <div class="enterprise-document-list">
                                ${documentos.map(doc => {
                                    const docUrl = doc.s3_key.startsWith('http') ? doc.s3_key : `${API_BASE_URL}/uploads/${doc.s3_key}`;
                                    const icono = this.getDocumentIcon(doc.tipo_documento);
                                    
                                    return `
                                        <a href="${docUrl}" class="enterprise-document-item">
                                            <div class="enterprise-document-icon">
                                                <span>${icono}</span>
                                            </div>
                                            <div class="enterprise-document-info">
                                                <div class="enterprise-document-name">${doc.tipo_documento}</div>
                                                <div class="enterprise-document-meta">
                                                    ${doc.codigo_seguimiento || 'DOC-2026-XXXXX'}
                                                </div>
                                            </div>
                                            <div class="enterprise-document-action">
                                                <span>VER</span>
                                                <span style="margin-left: 5px;">🔗</span>
                                            </div>
                                        </a>
                                    `;
                                }).join('')}
                            </div>
                        ` : `
                            <div style="border: 1px solid #e2e8f0; padding: 1.5rem; text-align: center;">
                                <span>📂</span>
                                <p style="margin-top: 0.5rem; color: var(--nubeware-gray-500);">Sin documentos asociados</p>
                            </div>
                        `}
                    </div>
                    
                    <!-- ADJUNTAR DOCUMENTO -->
                    <div class="enterprise-attach-section">
                        <div class="enterprise-attach-header">
                            <span style="color: var(--nubeware-primary); margin-right: 8px;">📤</span>
                            <span class="enterprise-attach-title">ADJUNTAR DOCUMENTO</span>
                        </div>
                        <button class="enterprise-attach-button" onclick="Notifications.info('Módulo en Desarrollo', 'Esta función estará disponible próximamente')">
                            <span style="margin-right: 5px;">+</span>
                            SELECCIONAR ARCHIVO
                        </button>
                    </div>
                </div>
            </div>
        `;
    },

    loadContractDetails: async function() {
        const params = this.getUrlParams();
        
        if (!this.validateParams(params)) {
            Notifications.error('Error', 'Parámetros de URL inválidos');
            setTimeout(() => window.history.back(), 2000);
            return;
        }

        try {
            const contrato = await apiClient.get(`/contratos/${params.tipo}/${params.codigo}`);
            
            const clienteNombre = document.getElementById('cliente-nombre');
            if (clienteNombre) clienteNombre.textContent = contrato.cliente_nombre;
            
            const codigoUnico = document.getElementById('codigo-unico');
            if (codigoUnico) {
                codigoUnico.innerHTML = `
                    <span style="margin-right: 5px;">#</span>
                    ${contrato.codigo_unico}
                `;
            }
            
            const estadoBadge = document.getElementById('estado-contrato-badge');
            if (estadoBadge) {
                estadoBadge.className = `enterprise-status-header ${this.getEstadoClass(contrato.estado)}`;
                estadoBadge.innerHTML = `
                    <span style="margin-right: 5px;">●</span>
                    ${contrato.estado.toUpperCase()}
                `;
            }
            
            const contentHtml = this.renderContract(contrato, params.tipo);
            document.getElementById('content-container').innerHTML = contentHtml;
            
        } catch (error) {
            console.error('Error:', error);
            Notifications.error('Error', 'No se pudo cargar la información del contrato');
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    NubewareContratoDetalle.init();
});