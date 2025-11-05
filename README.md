# RADIOBUSQUEDAS - Sistema de Búsqueda e Indexación XML (DALET)

Sistema completo para leer, indexar y consultar información contenida en archivos XML generados por DALET.

## 🎯 Características

- **Búsqueda Genérica**: Búsqueda rápida por título, código DLT y fechas
- **Búsqueda Avanzada**: Filtros específicos para texto, invitados, horarios
- **Búsqueda por Programa**: Navegación organizada por programas y fechas
- **Exportación**: Resultados en formato CSV o XML
- **Panel de Administración**: Gestión de procesamiento y estadísticas
- **Control de Acceso**: Sistema de login/logout
- **Interfaz Web**: Bootstrap con tablas interactivas y modales

## 📋 Requisitos

- Python 3.11+
- Flask 3.1+
- SQLAlchemy 2.0+
- Base de datos SQLite (desarrollo) / PostgreSQL (producción)

## 🚀 Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/ovidioa/RADIOBUSQUEDAS.git
cd RADIOBUSQUEDAS
```

2. Instalar dependencias:
```bash
pip install flask flask-sqlalchemy gunicorn werkzeug email-validator psycopg2-binary sqlalchemy
```

3. Crear usuario administrador:
```bash
python create_admin.py
```

4. Iniciar el servidor:
```bash
python main.py
```

5. Acceder a la aplicación:
```
http://localhost:5000
```

**Credenciales por defecto:**
- Usuario: `Admin`
- Contraseña: `Admin123!`

## 📁 Estructura del Proyecto

```
RADIOBUSQUEDAS/
├── app.py                      # Aplicación Flask principal
├── models.py                   # Modelos de datos (XMLData, User)
├── routes.py                   # Rutas y endpoints
├── xml_processor.py            # Procesador de archivos XML
├── main.py                     # Punto de entrada
├── create_admin.py            # Script para crear usuario admin
├── test_system.py             # Tests de validación
├── templates/                  # Plantillas HTML
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── search.html
│   ├── advanced_search.html
│   ├── programs.html
│   └── admin.html
├── attached_assets/           # Archivos XML de ejemplo
└── instance/                  # Base de datos SQLite
    └── database.db
