from app.database import SessionLocal
from app.models.usuario import Usuario
from app.models.cargo import Cargo
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin():
    db = SessionLocal()
    try:
        # 1. Asegurar el Cargo
        cargo_admin = db.query(Cargo).filter(Cargo.nombre_cargo == "Administrador").first()
        if not cargo_admin:
            cargo_admin = Cargo(
                codigo_cargo="ADM-001",
                nombre_cargo="Administrador",
                descripcion="Acceso total"
            )
            db.add(cargo_admin)
            db.commit()
            db.refresh(cargo_admin)

        # 2. Crear el Usuario con los nombres de tu modelo
        admin_email = "admin@contralog.com"
        exists = db.query(Usuario).filter(Usuario.email == admin_email).first()
        
        if not exists:
            # Hash de la contraseña
            hashed_password = pwd_context.hash("Admin12345*")
            
            new_admin = Usuario(
                codigo_usuario="USR-ADMIN-01",  # OBLIGATORIO según tu modelo
                nombre="Admin Sistema",
                email=admin_email,
                password=hashed_password,       # Se llama 'password', no 'password_hash'
                rol="admin",                    # Debe ser uno de los Enums ('admin', 'aprobador'...)
                estado="activo",                # Debe ser uno de los Enums ('activo', 'inactivo')
                id_cargo=cargo_admin.id_cargo
            )
            db.add(new_admin)
            db.commit()
            print(f"✅ Usuario admin creado: {admin_email}")
        else:
            print("⚠️ El usuario admin ya existe.")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear el admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()