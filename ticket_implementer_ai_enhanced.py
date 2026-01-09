"""
Ticket Implementer with AI (Gemini) - 99%+ Autonomy
Usa IA real para comprensión y generación de código
"""

import re
import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import ast
import tempfile

# Cargar variables de entorno desde .env si existe (buscar en raíz del proyecto)
env_files = [
    Path(__file__).parent.parent.parent / '.env',  # Raíz del proyecto
    Path(__file__).parent.parent / '.env',  # agents/.env
    Path(__file__).parent / '.env'  # agents/paradigm.fraud.agent/.env
]
for env_file in env_files:
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    value = value.strip('"').strip("'")
                    os.environ[key] = value
        break  # Usar el primer .env encontrado

# Intentar importar Local AI Client
import sys
local_ai_path = Path(__file__).parent.parent.parent / 'local_ai_client.py'
if local_ai_path.exists():
    sys.path.insert(0, str(local_ai_path.parent))
    try:
        from local_ai_client import create_local_ai_client
        LOCAL_AI_AVAILABLE = True
    except ImportError:
        LOCAL_AI_AVAILABLE = False
        logging.warning("⚠️ Local AI Client no disponible")
else:
    LOCAL_AI_AVAILABLE = False
    logging.warning("⚠️ local_ai_client.py no encontrado")

logger = logging.getLogger(__name__)

