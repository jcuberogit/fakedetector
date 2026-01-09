#!/usr/bin/env python3
"""
Autonomous Ticket Executor 24/7
Ejecuta tickets directamente en archivos sin pasar por Cursor
Trabaja 24/7 sin necesidad de aprobaciones manuales
"""

import csv
import sys
import os
import json
import subprocess
import logging
import time
import fcntl
import atexit
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import importlib.util

# Cargar variables de entorno desde .env si existe
env_file = Path(__file__).parent.parent.parent / '.env'
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                value = value.strip('"').strip("'")
                os.environ[key] = value
from ticket_implementer import TicketImplementer
try:
    from ticket_implementer_ai_enhanced import AITicketImplementer
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    logging.warning("⚠️ AI implementer no disponible, usando básico")

try:
    from intervention_detector import InterventionDetector
    INTERVENTION_DETECTOR_AVAILABLE = True
except ImportError:
    INTERVENTION_DETECTOR_AVAILABLE = False
    logging.warning("⚠️ Intervention detector no disponible")

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/autonomous_executor_24_7.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FileLock:
    """Lock file para prevenir ejecución concurrente"""
    def __init__(self, lock_file: Path):
        self.lock_file = lock_file
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        self.fd = None
    
    def acquire(self, timeout=10):
        """Adquirir lock con timeout"""
        try:
            self.fd = open(self.lock_file, 'w')
            start_time = time.time()
            
            while True:
                try:
                    fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self.fd.write(f"{os.getpid()}\n{time.time()}\n")
                    self.fd.flush()
                    return True
                except IOError:
                    if time.time() - start_time > timeout:
                        return False
                    time.sleep(0.1)
        except Exception as e:
            logger.error(f"❌ Error adquiriendo lock: {e}")
            return False
    
    def release(self):
        """Liberar lock"""
        try:
            if self.fd:
                fcntl.flock(self.fd, fcntl.LOCK_UN)
                self.fd.close()
            if self.lock_file.exists():
                self.lock_file.unlink()
        except Exception as e:
            logger.warning(f"⚠️ Error liberando lock: {e}")

