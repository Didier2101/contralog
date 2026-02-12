/**
 * Dashboard Logic for ContraLog
 * Handles navigation, rendering and interactions
 */

let activeSection = 'home';

document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
});

function initDashboard() {
    const userStr = localStorage.getItem('user');
    const token = localStorage.getItem('access_token');

    if (!userStr || !token) {
        window.location.href = 'index.html';
        return;
    }

    const user = JSON.parse(userStr);
    
    // UI Elements
    document.getElementById('userName').textContent = user.nombre;
    document.getElementById('userRole').textContent = user.rol;

    // Check Role-based Visibility
    if (user.rol !== 'admin') {
        document.querySelectorAll('.hide-colaborador').forEach(el => el.style.display = 'none');
    }

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

    // Logout
    document.getElementById('logoutBtn').addEventListener('click', logout);

    // Initial load
    loadSection('home');
    initNotifications();
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = 'index.html';
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
                <div class="notification-item warning" onclick="showContratoDetails('${a.contrato_codigo}', '${a.tipo}')">
                    <div class="notification-content" style="padding: 10px; border-bottom: 1px solid #eee; cursor: pointer;">
                        <div style="font-weight: 700; font-size: 0.8rem; color: #d97706;">⚠️ VENCIMIENTO PRÓXIMO</div>
                        <div style="font-size: 0.85rem;">${a.nombre_o_razon_social}</div>
                        <div style="font-size: 0.75rem; color: #666;">Vence el ${new Date(a.fecha_final).toLocaleDateString()}</div>
                    </div>
                </div>
            `).join('');
        } else {
            badge.style.display = 'none';
            list.innerHTML = '<div class="notification-empty">No hay alertas pendientes</div>';
        }
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

async function loadSection(section) {
    activeSection = section;
    const container = document.getElementById('content-container');
    container.innerHTML = `
        <div class="enterprise-loader">
            <div class="enterprise-spinner"></div>
            <p style="margin-top: 1rem; color: var(--nubeware-gray-600);">Cargando sección...</p>
        </div>
    `;

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
        <div class="section-header">
            <div>
                <h2 class="section-title">Resumen del Sistema</h2>
                <p style="color: var(--nubeware-gray-500); font-size: 0.9rem;">Estado actual de la gestión documental</p>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">👥</div>
                <div class="stat-info">
                    <span class="value">${clientes.length}</span>
                    <span class="label">Clientes</span>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📄</div>
                <div class="stat-info">
                    <span class="value">${activosCount}</span>
                    <span class="label">Contratos Activos</span>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="color: var(--nubeware-warning)">⚠️</div>
                <div class="stat-info">
                    <span class="value">${alerts.length}</span>
                    <span class="label">Vencimientos</span>
                </div>
            </div>
        </div>

        <div class="section-header" style="margin-top: 2rem; margin-bottom: 1rem;">
            <h3 class="section-title">Alertas Críticas</h3>
        </div>
        
        <div class="cl-table-container">
            <table class="cl-table">
                <thead>
                    <tr>
                        <th>Código</th>
                        <th>Cliente / Razón Social</th>
                        <th>Fecha Final</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
                    ${alerts.length > 0 ? alerts.map(a => `
                        <tr>
                            <td style="font-family: monospace; font-weight: 600;">${a.contrato_codigo}</td>
                            <td>${a.nombre_o_razon_social}</td>
                            <td>${new Date(a.fecha_final).toLocaleDateString()}</td>
                            <td>
                                <span class="enterprise-status-header vencido">
                                    VENCE PRONTO
                                </span>
                            </td>
                        </tr>
                    `).join('') : '<tr><td colspan="4" style="text-align: center; padding: 2rem; color: #666;">No hay alertas críticas</td></tr>'}
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
            <div class="section-header">
                <div>
                    <h2 class="section-title">Gestión de Clientes</h2>
                    <p style="color: var(--nubeware-gray-500); font-size: 0.9rem;">Directorio de personas naturales y jurídicas</p>
                </div>
                <button class="btn-primary" onclick="showCreateClienteModal()">
                    + Nuevo Cliente
                </button>
            </div>
            
            <div class="cl-table-container">
                <table class="cl-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nombre / Razón Social</th>
                            <th>Teléfono</th>
                            <th>Estado</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.length > 0 ? data.map(cliente => `
                            <tr>
                                <td style="font-family: monospace;">${cliente.identificacion}</td>
                                <td style="font-weight: 600;">${cliente.nombre_o_razon_social}</td>
                                <td>${cliente.telefono || '-'}</td>
                                <td>
                                    <span class="enterprise-status-header ${cliente.activo ? 'activo' : 'pendiente'}">
                                        ${cliente.activo ? 'ACTIVO' : 'INACTIVO'}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn-logout" title="Ver detalle" onclick="showClienteDetails('${cliente.codigo_unico}')">
                                        👁️
                                    </button>
                                </td>
                            </tr>
                        `).join('') : '<tr><td colspan="5" style="text-align: center; padding: 2rem;">No hay clientes registrados.</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        Notifications.error('Error', 'No se pudieron cargar los clientes');
    }
}

async function renderContratos() {
    const container = document.getElementById('content-container');
    try {
        const data = await apiClient.get('/contratos/listar?pagina=1');
        
        container.innerHTML = `
            <div class="section-header">
                <div>
                    <h2 class="section-title">Gestión de Contratos</h2>
                    <p style="color: var(--nubeware-gray-500); font-size: 0.9rem;">Seguimiento de vigencias y pólizas</p>
                </div>
                <div style="display: flex; gap: 0.5rem;">
                    <button class="enterprise-status-header" onclick="showCreateContratoModal('natural')">
                        + Natural
                    </button>
                    <button class="btn-primary" onclick="showCreateContratoModal('juridico')">
                        + Jurídico
                    </button>
                </div>
            </div>
            
            <div class="cl-table-container">
                <table class="cl-table">
                    <thead>
                        <tr>
                            <th>Código</th>
                            <th>Cliente</th>
                            <th>Tipo</th>
                            <th>Vencimiento</th>
                            <th>Estado</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.length > 0 ? data.map(c => `
                            <tr>
                                <td style="font-family: monospace; font-weight: 700; color: var(--nubeware-primary);">
                                    ${c.contrato_codigo || c.codigo_unico}
                                </td>
                                <td>
                                    <div style="display: flex; flex-direction: column;">
                                        <span style="font-weight: 600;">${c.cliente_nombre || 'Cliente'}</span>
                                        <span style="font-size: 0.75rem; color: #666;">${c.cliente_codigo || ''}</span>
                                    </div>
                                </td>
                                <td>
                                    <span class="enterprise-type-badge">${c.tipo_contrato}</span>
                                </td>
                                <td>${new Date(c.fecha_final).toLocaleDateString()}</td>
                                <td>
                                    <span class="enterprise-status-header ${c.estado === 'activo' ? 'activo' : (c.estado === 'vencido' ? 'vencido' : 'pendiente')}">
                                        ${c.estado.toUpperCase()}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn-logout" title="Ver Detalles" onclick="showContratoDetails('${c.contrato_codigo || c.codigo_unico}', '${c.tipo_contrato}')">
                                        👁️
                                    </button>
                                </td>
                            </tr>
                        `).join('') : '<tr><td colspan="6" style="text-align: center; padding: 2rem;">No hay contratos registrados.</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        Notifications.error('Error', 'No se pudieron cargar los contratos');
    }
}