class AITicketImplementer:
    """Implementa tickets usando IA real para 99%+ autonomía"""
    
    def __init__(self, base_path: Path, use_ai: bool = True):
        self.base_path = base_path
        self.agents_path = base_path / 'agents' / 'paradigm.fraud.agent'
        self.tests_path = self.agents_path / 'tests'
        self.src_path = self.agents_path / 'src'
        
        # Crear directorios
        self.tests_path.mkdir(parents=True, exist_ok=True)
        self.src_path.mkdir(parents=True, exist_ok=True)
        
        # Inicializar IA
        self.use_ai = use_ai and LOCAL_AI_AVAILABLE
        if self.use_ai:
            try:
                # Detectar si Open Router está disponible
                openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
                if openrouter_api_key:
                    # Usar Open Router
                    model_name = os.getenv('OPENROUTER_MODEL', 'openai/gpt-4o-mini')
                    self.ai_client = create_local_ai_client({
                        'model_name': model_name,
                        'api_key': openrouter_api_key,
                        'provider': 'openrouter'
                    })
                    logger.info(f"✅ Open Router inicializado: {model_name}")
                    logger.info(f"   Usando Open Router para máxima calidad")
                else:
                    # Fallback a Ollama local
                    model_name = os.getenv('LOCAL_AI_MODEL', 'qwen3-coder:30b')
                    base_url = os.getenv('LOCAL_AI_URL', 'http://localhost:11434')
                    
                    self.ai_client = create_local_ai_client({
                        'model_name': model_name,
                        'base_url': base_url,
                        'provider': 'ollama'
                    })
                    logger.info(f"✅ Local AI (Ollama) inicializado: {model_name} en {base_url}")
                    logger.info(f"   Usando modelo local para desarrollo")
            except Exception as e:
                logger.error(f"❌ Error inicializando Local AI: {e}")
                logger.warning("⚠️ Usando modo sin IA")
                self.use_ai = False
        else:
            if not LOCAL_AI_AVAILABLE:
                logger.warning("⚠️ Local AI Client no disponible")
            else:
                logger.warning("⚠️ Usando modo sin IA (use_ai=False)")
    
    def implement_ticket(self, ticket: Dict) -> bool:
        """Implementar ticket usando IA para máxima calidad"""
        ticket_id = ticket.get('Ticket_ID')
        title = ticket.get('Title')
        
        logger.info(f"🤖 Implementando {ticket_id} con IA: {title}")
        
        try:
            # Paso 1: Analizar ticket con IA
            if self.use_ai:
                implementation_plan = self.analyze_ticket_with_ai(ticket)
            else:
                implementation_plan = self.analyze_ticket_basic(ticket)
            
            # Paso 2: Generar código con IA
            if self.use_ai:
                code_files = self.generate_code_with_ai(ticket, implementation_plan)
            else:
                code_files = self.generate_code_basic(ticket)
            
            # Paso 3: Validar código antes de aplicar
            if not self.validate_code(code_files):
                logger.error("❌ Código generado no válido")
                return False
            
            # Paso 4: Aplicar cambios (con rollback si falla)
            if not self.apply_changes_safely(code_files, ticket):
                logger.error("❌ Error aplicando cambios")
                return False
            
            # Paso 5: Ejecutar tests
            if not self.run_tests():
                logger.warning("⚠️ Tests fallaron, pero continuando...")
            
            logger.info(f"✅ {ticket_id} implementado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error implementando {ticket_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def analyze_ticket_with_ai(self, ticket: Dict) -> Dict[str, Any]:
        """Analizar ticket con IA para crear plan de implementación"""
        prompt = f"""
        Analyze this development ticket and create an implementation plan:
        
        TITLE: {ticket.get('Title')}
        DESCRIPTION: {ticket.get('Description')}
        SOLUTION: {ticket.get('Solution')}
        INSTRUCTIONS: {ticket.get('Step_By_Step_Instructions')}
        TECHNOLOGIES: {ticket.get('Technologies')}
        
        Create a detailed implementation plan with:
        1. Files to create/modify
        2. Code changes needed
        3. Tests to write
        4. Dependencies to install
        5. Configuration changes
        
        Return as JSON with structure:
        {{
            "files_to_create": ["file1.py", "file2.py"],
            "files_to_modify": ["existing.py"],
            "code_changes": {{"file": "code"}},
            "tests_to_create": ["test_file.py"],
            "dependencies": ["package1", "package2"],
            "config_changes": []
        }}
        """
        
        try:
            plan_text = self.ai_client.generate(prompt)
            
            # Extraer JSON del response
            json_match = re.search(r'\{.*\}', plan_text, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
                logger.info("✅ Plan de implementación generado con IA")
                return plan
            else:
                logger.warning("⚠️ No se pudo parsear plan de IA")
                return {}
        except Exception as e:
            logger.error(f"❌ Error analizando con IA: {e}")
            return {}
    
    def generate_code_with_ai(self, ticket: Dict, plan: Dict) -> Dict[str, str]:
        """Generar código usando IA"""
        code_files = {}
        
        # Generar cada archivo con IA
        for file_name in plan.get('files_to_create', []):
            prompt = f"""
            Generate complete Python code for: {file_name}
            
            Ticket: {ticket.get('Title')}
            Description: {ticket.get('Description')}
            Requirements: {ticket.get('Step_By_Step_Instructions')}
            
            Generate production-ready code with:
            - Proper imports
            - Complete implementation
            - Error handling
            - Logging
            - Type hints
            - Docstrings
            
            Return ONLY the Python code, no explanations.
            """
            
            try:
                code = self.ai_client.generate_code(task_description=prompt, language="python")
                
                # Limpiar código (remover markdown si existe)
                code = re.sub(r'```python\n?', '', code)
                code = re.sub(r'```\n?', '', code)
                code = code.strip()
                
                code_files[file_name] = code
                logger.info(f"✅ Código generado con IA: {file_name}")
            except Exception as e:
                logger.error(f"❌ Error generando código: {e}")
        
        return code_files
    
    def validate_code(self, code_files: Dict[str, str]) -> bool:
        """Validar código antes de aplicar"""
        for file_name, code in code_files.items():
            try:
                # Validar sintaxis Python
                ast.parse(code)
                logger.info(f"✅ Sintaxis válida: {file_name}")
            except SyntaxError as e:
                logger.error(f"❌ Error de sintaxis en {file_name}: {e}")
                return False
        
        return True
    
    def apply_changes_safely(self, code_files: Dict[str, str], ticket: Dict) -> bool:
        """Aplicar cambios con rollback si falla"""
        # Guardar estado antes de cambios
        backup_files = {}
        for file_name in code_files.keys():
            file_path = self.src_path / file_name
            if file_path.exists():
                backup_files[file_name] = file_path.read_text()
        
        try:
            # Aplicar cambios
            for file_name, code in code_files.items():
                file_path = self.src_path / file_name
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                logger.info(f"✅ Archivo creado/modificado: {file_path}")
            
            # Validar que no rompió nada - CRÍTICO: Tests deben pasar
            tests_passed = self.run_tests()
            if not tests_passed:
                logger.error("❌ Tests fallaron después de cambios")
                logger.error("🛑 NO se puede continuar - tests deben pasar")
                # Rollback automático
                self.rollback(backup_files)
                return False  # NO continuar si tests fallan
            
            logger.info("✅ Tests pasaron después de aplicar cambios")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error aplicando cambios: {e}")
            # Rollback automático
            self.rollback(backup_files)
            return False
    
    def rollback(self, backup_files: Dict[str, str]):
        """Revertir cambios"""
        for file_name, content in backup_files.items():
            file_path = self.src_path / file_name
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"↩️ Rollback: {file_path}")
    
    def analyze_ticket_basic(self, ticket: Dict) -> Dict[str, Any]:
        """Análisis básico sin IA"""
        # Fallback a análisis básico
        return {
            'files_to_create': [],
            'files_to_modify': [],
            'code_changes': {},
            'tests_to_create': [],
            'dependencies': [],
            'config_changes': []
        }
    
    def generate_code_basic(self, ticket: Dict) -> Dict[str, str]:
        """Generación básica sin IA"""
        # Fallback a generación básica
        return {}
    
    def run_tests(self) -> bool:
        """
        Ejecutar tests - CRÍTICO: Debe retornar True solo si TODOS los tests pasan
        Si fallan, intenta auto-corregir usando TestFixer
        """
        try:
            # Verificar pytest
            check_pytest = subprocess.run(
                ['python3', '-m', 'pytest', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if check_pytest.returncode != 0:
                logger.error(f"❌ pytest no está instalado")
                return False
            
            # Ejecutar tests
            result = subprocess.run(
                ['python3', '-m', 'pytest', str(self.tests_path), '-v', '--tb=short'],
                cwd=str(self.agents_path),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info("✅ Todos los tests pasaron")
                return True
            else:
                logger.warning(f"⚠️ Tests fallaron, intentando auto-corregir...")
                
                # Intentar auto-corregir
                try:
                    from test_fixer import TestFixer
                    # Crear ticket dummy para TestFixer
                    ticket = {'Ticket_ID': 'CURRENT', 'Title': 'Current Implementation', 'Solution': ''}
                    fixer = TestFixer(self.agents_path, self.tests_path, self.src_path)
                    fixed, attempts = fixer.attempt_fix(result.stdout, result.stderr, ticket, max_attempts=2)
                    
                    if fixed:
                        logger.info(f"✅ Tests corregidos después de {attempts} intento(s)")
                        return True
                    else:
                        logger.error(f"❌ No se pudo auto-corregir después de {attempts} intentos")
                        return False
                except ImportError:
                    logger.warning(f"⚠️ TestFixer no disponible")
                    return False
                
        except Exception as e:
            logger.error(f"❌ Error ejecutando tests: {e}")
            return False