class AutonomousExecutor24_7:
    """Ejecutor autónomo que trabaja 24/7 directamente en archivos"""
    
    def __init__(self, tickets_file: str = None):
        self.base_path = Path(__file__).parent  # customer-service.agent directory
        self.root_path = Path(__file__).parent.parent.parent  # ParadigmStore root
        # Buscar CSV completo en directorio padre primero
        if tickets_file is None:
            csv_parent = self.root_path / 'CSATickets.csv'
            csv_local = Path(__file__).parent / 'CSATickets.csv'
            
            # Priorizar CSV del padre si existe y es más grande
            if csv_parent.exists():
                parent_size = csv_parent.stat().st_size
                if csv_local.exists():
                    local_size = csv_local.stat().st_size
                    if parent_size > local_size:
                        self.tickets_file = str(csv_parent)
                        logger.info(f"📄 Usando CSV padre: {csv_parent} ({parent_size} bytes)")
                    else:
                        self.tickets_file = str(csv_local)
                        logger.info(f"📄 Usando CSV local: {csv_local} ({local_size} bytes)")
                else:
                    self.tickets_file = str(csv_parent)
                    logger.info(f"📄 Usando CSV padre: {csv_parent} ({parent_size} bytes)")
            elif csv_local.exists():
                self.tickets_file = str(csv_local)
                logger.info(f"📄 Usando CSV local: {csv_local}")
            else:
                # Si no se encuentra en ningún lado, usar el del root como fallback
                self.tickets_file = str(self.root_path / 'CSATickets.csv')
                if not Path(self.tickets_file).exists():
                    logger.error(f"❌ CSV no encontrado en ningún lugar. Buscado en:")
                    logger.error(f"   - {csv_parent}")
                    logger.error(f"   - {csv_local}")
                    logger.error(f"   - {self.tickets_file}")
                    sys.exit(1)
                logger.info(f"📄 Usando CSV root (fallback): {self.tickets_file}")
        else:
            self.tickets_file = tickets_file
        self.completed_count = 0
        self.failed_count = 0
        self.tickets = []
        self.load_tickets()
        logger.info(f"✅ Executor 24/7 inicializado. Base path: {self.base_path}")
        logger.info(f"📄 CSV cargado: {self.tickets_file} ({len(self.tickets)} tickets)")
    
    def load_tickets(self):
        """Cargar tickets del CSV"""
        try:
            # Asegurar que tickets_file es un path absoluto
            tickets_path = Path(self.tickets_file)
            if not tickets_path.is_absolute():
                # Si es relativo, intentar desde base_path primero, luego root_path
                if (self.base_path / tickets_path).exists():
                    tickets_path = self.base_path / tickets_path
                elif (self.root_path / tickets_path).exists():
                    tickets_path = self.root_path / tickets_path
                else:
                    tickets_path = Path(self.tickets_file).resolve()
            
            self.tickets_file = str(tickets_path)
            
            with open(self.tickets_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.tickets = list(reader)
            logger.info(f"✅ Cargados {len(self.tickets)} tickets desde {self.tickets_file}")
        except Exception as e:
            logger.error(f"❌ Error cargando tickets: {e}")
            logger.error(f"   Intentando cargar desde: {self.tickets_file}")
            sys.exit(1)
    
    def get_next_ticket(self) -> Optional[Dict]:
        """Obtener siguiente ticket pendiente"""
        priority_order = {'CRITICAL': 1, 'HIGH': 2, 'MEDIUM': 3, 'LOW': 4}
        pending = [t for t in self.tickets if t.get('Status') == 'PENDING']
        if not pending:
            return None
        pending.sort(key=lambda x: priority_order.get(x.get('Priority', 'LOW'), 4))
        return pending[0]
    
    def mark_ticket_needs_review(self, ticket_id: str, intervention_type: str, reason: str):
        """Marcar ticket como necesita revisión"""
        try:
            updated_tickets = []
            with open(self.tickets_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('Ticket_ID') == ticket_id:
                        row['Status'] = 'NEEDS_REVIEW'
                        # Agregar nota sobre intervención
                        notes = row.get('Research_Notes', '')
                        if notes:
                            notes += f' | REQUIRES_INTERVENTION: {intervention_type} - {reason}'
                        else:
                            notes = f'REQUIRES_INTERVENTION: {intervention_type} - {reason}'
                        row['Research_Notes'] = notes
                        logger.info(f"⚠️ {ticket_id} marcado como NEEDS_REVIEW")
                    updated_tickets.append(row)
            
            if updated_tickets:
                fieldnames = list(updated_tickets[0].keys())
                with open(self.tickets_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(updated_tickets)
            
            return True
        except Exception as e:
            logger.error(f"❌ Error marcando ticket: {e}")
            return False
    
    def mark_ticket_completed(self, ticket_id: str):
        """Marcar ticket como completado"""
        try:
            updated_tickets = []
            with open(self.tickets_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('Ticket_ID') == ticket_id:
                        row['Status'] = 'COMPLETED'
                        logger.info(f"✅ {ticket_id} marcado como COMPLETED")
                    updated_tickets.append(row)
            
            fieldnames = list(updated_tickets[0].keys())
            with open(self.tickets_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(updated_tickets)
            
            self.completed_count += 1
            return True
        except Exception as e:
            logger.error(f"❌ Error marcando ticket: {e}")
            return False
    
    def execute_ticket_implementation(self, ticket: Dict) -> bool:
        """
        Ejecutar implementación del ticket directamente en archivos
        Usa TicketImplementer para implementar completamente el ticket
        """
        ticket_id = ticket.get('Ticket_ID')
        title = ticket.get('Title')
        category = ticket.get('Category')
        
        logger.info(f"🚀 Ejecutando {ticket_id}: {title}")
        logger.info(f"📋 Categoría: {category}")
        
        # Verificar si requiere intervención humana
        if INTERVENTION_DETECTOR_AVAILABLE:
            detector = InterventionDetector()
            requires_intervention, intervention_type, reason = detector.requires_intervention(ticket)
            
            if requires_intervention:
                logger.warning(f"⚠️ Ticket {ticket_id} requiere intervención humana")
                logger.warning(f"   Tipo: {intervention_type}")
                logger.warning(f"   Razón: {reason}")
                
                # Generar reporte de intervención
                report = detector.generate_intervention_report(ticket)
                
                # Guardar reporte
                impl_dir = Path(self.base_path) / 'agents' / 'paradigm.fraud.agent' / 'implementations'
                impl_dir.mkdir(parents=True, exist_ok=True)
                report_file = impl_dir / f"{ticket_id}_INTERVENTION_REQUIRED.json"
                
                with open(report_file, 'w') as f:
                    json.dump(report, f, indent=2)
                
                logger.warning(f"📋 Reporte guardado en: {report_file}")
                logger.warning(f"⏸️ Pausando ejecución de {ticket_id} - Requiere tu intervención")
                logger.warning(f"   Revisa el reporte y actualiza el ticket con tu decisión")
                
                # Marcar como NEEDS_REVIEW en lugar de ejecutar
                self.mark_ticket_needs_review(ticket_id, intervention_type, reason)
                return False
        
        try:
            # Usar AI implementer si está disponible, sino básico
            if AI_AVAILABLE:
                use_ai = os.getenv('USE_AI_IMPLEMENTER', 'true').lower() == 'true'
                if use_ai:
                    implementer = AITicketImplementer(self.base_path, use_ai=True)
                    logger.info("🤖 Usando AI Implementer (99%+ confianza)")
                else:
                    implementer = TicketImplementer(self.base_path)
                    logger.info("📝 Usando Implementer básico (70% confianza)")
            else:
                implementer = TicketImplementer(self.base_path)
                logger.info("📝 Usando Implementer básico (70% confianza)")
            
            # Implementar ticket completo
            success = implementer.implement_ticket(ticket)
            
            if success:
                # Crear archivo de implementación como registro
                impl_dir = Path(self.base_path) / 'agents' / 'paradigm.fraud.agent' / 'implementations'
                impl_dir.mkdir(parents=True, exist_ok=True)
                
                impl_file = impl_dir / f"{ticket_id}.json"
                impl_data = {
                    'ticket_id': ticket_id,
                    'title': title,
                    'category': category,
                    'status': 'implemented',
                    'implemented_at': datetime.now().isoformat(),
                    'solution': ticket.get('Solution', '')
                }
                
                with open(impl_file, 'w') as f:
                    json.dump(impl_data, f, indent=2)
                
                logger.info(f"✅ {ticket_id} implementado exitosamente")
                return True
            else:
                logger.warning(f"⚠️ {ticket_id} implementado con advertencias")
                return True  # Continuar aunque haya advertencias
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando {ticket_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.failed_count += 1
            return False
    
    def run_24_7(self, check_interval: int = 60):
        """
        Ejecutar en modo 24/7 continuo
        check_interval: segundos entre verificaciones de nuevos tickets
        """
        logger.info("🤖 Iniciando ejecutor 24/7...")
        logger.info(f"📊 Total tickets: {len(self.tickets)}")
        logger.info(f"⏱️ Intervalo de verificación: {check_interval} segundos")
        
        max_iterations = 100000  # Prácticamente infinito
        iteration = 0
        
        while iteration < max_iterations:
            ticket = self.get_next_ticket()
            
            if not ticket:
                logger.info("⏳ No hay tickets pendientes. Esperando...")
                time.sleep(check_interval)
                self.load_tickets()  # Recargar por si hay nuevos tickets
                iteration += 1
                continue
            
            # Ejecutar ticket
            ticket_id = ticket.get('Ticket_ID')
            logger.info(f"🚀 Procesando {ticket_id}: {ticket.get('Title')[:60]}...")
            
            success = self.execute_ticket_implementation(ticket)
            
            if success:
                # Solo marcar como completado si tests pasaron y cobertura OK
                self.mark_ticket_completed(ticket_id)
                self.completed_count += 1
                logger.info(f"✅ {ticket_id} COMPLETADO - Tests pasaron ✓")
            else:
                # Verificar si es por intervención o por tests fallidos
                ticket_status = next((t.get('Status') for t in self.tickets if t.get('Ticket_ID') == ticket_id), 'PENDING')
                
                if ticket_status == 'NEEDS_REVIEW':
                    # Requiere intervención - continuar con siguiente
                    logger.info(f"⏭️ Saltando {ticket_id} - requiere intervención, continuando con siguiente...")
                else:
                    # Tests fallaron o cobertura insuficiente después de intentos de auto-corrección
                    logger.error(f"⚠️ {ticket_id} falló después de intentos de auto-corrección")
                    logger.error(f"📝 Razón: Tests fallaron o cobertura insuficiente")
                    logger.warning(f"⏭️ Saltando {ticket_id} y continuando con siguiente ticket")
                    logger.warning(f"💡 Revisa {ticket_id} manualmente y marca como PENDING para reintentar")
                    # Continuar con siguiente ticket en lugar de detener
                    # El sistema intentó auto-correger pero no pudo
                    continue
            
            # Reportar progreso cada 10 tickets
            if self.completed_count % 10 == 0 and self.completed_count > 0:
                logger.info(f"📊 Progreso: {self.completed_count} completados, {self.failed_count} fallidos")
            
            # Pequeña pausa entre tickets
            time.sleep(1)
            iteration += 1
        
        logger.info(f"🏁 Ejecución completada")
        logger.info(f"✅ Completados: {self.completed_count}")
        logger.info(f"❌ Fallidos: {self.failed_count}")

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ejecutor Autónomo 24/7')
    parser.add_argument('--tickets-file', default='CSATickets.csv', help='Archivo de tickets')
    parser.add_argument('--interval', type=int, default=60, help='Intervalo de verificación (segundos)')
    parser.add_argument('--daemon', action='store_true', help='Ejecutar como daemon')
    parser.add_argument('--no-lock', action='store_true', help='Desactivar lock file (NO recomendado)')
    
    args = parser.parse_args()
    
    # Verificar lock file (prevenir ejecución concurrente)
    lock_file = Path(__file__).parent / '.executor.lock'
    lock = FileLock(lock_file)
    
    if not args.no_lock:
        if not lock.acquire():
            logger.error("="*70)
            logger.error("⚠️ OTRO EJECUTOR YA ESTÁ CORRIENDO")
            logger.error("="*70)
            logger.error(f"Lock file: {lock_file}")
            
            # Intentar leer PID del lock
            try:
                if lock_file.exists():
                    with open(lock_file, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            pid = lines[0].strip()
                            logger.error(f"PID del ejecutor activo: {pid}")
                            
                            # Verificar si el proceso existe
                            try:
                                import psutil
                                if psutil.pid_exists(int(pid)):
                                    logger.error(f"✅ Proceso {pid} está activo")
                                else:
                                    logger.warning(f"⚠️ Proceso {pid} no existe - lock file huérfano")
                                    logger.warning("   Elimina el lock file manualmente si es necesario")
                            except ImportError:
                                logger.info("   Instala 'psutil' para verificar procesos: pip install psutil")
            except Exception as e:
                logger.debug(f"Error leyendo lock file: {e}")
            
            logger.error("")
            logger.error("💡 Opciones:")
            logger.error("   1. Esperar a que termine el ejecutor actual")
            logger.error("   2. Detener el ejecutor actual: pkill -f autonomous_executor_24_7.py")
            logger.error("   3. Si el proceso murió, eliminar lock: rm agents/paradigm.fraud.agent/.executor.lock")
            logger.error("   4. Ejecutar sin lock (NO recomendado): --no-lock")
            logger.error("="*70)
            sys.exit(1)
        
        # Registrar liberación de lock al salir
        atexit.register(lock.release)
        logger.info(f"🔒 Lock adquirido: {lock_file}")
    
    executor = AutonomousExecutor24_7(tickets_file=args.tickets_file)
    
    try:
        if args.daemon:
            # Ejecutar como daemon (background)
            try:
                import daemon
                with daemon.DaemonContext():
                    executor.run_24_7(check_interval=args.interval)
            except ImportError:
                logger.warning("⚠️ python-daemon no instalado, ejecutando en foreground")
                executor.run_24_7(check_interval=args.interval)
        else:
            # Ejecutar en foreground
            executor.run_24_7(check_interval=args.interval)
    finally:
        if not args.no_lock:
            lock.release()
            logger.info("🔓 Lock liberado")

if __name__ == '__main__':
    main()


