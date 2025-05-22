import os
import struct
import zipfile
from typing import Union, Tuple, Optional
from xml.etree import ElementTree as ET

class FileTypeDetector:
    """
    A class to detect file types based on their magic bytes and internal structure,
    without relying on file extensions.
    """
    
    # Magic bytes signatures for various file types
    SIGNATURES = {
        # Images
        'image': {
            b'\xFF\xD8\xFF': 'jpeg',
            b'\x89PNG\r\n\x1A\n': 'png',
            b'BM': 'bmp',
            b'GIF87a': 'gif',
            b'GIF89a': 'gif',
            b'II*\x00': 'tiff',  # Little-endian TIFF
            b'MM\x00*': 'tiff',  # Big-endian TIFF
            b'\x00\x00\x01\x00': 'ico',
            b'\x00\x00\x02\x00': 'cur',
            b'\x49\x49\x2A\x00': 'tiff',  # Another TIFF variant
            b'\x4D\x4D\x00\x2A': 'tiff',  # Another TIFF variant
        },
        
        # Documents
        'word': {
            b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1': 'doc',  # DOC (OLE Compound File)
        },
        
        # PDFs
        'pdf': {
            b'%PDF-': 'pdf',
        },
        
        # Spreadsheets
        'excel': {
            b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1': 'xls',  # XLS (OLE Compound File)
        },
        
        # Presentations
        'powerpoint': {
            b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1': 'ppt',  # PPT (OLE Compound File)
        },
        
        # Compressed/Mixed files
        'mixed': {
            b'PK\x03\x04': 'zip',  # Will be further analyzed for Office documents
            b'Rar!\x1A\x07\x00': 'rar',
            b'Rar!\x1A\x07\x01\x00': 'rar',
            b'\x1F\x8B\x08': 'gzip',
            b'BZh': 'bzip2',
            b'\xFD7zXZ\x00': 'xz',
            b'7z\xBC\xAF\x27\x1C': '7z',
            b'ustar': 'tar',
        }
    }
    
    # MIME types mapping
    MIME_TYPES = {
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'bmp': 'image/bmp',
        'gif': 'image/gif',
        'tiff': 'image/tiff',
        'ico': 'image/x-icon',
        'cur': 'image/x-icon',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'doc': 'application/msword',
        'odt': 'application/vnd.oasis.opendocument.text',
        'pdf': 'application/pdf',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'xls': 'application/vnd.ms-excel',
        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'ppt': 'application/vnd.ms-powerpoint',
        'ods': 'application/vnd.oasis.opendocument.spreadsheet',
        'odp': 'application/vnd.oasis.opendocument.presentation',
        'zip': 'application/zip',
        'rar': 'application/x-rar-compressed',
        'gzip': 'application/gzip',
        'bzip2': 'application/x-bzip2',
        'xz': 'application/x-xz',
        '7z': 'application/x-7z-compressed',
        'tar': 'application/x-tar',
    }
    
    @staticmethod
    def _detect_office_open_xml(file_path: str) -> Optional[Tuple[str, str]]:
        """
        Detect the specific type of Office Open XML document (DOCX, XLSX, PPTX).
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Tuple of (category, file_type) if detected, None otherwise
        """
        try:
            with zipfile.ZipFile(file_path) as z:
                # Check for [Content_Types].xml
                if '[Content_Types].xml' not in z.namelist():
                    return None
                
                # Parse the content types file
                with z.open('[Content_Types].xml') as f:
                    content_types = f.read().decode('utf-8')
                    
                    # Check for Word document
                    if 'wordprocessingml.document' in content_types:
                        return 'word', 'docx'
                    # Check for Excel spreadsheet
                    elif 'spreadsheetml.sheet' in content_types:
                        return 'excel', 'xlsx'
                    # Check for PowerPoint presentation
                    elif 'presentationml.presentation' in content_types:
                        return 'powerpoint', 'pptx'
                    # Check for OpenDocument formats
                    elif 'opendocument.text' in content_types:
                        return 'word', 'odt'
                    elif 'opendocument.spreadsheet' in content_types:
                        return 'excel', 'ods'
                    elif 'opendocument.presentation' in content_types:
                        return 'powerpoint', 'odp'
                    
        except (zipfile.BadZipFile, KeyError, ValueError):
            return None
        
        return None
    
    @staticmethod
    def _detect_ole_compound_file(file_path: str) -> Optional[Tuple[str, str]]:
        """
        Detect the specific type of OLE Compound File (DOC, XLS, PPT).
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Tuple of (category, file_type) if detected, None otherwise
        """
        try:
            with open(file_path, 'rb') as f:
                # Read the header
                header = f.read(512)
                
                # Check for Word document
                if b'WordDocument' in header:
                    return 'word', 'doc'
                # Check for Excel spreadsheet
                elif b'Workbook' in header or b'Book' in header:
                    return 'excel', 'xls'
                # Check for PowerPoint presentation
                elif b'PowerPoint' in header:
                    return 'powerpoint', 'ppt'
                
        except Exception:
            return None
        
        return None
    
    @staticmethod
    def detect_file_type(file_path: str, return_mime: bool = False) -> Union[str, Tuple[str, str]]:
        """
        Detect the file type based on its content.
        
        Args:
            file_path: Path to the file to analyze
            return_mime: If True, returns both category and MIME type
            
        Returns:
            The detected file type category or (category, MIME type) if return_mime is True.
            Returns "unknown" if file type cannot be determined.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            # Read the first 8KB to check magic bytes (enough for most signatures)
            header = f.read(8192)
            
            # First check for ZIP-based files (Office Open XML)
            if header.startswith(b'PK\x03\x04'):
                result = FileTypeDetector._detect_office_open_xml(file_path)
                if result:
                    category, file_type = result
                    if return_mime:
                        return category, FileTypeDetector.MIME_TYPES.get(file_type, 'application/octet-stream')
                    return category
            
            # Check for OLE Compound files (older Office formats)
            if header.startswith(b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'):
                result = FileTypeDetector._detect_ole_compound_file(file_path)
                if result:
                    category, file_type = result
                    if return_mime:
                        return category, FileTypeDetector.MIME_TYPES.get(file_type, 'application/octet-stream')
                    return category
            
            # Check each category and signature
            for category, signatures in FileTypeDetector.SIGNATURES.items():
                for signature, file_type in signatures.items():
                    if header.startswith(signature):
                        # Skip ZIP and OLE signatures since we already checked them
                        if signature == b'PK\x03\x04' or signature == b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1':
                            continue
                        if return_mime:
                            return category, FileTypeDetector.MIME_TYPES.get(file_type, 'application/octet-stream')
                        return category
        
        if return_mime:
            return 'unknown', 'application/octet-stream'
        return 'unknown'
