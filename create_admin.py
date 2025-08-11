
from app import app, db
from models import User

def create_admin_user():
    with app.app_context():
        # Verificar si ya existe un usuario admin
        existing_user = User.query.filter_by(username='admin').first()
        
        if existing_user:
            print("El usuario 'admin' ya existe.")
            return
        
        # Crear usuario administrador
        admin_user = User(username='admin')
        admin_user.set_password('admin123')  # Cambia esta contraseña por una más segura
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("Usuario administrador creado:")
        print("Usuario: admin")
        print("Contraseña: admin123")
        print("\n¡IMPORTANTE: Cambia esta contraseña por una más segura!")

if __name__ == '__main__':
    create_admin_user()
