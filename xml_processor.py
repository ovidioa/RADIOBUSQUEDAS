import os
import defusedxml.ElementTree as ET
import glob
import logging
from datetime import datetime
from app import app, db
from models import XMLData

class XMLProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_text_content(self, element):
        """Extract text content from various text fields in the XML"""
        if element is None:
            return None
        
        # Try to find text content in various sub-elements
        text_elem = element.find('.//text[@t="ws"]')
        if text_elem is not None and text_elem.text:
            return text_elem.text.strip()
        
        # Fallback to element text
        if element.text:
            return element.text.strip()
        
        return None
    
    def extract_timing_flags(self, story_content):
        """Extract timing flags from StoryContent"""
        timing_data = {}
        
        timing_flags = story_content.find('.//timingFlags[@t="lt"]')
        if timing_flags is not None:
            for flag in timing_flags.findall('TimingFlag'):
                flag_name = flag.find('flagName[@t="ws"]')
                value = flag.get('value.l')
                if flag_name is not None and flag_name.text:
                    flag_key = flag_name.text.lower().replace(' ', '_')
                    timing_data[flag_key] = value
        
        return timing_data
    
    def extract_program_info_from_filename(self, file_path):
        """Extract program name and date from filename"""
        filename = os.path.basename(file_path)
        program_info = {}
        
        # Extract program name and date from filename like "R_Radio Cadena_INFORMATIU MATI 07 H_07082025, 070000_1754557296557.xml"
        if '_' in filename:
            parts = filename.split('_')
            if len(parts) >= 3:
                # Remove "R_Radio Cadena_" prefix and ".xml" suffix
                program_part = '_'.join(parts[2:]).replace('.xml', '')
                # Remove the timestamp part at the end
                if ',' in program_part:
                    program_name = program_part.split(',')[0].strip()
                    program_info['program_name'] = program_name
                    
                    # Extract date from program name (format like "07082025")
                    import re
                    date_match = re.search(r'(\d{8})', program_name)
                    if date_match:
                        date_str = date_match.group(1)
                        # Convert to readable format: 07082025 -> 2025-08-07
                        if len(date_str) == 8:
                            day = date_str[:2]
                            month = date_str[2:4]
                            year = date_str[4:]
                            program_info['program_date'] = f"{year}-{month}-{day}"
        
        return program_info

    def process_xml_file(self, file_path):
        """Process a single XML file and extract data"""
        try:
            # Validate file path to prevent path injection
            if not os.path.isfile(file_path):
                self.logger.error(f"File does not exist or is not a file: {file_path}")
                return []
            
            # Ensure file is within allowed directory (prevent directory traversal)
            file_path = os.path.abspath(file_path)
            
            self.logger.info(f"Processing XML file: {file_path}")
            
            # Parse the XML file using defusedxml (protects against XML bombs)
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract program info from filename
            program_info = self.extract_program_info_from_filename(file_path)
            
            # Extract records from different pack types
            records = []
            
            # Process all Story elements throughout the document
            story_elements = root.findall('.//Story')
            for story_elem in story_elements:
                # titleId is an element, not an attribute
                title_id_elem = story_elem.find('titleId[@t="ws"]')
                if title_id_elem is not None and title_id_elem.text:
                    story_record = self.extract_story_data(story_elem, file_path, program_info)
                    if story_record:
                        records.append(story_record)
            
            # Process GroupPack elements
            group_packs = root.findall('.//GroupPack')
            for group_pack in group_packs:
                record = self.extract_group_pack_data(group_pack, file_path, program_info)
                if record:
                    records.append(record)
            
            # Process any StoryPack elements that might exist independently
            story_packs = root.findall('.//StoryPack')
            for story_pack in story_packs:
                record = self.extract_story_pack_data(story_pack, file_path, program_info)
                if record:
                    records.append(record)
            
            return records
            
        except ET.ParseError as e:
            self.logger.error(f"XML parsing error in {file_path}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {e}")
            return []
    
    def extract_story_data(self, story_elem, file_path, program_info):
        """Extract data from a Story element"""
        data = {}
        
        # Basic identification - titleId is an element, not an attribute
        title_id_elem = story_elem.find('titleId[@t="ws"]')
        if title_id_elem is not None and title_id_elem.text:
            data['object_id'] = title_id_elem.text.strip()
        
        data['object_type'] = 'Story'
        data['source_file'] = os.path.basename(file_path)
        
        # Program information from filename
        data.update(program_info)
        
        # Extract title from Story name
        story_name_elem = story_elem.find('name[@t="ws"]')
        if story_name_elem is not None and story_name_elem.text:
            data['title'] = story_name_elem.text.strip()
        
        # Extract duration and timing information
        data['duration'] = story_elem.get('duration.tc')
        data['computed_start_time'] = story_elem.get('startMode.l')
        
        # Extract text content from Text spots
        text_spots = story_elem.findall('.//Text')
        text_contents = []
        for text_spot in text_spots:
            text_elem = text_spot.find('text[@t="ws"]')
            if text_elem is not None and text_elem.text:
                text_contents.append(text_elem.text.strip())
        
        if text_contents:
            data['text_content'] = '\n\n'.join(text_contents)
        
        # Extract item_code - search all possible variations and locations
        item_code = None
        
        # Try multiple tag names and attributes
        search_patterns = [
            './/itemCode[@t="ws"]',
            './/item_code[@t="ws"]',
            './/ItemCode[@t="ws"]',
            './/itemCode',
            './/item_code',
            './/ItemCode',
            './/ITEMCODE'
        ]
        
        for pattern in search_patterns:
            item_code_elem = story_elem.find(pattern)
            if item_code_elem is not None and item_code_elem.text:
                item_code = item_code_elem.text.strip()
                break
        
        # If not found in elements, search in attributes and text content
        if not item_code:
            # Search for any element containing "DLT" in its text
            for elem in story_elem.iter():
                if elem.text and 'DLT' in elem.text:
                    # Extract DLT code pattern
                    import re
                    dlt_match = re.search(r'DLT\d+', elem.text)
                    if dlt_match:
                        item_code = dlt_match.group()
                        break
        
        if item_code:
            data['item_code'] = item_code
        
        return data

    def extract_story_pack_data(self, story_pack, file_path, program_info):
        """Extract data from a StoryPack element"""
        data = {}
        
        # Basic identification
        data['object_id'] = story_pack.get('id.l')
        data['object_type'] = 'StoryPack'
        data['source_file'] = os.path.basename(file_path)
        
        # Program information from filename
        data.update(program_info)
        
        # GUID
        guid_elem = story_pack.find('guid[@t="ws"]')
        if guid_elem is not None:
            data['guid'] = guid_elem.text
        
        # Try to find title in Story name first (this is where the actual title is)
        story_elem = story_pack.find('.//Story')
        if story_elem is not None:
            story_name_elem = story_elem.find('name[@t="ws"]')
            if story_name_elem is not None and story_name_elem.text:
                data['title'] = story_name_elem.text.strip()
        
        # Title information from Title element
        title_elem = story_pack.find('.//Title')
        if title_elem is not None:
            data['title_type'] = title_elem.get('type.l')
            data['duration'] = title_elem.get('duration.tc')
            data['broadcast_start_time'] = title_elem.get('startDate.td')
            data['broadcast_end_time'] = title_elem.get('endDate.td')
            data['record_date'] = title_elem.get('recordDate.td')
            data['kill_date'] = title_elem.get('killDate.td')
            
            # Fallback: Extract title text from Title element if not found in Story
            if not data.get('title'):
                title_text_elem = title_elem.find('.//text[@t="ws"]')
                if title_text_elem is not None and title_text_elem.text:
                    data['title'] = title_text_elem.text.strip()
        
        # Story content
        story_content = story_pack.find('.//StoryContent')
        if story_content is not None:
            # Extract text content
            content_elem = story_content.find('.//text[@t="ws"]')
            if content_elem is not None and content_elem.text:
                data['text_content'] = content_elem.text.strip()
            
            # Extract timing flags
            timing_data = self.extract_timing_flags(story_content)
            data.update(timing_data)
        
        # Extract item_code - search all possible variations and locations
        item_code = None
        
        # Try multiple tag names and attributes
        search_patterns = [
            './/itemCode[@t="ws"]',
            './/item_code[@t="ws"]',
            './/ItemCode[@t="ws"]',
            './/itemCode',
            './/item_code',
            './/ItemCode',
            './/ITEMCODE'
        ]
        
        for pattern in search_patterns:
            item_code_elem = story_pack.find(pattern)
            if item_code_elem is not None and item_code_elem.text:
                item_code = item_code_elem.text.strip()
                break
        
        # If not found in elements, search in attributes and text content
        if not item_code:
            # Search for any element containing "DLT" in its text
            for elem in story_pack.iter():
                if elem.text and 'DLT' in elem.text:
                    # Extract DLT code pattern
                    import re
                    dlt_match = re.search(r'DLT\d+', elem.text)
                    if dlt_match:
                        item_code = dlt_match.group()
                        break
        
        if item_code:
            data['item_code'] = item_code
        
        return data
    
    def extract_group_pack_data(self, group_pack, file_path, program_info):
        """Extract data from a GroupPack element"""
        data = {}
        
        # Basic identification
        data['object_id'] = group_pack.get('id.l')
        data['object_type'] = 'GroupPack'
        data['source_file'] = os.path.basename(file_path)
        
        # Program information from filename
        data.update(program_info)
        
        # GUID
        guid_elem = group_pack.find('guid[@t="ws"]')
        if guid_elem is not None:
            data['guid'] = guid_elem.text
        
        # Try to find title in Story name first (this is where the actual title is)
        story_elem = group_pack.find('.//Story')
        if story_elem is not None:
            story_name_elem = story_elem.find('name[@t="ws"]')
            if story_name_elem is not None and story_name_elem.text:
                data['title'] = story_name_elem.text.strip()
        
        # Title information from Title element
        title_elem = group_pack.find('.//Title')
        if title_elem is not None:
            data['title_type'] = title_elem.get('type.l')
            data['duration'] = title_elem.get('duration.tc')
            data['broadcast_start_time'] = title_elem.get('startDate.td')
            data['broadcast_end_time'] = title_elem.get('endDate.td')
            data['record_date'] = title_elem.get('recordDate.td')
            data['kill_date'] = title_elem.get('killDate.td')
            
            # Fallback: Extract title text from Title element if not found in Story
            if not data.get('title'):
                title_text_elem = title_elem.find('.//text[@t="ws"]')
                if title_text_elem is not None and title_text_elem.text:
                    data['title'] = title_text_elem.text.strip()
        
        # Story content
        story_content = group_pack.find('.//StoryContent')
        if story_content is not None:
            # Extract text content
            content_elem = story_content.find('.//text[@t="ws"]')
            if content_elem is not None and content_elem.text:
                data['text_content'] = content_elem.text.strip()
            
            # Extract timing flags
            timing_data = self.extract_timing_flags(story_content)
            data.update(timing_data)
        
        # Extract item_code - search all possible variations and locations
        item_code = None
        
        # Try multiple tag names and attributes
        search_patterns = [
            './/itemCode[@t="ws"]',
            './/item_code[@t="ws"]',
            './/ItemCode[@t="ws"]',
            './/itemCode',
            './/item_code',
            './/ItemCode',
            './/ITEMCODE'
        ]
        
        for pattern in search_patterns:
            item_code_elem = group_pack.find(pattern)
            if item_code_elem is not None and item_code_elem.text:
                item_code = item_code_elem.text.strip()
                break
        
        # If not found in elements, search in attributes and text content
        if not item_code:
            # Search for any element containing "DLT" in its text
            for elem in group_pack.iter():
                if elem.text and 'DLT' in elem.text:
                    # Extract DLT code pattern
                    import re
                    dlt_match = re.search(r'DLT\d+', elem.text)
                    if dlt_match:
                        item_code = dlt_match.group()
                        break
        
        if item_code:
            data['item_code'] = item_code
        
        return data
    
    def save_records_to_db(self, records):
        """Save extracted records to the database"""
        with app.app_context():
            try:
                for record_data in records:
                    # Create new XMLData instance
                    xml_record = XMLData(
                        guid=record_data.get('guid'),
                        object_id=record_data.get('object_id'),
                        object_type=record_data.get('object_type'),
                        timestamp=record_data.get('timestamp'),
                        broadcast_start_time=record_data.get('broadcast_start_time'),
                        broadcast_end_time=record_data.get('broadcast_end_time'),
                        duration=record_data.get('duration'),
                        title=record_data.get('title'),
                        text_content=record_data.get('text_content'),
                        text_duration=record_data.get('text_duration'),
                        text_timing=record_data.get('story_text_timing'),
                        timegap_timing=record_data.get('story_timegap_timing'),
                        clip_timing=record_data.get('story_clip_timing'),
                        title_status=record_data.get('title_status'),
                        title_type=record_data.get('title_type'),
                        site_name=record_data.get('site_name'),
                        site_version=record_data.get('site_version'),
                        export_path=record_data.get('export_path'),
                        planning_area=record_data.get('planning_area'),
                        linked_story=record_data.get('linked_story'),
                        language_cat=record_data.get('language_cat'),
                        language_vo=record_data.get('language_vo'),
                        language_esp=record_data.get('language_esp'),
                        has_audio_track=record_data.get('has_audio_track'),
                        fact_date=record_data.get('fact_date'),
                        cms_publish_date=record_data.get('cms_publish_date'),
                        la_carta_publish_date=record_data.get('la_carta_publish_date'),
                        record_date=record_data.get('record_date'),
                        start_date=record_data.get('start_date'),
                        end_date=record_data.get('end_date'),
                        kill_date=record_data.get('kill_date'),
                        comment=record_data.get('comment'),
                        locator_type=record_data.get('locator_type'),
                        locator_family=record_data.get('locator_family'),
                        # New fields
                        computed_start_time=record_data.get('computed_start_time'),
                        planned_duration=record_data.get('planned_duration'),
                        calculated_duration=record_data.get('calculated_duration'),
                        program_start_time=record_data.get('program_start_time'),
                        reporter=record_data.get('reporter'),
                        guest=record_data.get('guest'),
                        contact=record_data.get('contact'),
                        contact_phone=record_data.get('contact_phone'),
                        edi=record_data.get('edi'),
                        lin=record_data.get('lin'),
                        observations=record_data.get('observations'),
                        item_code=record_data.get('item_code'),
                        program_name=record_data.get('program_name'),
                        program_date=record_data.get('program_date'),
                        source_file=record_data.get('source_file')
                    )
                    
                    db.session.add(xml_record)
                
                db.session.commit()
                self.logger.info(f"Successfully saved {len(records)} records to database")
                
            except Exception as e:
                db.session.rollback()
                self.logger.error(f"Error saving records to database: {e}")
                raise
    
    def process_directory(self, directory_path):
        """Process all XML files in a directory"""
        # Validate and normalize directory path to prevent path injection
        directory_path = os.path.abspath(directory_path)
        
        if not os.path.exists(directory_path):
            self.logger.error(f"Directory does not exist: {directory_path}")
            return
        
        if not os.path.isdir(directory_path):
            self.logger.error(f"Path is not a directory: {directory_path}")
            return
        
        xml_files = glob.glob(os.path.join(directory_path, "*.xml"))
        
        if not xml_files:
            self.logger.warning(f"No XML files found in directory: {directory_path}")
            return
        
        self.logger.info(f"Found {len(xml_files)} XML files to process")
        
        total_records = 0
        for xml_file in xml_files:
            records = self.process_xml_file(xml_file)
            if records:
                self.save_records_to_db(records)
                total_records += len(records)
        
        self.logger.info(f"Processing complete. Total records processed: {total_records}")
