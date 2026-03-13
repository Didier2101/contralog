const API_BASE_URL = window.CONFIG ? window.CONFIG.API_BASE : "http://localhost:8000";

const apiClient = {
    get: (endpoint) => request(endpoint, 'GET'),
    post: (endpoint, body) => request(endpoint, 'POST', body),
    put: (endpoint, body) => request(endpoint, 'PUT', body),
    patch: (endpoint, body) => request(endpoint, 'PATCH', body),
    delete: (endpoint) => request(endpoint, 'DELETE'),
    
    // Especial para archivos (Contratos)
    postMultipart: (endpoint, formData) => request(endpoint, 'POST', formData, true)
};

async function request(endpoint, method, body = null, isMultipart = false) {
    const token = localStorage.getItem('access_token');
    
    const headers = {};
    if (!isMultipart) {
        headers['Content-Type'] = 'application/json';
    }
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        method,
        headers,
    };

    if (body) {
        config.body = isMultipart ? body : JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        
        if (response.status === 401) {
            // Token expirado o inválido
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            if (window.location.pathname !== '/login.html') {
                window.location.href = 'login.html';
            }
            throw new Error('Sesión expirada');
        }

        const data = await response.json();
        
        if (!response.ok) {
            console.error('❌ Error HTTP:', response.status);
            console.error('📦 Respuesta completa:', data);
            
            // Para errores 422, mostrar detalles de validación
            if (response.status === 422 && data.detail) {
                console.error('🔍 Errores de validación:', data.detail);
                
                // Si es un array de errores de validación de FastAPI
                if (Array.isArray(data.detail)) {
                    const errorMessages = data.detail.map(err => 
                        `${err.loc.join(' -> ')}: ${err.msg}`
                    ).join('\n');
                    throw new Error(`Errores de validación:\n${errorMessages}`);
                }
                
                // Si es un string u objeto simple
                throw new Error(typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail));
            }
            
            throw new Error(data.detail || data.message || 'Ocurrió un error en la petición');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}