```

## 🔍 Funcionalidades Principales

### 1. Procesamiento de XML

El sistema procesa archivos XML de DALET y extrae:
- Información de programas (nombre, fecha, hora)
- Detalles de historias (título, contenido, duración)
- Metadatos (invitados, reporteros, códigos DLT)
- Información de emisión (horarios, duración)

**Tipos de elementos procesados:**
- Story (historias individuales)
- StoryPack (paquetes de historias)
- GroupPack (grupos de contenido)

**Nota:** Por defecto, las búsquedas y exportaciones solo muestran elementos tipo "Story", excluyendo StoryPack y GroupPack.

### 2. Búsqueda Genérica (`/search`)

Búsqueda rápida con filtros:
- Título
- Código DLT (item_code)
- Nombre del programa
- Fecha del programa
- Tipo de objeto
- Y más campos...

**Características:**
- Limitado a 100 resultados por búsqueda
- Aviso si hay más resultados disponibles
- Exportación directa de resultados

### 3. Búsqueda Avanzada (`/advanced_search`)

Filtros específicos:
- Contenido de texto
- Hora de inicio del programa
- Hora de emisión de la historia
- Invitados
- Título
- Nombre del programa
- Fecha del programa
- Código DLT

**Visualización:**
- Fecha del programa
- Nombre del programa
- Hora de emisión del programa
- Hora de emisión de la historia
- Título
- Duración
- Botón de detalles con modal

### 4. Búsqueda por Programa (`/programs`)

Navegación por programas:
- Lista de todos los programas con fechas
- Filtrado por nombre de programa
- Filtrado por fecha
- Contador de historias por programa

### 5. Exportación (`/export`)

Exporta resultados a:
- **CSV**: Archivo separado por comas
- **XML**: Formato XML estructurado

**Campos exportados:**
- Código DLT (item_code)
- Nombre del programa
- Fecha del programa
- Hora de inicio del programa
- Hora de emisión de la historia
- Duración
- Título
- Archivo fuente

**Opciones:**
- Incluir/excluir contenido de texto
- Truncamiento automático de texto largo (500 caracteres)
- Exportación sin texto por defecto

### 6. Panel de Administración (`/admin`)

Gestión del sistema:
- **Estadísticas:**
  - Total de registros
  - Archivos procesados
  - Total de programas
  - Rango de fechas

- **Acciones:**
  - Procesar archivos XML desde directorio
  - Limpiar base de datos completa
  - Ver estado del sistema

## 🔧 Configuración

### Base de Datos

Por defecto usa SQLite:
```python
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
```

Para PostgreSQL (producción):
```python
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:password@host:port/database"
```

### Secret Key

Cambiar en producción:
```python
app.secret_key = os.environ.get("SESSION_SECRET", "tu-clave-secreta-aqui")
```

## 🧪 Testing

Ejecutar tests de validación:
```bash
python test_system.py
```

El script valida:
- Modelo de datos y ORM
- Funcionalidad de búsqueda genérica
- Búsqueda avanzada
- Agrupación de programas
- Capacidades de exportación
- Estadísticas de administración
- Filtrado de tipos

## 📊 Modelo de Datos

### XMLData
Campos principales:
- `id`: Identificador único
- `title`: Título de la historia
- `item_code`: Código DLT
- `program_name`: Nombre del programa
- `program_date`: Fecha del programa
- `program_start_time`: Hora de inicio
- `broadcast_start_time`: Hora de emisión
- `duration`: Duración
- `text_content`: Contenido de texto
- `guest`: Invitados
- `source_file`: Archivo fuente
- `object_type`: Tipo (Story/StoryPack/GroupPack)
- Y más...

### User
- `username`: Nombre de usuario
- `password_hash`: Contraseña hasheada
- `created_at`: Fecha de creación

## 🔒 Seguridad

- Contraseñas hasheadas con Werkzeug
- Sesiones seguras con Flask
- Autenticación requerida para todas las páginas (excepto /login)
- Protección contra inyección SQL con SQLAlchemy ORM

## 📝 Notas Importantes

1. **Tipos Excluidos**: Por defecto, GroupPack y StoryPack se excluyen de búsquedas y exportaciones para enfocarse en historias individuales.

2. **Límite de Resultados**: Las búsquedas están limitadas a 100 resultados para rendimiento. Refinar búsqueda si hay más resultados.

3. **Truncamiento de Texto**: En exportaciones, el texto se trunca a 500 caracteres para mantener archivos manejables.

4. **Procesamiento de XML**: Los archivos XML deben seguir el formato DALET estándar.

## 🔄 Flujo de Trabajo Típico

1. **Login** → Acceder con credenciales
2. **Administración** → Procesar archivos XML desde directorio
3. **Búsqueda** → Buscar historias usando filtros
4. **Visualización** → Ver detalles en modales
5. **Exportación** → Descargar resultados en CSV/XML
6. **Programas** → Navegar por programas y fechas

## 🛠️ Desarrollo Futuro (Opcional)

- Integración con Elasticsearch/OpenSearch
- Procesamiento asíncrono con Celery + Redis
- API REST autenticada
- Procesamiento programado nocturno
- Mejoras de UI con DataTables.js
- Paginación avanzada

## 📞 Soporte

Para problemas o preguntas, consultar la documentación en PROJECT_INSTRUCTIONS.md o crear un issue en GitHub.

## ✅ Estado del Proyecto

**Fases Completadas:**
- ✅ Fase 1: Análisis y Modelo de Datos
- ✅ Fase 2: Búsqueda Genérica
- ✅ Fase 3: Búsqueda Avanzada
- ✅ Fase 4: Búsqueda por Programa
- ✅ Fase 5: Visualización de Resultados
- ✅ Fase 6: Exportación
- ✅ Fase 7: Administración
- ✅ Fase 8: Ajustes Técnicos
- ⏭️ Fase 9: Optimización (Opcional)
- ✅ Fase 10: Pruebas y Validación

**Sistema completamente funcional y listo para producción.**
