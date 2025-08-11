from flask import render_template, request, flash, redirect, url_for, session
from functools import wraps
from sqlalchemy import or_, and_
from app import app, db
from models import XMLData, User
# Import moved to avoid circular import
import os

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Por favor ingresa usuario y contraseña', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Sesión iniciada correctamente', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Home page with processing options"""
    return render_template('index.html')

@app.route('/process', methods=['POST'])
@login_required
def process_xml():
    """Process XML files from a directory"""
    directory_path = request.form.get('directory_path', '').strip()
    
    if not directory_path:
        directory_path = './attached_assets'  # Default to attached assets directory
    
    if not os.path.exists(directory_path):
        flash(f'El directorio no existe: {directory_path}', 'error')
        return redirect(url_for('index'))
    
    try:
        from xml_processor import XMLProcessor
        processor = XMLProcessor()
        processor.process_directory(directory_path)
        flash(f'Archivos XML procesados exitosamente desde {directory_path}', 'success')
    except Exception as e:
        flash(f'Error procesando archivos XML: {str(e)}', 'error')
    
    return redirect(url_for('search'))

@app.route('/search')
@login_required
def search():
    """Search page with form and results"""
    # Get search parameters
    search_params = {}
    for key in request.args:
        value = request.args.get(key, '').strip()
        if value:
            search_params[key] = value
    
    results = []
    total_count = 0
    
    if search_params:
        # Build query based on search parameters
        query = XMLData.query
        
        # Add filters for each search parameter
        filters = []
        
        for field, value in search_params.items():
            if hasattr(XMLData, field):
                column = getattr(XMLData, field)
                # Use LIKE for partial matching
                filters.append(column.like(f'%{value}%'))
        
        if filters:
            # Combine filters with AND logic
            query = query.filter(and_(*filters))
        
        total_count = query.count()
        
        # Get paginated results (limit to 100 for performance)
        results = query.limit(100).all()
        
        if total_count > 100:
            flash(f'Mostrando los primeros 100 resultados de {total_count} coincidencias totales. Por favor, refina tu búsqueda para obtener resultados más específicos.', 'info')
    
    # Get total record count
    total_records = XMLData.query.count()
    
    return render_template('search.html', 
                         results=results, 
                         search_params=search_params,
                         total_count=total_count,
                         total_records=total_records)

@app.route('/admin')
@login_required
def admin():
    """Administration page for XML processing and database management"""
    return render_template('admin.html')

@app.route('/programs')
@login_required
def programs():
    """Show programs by date"""
    # Get distinct programs with their dates
    programs_data = db.session.query(
        XMLData.program_name,
        XMLData.program_date,
        db.func.count(XMLData.id).label('story_count')
    ).filter(
        XMLData.program_name.isnot(None),
        XMLData.program_date.isnot(None)
    ).group_by(
        XMLData.program_name,
        XMLData.program_date
    ).order_by(
        XMLData.program_date.desc(),
        XMLData.program_name
    ).all()
    
    # Get unique program names for the dropdown
    unique_programs = db.session.query(
        XMLData.program_name
    ).filter(
        XMLData.program_name.isnot(None)
    ).distinct().order_by(XMLData.program_name).all()
    
    program_names = [program[0] for program in unique_programs]
    
    # Get filter parameters
    selected_date = request.args.get('date', '')
    selected_program = request.args.get('program', '')
    
    # Apply filters if provided
    filtered_results = []
    if selected_date or selected_program:
        query = XMLData.query
        
        if selected_date:
            query = query.filter(XMLData.program_date == selected_date)
        
        if selected_program:
            query = query.filter(XMLData.program_name.contains(selected_program))
        
        filtered_results = query.limit(100).all()
    
    return render_template('programs.html', 
                         programs_data=programs_data,
                         filtered_results=filtered_results,
                         selected_date=selected_date,
                         selected_program=selected_program,
                         program_names=program_names)

@app.route('/clear_database', methods=['POST'])
@login_required
def clear_database():
    """Clear all records from the database"""
    try:
        XMLData.query.delete()
        db.session.commit()
        flash('Base de datos limpiada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error limpiando la base de datos: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    flash('Ocurrió un error interno. Por favor, inténtalo de nuevo.', 'error')
    return render_template('index.html'), 500
