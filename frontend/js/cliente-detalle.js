/**
 * CLIENTE DETALLE - Nubeware Colombia
 * Logic for client view and historic contracts
 */

const ClientDetailManager = {
    init: function() {
        this.loadDetails();
    },

    loadDetails: async function() {
        const urlParams = new URLSearchParams(window.location.search);
        const codigo = urlParams.get('codigo');

        if (!codigo) {
            Notifications.error('Error', 'Código de cliente no especificado');
            setTimeout(() => window.location.href = 'dashboard.html', 2000);
            return;
        }

        try {
            const cliente = await apiClient.get(`/clientes/codigo/${codigo}`);
            this.render(cliente);
        } catch (error) {
            console.error('Error:', error);
            Notifications.error('Error', 'No se pudo cargar la información del cliente');
        }
    },

    render: function(cliente) {
        const container = document.getElementById('content-container');
        
        // Normalize contracts
        const contratosNaturales = (cliente.contratos_naturales || []).map(code => ({ codigo: code, tipo: 'natural' }));
        const contratosJuridicos = (cliente.contratos_juridicos || []).map(code => ({ codigo: code, tipo: 'juridico' }));
        const todosContratos = [...contratosNaturales, ...contratosJuridicos];

        // Update Header (outside content-container)
        const headerPlaceholder = document.getElementById('header-banner-target');
        headerPlaceholder.innerHTML = `
            <div class="enterprise-header-banner">
                <div class="enterprise-header-banner-content">
                    <div>
                        <div class="client-badges">
                            <span class="client-badge">${cliente.tipo_persona === 'juridica' ? 'Persona Jurídica' : 'Persona Natural'}</span>
                            <span class="client-badge active">${cliente.activo ? 'ACTIVO' : 'INACTIVO'}</span>
                        </div>
                        <h1 class="client-name-title">${cliente.nombre_o_razon_social}</h1>
                        <p style="margin-top: 5px; opacity: 0.8; font-family: monospace;"># ${cliente.codigo_unico}</p>
                    </div>
                    <div style="text-align: right; opacity: 0.8; font-size: 0.85rem;">
                        Registrado por: ${cliente.nombre_creador || 'Didier Guerrero'}
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = `
            <div class="enterprise-breadcrumb">
                <a href="dashboard.html">Dashboard</a>
                <span style="font-size: 0.7rem; margin: 0 5px;">></span>
                <a href="dashboard.html#clientes">Clientes</a>
                <span style="font-size: 0.7rem; margin: 0 5px;">></span>
                <span>${cliente.nombre_o_razon_social}</span>
            </div>

            <div class="info-section-grid">
                <!-- Column 1: Profile -->
                <div>
                    <h3 class="section-title-line">
                        <span>👤</span> INFORMACIÓN DE CONTACTO
                    </h3>
                    
                    <div class="info-field-group">
                        <div class="info-field-label">Identificación (${cliente.tipo_identificacion})</div>
                        <div class="info-field-value">${cliente.identificacion}</div>
                    </div>

                    <div class="info-field-group">
                        <div class="info-field-label">Email Corporativo</div>
                        <div class="info-field-value">
                            <a href="mailto:${cliente.email_contacto}" style="color: var(--nubeware-primary); text-decoration: none;">
                                ${cliente.email_contacto || 'No registrado'}
                            </a>
                        </div>
                    </div>

                    <div class="info-field-group">
                        <div class="info-field-label">Teléfono / WhatsApp</div>
                        <div class="info-field-value">${cliente.telefono || 'No registrado'}</div>
                    </div>
                </div>

                <!-- Column 2: History -->
                <div>
                    <h3 class="section-title-line">
                        <span>📂</span> HISTORIAL DE CONTRATOS (${todosContratos.length})
                    </h3>
                    
                    <div class="contract-list">
                        ${todosContratos.length > 0 ? todosContratos.map(c => `
                            <a href="contrato-detalle.html?codigo=${c.codigo}&tipo=${c.tipo}" class="contract-card-mini">
                                <div class="contract-info-left">
                                    <span class="contract-code-text">${c.codigo}</span>
                                    <span class="contract-type-sub">${c.tipo === 'juridico' ? 'Contrato Jurídico' : 'Contrato Natural'}</span>
                                </div>
                                <span class="contract-action-btn">VER ></span>
                            </a>
                        `).join('') : `
                            <div style="text-align: center; padding: 3rem; border: 2px dashed #eee; color: #999;">
                                <p>No hay contratos históricos asociados</p>
                            </div>
                        `}
                    </div>
                </div>
            </div>
        `;
    }
};

document.addEventListener('DOMContentLoaded', () => ClientDetailManager.init());
