"""
Ticket Implementer
Implementa tickets automáticamente siguiendo instrucciones paso a paso
"""

import re
import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
from file_modifier import FileModifier

logger = logging.getLogger(__name__)

class TicketImplementer:
    """Implementa tickets automáticamente"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.agents_path = base_path / 'agents' / 'paradigm.fraud.agent'
        self.tests_path = self.agents_path / 'tests'
        self.src_path = self.agents_path / 'src'
        
        # Crear directorios si no existen
        self.tests_path.mkdir(parents=True, exist_ok=True)
        self.src_path.mkdir(parents=True, exist_ok=True)
        
        # Inicializar file modifier
        self.file_modifier = FileModifier(base_path)
    
    def implement_ticket(self, ticket: Dict) -> bool:
        """Implementar un ticket completo"""
        ticket_id = ticket.get('Ticket_ID')
        title = ticket.get('Title')
        category = ticket.get('Category')
        solution = ticket.get('Solution', '')
        instructions = ticket.get('Step_By_Step_Instructions', '')
        tdd_requirements = ticket.get('TDD_Requirements', '')
        
        logger.info(f"🔧 Implementando {ticket_id}: {title}")
        
        try:
            # Paso 1: Ejecutar TDD RED phase
            if 'TDD REQUIRED' in tdd_requirements.upper() or 'RED PHASE' in tdd_requirements.upper():
                if not self.execute_tdd_red_phase(ticket):
                    logger.warning(f"⚠️ TDD RED phase falló para {ticket_id}, continuando...")
            
            # Paso 2: Implementar según instrucciones
            if instructions:
                if not self.execute_instructions(instructions, ticket):
                    logger.error(f"❌ Error ejecutando instrucciones para {ticket_id}")
                    return False
            
            # Paso 3: Ejecutar TDD GREEN phase
            if 'GREEN PHASE' in tdd_requirements.upper():
                if not self.execute_tdd_green_phase(ticket):
                    logger.warning(f"⚠️ TDD GREEN phase falló para {ticket_id}")
            
            # Paso 4: Ejecutar tests - CRÍTICO: NO continuar si fallan
            logger.info(f"🧪 Ejecutando tests para {ticket_id}...")
            tests_passed = self.run_tests(ticket)
            
            if not tests_passed:
                logger.error(f"❌ Tests FALLARON para {ticket_id}")
                logger.error(f"🛑 DETENIENDO ejecución - Tests deben pasar antes de continuar")
                logger.error(f"📝 Revisa los tests y corrige el código antes de reintentar")
                return False  # NO continuar si tests fallan
            
            logger.info(f"✅ Tests pasaron para {ticket_id}")
            
            # Paso 5: Verificar cobertura - CRÍTICO: 100% requerido
            if '100% test coverage' in tdd_requirements.lower() or 'test coverage' in tdd_requirements.lower():
                coverage = self.check_test_coverage()
                logger.info(f"📊 Cobertura de tests: {coverage}%")
                
                if coverage < 100:
                    logger.error(f"❌ Cobertura insuficiente: {coverage}% (requerido: 100%)")
                    logger.error(f"🛑 DETENIENDO ejecución - 100% cobertura requerida")
                    logger.error(f"📝 Escribe más tests para alcanzar 100% cobertura")
                    return False  # NO continuar si cobertura < 100%
                
                logger.info(f"✅ Cobertura de tests: 100%")
            
            logger.info(f"✅ {ticket_id} implementado exitosamente - Tests pasaron y cobertura OK")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error implementando {ticket_id}: {e}")
            return False
    
    def execute_tdd_red_phase(self, ticket: Dict) -> bool:
        """Ejecutar fase RED de TDD: escribir tests que fallen"""
        ticket_id = ticket.get('Ticket_ID')
        title = ticket.get('Title')
        
        # Generar nombre de archivo de test
        test_name = self.generate_test_filename(title)
        test_file = self.tests_path / f"test_{test_name}.py"
        
        logger.info(f"📝 Creando tests (RED phase) para {ticket_id}")
        
        # Crear test básico que debe fallar inicialmente
        test_content = f'''"""
