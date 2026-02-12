/**
 * Login Logic for ContraLog
 */

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    
    // Check if already logged in
    const token = localStorage.getItem('access_token');
    if (token) {
        window.location.href = 'dashboard.html';
    }

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const submitBtn = e.target.querySelector('button');
        const errorMsg = document.getElementById('loginError');

        // Loading state
        submitBtn.disabled = true;
        submitBtn.textContent = 'Verificando...';
        errorMsg.style.display = 'none';

        try {
            const response = await apiClient.post('/auth/login', { email, password });
            
            if (response.access_token) {
                localStorage.setItem('access_token', response.access_token);
                localStorage.setItem('user', JSON.stringify(response.user));
                
                Notifications.success('¡Bienvenido!', 'Acceso concedido correctamente');
                
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1000);
            }
        } catch (error) {
            console.error('Login error:', error);
            errorMsg.style.display = 'block';
            Notifications.error('Error de Acceso', 'Email o contraseña incorrectos');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Ingresar al Sistema';
        }
    });
});
