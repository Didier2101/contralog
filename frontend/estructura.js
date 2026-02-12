// estructura.js
const fs = require('fs');
const path = require('path');

function mostrarEstructura(dir, nivel = 0) {
    // Leer contenido del directorio
    const elementos = fs.readdirSync(dir);
    
    // Filtrar solo los archivos que nos interesan (y directorios)
    elementos.forEach((elemento, index) => {
        const rutaCompleta = path.join(dir, elemento);
        const esUltimo = index === elementos.length - 1;
        const prefijo = nivel === 0 ? '' : '│   '.repeat(nivel - 1) + (esUltimo ? '└── ' : '├── ');
        
        try {
            const stats = fs.statSync(rutaCompleta);
            
            if (stats.isDirectory()) {
                // Es una carpeta
                console.log(`${prefijo}📁 ${elemento}/`);
                mostrarEstructura(rutaCompleta, nivel + 1);
            } else {
                // Es un archivo - mostrar solo los tipos que nos interesan
                const extension = path.extname(elemento).toLowerCase();
                if (['.html', '.css', '.js'].includes(extension)) {
                    let icono = '📄';
                    if (extension === '.html') icono = '🌐';
                    else if (extension === '.css') icono = '🎨';
                    else if (extension === '.js') icono = '📜';
                    
                    console.log(`${prefijo}${icono} ${elemento}`);
                }
            }
        } catch (error) {
            // Ignorar errores de permisos
        }
    });
}

// Obtener el directorio actual o el especificado
const directorio = process.argv[2] || '.';

console.log(`\n📂 Estructura de: ${path.resolve(directorio)}\n`);
mostrarEstructura(directorio);
console.log(''); // Línea en blanco al final
