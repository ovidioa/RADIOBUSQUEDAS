from app import db
from sqlalchemy import Text, Integer, DateTime
from datetime import datetime

class XMLData(db.Model):
    __tablename__ = 'xml_data'
    
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    
    # Core identification fields
    guid = db.Column(Text)
    object_id = db.Column(Text)
    object_type = db.Column(Text)
    
    # Timing and scheduling
    timestamp = db.Column(Text)
    broadcast_start_time = db.Column(Text)
    broadcast_end_time = db.Column(Text)
    duration = db.Column(Text)
    
    # Content fields
    title = db.Column(Text)
    text_content = db.Column(Text)
    text_duration = db.Column(Text)
    
    # Timing flags
    text_timing = db.Column(Text)
    timegap_timing = db.Column(Text)
    clip_timing = db.Column(Text)
    
    # Status and type information
    title_status = db.Column(Text)
    title_type = db.Column(Text)
    
    # System information
    site_name = db.Column(Text)
    site_version = db.Column(Text)
    export_path = db.Column(Text)
    
    # Content metadata
    planning_area = db.Column(Text)
    linked_story = db.Column(Text)
    
    # Language information
    language_cat = db.Column(Text)
    language_vo = db.Column(Text)
    language_esp = db.Column(Text)
    
    # Audio/media flags
    has_audio_track = db.Column(Text)
    
    # Date fields
    fact_date = db.Column(Text)
    cms_publish_date = db.Column(Text)
    la_carta_publish_date = db.Column(Text)
    record_date = db.Column(Text)
    start_date = db.Column(Text)
    end_date = db.Column(Text)
    kill_date = db.Column(Text)
    
    # Additional metadata
    comment = db.Column(Text)
    locator_type = db.Column(Text)
    locator_family = db.Column(Text)
    
    # Additional broadcast metadata
    computed_start_time = db.Column(Text)
    planned_duration = db.Column(Text)
    calculated_duration = db.Column(Text)
    program_start_time = db.Column(Text)
    reporter = db.Column(Text)
    guest = db.Column(Text)
    contact = db.Column(Text)
    contact_phone = db.Column(Text)
    edi = db.Column(Text)
    lin = db.Column(Text)
    observations = db.Column(Text)
    item_code = db.Column(Text)
    
    # Program information extracted from filename
    program_name = db.Column(Text)
    program_date = db.Column(Text)
    
    # File information
    source_file = db.Column(Text)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<XMLData {self.id}: {self.title}>'
