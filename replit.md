# Overview

This is a Flask-based web application for processing and searching XML broadcast data. The application extracts broadcast rundown information from XML files and stores it in a SQLite database, providing a comprehensive Spanish-language web interface for users to search and filter the data. The system now includes advanced search capabilities with program-based filtering and day-based program navigation. It's designed to handle hundreds of XML files containing broadcast scheduling and content information.

# User Preferences

Preferred communication style: Simple, everyday language.
User interface language: Spanish (completely translated from English).

# System Architecture

## Backend Framework
The application uses Flask as the web framework with SQLAlchemy for database operations. The architecture follows a modular design with separate files for models, routes, and XML processing logic.

## Database Design
Uses SQLite as the database solution with a comprehensive `XMLData` model that captures extensive broadcast information including:
- Core identification (GUID, object ID, object type)
- Timing and scheduling data (broadcast times, duration, computed start time)
- Content metadata (title, text content, planning area)
- Program information (program name, program date extracted from filenames)
- Extended broadcast metadata (planned duration, calculated duration, reporter, guest, contact information)
- Technical fields (EDI, LIN, observations, item code)
- Language and audio track information
- System metadata (site name, version, export path)

The choice of SQLite provides simplicity for deployment and sufficient performance for the expected data volume. The database now supports over 40 fields for comprehensive broadcast data analysis.

## Data Processing Pipeline
Implements a dedicated `XMLProcessor` class that:
- Scans directories for XML files
- Extracts structured data from complex XML hierarchies
- Handles various text content formats and timing flags
- Provides robust error handling and logging

## Web Interface Architecture
The frontend uses Bootstrap with a dark theme and Feather icons for a modern interface. The application provides three main workflows:
1. XML file processing from specified directories
2. Advanced search functionality with multiple filter criteria including all broadcast metadata fields
3. Program-based navigation allowing users to browse content by specific days and program names

Key features include:
- Comprehensive search with 15+ filter fields
- Program date/name extraction from XML filenames
- Day-based program browser with story counts
- Detailed modal views for individual broadcast elements
- Responsive table design with truncated content preview

## Application Structure
- `app.py`: Application factory and configuration
- `models.py`: Database schema definition
- `routes.py`: Web request handling and business logic
- `xml_processor.py`: XML parsing and data extraction
- `templates/`: Jinja2 templates for the web interface

# External Dependencies

## Frontend Libraries
- Bootstrap CSS framework (via CDN) for responsive UI components
- Feather Icons for consistent iconography
- Custom CSS for enhanced dark theme styling

## Backend Dependencies
- Flask: Web framework for handling HTTP requests and routing
- Flask-SQLAlchemy: ORM for database operations and model definitions
- SQLAlchemy: Database abstraction layer with declarative base

## Development Tools
- Python logging module for debugging and error tracking
- XML ElementTree for parsing XML broadcast files
- OS and glob modules for file system operations