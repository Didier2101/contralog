usuario: admin@contralog.com
contraseña: admin123
arrancar el backend: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
virtualizar: source venv/bin/activate
mostrar estructura: python3 estructura.py
sube las imagenes: sudo docker-compose up --build -d
arranca la maquina: uvicorn app.main:app --reload