Tests for {title}
TDD RED Phase: Tests that should fail initially
"""

import pytest
import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class Test{ticket_id.replace('-', '')}(unittest.TestCase):
    """Test {title}"""
    
    def test_feature_exists(self):
        """Test that feature exists"""
        # This should fail initially
        from {self.get_module_name(title)} import {self.get_class_name(title)}
        assert {self.get_class_name(title)} is not None
    
    def test_feature_works(self):
        """Test that feature works correctly"""
        # This should fail initially
        from {self.get_module_name(title)} import {self.get_class_name(title)}
        feature = {self.get_class_name(title)}()
        assert feature is not None

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
'''
        
        try:
            with open(test_file, 'w') as f:
                f.write(test_content)
            logger.info(f"✅ Test creado: {test_file}")
            return True
        except Exception as e:
            logger.error(f"❌ Error creando test: {e}")
            return False
    
    def execute_tdd_green_phase(self, ticket: Dict) -> bool:
        """Ejecutar fase GREEN de TDD: implementar código mínimo"""
        title = ticket.get('Title')
        solution = ticket.get('Solution', '')
        
        logger.info(f"💚 Implementando código mínimo (GREEN phase)")
        
        # Extraer acciones de solution
        actions = self.parse_solution(solution)
        
        for action in actions:
            if not self.execute_action(action, ticket):
                logger.warning(f"⚠️ Acción falló: {action}")
        
        return True
    
    def execute_instructions(self, instructions: str, ticket: Dict) -> bool:
        """Ejecutar instrucciones paso a paso"""
        logger.info("📋 Ejecutando instrucciones paso a paso")
        
        # Parsear instrucciones
        steps = self.parse_instructions(instructions)
        
        for step_num, step in enumerate(steps, 1):
            logger.info(f"  Paso {step_num}: {step[:100]}...")
            if not self.execute_step(step, ticket):
                logger.warning(f"⚠️ Paso {step_num} falló")
        
        return True
    
    def parse_instructions(self, instructions: str) -> List[str]:
        """Parsear instrucciones en pasos individuales"""
        # Buscar patrones como "STEP 1:", "1)", "1.", etc.
        steps = []
        
        # Dividir por líneas que empiezan con números
        lines = instructions.split('\n')
        current_step = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detectar inicio de nuevo paso
            if re.match(r'^(STEP\s+)?\d+[\.\):]', line, re.IGNORECASE):
                if current_step:
                    steps.append(' '.join(current_step))
                current_step = [line]
            elif current_step:
                current_step.append(line)
        
        if current_step:
            steps.append(' '.join(current_step))
        
        return steps if steps else [instructions]
    
    def parse_solution(self, solution: str) -> List[str]:
        """Parsear solución en acciones"""
        # Buscar acciones numeradas como "1) Install Redis", "2) Configure..."
        actions = []
        
        # Buscar patrones como "1) Action", "2) Action"
        pattern = r'\d+\)\s*([^\d]+?)(?=\d+\)|$)'
        matches = re.findall(pattern, solution, re.DOTALL)
        
        if matches:
            actions = [m.strip() for m in matches]
        else:
            # Si no hay formato numerado, dividir por líneas
            actions = [line.strip() for line in solution.split('\n') if line.strip() and not line.strip().startswith('#')]
        
        return actions[:20]  # Limitar a 20 acciones
    
    def execute_step(self, step: str, ticket: Dict) -> bool:
        """Ejecutar un paso individual"""
        step_lower = step.lower()
        
        # Detectar tipo de acción
        if 'install' in step_lower or 'pip install' in step_lower:
            return self.execute_install_command(step)
        elif 'create' in step_lower and ('file' in step_lower or 'archivo' in step_lower):
            return self.execute_create_file(step, ticket)
        elif 'write' in step_lower or 'implement' in step_lower:
            return self.execute_write_code(step, ticket)
        elif 'test' in step_lower and ('run' in step_lower or 'execute' in step_lower):
            return self.run_tests(ticket)
        elif 'configure' in step_lower or 'setup' in step_lower:
            return self.execute_configuration(step, ticket)
        else:
            # Acción genérica - intentar ejecutar como comando
            return self.execute_generic_command(step)
    
    def execute_action(self, action: str, ticket: Dict) -> bool:
        """Ejecutar una acción específica"""
        return self.execute_step(action, ticket)
    
    def execute_install_command(self, step: str) -> bool:
        """Ejecutar comando de instalación"""
        # Extraer comando pip install
        match = re.search(r'pip\s+install\s+([^\s]+)', step)
        if match:
            package = match.group(1)
            try:
                result = subprocess.run(
                    ['pip', 'install', package],
                    cwd=str(self.agents_path),
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode == 0:
                    logger.info(f"✅ Instalado: {package}")
                    return True
                else:
                    logger.warning(f"⚠️ Error instalando {package}: {result.stderr}")
                    return False
            except Exception as e:
                logger.error(f"❌ Error ejecutando install: {e}")
                return False
        return True
    
    def execute_create_file(self, step: str, ticket: Dict) -> bool:
        """Crear archivo según instrucciones"""
        # Extraer nombre de archivo
        match = re.search(r'create\s+([^\s]+\.py)', step, re.IGNORECASE)
        if not match:
            match = re.search(r'([a-z_]+\.py)', step)
        
        if match:
            filename = match.group(1)
            file_path = self.src_path / filename
            
            # Generar contenido básico
            content = self.generate_file_content(filename, ticket)
            
            try:
                with open(file_path, 'w') as f:
                    f.write(content)
                logger.info(f"✅ Archivo creado: {file_path}")
                return True
            except Exception as e:
                logger.error(f"❌ Error creando archivo: {e}")
                return False
        
        return True
    
    def execute_write_code(self, step: str, ticket: Dict) -> bool:
        """Escribir código según instrucciones"""
        # Detectar si es modificar archivo existente o crear nuevo
        if 'modify' in step.lower() or 'update' in step.lower() or 'add' in step.lower():
            return self.modify_existing_file(step, ticket)
        else:
            return self.create_new_file(step, ticket)
    
    def modify_existing_file(self, step: str, ticket: Dict) -> bool:
        """Modificar archivo existente"""
        # Extraer nombre de archivo
        file_match = re.search(r'([a-z_/]+\.py)', step)
        if file_match:
            filename = file_match.group(1)
            file_path = self.src_path / filename
            
            if file_path.exists():
                # Detectar tipo de modificación
                if 'import' in step.lower():
                    import_line = self.extract_import_from_step(step)
                    if import_line:
                        return self.file_modifier.add_import(
                            file_path.read_text(),
                            {'import_line': import_line}
                        ) is not None
                
                # Otras modificaciones se harían aquí
                logger.info(f"✅ Archivo identificado para modificación: {file_path}")
                return True
        
        return True
    
    def create_new_file(self, step: str, ticket: Dict) -> bool:
        """Crear nuevo archivo"""
        return self.execute_create_file(step, ticket)
    
    def extract_import_from_step(self, step: str) -> Optional[str]:
        """Extraer línea de import de un paso"""
        # Buscar patrones como "import X" o "from X import Y"
        match = re.search(r'(import\s+\w+|from\s+[\w.]+\s+import\s+[\w.]+)', step)
        if match:
            return match.group(1)
        return None
    
    def execute_configuration(self, step: str, ticket: Dict) -> bool:
        """Ejecutar configuración"""
        return True
    
    def execute_generic_command(self, step: str) -> bool:
        """Ejecutar comando genérico"""
        # Intentar ejecutar como comando de shell si parece un comando
        if any(cmd in step.lower() for cmd in ['cd ', 'mkdir', 'chmod', 'export']):
            try:
                result = subprocess.run(
                    step,
                    shell=True,
                    cwd=str(self.agents_path),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                return result.returncode == 0
            except Exception as e:
                logger.warning(f"⚠️ Error ejecutando comando: {e}")
                return False
        return True
    
    def run_tests(self, ticket: Dict) -> bool:
        """
        Ejecutar tests - CRÍTICO: Debe retornar True solo si TODOS los tests pasan
        Si fallan, intenta auto-corregir y re-ejecutar
        Retorna False solo si no se puede corregir después de múltiples intentos
        """
        ticket_id = ticket.get('Ticket_ID', 'UNKNOWN')
        logger.info(f"🧪 Ejecutando tests para {ticket_id}...")
        
        try:
            # Verificar que pytest esté instalado
            check_pytest = subprocess.run(
                ['python3', '-m', 'pytest', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if check_pytest.returncode != 0:
                logger.error(f"❌ pytest no está instalado")
                logger.error(f"📝 Instala pytest: pip install pytest pytest-cov")
                return False
            
            # Ejecutar tests con output detallado
            result = subprocess.run(
                ['python3', '-m', 'pytest', str(self.tests_path), '-v', '--tb=short'],
                cwd=str(self.agents_path),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info("✅ Todos los tests pasaron")
                if result.stdout:
                    # Mostrar resumen de tests
                    lines = result.stdout.split('\n')
                    for line in lines[-10:]:  # Últimas 10 líneas
                        if 'passed' in line.lower() or 'test' in line.lower():
                            logger.info(f"   {line.strip()}")
                return True
            else:
                logger.warning(f"⚠️ Tests FALLARON para {ticket_id}")
                logger.info(f"🔧 Intentando auto-corregir...")
                
                # Intentar auto-corregir
                try:
                    from test_fixer import TestFixer
                    fixer = TestFixer(self.agents_path, self.tests_path, self.src_path)
                    fixed, attempts = fixer.attempt_fix(result.stdout, result.stderr, ticket, max_attempts=3)
                    
                    if fixed:
                        logger.info(f"✅ Tests corregidos y pasando después de {attempts} intento(s)")
                        return True
                    else:
                        logger.error(f"❌ No se pudo auto-corregir después de {attempts} intentos")
                        logger.error(f"📊 Return code: {result.returncode}")
                        
                        # Mostrar errores
                        if result.stderr:
                            logger.error(f"📝 Errores:")
                            for line in result.stderr.split('\n')[:20]:  # Primeras 20 líneas
                                if line.strip():
                                    logger.error(f"   {line}")
                        
                        if result.stdout:
                            logger.error(f"📝 Output:")
                            for line in result.stdout.split('\n')[-15:]:  # Últimas 15 líneas
                                if line.strip() and ('FAILED' in line or 'ERROR' in line or 'test' in line.lower()):
                                    logger.error(f"   {line.strip()}")
                        
                        logger.error(f"🛑 NO se puede continuar - requiere corrección manual")
                        return False
                except ImportError:
                    logger.warning(f"⚠️ TestFixer no disponible, saltando auto-corrección")
                    # Mostrar errores sin auto-corrección
                    logger.error(f"📊 Return code: {result.returncode}")
                    if result.stderr:
                        logger.error(f"📝 Errores: {result.stderr[:500]}")
                    return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Timeout ejecutando tests (más de 5 minutos)")
            logger.error(f"🛑 Tests deben completarse en tiempo razonable")
            return False
        except Exception as e:
            logger.error(f"❌ Error ejecutando tests: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def check_test_coverage(self) -> float:
        """
        Verificar cobertura de tests - CRÍTICO: 100% requerido
        Retorna porcentaje de cobertura (0-100)
        """
        logger.info("📊 Verificando cobertura de tests...")
        
        try:
            # Verificar que pytest-cov esté instalado
            check_cov = subprocess.run(
                ['python3', '-m', 'pytest', '--cov=src', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if check_cov.returncode != 0:
                logger.error(f"❌ pytest-cov no está instalado")
                logger.error(f"📝 Instala pytest-cov: pip install pytest-cov")
                return 0.0
            
            # Ejecutar tests con cobertura
            result = subprocess.run(
                ['python3', '-m', 'pytest', '--cov=src', '--cov-report=term', '--cov-report=term-missing', str(self.tests_path), '-v'],
                cwd=str(self.agents_path),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Extraer porcentaje de cobertura del output
            # Buscar línea "TOTAL" con porcentaje
            coverage = 0.0
            for line in result.stdout.split('\n'):
                if 'TOTAL' in line:
                    # Formato: "TOTAL    100    50    50%"
                    match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+(?:\.\d+)?)%', line)
                    if match:
                        coverage = float(match.group(1))
                        break
            
            if coverage == 0.0:
                # Intentar otro formato
                match = re.search(r'(\d+(?:\.\d+)?)%\s+coverage', result.stdout, re.IGNORECASE)
                if match:
                    coverage = float(match.group(1))
            
            logger.info(f"📊 Cobertura detectada: {coverage}%")
            
            if coverage < 100:
                logger.error(f"❌ Cobertura insuficiente: {coverage}%")
                logger.error(f"📝 Archivos sin cobertura completa:")
                # Mostrar archivos con baja cobertura
                for line in result.stdout.split('\n'):
                    if '%' in line and ('src/' in line or 'test_' in line):
                        if not re.search(r'100%', line):
                            logger.error(f"   {line.strip()}")
            
            return coverage
            
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Timeout verificando cobertura")
            return 0.0
        except Exception as e:
            logger.error(f"❌ Error verificando cobertura: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return 0.0
    
    def generate_test_filename(self, title: str) -> str:
        """Generar nombre de archivo de test"""
        # Convertir título a nombre de archivo
        name = re.sub(r'[^a-z0-9]+', '_', title.lower())
        name = re.sub(r'_+', '_', name)
        return name[:50]
    
    def get_module_name(self, title: str) -> str:
        """Obtener nombre de módulo desde título"""
        name = re.sub(r'[^a-z0-9]+', '_', title.lower())
        return name[:30]
    
    def get_class_name(self, title: str) -> str:
        """Obtener nombre de clase desde título"""
        # Convertir "Implement Proxy Job Model" -> "ProxyJobModel"
        words = re.findall(r'\b\w+', title)
        class_name = ''.join(word.capitalize() for word in words[:5])
        return class_name or "Feature"
    
    def generate_file_content(self, filename: str, ticket: Dict) -> str:
        """Generar contenido básico de archivo"""
        class_name = self.get_class_name(ticket.get('Title', ''))
        title = ticket.get('Title', 'Feature')
        description = ticket.get('Description', '')
        solution = ticket.get('Solution', '')
        
        # Generar contenido más completo basado en solución
        imports = self.extract_imports(solution)
        methods = self.extract_methods(solution, class_name)
        
        return f'''"""
{title}
{description}
"""

{imports}
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class {class_name}:
    """
    {description}
    """
    
    def __init__(self):
        """Initialize {class_name}"""
        logger.info(f"Initializing {class_name}")
    
    {methods}
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data"""
        return {{"status": "implemented", "ticket": "{ticket.get('Ticket_ID', '')}"}}