async function renderUsuarios() {
    const container = document.getElementById('content-container');
    try {
        const data = await apiClient.get('/usuarios/listar');
        
        container.innerHTML = `
            <div class="section-header">
                <div>
                    <h2 class="section-title">Usuarios del Sistema</h2>
                    <p style="color: var(--nubeware-gray-500); font-size: 0.9rem;">Accesos y privilegios</p>
                </div>
                <button class="btn-primary" onclick="showCreateUsuarioModal()">
                    + Crear Usuario
                </button>
            </div>
            
            <div class="cl-table-container">
                <table class="cl-table">
                    <thead>
                        <tr>
                            <th>Nombre</th>
                            <th>Email</th>
                            <th>Rol</th>
                            <th>Estado</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.map(u => `
                            <tr>
                                <td style="font-weight: 600;">${u.nombre}</td>
                                <td>${u.email}</td>
                                <td><span class="enterprise-type-badge">${u.rol}</span></td>
                                <td>
                                    <span class="enterprise-status-header ${u.estado === 'activo' ? 'activo' : 'pendiente'}">
                                        ${u.estado.toUpperCase()}
                                    </span>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        Notifications.error('Error', 'No se pudieron cargar los usuarios');
    }
}

async function renderAuditoria() {
    const container = document.getElementById('content-container');
    try {
        const data = await apiClient.get('/usuarios/auditoria');
        
        container.innerHTML = `
            <div class="section-header">
                <div>
                    <h2 class="section-title">Registro de Auditoría</h2>
                    <p style="color: var(--nubeware-gray-500); font-size: 0.9rem;">Historial de actividades del sistema</p>
                </div>
            </div>
            
            <div class="cl-table-container">
                <table class="cl-table">
                    <thead>
                        <tr>
                            <th>Fecha</th>
                            <th>Usuario</th>
                            <th>Acción</th>
                            <th>Módulo</th>
                            <th>Detalle</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.slice(0, 50).map(a => `
                            <tr>
                                <td style="font-size: 0.8rem;">${new Date(a.fecha_accion).toLocaleString()}</td>
                                <td style="font-weight: 600;">${a.nombre_usuario}</td>
                                <td><span class="enterprise-type-badge">${a.accion}</span></td>
                                <td>${a.modulo}</td>
                                <td style="font-size: 0.8rem; color: #666;">${a.detalle}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        Notifications.error('Error', 'No se pudo cargar la auditoría');
    }
}

function showContratoDetails(codigo, tipo) {
    if (!codigo) return;
    window.location.href = `contrato-detalle.html?codigo=${codigo}&tipo=${tipo}`;
}

function showClienteDetails(codigo) {
    if (!codigo) return;
    window.location.href = `cliente-detalle.html?codigo=${codigo}`;
}

// Global modal helper
function showModal(title, content) {
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalBody').innerHTML = content;
    document.getElementById('modal-container').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('modal-container').classList.add('hidden');
}

document.getElementById('closeModalBtn').onclick = closeModal;
window.onclick = (e) => {
    if (e.target.id === 'modal-container') closeModal();
};
