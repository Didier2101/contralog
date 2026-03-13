document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const submitBtn = document.getElementById('submitBtn');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value.trim();

            // Detailed validation with SweetAlert2
            if (!email) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Email requerido',
                    text: 'Por favor, ingresa tu dirección de correo electrónico.',
                    confirmButtonColor: '#4F46E5'
                });
                return;
            }

            if (!password) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Contraseña requerida',
                    text: 'La contraseña es obligatoria para ingresar.',
                    confirmButtonColor: '#4F46E5',
                    timer: 3000,
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false
                });
                return;
            }

            // UI State: Loading
            const originalBtnContent = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="loader-sm"></span>';
            submitBtn.disabled = true;

            try {
                const response = await apiClient.post('/auth/login', { email, password });
                
                // Store session data
                localStorage.setItem('access_token', response.access_token);
                localStorage.setItem('user', JSON.stringify(response.user));
                
                // Success Message
                Swal.fire({
                    icon: 'success',
                    title: '¡Ingreso Exitoso!',
                    text: `Bienvenido de nuevo, ${response.user.nombre}.`,
                    showConfirmButton: false,
                    timer: 1500,
                    background: '#F9FAFB'
                }).then(() => {
                    window.location.href = 'index.html';
                });

            } catch (error) {
                // Error handling with SweetAlert2
                Swal.fire({
                    icon: 'error',
                    title: 'Error de acceso',
                    text: error.message || 'Verifica tus credenciales e intenta nuevamente.',
                    confirmButtonColor: '#4F46E5',
                    background: '#F9FAFB'
                });
                console.error('Login failed:', error);
            } finally {
                // Reset UI State
                submitBtn.innerHTML = originalBtnContent;
                submitBtn.disabled = false;
            }
        });
    }

    // Check if already logged in
    const token = localStorage.getItem('access_token');
    if (token && window.location.pathname.endsWith('login.html')) {
        window.location.href = 'index.html';
    }
});

async function logout() {
    const userStr = localStorage.getItem('user');
    const user = userStr ? JSON.parse(userStr) : null;

    if (user && user.id_usuario) {
        try {
            await apiClient.post(`/auth/logout/${user.id_usuario}`);
        } catch (error) {
            console.error('Logout error:', error);
        }
    }
    
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    
    Swal.fire({
        icon: 'info',
        title: 'Sesión Finalizada',
        text: 'Has salido del sistema de forma segura.',
        timer: 2000,
        showConfirmButton: false,
        background: '#F9FAFB'
    }).then(() => {
        window.location.href = 'login.html';
    });
}