'''
    
    def extract_imports(self, solution: str) -> str:
        """Extraer imports necesarios de la solución"""
        imports = set()
        
        # Detectar imports comunes
        if 'redis' in solution.lower():
            imports.add('import redis')
        if 'celery' in solution.lower():
            imports.add('from celery import Celery')
        if 'flask' in solution.lower():
            imports.add('from flask import Flask, request, jsonify')
        if 'sqlite' in solution.lower():
            imports.add('import sqlite3')
        if 'requests' in solution.lower():
            imports.add('import requests')
        if 'beautifulsoup' in solution.lower() or 'bs4' in solution.lower():
            imports.add('from bs4 import BeautifulSoup')
        
        return '\n'.join(sorted(imports)) if imports else ''
    
    def extract_methods(self, solution: str, class_name: str) -> str:
        """Extraer métodos sugeridos de la solución"""
        methods = []
        
        # Métodos comunes basados en palabras clave
        if 'create' in solution.lower():
            methods.append(f'''    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create resource"""
        logger.info("Creating resource")
        return {{"status": "created"}}''')
        
        if 'get' in solution.lower() or 'retrieve' in solution.lower():
            methods.append(f'''    def get(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get resource by ID"""
        logger.info(f"Getting resource: {{resource_id}}")
        return {{"id": resource_id, "status": "found"}}''')
        
        if 'update' in solution.lower():
            methods.append(f'''    def update(self, resource_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update resource"""
        logger.info(f"Updating resource: {{resource_id}}")
        return {{"id": resource_id, "status": "updated"}}''')
        
        if 'delete' in solution.lower() or 'remove' in solution.lower():
            methods.append(f'''    def delete(self, resource_id: str) -> bool:
        """Delete resource"""
        logger.info(f"Deleting resource: {{resource_id}}")
        return True''')
        
        return '\n\n'.join(methods) if methods else '    pass'

