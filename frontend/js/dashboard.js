console.log("Dashboard JS Parsing...");

// GLOBAL REDIRECTION FUNCTIONS
// Defined immediately on window to prevent ReferenceError
window.showCreateClienteModal = function() {
    window.location.href = 'crear-cliente.html';
};

window.showCreateUsuarioModal = function() {
    window.location.href = 'crear-usuario.html';
};

window.showCreateContratoModal = function(tipo) {
    if (tipo) {
        window.location.href = `crear-contrato.html?tipo=${tipo}`;
    } else {
        console.error("Tipo de contrato no especificado");
    }
};

// Global assignments for other functions will happen after they are defined.
if (typeof window !== 'undefined') {
    // Audit logs, etc will be assigned at the end of file
    console.log("Global redirection functions assigned.");
}

console.log("Dashboard JS Loaded");
let activeSection = 'home';
let currentViewData = [];

document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
});

function initDashboard() {
    const userStr = localStorage.getItem('user');
    if (!userStr) {
        window.location.href = 'login.html';
        return;
    }

    const user = JSON.parse(userStr);
    
    // UI Elements
    document.getElementById('userName').textContent = user.nombre;
    document.getElementById('userRole').textContent = user.rol;
    document.getElementById('userInitial').textContent = user.nombre.charAt(0).toUpperCase();

    // Check Role-based Visibility
    if (user.rol !== 'admin') {
        document.querySelectorAll('.hide-colaborador').forEach(el => el.style.display = 'none');
    }

    // Set Date
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('currentDate').textContent = new Date().toLocaleDateString('es-ES', options);

    // Navigation Handling
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.getAttribute('data-section');
            
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            loadSection(section);
        });
    });

    // Load initial section (Summary)
    loadSection('home');
    
    // Notifications logic
    initNotifications();

    // Global Search Listener
    const searchInput = document.getElementById('globalSearch');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            handleGlobalSearch(e.target.value);
        });
    }

    // Initialize icons
    lucide.createIcons();
}

async function initNotifications() {
    const bellBtn = document.getElementById('bellBtn');
    const notifMenu = document.getElementById('notifMenu');

    bellBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        notifMenu.classList.toggle('show');
        loadAlerts();
    });

    document.addEventListener('click', () => {
        notifMenu.classList.remove('show');
    });

    notifMenu.addEventListener('click', (e) => e.stopPropagation());

    // Initial load of alerts count
    loadAlerts();
}

