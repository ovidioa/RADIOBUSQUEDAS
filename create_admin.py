
from app import app, db
from models import User

def create_admin_user():
    with app.app_context():
        # Verificar si ya existe un usuario Admin
        existing_user = User.query.filter_by(username='Admin').first()
        
        if existing_user:
            # Si existe, actualizar la contraseña
            existing_user.set_password('Admin123!')
            db.session.commit()
            print("Usuario 'Admin' actualizado.")
            print("Usuario: Admin")
            print("Contraseña: Admin123!")
            return
        
        # Crear usuario administrador
        admin_user = User(username='Admin')
        admin_user.set_password('Admin123!')
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("Usuario administrador creado:")
        print("Usuario: Admin")
        print("Contraseña: Admin123!")
        print("\n¡IMPORTANTE: Cambia esta contraseña por una más segura!")

if __name__ == '__main__':
    create_admin_user()
