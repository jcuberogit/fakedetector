"""
File Modifier
Modifica archivos existentes automáticamente según instrucciones
"""

import re
import ast
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class FileModifier:
    """Modifica archivos existentes automáticamente"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
    
    def modify_file(self, file_path: Path, modifications: List[Dict]) -> bool:
        """Aplicar modificaciones a un archivo"""
        try:
            if not file_path.exists():
                logger.warning(f"⚠️ Archivo no existe: {file_path}")
                return False
            
            # Leer archivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Aplicar modificaciones
            for mod in modifications:
                content = self.apply_modification(content, mod)
            
            # Escribir archivo modificado
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✅ Archivo modificado: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error modificando archivo: {e}")
            return False
    
    def apply_modification(self, content: str, modification: Dict) -> str:
        """Aplicar una modificación específica"""
        mod_type = modification.get('type')
        
        if mod_type == 'replace':
            return self.replace_text(content, modification)
        elif mod_type == 'insert':
            return self.insert_text(content, modification)
        elif mod_type == 'append':
            return self.append_text(content, modification)
        elif mod_type == 'add_import':
            return self.add_import(content, modification)
        elif mod_type == 'add_method':
            return self.add_method(content, modification)
        else:
            logger.warning(f"⚠️ Tipo de modificación desconocido: {mod_type}")
            return content
    
    def replace_text(self, content: str, modification: Dict) -> str:
        """Reemplazar texto en archivo"""
        old_text = modification.get('old_text')
        new_text = modification.get('new_text')
        
        if old_text and new_text:
            if old_text in content:
                content = content.replace(old_text, new_text)
                logger.info("✅ Texto reemplazado")
            else:
                logger.warning(f"⚠️ Texto no encontrado para reemplazar: {old_text[:50]}...")
        
        return content
    
    def insert_text(self, content: str, modification: Dict) -> str:
        """Insertar texto en posición específica"""
        marker = modification.get('marker')
        new_text = modification.get('new_text')
        position = modification.get('position', 'after')  # 'before' or 'after'
        
        if marker and new_text:
            if marker in content:
                if position == 'after':
                    content = content.replace(marker, marker + '\n' + new_text)
                else:
                    content = content.replace(marker, new_text + '\n' + marker)
                logger.info("✅ Texto insertado")
            else:
                logger.warning(f"⚠️ Marcador no encontrado: {marker[:50]}...")
        
        return content
    
    def append_text(self, content: str, modification: Dict) -> str:
        """Agregar texto al final del archivo"""
        new_text = modification.get('new_text')
        
        if new_text:
            content += '\n' + new_text
            logger.info("✅ Texto agregado al final")
        
        return content
    
    def add_import(self, content: str, modification: Dict) -> str:
        """Agregar import al inicio del archivo"""
        import_line = modification.get('import_line')
        
        if import_line:
            # Buscar última línea de imports
            lines = content.split('\n')
            last_import_idx = 0
            
            for i, line in enumerate(lines):
                if re.match(r'^(import|from)\s+', line):
                    last_import_idx = i
            
            # Insertar después del último import
            if import_line not in content:
                lines.insert(last_import_idx + 1, import_line)
                content = '\n'.join(lines)
                logger.info(f"✅ Import agregado: {import_line}")
            else:
                logger.info(f"ℹ️ Import ya existe: {import_line}")
        
        return content
    
    def add_method(self, content: str, modification: Dict) -> str:
        """Agregar método a una clase"""
        class_name = modification.get('class_name')
        method_code = modification.get('method_code')
        position = modification.get('position', 'end')  # 'beginning' or 'end'
        
        if class_name and method_code:
            # Buscar clase
            class_pattern = rf'class\s+{class_name}.*?:'
            match = re.search(class_pattern, content, re.MULTILINE)
            
            if match:
                # Encontrar inicio de la clase
                class_start = match.end()
                
                # Encontrar métodos existentes o __init__
                if position == 'end':
                    # Buscar último método antes del siguiente class o al final
                    next_class = re.search(r'\nclass\s+', content[class_start:])
                    if next_class:
                        insert_pos = class_start + next_class.start()
                    else:
                        insert_pos = len(content)
                else:
                    # Insertar después de __init__
                    init_match = re.search(r'def\s+__init__.*?\n(.*?)(?=\n    def|\nclass|\Z)', 
                                         content[class_start:], re.DOTALL)
                    if init_match:
                        insert_pos = class_start + init_match.end()
                    else:
                        insert_pos = class_start
                
                # Insertar método
                indent = '    '  # 4 espacios
                method_with_indent = '\n'.join(indent + line if line else '' 
                                             for line in method_code.split('\n'))
                content = content[:insert_pos] + '\n' + method_with_indent + '\n' + content[insert_pos:]
                logger.info(f"✅ Método agregado a clase {class_name}")
            else:
                logger.warning(f"⚠️ Clase no encontrada: {class_name}")
        
        return content
    
    def find_and_replace_in_file(self, file_path: Path, old_text: str, new_text: str) -> bool:
        """Buscar y reemplazar texto en archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if old_text in content:
                content = content.replace(old_text, new_text)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"✅ Texto reemplazado en {file_path}")
                return True
            else:
                logger.warning(f"⚠️ Texto no encontrado en {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error en find_and_replace: {e}")
            return False

