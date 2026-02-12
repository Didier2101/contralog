/**
 * LOGIN NUBEWARE - Módulo de autenticación
 * Gestión de contratos y documentos
 */

const NubewareLogin = {
    
    /**
     * Inicializa el módulo de login
     */
    init: function() {
        this.bindEvents();
        this.initIcons();
    },

    /**
     * Inicializa iconos Lucide
     */
    initIcons: function() {
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    },

    /**
     * Bind de eventos
     */
    bindEvents: function() {
        // Toggle password visibility
        const toggleBtn = document.querySelector('#togglePassword');
        const passwordInput = document.querySelector('#password');
        
        if (toggleBtn && passwordInput) {
            toggleBtn.addEventListener('click', function(e) {
                e.preventDefault();
                NubewareLogin.togglePasswordVisibility(passwordInput, toggleBtn);
            });
        }

        // Login form submit
        const loginForm = document.querySelector('#loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', function(e) {
                e.preventDefault();
                NubewareLogin.handleLogin();
            });
        }

        // Enter key support
        document.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const loginForm = document.querySelector('#loginForm');
                if (loginForm && document.activeElement?.form === loginForm) {
                    e.preventDefault();
                    NubewareLogin.handleLogin();
                }
            }
        });
    },

    /**
     * Toggle visibilidad de contraseña
     */
    togglePasswordVisibility: function(passwordInput, toggleBtn) {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        const eyeIcon = toggleBtn.querySelector('i');
        if (eyeIcon) {
            const newIconName = type === 'password' ? 'eye' : 'eye-off';
            eyeIcon.setAttribute('data-lucide', newIconName);
            
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        }
    },

    /**
     * Validar email
     */
    validateEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    /**
     * Mostrar error
     */
    showError: function(message) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'error',
                title: 'Error de autenticación',
                text: message,
                confirmButtonColor: '#0a3a5c',
                confirmButtonText: 'Intentar nuevamente',
                background: 'white',
                backdrop: 'rgba(10, 58, 92, 0.1)'
            });
        } else {
            alert('Error: ' + message);
        }
    },

    /**
     * Mostrar loader
     */
    showLoading: function(show) {
        const submitBtn = document.querySelector('#submitBtn');
        if (!submitBtn) return;
        
        if (show) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
                <span>Ingresando...</span>
                <i data-lucide="loader-2" size="20" class="animate-spin"></i>
            `;
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        } else {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `
                <span>Ingresar</span>
                <i data-lucide="arrow-right" size="20"></i>
            `;
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        }
    },

    /**
     * Manejar login
     */
    handleLogin: async function() {
        // Obtener valores
        const emailInput = document.querySelector('#email');
        const passwordInput = document.querySelector('#password');
        
        const email = emailInput?.value.trim();
        const password = passwordInput?.value.trim();

        // Validaciones
        if (!email || !password) {
            this.showError('Por favor ingresa tu email y contraseña');
            return;
        }

        if (!this.validateEmail(email)) {
            this.showError('Por favor ingresa un email válido');
            return;
        }

        if (password.length < 6) {
            this.showError('La contraseña debe tener al menos 6 caracteres');
            return;
        }

        // Mostrar loader
        this.showLoading(true);

        try {
            // Verificar que apiClient existe
            if (typeof apiClient === 'undefined') {
                console.error('apiClient no está definido');
                
                // Simular login exitoso para demo
                setTimeout(() => {
                    this.showLoading(false);
                    
                    if (typeof Swal !== 'undefined') {
                        Swal.fire({
                            icon: 'success',
                            title: '¡Bienvenido!',
                            text: 'Inicio de sesión exitoso',
                            confirmButtonColor: '#0a3a5c',
                            timer: 1500,
                            showConfirmButton: false
                        }).then(() => {
                            window.location.href = 'dashboard.html';
                        });
                    }
                }, 1000);
                return;
            }

            // Llamar a la API
            const response = await apiClient.post('/auth/login', {
                email: email,
                password: password
            });

            this.showLoading(false);

            if (response && response.token) {
                // Guardar token
                localStorage.setItem('auth_token', response.token);
                localStorage.setItem('user_data', JSON.stringify(response.user));
                
                // Mostrar éxito y redirigir
                if (typeof Swal !== 'undefined') {
                    Swal.fire({
                        icon: 'success',
                        title: '¡Bienvenido!',
                        text: `Hola ${response.user?.nombre || 'Usuario'}`,
                        confirmButtonColor: '#0a3a5c',
                        timer: 1500,
                        showConfirmButton: false
                    }).then(() => {
                        window.location.href = 'dashboard.html';
                    });
                } else {
                    window.location.href = 'dashboard.html';
                }
            } else {
                this.showError('Credenciales incorrectas');
            }
            
        } catch (error) {
            this.showLoading(false);
            console.error('Error login:', error);
            
            let errorMessage = 'Error al conectar con el servidor';
            if (error.response?.data?.message) {
                errorMessage = error.response.data.message;
            } else if (error.message) {
                errorMessage = error.message;
            }
            
            this.showError(errorMessage);
        }
    },

    /**
     * Limpiar formulario
     */
    resetForm: function() {
        const emailInput = document.querySelector('#email');
        const passwordInput = document.querySelector('#password');
        
        if (emailInput) emailInput.value = '';
        if (passwordInput) passwordInput.value = '';
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    NubewareLogin.init();
});