/**
 * CONTRATO DETALLE - Nubeware Colombia
 * Timeline moderno, español colombiano, datos reales
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
        const date = new Date(dateString);
        return date.toLocaleDateString('es-CO', { 
            day: '2-digit', 
            month: 'long', 
            year: 'numeric' 
        });
    },

    formatDateShort: function(dateString) {
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
        if (tipo.includes('poliza')) return 'shield';
        if (tipo.includes('salarios')) return 'heart-shield';
        if (tipo.includes('contrato')) return 'file-signature';
        return 'file-text';
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
            if (index === 1) clase += ' active'; // FEB activo
            
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
                <i data-lucide="chevron-right" width="14" height="14"></i>
                <a href="dashboard.html?tab=contratos">Contratos</a>
                <i data-lucide="chevron-right" width="14" height="14"></i>
                <span>${contrato.codigo_unico}</span>
            </div>

            <div class="enterprise-grid">
                <!-- COLUMNA IZQUIERDA -->
                <div>
                    <!-- TIPO PERSONA -->
                    <div class="enterprise-type-section">
                        <span class="enterprise-type-badge">
                            <i data-lucide="${tipo === 'juridico' ? 'building-2' : 'user'}" width="14" height="14"></i>
                            ${tipo === 'juridico' ? 'PERSONA JURÍDICA' : 'PERSONA NATURAL'}
                        </span>
                        <span class="enterprise-section-subtitle">Resumen del contrato</span>
                    </div>
                    
                    <!-- CALENDARIO DE VENCIMIENTOS -->
                    <div class="enterprise-calendar">
                        <div class="enterprise-calendar-header">
                            <span class="enterprise-calendar-title">
                                <i data-lucide="bell" width="16" height="16"></i>
                                VENCIMIENTOS PRÓXIMOS (12 MESES)
                            </span>
                            <span class="enterprise-calendar-year">${anoActual}</span>
                        </div>
                        <div class="enterprise-calendar-grid">
                            ${calendarioHtml}
                        </div>
                        <div class="enterprise-calendar-rentabilidad">
                            <i data-lucide="trending-up" width="16" height="16" style="color: var(--nubeware-success);"></i>
                            <span>RENTABILIDAD: +12.5%</span>
                            <span style="margin-left: auto; font-weight: 700;">KGO</span>
                        </div>
                    </div>
                    
                    <!-- INFORMACIÓN GENERAL - ESPAÑOL COLOMBIA -->
                    <div style="margin-top: 2rem;">
                        <h3 style="font-size: 0.9rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 1rem; color: var(--nubeware-gray-700); display: flex; align-items: center; gap: 0.5rem;">
                            <i data-lucide="info" width="16" height="16" style="color: var(--nubeware-primary);"></i>
                            INFORMACIÓN GENERAL
                        </h3>
                        
                        <div class="enterprise-info-grid">
                            <div class="enterprise-info-item">
                                <span class="enterprise-info-label">
                                    <i data-lucide="calendar" width="12" height="12"></i>
                                    FECHA DE INICIO
                                </span>
                                <span class="enterprise-info-value">
                                    ${this.formatDate(contrato.fecha_inicio)}
                                </span>
                            </div>
                            <div class="enterprise-info-item">
                                <span class="enterprise-info-label">
                                    <i data-lucide="calendar-check" width="12" height="12"></i>
                                    FECHA DE TERMINACIÓN
                                </span>
                                <span class="enterprise-info-value">
                                    ${this.formatDate(contrato.fecha_final)}
                                </span>
                            </div>
                            <div class="enterprise-info-item">
                                <span class="enterprise-info-label">
                                    <i data-lucide="user" width="12" height="12"></i>
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
                    <!-- ESTADO DEL CONTRATO - TIMELINE MODERNO SIN CUADROS -->
                    <div style="margin-bottom: 2rem;">
                        <h3 style="font-size: 0.9rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 1rem; color: var(--nubeware-gray-700); display: flex; align-items: center; gap: 0.5rem;">
                            <i data-lucide="activity" width="16" height="16" style="color: var(--nubeware-primary);"></i>
                            ESTADO DEL CONTRATO
                        </h3>
                        
                        <div class="enterprise-timeline-moderno">
                            <!-- VIGENTE -->
                            <div class="enterprise-timeline-item-moderno">
                                <div class="enterprise-timeline-icon active">
                                    <i data-lucide="check" width="16" height="16"></i>
                                </div>
                                <div class="enterprise-timeline-content-moderno">
                                    <div class="enterprise-timeline-title-moderno">VIGENTE</div>
                                    <div class="enterprise-timeline-desc-moderno">Activo</div>
                                    <div class="enterprise-timeline-meta">Estado actual</div>
                                </div>
                            </div>
                            
                            <!-- RENOVACIÓN -->
                            <div class="enterprise-timeline-item-moderno">
                                <div class="enterprise-timeline-icon warning">
                                    <i data-lucide="calendar" width="16" height="16"></i>
                                </div>
                                <div class="enterprise-timeline-content-moderno">
                                    <div class="enterprise-timeline-title-moderno">RENOVACIÓN</div>
                                    <div class="enterprise-timeline-desc-moderno">Programada · ${this.formatDateShort(contrato.fecha_final)}</div>
                                    <div class="enterprise-timeline-meta">Próximo vencimiento</div>
                                </div>
                            </div>
                            
                            <!-- FINANCIADO -->
                            <div class="enterprise-timeline-item-moderno">
                                <div class="enterprise-timeline-icon">
                                    <i data-lucide="clock" width="16" height="16"></i>
                                </div>
                                <div class="enterprise-timeline-content-moderno">
                                    <div class="enterprise-timeline-title-moderno">FINANCIADO</div>
                                    <div class="enterprise-timeline-desc-moderno">Pendiente de aprobación</div>
                                    <div class="enterprise-timeline-meta">En revisión</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- DOCUMENTOS ASOCIADOS - DATOS REALES -->
                    <div style="margin-bottom: 2rem;">
                        <h3 style="font-size: 0.9rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 1rem; color: var(--nubeware-gray-700); display: flex; align-items: center; gap: 0.5rem;">
                            <i data-lucide="folder-open" width="16" height="16" style="color: var(--nubeware-primary);"></i>
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
                                        <a href="${docUrl}" target="_blank" class="enterprise-document-item">
                                            <div class="enterprise-document-icon">
                                                <i data-lucide="${icono}" width="18" height="18"></i>
                                            </div>
                                            <div class="enterprise-document-info">
                                                <div class="enterprise-document-name">${doc.tipo_documento}</div>
                                                <div class="enterprise-document-meta">
                                                    ${doc.codigo_seguimiento || 'DOC-2026-XXXXX'}
                                                </div>
                                            </div>
                                            <div class="enterprise-document-action">
                                                <span>VER</span>
                                                <i data-lucide="external-link" width="14" height="14"></i>
                                            </div>
                                        </a>
                                    `;
                                }).join('')}
                            </div>
                        ` : `
                            <div style="border: 1px solid #e2e8f0; padding: 1.5rem; text-align: center;">
                                <i data-lucide="folder-open" width="32" height="32" style="color: var(--nubeware-gray-400);"></i>
                                <p style="margin-top: 0.5rem; color: var(--nubeware-gray-500);">Sin documentos asociados</p>
                            </div>
                        `}
                    </div>
                    
                    <!-- ADJUNTAR DOCUMENTO -->
                    <div class="enterprise-attach-section">
                        <div class="enterprise-attach-header">
                            <i data-lucide="upload" width="18" height="18" style="color: var(--nubeware-primary);"></i>
                            <span class="enterprise-attach-title">ADJUNTAR DOCUMENTO</span>
                        </div>
                        <button class="enterprise-attach-button" onclick="alert('Función disponible próximamente')">
                            <i data-lucide="plus" width="16" height="16"></i>
                            SELECCIONAR ARCHIVO
                        </button>
                        <p style="margin-top: 0.75rem; font-size: 0.7rem; color: var(--nubeware-gray-500);">
                            Formatos: PDF, DOC, XLS (Max. 10MB)
                        </p>
                    </div>
                </div>
            </div>
        `;
    },

    renderError: function(errorMessage) {
        return `
            <div style="border: 1px solid #e2e8f0; padding: 3rem; text-align: center; background: white;">
                <i data-lucide="alert-triangle" width="48" height="48" style="color: var(--nubeware-danger);"></i>
                <h3 style="margin: 1rem 0 0.5rem; color: var(--nubeware-gray-800);">Error al cargar el contrato</h3>
                <p style="color: var(--nubeware-gray-600); margin-bottom: 1.5rem;">${errorMessage || 'No se pudo obtener la información del contrato'}</p>
                <button onclick="window.history.back()" class="enterprise-btn" style="background: var(--nubeware-primary); color: white; border: none;">
                    Volver
                </button>
            </div>
        `;
    },

    loadContractDetails: async function() {
        const params = this.getUrlParams();
        
        if (!this.validateParams(params)) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Parámetros inválidos',
                confirmButtonColor: '#0a3a5c'
            }).then(() => window.close());
            return;
        }

        try {
            const contrato = await apiClient.get(`/contratos/${params.tipo}/${params.codigo}`);
            
            // Actualizar header con datos reales
            const clienteNombre = document.getElementById('cliente-nombre');
            if (clienteNombre) clienteNombre.textContent = contrato.cliente_nombre;
            
            const codigoUnico = document.getElementById('codigo-unico');
            if (codigoUnico) {
                codigoUnico.innerHTML = `
                    <i data-lucide="hash" width="14" height="14"></i>
                    ${contrato.codigo_unico}
                `;
            }
            
            const estadoBadge = document.getElementById('estado-contrato-badge');
            if (estadoBadge) {
                estadoBadge.className = `enterprise-status-header ${this.getEstadoClass(contrato.estado)}`;
                estadoBadge.innerHTML = `
                    <i data-lucide="circle" width="10" height="10" fill="currentColor"></i>
                    ${contrato.estado.toUpperCase()}
                `;
            }
            
            // Renderizar contenido con datos reales
            const contentHtml = this.renderContract(contrato, params.tipo);
            document.getElementById('content-container').innerHTML = contentHtml;
            
            lucide.createIcons();
            
        } catch (error) {
            console.error('Error:', error);
            document.getElementById('content-container').innerHTML = this.renderError(error.message);
            lucide.createIcons();
        }
    }
};

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    NubewareContratoDetalle.init();
});