async function loadAlerts() {
    try {
        const alerts = await apiClient.get('/contratos/alertas');
        const badge = document.getElementById('notifBadge');
        const list = document.getElementById('notifList');

        if (alerts.length > 0) {
            badge.textContent = alerts.length;
            badge.style.display = 'block';
            
            list.innerHTML = alerts.map(a => `
                <div class="notification-item warning" onclick="showContratoDetails(${a.id}, '${a.tipo}')">
                    <i data-lucide="alert-triangle"></i>
                    <div class="content">
                        <div class="title">Contrato por vencer</div>
                        <div class="desc">${a.nombre_o_razon_social} vence el ${new Date(a.fecha_final).toLocaleDateString()}</div>
                    </div>
                </div>
            `).join('');
        } else {
            badge.style.display = 'none';
            list.innerHTML = '<div class="notification-empty">No hay alertas pendientes</div>';
        }
        lucide.createIcons();
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

async function loadSection(section) {
    activeSection = section; // Update active section
    const container = document.getElementById('content-container');
    container.innerHTML = '<div class="loader-container"><div class="loader"></div></div>';
    
    // Clear search input on section change
    const searchInput = document.getElementById('globalSearch');
    if (searchInput) searchInput.value = '';

    try {
        switch(section) {
            case 'home':
                await renderSummary();
                break;
            case 'clientes':
                await renderClientes();
                break;
            case 'contratos':
                await renderContratos();
                break;
            case 'usuarios':
                await renderUsuarios();
                break;
            case 'auditoria':
                await renderAuditoria();
                break;
        }
        lucide.createIcons();
    } catch (error) {
        console.error('Error loading section:', error);
        container.innerHTML = `<div class="error-state">Error cargando contenido: ${error.message}</div>`;
    }
}

async function renderSummary() {
    const container = document.getElementById('content-container');
    let alerts = [];
    let clientes = [];
    let contratos = [];
    
    try { 
        [alerts, clientes, contratos] = await Promise.all([
            apiClient.get('/contratos/alertas'),
            apiClient.get('/clientes/listar?pagina=1'),
            apiClient.get('/contratos/listar?pagina=1')
        ]); 
    } catch(e) {
        console.error('Error fetching summary data:', e);
    }

    const activosCount = contratos.filter(c => c.estado === 'activo').length;

    container.innerHTML = `
        <div class="summary-header mb-2">
            <h2>Resumen del Sistema</h2>
            <p class="text-muted">Estado actual de la gestión de contratos</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card glass animate-fade" style="animation-delay: 0.1s">
                <div class="stat-icon" style="background: var(--primary)">
                    <i data-lucide="users"></i>
                </div>
                <div class="stat-info">
                    <span class="value">${clientes.length}</span>
                    <span class="label">Clientes Registrados</span>
                </div>
            </div>
            <div class="stat-card glass animate-fade" style="animation-delay: 0.2s">
                <div class="stat-icon" style="background: var(--success)">
                    <i data-lucide="file-check"></i>
                </div>
                <div class="stat-info">
                    <span class="value">${activosCount}</span>
                    <span class="label">Contratos Activos</span>
                </div>
            </div>
            <div class="stat-card glass animate-fade" style="animation-delay: 0.3s">
                <div class="stat-icon" style="background: var(--warning)">
                    <i data-lucide="alert-triangle"></i>
                </div>
                <div class="stat-info">
                    <span class="value">${alerts.length}</span>
                    <span class="label">Alertas de Vencimiento</span>
                </div>
            </div>
        </div>

        <div class="glass p-2 animate-fade" style="animation-delay: 0.4s">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="margin:0;">Alertas Críticas</h3>
                <span class="badge-rol role-admin" style="font-size: 0.7rem;">Vigilancia Nocturna Activa</span>
            </div>
            ${alerts.length > 0 ? renderAlertsTable(alerts) : `
                <div class="text-center py-3">
                    <i data-lucide="shield-check" size="48" style="color: var(--success); opacity: 0.5;"></i>
                    <p class="text-muted mt-1">No hay alertas críticas en este momento.</p>
                </div>
            `}
        </div>
    `;
    lucide.createIcons();
}

function renderAlertsTable(alerts) {
    return `
        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Cliente</th>
                        <th>Fecha Final</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
                    ${alerts.map(a => `
                        <tr>
                            <td>#${a.id_contrato_j || a.id_contrato_n}</td>
                            <td>${a.nombre_cliente || 'Cargando...'}</td>
                            <td>${new Date(a.fecha_final).toLocaleDateString()}</td>
                            <td><span class="status status-${a.estado}">${a.estado}</span></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

async function renderClientes() {
    const container = document.getElementById('content-container');
    try {
        const data = await apiClient.get('/clientes/listar?pagina=1');
        
        container.innerHTML = `
            <div class="header-with-action">
                <div>
                    <h2>Gestión de Clientes</h2>
                    <p class="text-muted">Directorio de personas naturales y jurídicas</p>
                </div>
                <button class="btn btn-primary" onclick="showCreateClienteModal()">
                    <i data-lucide="plus"></i> Nuevo Cliente
                </button>
            </div>
            
            <div class="glass mt-2">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Identificación</th>
                            <th>Nombre / Razón Social</th>
                            <th>Teléfono</th>
                            <th>Estado</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.length > 0 ? data.map(cliente => `
                            <tr>
                                <td><span style="font-weight: 600;">#</span> ${cliente.identificacion}</td>
                                <td>${cliente.nombre_o_razon_social}</td>
                                <td>${cliente.telefono || '-'}</td>
                                <td>
                                    <label class="switch">
                                        <input type="checkbox" ${cliente.activo ? 'checked' : ''} 
                                               onchange="toggleClienteEstado('${cliente.codigo_unico}', ${cliente.activo})">
                                        <span class="slider"></span>
                                    </label>
                                </td>
                                <td class="actions">
                                    <button class="btn-icon" title="Ver detalle" onclick="showClienteDetails('${cliente.codigo_unico}')">
                                        <i data-lucide="eye"></i>
                                    </button>
                                    <button class="btn-icon btn-edit" title="Editar" onclick="showEditClienteModal('${cliente.codigo_unico}')">
                                        <i data-lucide="edit-3"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('') : '<tr><td colspan="4" class="text-center py-2 text-muted">No se encontraron clientes registrados.</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;
        lucide.createIcons();
    } catch (error) {
        Swal.fire('Error', 'No se pudieron cargar los clientes: ' + error.message, 'error');
    }
}

async function toggleClienteEstado(codigo, estadoActual) {
    const nuevoEstado = !estadoActual;
    const accion = nuevoEstado ? 'activar' : 'desactivar';

    const result = await Swal.fire({
        title: `¿${accion.charAt(0).toUpperCase() + accion.slice(1)} cliente?`,
        text: `¿Estás seguro de que deseas ${accion} este cliente?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: 'var(--primary)',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, confirmar',
        cancelButtonText: 'Cancelar'
    });

    if (result.isConfirmed) {
        try {
            // BACKEND ESPECÍFICO: PATCH /clientes/codigo/{codigo_cliente}/estado?activo=true/false
            await apiClient.patch(`/clientes/codigo/${codigo}/estado?activo=${nuevoEstado}`, {});

            Swal.fire({
                icon: 'success',
                title: 'Estado actualizado',
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 2000
            });
            // No recargamos toda la tabla para mantener la fluidez, o sí si queremos asegurar sincronización
            renderClientes(); 
        } catch (error) {
            console.error(error);
            Swal.fire('Error', 'No se pudo cambiar el estado: ' + error.message, 'error');
            // Si falla, revertimos el checkbox visualmente (necesitamos volver a renderizar o manipular el DOM específico)
            renderClientes(); 
        }
    } else {
        renderClientes(); // Revertir switch si cancela
    }
}

async function renderContratos() {
    const container = document.getElementById('content-container');
    try {
        const data = await apiClient.get('/contratos/listar?pagina=1');
        
        container.innerHTML = `
            <div class="header-with-action">
                <div>
                    <h2>Gestión de Contratos</h2>
                    <p class="text-muted">Seguimiento de vigencias y pólizas unificadas</p>
                </div>
                <div class="btn-group" style="display: flex; gap: 0.5rem;">
                    <button class="btn btn-ghost" onclick="showCreateContratoModal('natural')">
                        <i data-lucide="user"></i> Persona Natural
                    </button>
                    <button class="btn btn-primary" onclick="showCreateContratoModal('juridico')">
                        <i data-lucide="briefcase"></i> Persona Jurídica
                    </button>
                </div>
            </div>
            
            <div class="glass mt-2">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Código</th>
                            <th>Cliente</th>
                            <th>Tipo</th>
                            <th>Inicio</th>
                            <th>Vencimiento</th>
                            <th>Estado</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.length > 0 ? data.map(c => `
                            <tr>
                                <td>
                                    <span style="color: var(--primary); font-weight: 700; font-family: monospace;">
                                        ${c.contrato_codigo || c.codigo_unico}
                                    </span>
                                </td>
                                <td>
                                    <div style="display: flex; flex-direction: column;">
                                        <a href="#" onclick="window.open('cliente-detalle.html?codigo=${c.cliente_codigo || ''}', '_blank'); return false;" 
                                           style="font-weight: 600; color: var(--text-main); text-decoration: none; transition: color 0.2s;" 
                                           onmouseover="this.style.color='var(--primary)'" 
                                           onmouseout="this.style.color='var(--text-main)'">
                                            ${c.cliente_nombre || 'Cliente #' + c.id_cliente}
                                        </a>
                                        <span style="font-size: 0.75rem; color: var(--text-muted); font-family: monospace;">
                                            ${c.cliente_codigo || ''}
                                        </span>
                                    </div>
                                </td>
                                <td><span class="badge-rol role-${c.tipo_contrato === 'natural' ? 'colaborador' : 'admin'}">${c.tipo_contrato}</span></td>
                                <td>${new Date(c.fecha_inicio).toLocaleDateString()}</td>
                                <td>${new Date(c.fecha_final).toLocaleDateString()}</td>
                                <td><span class="status status-${c.estado}">${c.estado}</span></td>
                                <td class="actions">
                                    <button class="btn-icon" title="Ver Detalles del Contrato" onclick="showContratoDetails('${c.contrato_codigo || c.codigo_unico}', '${c.tipo_contrato}')">
                                        <i data-lucide="eye"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('') : '<tr><td colspan="7" class="text-center py-5 text-muted">No hay contratos registrados.</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;
        lucide.createIcons();
    } catch (error) {
        Swal.fire('Error', 'No se pudieron cargar los contratos: ' + error.message, 'error');
    }
}

async function renderUsuarios() {
    const container = document.getElementById('content-container');
    try {
        const data = await apiClient.get('/usuarios/listar');
        
        container.innerHTML = `
            <div class="header-with-action">
                <div>
                    <h2>Gestión de Usuarios</h2>
                    <p class="text-muted">Administra los accesos y roles del sistema</p>
                </div>
                <button class="btn btn-primary" onclick="showCreateUsuarioModal()">
                    <i data-lucide="user-plus"></i> Crear Usuario
                </button>
            </div>
            
            <div class="glass mt-2">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Nombre</th>
                            <th>Email</th>
                            <th>Rol</th>
                            <th>Estado</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.map(u => `
                            <tr>
                                <td>
                                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                                        <div class="user-avatar" style="width: 32px; height: 32px; font-size: 0.8rem;">${u.nombre.charAt(0).toUpperCase()}</div>
                                        <span style="font-weight: 600;">${u.nombre}</span>
                                    </div>
                                </td>
                                <td>${u.email}</td>
                                <td><span class="badge-rol role-${u.rol}">${u.rol}</span></td>
                                <td>
                                    <label class="switch">
                                        <input type="checkbox" ${u.estado === 'activo' ? 'checked' : ''} 
                                               onchange="toggleUsuarioEstado(${u.id_usuario}, '${u.estado}')">
                                        <span class="slider"></span>
                                    </label>
                                </td>
                                <td class="actions">
                                    <button class="btn-icon" title="Ver Detalle" onclick="showUsuarioDetails(${u.id_usuario})">
                                        <i data-lucide="eye"></i>
                                    </button>
                                    <button class="btn-icon" title="Editar" onclick="showEditUsuarioModal(${u.id_usuario})">
                                        <i data-lucide="edit-3"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        lucide.createIcons();
    } catch (error) {
        Swal.fire('Error', 'No se pudieron cargar los usuarios: ' + error.message, 'error');
    }
}

// Help function for date formatting
function formatDate(dateStr) {
    if (!dateStr) return 'No registrado';
    const date = new Date(dateStr);
    return isNaN(date.getTime()) ? 'No registrado' : date.toLocaleDateString();
}

// Modals Logic
function showModal(title, content, options = {}) {
    const container = document.getElementById('modal-container');
    const modalContent = container.querySelector('.modal-content');
    const header = container.querySelector('.modal-header');
    const body = document.getElementById('modalBody');
    
    // Default options
    const { bodyClass = '', hideHeader = false } = typeof options === 'string' ? { bodyClass: options } : options;

    document.getElementById('modalTitle').textContent = title;
    body.innerHTML = content;
    
    // Reset and apply class
    body.className = 'modal-body';
    if (bodyClass) body.classList.add(bodyClass);
    
    // Handle header visibility
    if (hideHeader) {
        header.style.display = 'none';
        modalContent.classList.add('no-header');
    } else {
        header.style.display = 'flex';
        modalContent.classList.remove('no-header');
    }
    
    container.classList.remove('hidden');
    container.style.display = 'flex';
    lucide.createIcons();
}

function closeModal() {
    const container = document.getElementById('modal-container');
    const body = document.getElementById('modalBody');
    container.classList.add('hidden');
    container.style.display = 'none';
    body.className = 'modal-body'; // Reset for next use
}

document.getElementById('closeModalBtn').addEventListener('click', closeModal);

// Close modal when clicking outside
document.getElementById('modal-container').addEventListener('click', (e) => {
    if (e.target.id === 'modal-container') {
        closeModal();
    }
});


// MODAL REPLACED BY REDIRECT
function showCreateClienteModal() {
    window.location.href = 'crear-cliente.html';
}
window.showCreateClienteModal = showCreateClienteModal;


async function showClienteDetails(codigo) {
    if (!codigo || codigo === 'undefined') {
        Swal.fire('Error', 'No se puede ver el detalle: El código del cliente no está disponible.', 'warning');
        return;
    }
    window.open(`cliente-detalle.html?codigo=${codigo}`, '_blank');
}

async function showEditClienteModal(codigo) {
    showModal('Editar Cliente', '<div class="loader-container"><div class="loader"></div></div>', { hideHeader: true, bodyClass: 'no-padding' });
    try {
        const c = await apiClient.get(`/clientes/codigo/${codigo}`);
        const formHtml = `
            <form id="editClienteForm" class="modal-form">
                <div class="modal-form-header">
                    <button type="button" class="close-banner" onclick="closeModal()"><i data-lucide="x" size="20"></i></button>
                    <i data-lucide="edit-3"></i>
                    <div class="title">Modificar Cliente</div>
                </div>
                <div class="modal-form-container">
                    <div class="form-grid">
                        <div class="form-group">
                            <label>Tipo Persona</label>
                            <select id="edit_tipo_persona" class="form-control" required>
                                <option value="natural" ${c.tipo_persona === 'natural' ? 'selected' : ''}>Natural</option>
                                <option value="juridica" ${c.tipo_persona === 'juridica' ? 'selected' : ''}>Jurídica</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Tipo Identificación</label>
                            <select id="edit_tipo_identificacion" class="form-control" required>
                                <option value="cc" ${c.tipo_identificacion === 'cc' ? 'selected' : ''}>Cédula de Ciudadanía</option>
                                <option value="ce" ${c.tipo_identificacion === 'ce' ? 'selected' : ''}>Cédula de Extranjería</option>
                                <option value="pasaporte" ${c.tipo_identificacion === 'pasaporte' ? 'selected' : ''}>Pasaporte</option>
                                <option value="nit" ${c.tipo_identificacion === 'nit' ? 'selected' : ''}>NIT</option>
                                <option value="pep" ${c.tipo_identificacion === 'pep' ? 'selected' : ''}>PEP</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Identificación</label>
                            <input type="text" id="edit_identificacion" class="form-control" value="${c.identificacion}" required>
                        </div>
                        <div class="form-group">
                            <label>Nombre o Razón Social</label>
                            <input type="text" id="edit_nombre_o_razon_social" class="form-control" value="${c.nombre_o_razon_social}" required>
                        </div>
                        <div class="form-group">
                            <label>Teléfono</label>
                            <input type="text" id="edit_telefono" class="form-control" value="${c.telefono || ''}">
                        </div>
                        <div class="form-group">
                            <label>Email de Contacto</label>
                            <input type="email" id="edit_email_contacto" class="form-control" value="${c.email_contacto || ''}">
                        </div>
                        <div class="form-group">
                            <label>Estado del Cliente</label>
                            <div style="display: flex; align-items: center; gap: 10px; margin-top: 5px;">
                                <label class="switch">
                                    <input type="checkbox" id="edit_activo" ${c.activo ? 'checked' : ''}>
                                    <span class="slider"></span>
                                </label>
                                <span id="status_label_cli" class="status ${c.activo ? 'status-activo' : 'status-inactivo'}">
                                    ${c.activo ? 'Activo' : 'Inactivo'}
                                </span>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer-premium">
                        <button type="button" class="btn btn-ghost" onclick="closeModal()">Cancelar</button>
                        <button type="submit" class="btn btn-primary">Guardar Cambios</button>
                    </div>
                </div>
            </form>
        `;
        document.getElementById('modalBody').innerHTML = formHtml;
        
        // Manejo visual del switch
        const toggle = document.getElementById('edit_activo');
        const label = document.getElementById('status_label_cli');
        toggle.addEventListener('change', () => {
            const isActivo = toggle.checked;
            label.textContent = isActivo ? 'Activo' : 'Inactivo';
            label.className = `status ${isActivo ? 'status-activo' : 'status-inactivo'}`;
        });

        document.getElementById('editClienteForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = {
                tipo_persona: document.getElementById('edit_tipo_persona').value,
                tipo_identificacion: document.getElementById('edit_tipo_identificacion').value,
                identificacion: document.getElementById('edit_identificacion').value,
                nombre_o_razon_social: document.getElementById('edit_nombre_o_razon_social').value,
                telefono: document.getElementById('edit_telefono').value || null,
                email_contacto: document.getElementById('edit_email_contacto').value || null,
                activo: document.getElementById('edit_activo').checked
            };

            try {
                // Actualización general vía Código Único
                await apiClient.put(`/clientes/codigo/${codigo}`, formData);
                
                Swal.fire({
                    icon: 'success',
                    title: '¡Actualizado!',
                    text: 'Los datos del cliente han sido guardados.',
                    timer: 2000,
                    showConfirmButton: false
                });
                closeModal();
                renderClientes();
            } catch (error) {
                Swal.fire('Error', error.message, 'error');
            }
        });
    } catch (error) {
        Swal.fire('Error', 'No se pudo cargar la información del cliente: ' + error.message, 'error');
    }
}



// MODAL REPLACED BY REDIRECT
function showCreateUsuarioModal() {
    window.location.href = 'crear-usuario.html';
}
window.showCreateUsuarioModal = showCreateUsuarioModal;


async function showUsuarioDetails(id) {
    showModal('Detalles del Usuario', '<div class="loader-container"><div class="loader"></div></div>', { hideHeader: true });
    
    try {
        const u = await apiClient.get(`/usuarios/${id}`);
        const html = `
            <div class="detail-view-container">
                <div class="detail-header-banner">
                    <button class="close-banner" onclick="closeModal()"><i data-lucide="x" size="20"></i></button>
                    <div class="detail-avatar-circle">
                        <i data-lucide="user"></i>
                    </div>
                    <div class="detail-header-info">
                        <h2>${u.nombre}</h2>
                        <p>${u.email} • <span class="badge-rol role-${u.rol}" style="background: white; color: var(--primary);">${u.rol}</span></p>
                    </div>
                </div>

                <div class="detail-content-area">
                    <div class="detail-section-title">
                        <i data-lucide="activity" size="16"></i> Historial de Sesiones
                    </div>
                    
                    <div class="table-mini" style="background: white; border-radius: 12px; border: 1px solid var(--border); overflow: hidden;">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Ingreso</th>
                                    <th>Salida</th>
                                    <th>Duración</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${u.historial_sesiones.length > 0 ? u.historial_sesiones.slice(0, 5).map(s => `
                                    <tr>
                                        <td>${new Date(s.fecha_ingreso).toLocaleString()}</td>
                                        <td>${s.fecha_salida ? new Date(s.fecha_salida).toLocaleString() : '<span class="status status-activo">En curso</span>'}</td>
                                        <td>${s.duracion_minutos ? s.duracion_minutos + ' min' : '-'}</td>
                                    </tr>
                                `).join('') : '<tr><td colspan="3" class="text-center text-muted">No hay sesiones registradas</td></tr>'}
                            </tbody>
                        </table>
                    </div>

                    <div class="detail-section-title">
                        <i data-lucide="users" size="16"></i> Clientes Registrados
                    </div>
                    <div class="registered-tags">
                        ${u.clientes_registrados.length > 0 ? u.clientes_registrados.map(c => `
                            <span class="client-tag-premium"><i data-lucide="user"></i> ${c.nombre_o_razon_social}</span>
                        `).join('') : '<p class="text-muted" style="padding: 1rem; text-align: center;">No ha registrado clientes todavía.</p>'}
                    </div>

                    <div class="modal-footer-premium">
                        <button class="btn btn-ghost" onclick="closeModal()">Cerrar</button>
                        <button class="btn btn-primary" onclick="showEditUsuarioModal(${u.id_usuario})">
                            <i data-lucide="edit-3"></i> Editar Usuario
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.getElementById('modalBody').innerHTML = html;
        lucide.createIcons();
    } catch (error) {
        Swal.fire('Error', 'No se pudieron cargar los detalles: ' + error.message, 'error');
    }
}

async function toggleUsuarioEstado(id, estadoActual) {
    const nuevoEstado = estadoActual === 'activo' ? 'inactivo' : 'activo';
    
    const result = await Swal.fire({
        title: '¿Confirmar cambio?',
        text: `¿Estás seguro de cambiar el estado a ${nuevoEstado}?`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: 'var(--primary)',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, cambiar',
        cancelButtonText: 'Cancelar'
    });

    if (result.isConfirmed) {
        try {
            // El backend ahora espera { "nuevo_estado": "..." }
            await apiClient.put(`/usuarios/${id}/estado`, { nuevo_estado: nuevoEstado });
            Swal.fire({
                icon: 'success',
                title: 'Estado actualizado',
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 2000
            });
            renderUsuarios();
        } catch (error) {
            Swal.fire('Error', error.message, 'error');
        }
    } else {
        renderUsuarios(); // Re-render to reset switch
    }
}

async function showEditUsuarioModal(id) {
    showModal('Editar Usuario', '<div class="loader-container"><div class="loader"></div></div>', { hideHeader: true, bodyClass: 'no-padding' });
    try {
        const u = await apiClient.get(`/usuarios/${id}`);
        const html = `
            <form id="editUsuarioForm" class="modal-form">
                <div class="modal-form-header">
                    <button type="button" class="close-banner" onclick="closeModal()"><i data-lucide="x" size="20"></i></button>
                    <i data-lucide="user-plus"></i>
                    <div class="title">Modificar Usuario</div>
                </div>
                <div class="modal-form-container">
                    <div class="form-grid">
                        <div class="form-group">
                            <label>Nombre Completo</label>
                            <input type="text" id="edit_u_nombre" class="form-control" value="${u.nombre}" required minlength="3">
                        </div>
                        <div class="form-group">
                            <label>Email</label>
                            <input type="email" id="edit_u_email" class="form-control" value="${u.email}" required>
                        </div>
                        <div class="form-group">
                            <label>Rol</label>
                            <select id="edit_u_rol" class="form-control" required>
                                <option value="colaborador" ${u.rol === 'colaborador' ? 'selected' : ''}>Colaborador</option>
                                <option value="admin" ${u.rol === 'admin' ? 'selected' : ''}>Administrador</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Estado</label>
                            <div style="display: flex; align-items: center; gap: 10px; margin-top: 5px;">
                                <label class="switch">
                                    <input type="checkbox" id="edit_u_estado_toggle" ${u.estado === 'activo' ? 'checked' : ''}>
                                    <span class="slider"></span>
                                </label>
                                <span id="status_label" class="status status-${u.estado}">${u.estado}</span>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer-premium">
                        <button type="button" class="btn btn-ghost" onclick="closeModal()">Cancelar</button>
                        <button type="submit" class="btn btn-primary">Guardar Cambios</button>
                    </div>
                </div>
            </form>
        `;
        document.getElementById('modalBody').innerHTML = html;

        // Toggle label update
        const toggle = document.getElementById('edit_u_estado_toggle');
        const label = document.getElementById('status_label');
        toggle.addEventListener('change', () => {
            const isActivo = toggle.checked;
            label.textContent = isActivo ? 'activo' : 'inactivo';
            label.className = `status status-${isActivo ? 'activo' : 'inactivo'}`;
        });

        document.getElementById('editUsuarioForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                nombre: document.getElementById('edit_u_nombre').value,
                email: document.getElementById('edit_u_email').value,
                rol: document.getElementById('edit_u_rol').value,
                estado: toggle.checked ? 'activo' : 'inactivo'
            };
            try {
                await apiClient.patch(`/usuarios/${id}`, data);
                Swal.fire({
                    icon: 'success',
                    title: '¡Actualizado!',
                    text: 'Los datos del usuario han sido guardados.',
                    timer: 2000,
                    showConfirmButton: false
                });
                closeModal();
                renderUsuarios();
            } catch (error) {
                Swal.fire('Error', error.message, 'error');
            }
        });
    } catch (error) {
        Swal.fire('Error', error.message, 'error');
    }
}
async function showContratoDetails(codigo, tipo) {
    // Abrir en nueva pestaña en lugar de modal
    window.open(`/contrato-detalle.html?codigo=${codigo}&tipo=${tipo}`, '_blank');
}

// Función auxiliar para descargar
function downloadPDF(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}


// MODAL REPLACED BY REDIRECT
function showCreateContratoModal(tipo) {
    window.location.href = `crear-contrato.html?tipo=${tipo}`;
}
window.showCreateContratoModal = showCreateContratoModal;


// --- AUDIT LOGS FUNCTIONS ---

async function renderAuditoria() {
    const container = document.getElementById('content-container');
    try {
        const data = await apiClient.get('/auditoria/logs?limit=50');
        
        container.innerHTML = `
            <div class="header-with-action animate-fade-in">
                <div>
                    <h2>Registro de Auditoría</h2>
                    <p class="text-muted">Seguimiento detallado de cambios y acciones en el sistema</p>
                </div>
                <div class="header-badges">
                    <span class="badge-rol role-admin"><i data-lucide="shield-check" size="14"></i> Solo Administradores</span>
                </div>
            </div>
            
            <div class="glass mt-2 animate-slide-up">
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Fecha y Hora</th>
                                <th>Usuario</th>
                                <th>Acción</th>
                                <th>Tabla</th>
                                <th>ID Ref.</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.length > 0 ? data.map(log => `
                                <tr>
                                    <td>
                                        <div style="font-weight: 600;">${new Date(log.fecha_cambio).toLocaleDateString()}</div>
                                        <div class="text-muted" style="font-size: 0.75rem;">${new Date(log.fecha_cambio).toLocaleTimeString()}</div>
                                    </td>
                                    <td>
                                        <div class="audit-table-user">
                                            <div class="avatar-mini">${(log.usuario_nombre || 'S').charAt(0)}</div>
                                            <span>${log.usuario_nombre || 'Sistema'}</span>
                                        </div>
                                    </td>
                                    <td>${formatAuditAction(log.accion)}</td>
                                    <td><span class="status status-inactivo" style="font-size: 0.7rem; font-family: monospace;">${log.tabla_afectada}</span></td>
                                    <td><span class="audit-id-badge">#${log.id_registro_afectado}</span></td>
                                    <td class="actions">
                                        <button class="btn-icon" title="Ver detalle de cambios" onclick="showAuditLogDetail(${JSON.stringify(log).replace(/"/g, '&quot;')})">
                                            <i data-lucide="code"></i>
                                        </button>
                                    </td>
                                </tr>
                            `).join('') : '<tr><td colspan="6" class="text-center py-4 text-muted">No se encontraron registros de auditoría.</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        lucide.createIcons();
    } catch (error) {
        Swal.fire('Error', 'No se pudieron cargar los logs de auditoría: ' + error.message, 'error');
    }
}

function formatAuditAction(accion) {
    const act = accion.toLowerCase();
    let label = accion;
    let className = 'audit-action-other';
    let icon = 'info';

    if (act.includes('crear') || act.includes('create') || act.includes('insert')) {
        className = 'audit-action-create';
        icon = 'plus-circle';
    } else if (act.includes('actualizar') || act.includes('update') || act.includes('edit')) {
        className = 'audit-action-update';
        icon = 'refresh-cw';
    } else if (act.includes('borrar') || act.includes('delete') || act.includes('eliminar')) {
        className = 'audit-action-delete';
        icon = 'trash-2';
    } else if (act.includes('login')) {
        className = 'audit-action-login';
        icon = 'log-in';
    }

    return `<span class="audit-action-badge ${className}"><i data-lucide="${icon}" size="12"></i> ${label}</span>`;
}

function showAuditLogDetail(log) {
    const detailHtml = `
        <div class="detail-view-container">
            <div class="detail-header-banner" style="padding: 2rem; background: linear-gradient(135deg, #1e293b 0%, #334155 100%);">
                <button class="close-banner" onclick="closeModal()"><i data-lucide="x" size="20"></i></button>
                <div class="detail-avatar-circle" style="background: rgba(255,255,255,0.1);">
                    <i data-lucide="database"></i>
                </div>
                <div class="detail-header-info">
                    <h2 style="font-size: 1.5rem;">Detalle de Operación</h2>
                    <p>${log.accion} en ${log.tabla_afectada} (ID: ${log.id_registro_afectado})</p>
                </div>
            </div>

            <div class="detail-content-area" style="padding: 1.5rem;">
                <div class="detail-stats-grid" style="grid-template-columns: repeat(3, 1fr); margin-bottom: 2rem;">
                    <div class="stat-item-premium">
                        <label>Responsable</label>
                        <div class="stat-value-premium">${log.usuario_nombre || 'Sistema'}</div>
                    </div>
                    <div class="stat-item-premium">
                        <label>Fecha del Cambio</label>
                        <div class="stat-value-premium">${new Date(log.fecha_cambio).toLocaleString()}</div>
                    </div>
                    <div class="stat-item-premium">
                        <label>Log ID</label>
                        <div class="stat-value-premium">#${log.id_log}</div>
                    </div>
                </div>

                <div class="detail-section-title">
                    <i data-lucide="file-json" size="16"></i> Carga de Datos (JSON)
                </div>
                
                <div class="audit-detail-json mt-1">
                    ${log.detalle_cambio ? syntaxHighlightJSON(log.detalle_cambio) : '<span class="text-muted">No hay detalles específicos registrados para este cambio.</span>'}
                </div>

                <div class="modal-footer-premium">
                    <button class="btn btn-ghost" onclick="closeModal()">Cerrar</button>
                    ${log.detalle_cambio ? `<button class="btn btn-primary" id="btnCopyJson">
                        <i data-lucide="copy"></i> Copiar JSON
                    </button>` : ''}
                </div>
            </div>
        </div>
    `;
    showModal('Detalle de Auditoría', detailHtml, { hideHeader: true, bodyClass: 'no-padding' });
    
    if (log.detalle_cambio) {
        document.getElementById('btnCopyJson').addEventListener('click', () => {
            copyJSONToClipboard(log.detalle_cambio);
        });
    }
}

function syntaxHighlightJSON(json) {
    if (typeof json !== 'string') {
        json = JSON.stringify(json, undefined, 2);
    }
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        let cls = 'span'; // string
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                return '<b>' + match + '</b>'; // key
            } else {
                return '<span>' + match + '</span>'; // string value
            }
        } else if (/true|false/.test(match)) {
            return '<i style="color: #6ee7b7;">' + match + '</i>'; // boolean
        } else if (/null/.test(match)) {
            return '<i style="color: #94a3b8;">' + match + '</i>'; // null
        }
        return '<i>' + match + '</i>'; // number
    });
}

function copyJSONToClipboard(json) {
    const text = JSON.stringify(json, null, 2);
    navigator.clipboard.writeText(text).then(() => {
        Swal.fire({
            icon: 'success',
            title: 'Copiado',
            text: 'El JSON ha sido copiado al portapapeles',
            toast: true,
            position: 'top-end',
            timer: 2000,
            showConfirmButton: false
        });
    });
}

function handleGlobalSearch(query) {
    const q = query.toLowerCase().trim();
    if (activeSection === 'home') return; // En el dashboard principal por ahora no filtramos la tabla de alertas así

    const rows = document.querySelectorAll('.data-table tbody tr');
    
    rows.forEach(row => {
        // Ignorar la fila de "no hay resultados" si ya existe
        if (row.id === 'no-results-msg') return;

        const text = row.textContent.toLowerCase();
        if (text.includes(q)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });

    // Gestionar mensaje de "sin resultados"
    const tbody = document.querySelector('.data-table tbody');
    if (tbody) {
        const visibleRows = Array.from(rows).filter(r => r.style.display !== 'none' && r.id !== 'no-results-msg');
        const noResultsId = 'no-results-msg';
        let noResultsMsg = document.getElementById(noResultsId);

        if (visibleRows.length === 0) {
            if (!noResultsMsg) {
                const colCount = document.querySelectorAll('.data-table thead th').length;
                noResultsMsg = document.createElement('tr');
                noResultsMsg.id = noResultsId;
                noResultsMsg.innerHTML = `<td colspan="${colCount}" class="text-center py-4 text-muted">No se encontraron resultados para "${query}"</td>`;
                tbody.appendChild(noResultsMsg);
            }
        } else {
            if (noResultsMsg) noResultsMsg.remove();
        }
    }
}

// REDIRECTION FUNCTIONS - Explicitly defined at top level for onclick access
window.showCreateClienteModal = function() {
    window.location.href = 'crear-cliente.html';
};

window.showCreateUsuarioModal = function() {
    window.location.href = 'crear-usuario.html';
};

window.showCreateContratoModal = function(tipo) {
    if (tipo) {
        window.location.href = `crear-contrato.html?tipo=${tipo}`;
    } else {
        console.error("Tipo de contrato no especificado");
    }
};

// Registro global de otras funciones para acceso desde HTML (onclick)
if (typeof window !== 'undefined') {
    window.showEditClienteModal = showEditClienteModal;
    window.showClienteDetails = showClienteDetails;
    window.toggleClienteEstado = toggleClienteEstado;
    window.showContratoDetails = showContratoDetails;
    window.showEditUsuarioModal = showEditUsuarioModal;
    window.showUsuarioDetails = showUsuarioDetails;
    window.toggleUsuarioEstado = toggleUsuarioEstado;
    window.showAuditLogDetail = showAuditLogDetail;
    window.loadSection = loadSection;
    window.renderSummary = renderSummary;
    window.renderClientes = renderClientes;
    window.renderContratos = renderContratos;
    window.renderUsuarios = renderUsuarios;
    window.renderAuditoria = renderAuditoria;

    console.log("Funciones del dashboard registradas globalmente.");
}


