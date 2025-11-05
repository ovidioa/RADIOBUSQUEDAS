from flask import render_template, request, flash, redirect, url_for, session, Response
from functools import wraps
from sqlalchemy import or_, and_
from app import app, db
from models import XMLData, User
# Import moved to avoid circular import
import os
import csv
import io
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Constants
MAX_EXPORT_TEXT_LENGTH = 500  # Maximum characters for text content in exports

def get_story_only_filter():
    """Helper function to get filter for Story type records only.
    Excludes GroupPack and StoryPack types as per Phase 8."""
    return or_(
        XMLData.object_type == 'Story',
        XMLData.object_type.is_(None)
    )

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
        
        # Exclude GroupPack and StoryPack types by default (as per Phase 8)
        # Only show Story type unless explicitly searching for a specific type
        if 'object_type' not in search_params:
            query = query.filter(get_story_only_filter())
        
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

@app.route('/advanced_search')
@login_required
def advanced_search():
    """Advanced search page with more specific filters"""
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
        
        # Exclude GroupPack and StoryPack types by default (as per Phase 8)
        if 'object_type' not in search_params:
            query = query.filter(get_story_only_filter())
        
        # Add filters for each search parameter
        filters = []
        
        # Text content filter
        if 'text_content' in search_params:
            filters.append(XMLData.text_content.like(f'%{search_params["text_content"]}%'))
        
        # Program start time filter
        if 'program_start_time' in search_params:
            filters.append(XMLData.program_start_time.like(f'%{search_params["program_start_time"]}%'))
        
        # Story broadcast time filter
        if 'broadcast_start_time' in search_params:
            filters.append(XMLData.broadcast_start_time.like(f'%{search_params["broadcast_start_time"]}%'))
        
        # Guest filter
        if 'guest' in search_params:
            filters.append(XMLData.guest.like(f'%{search_params["guest"]}%'))
        
        # Title filter
        if 'title' in search_params:
            filters.append(XMLData.title.like(f'%{search_params["title"]}%'))
        
        # Program name filter
        if 'program_name' in search_params:
            filters.append(XMLData.program_name.like(f'%{search_params["program_name"]}%'))
        
        # Program date filter
        if 'program_date' in search_params:
            filters.append(XMLData.program_date.like(f'%{search_params["program_date"]}%'))
        
        # Item code filter
        if 'item_code' in search_params:
            filters.append(XMLData.item_code.like(f'%{search_params["item_code"]}%'))
        
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
    
    return render_template('advanced_search.html', 
                         results=results, 
                         search_params=search_params,
                         total_count=total_count,
                         total_records=total_records)

@app.route('/admin')
@login_required
def admin():
    """Administration page for XML processing and database management"""
    # Get total record count
    total_records = XMLData.query.count()
    
    # Get distinct source files (processed directories)
    distinct_files = db.session.query(XMLData.source_file).distinct().count()
    
    # Get statistics
    stats = {
        'total_records': total_records,
        'distinct_files': distinct_files,
        'total_programs': db.session.query(XMLData.program_name).filter(XMLData.program_name.isnot(None)).distinct().count(),
        'date_range': db.session.query(
            db.func.min(XMLData.program_date),
            db.func.max(XMLData.program_date)
        ).first()
    }
    
    return render_template('admin.html', stats=stats)

@app.route('/export')
@login_required
def export():
    """Export search results to CSV or XML"""
    # Get export format and options
    export_format = request.args.get('format', 'csv').lower()
    include_text = request.args.get('include_text', 'false').lower() == 'true'
    
    # Get search parameters to filter results
    search_params = {}
    for key in request.args:
        if key not in ['format', 'include_text']:
            value = request.args.get(key, '').strip()
            if value:
                search_params[key] = value
    
    # Build query based on search parameters
    query = XMLData.query
    
    # Exclude GroupPack and StoryPack types by default (as per Phase 8)
    if 'object_type' not in search_params:
        query = query.filter(get_story_only_filter())
    
    if search_params:
        filters = []
        for field, value in search_params.items():
            if hasattr(XMLData, field):
                column = getattr(XMLData, field)
                filters.append(column.like(f'%{value}%'))
        
        if filters:
            query = query.filter(and_(*filters))
    
    # Get all matching results
    # Note: For very large datasets, consider implementing streaming or pagination
    results = query.all()
    
    if not results:
        flash('No hay resultados para exportar', 'warning')
        return redirect(request.referrer or url_for('search'))
    
    # Define fields to export
    base_fields = [
        'item_code', 'program_name', 'program_date', 'program_start_time',
        'broadcast_start_time', 'duration', 'title', 'source_file'
    ]
    
    if include_text:
        base_fields.append('text_content')
    
    # Export to CSV
    if export_format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([field.upper().replace('_', ' ') for field in base_fields])
        
        # Write data
        for result in results:
            row = []
            for field in base_fields:
                value = getattr(result, field, '')
                # Truncate text_content if too long
                if field == 'text_content' and value and len(str(value)) > MAX_EXPORT_TEXT_LENGTH:
                    value = str(value)[:MAX_EXPORT_TEXT_LENGTH] + '...'
                row.append(value or '')
            writer.writerow(row)
        
        # Create response
        response = Response(output.getvalue(), mimetype='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=export.csv'
        return response
    
    # Export to XML
    elif export_format == 'xml':
        root = ET.Element('broadcast_data')
        
        for result in results:
            item = ET.SubElement(root, 'item')
            
            for field in base_fields:
                value = getattr(result, field, '')
                if value:
                    # Truncate text_content if too long
                    if field == 'text_content' and len(str(value)) > MAX_EXPORT_TEXT_LENGTH:
                        value = str(value)[:MAX_EXPORT_TEXT_LENGTH] + '...'
                    elem = ET.SubElement(item, field)
                    elem.text = str(value)
        
        # Pretty print XML
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent='  ')
        
        # Create response
        response = Response(pretty_xml, mimetype='application/xml')
        response.headers['Content-Disposition'] = 'attachment; filename=export.xml'
        return response
    
    else:
        flash('Formato de exportación no válido', 'error')
        return redirect(request.referrer or url_for('search'))

@app.route('/programs')
@login_required
def programs():
    """Show programs by date"""
    # Get distinct programs with their dates
    # Exclude GroupPack and StoryPack types by default (as per Phase 8)
    programs_data = db.session.query(
        XMLData.program_name,
        XMLData.program_date,
        db.func.count(XMLData.id).label('story_count')
    ).filter(
        XMLData.program_name.isnot(None),
        XMLData.program_date.isnot(None),
        get_story_only_filter()
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
        XMLData.program_name.isnot(None),
        get_story_only_filter()
    ).distinct().order_by(XMLData.program_name).all()
    
    program_names = [program[0] for program in unique_programs]
    
    # Get filter parameters
    selected_date = request.args.get('date', '')
    selected_program = request.args.get('program', '')
    
    # Apply filters if provided
    filtered_results = []
    if selected_date or selected_program:
        query = XMLData.query.filter(get_story_only_filter())
        
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
