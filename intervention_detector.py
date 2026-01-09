"""
Intervention Detector
Detecta automáticamente cuándo un ticket requiere intervención humana
"""

import re
import logging
from typing import Dict, Tuple, Optional, List

logger = logging.getLogger(__name__)

class InterventionDetector:
    """Detecta si un ticket requiere intervención humana"""
    
    # Palabras clave que indican necesidad de decisión arquitectónica
    # Solo palabras que realmente requieren decisión, no implementación
    ARCHITECTURE_KEYWORDS = [
        'migrate from', 'migration from', 'choose between', 'select architecture',
        'refactor major', 'restructure system', 'redesign architecture',
        'microservices vs', 'monolith vs', 'database migration from',
        'infrastructure change', 'system redesign', 'which architecture'
    ]
    
    # Palabras clave que indican decisión de negocio
    # Solo decisiones reales, no implementación de features
    BUSINESS_DECISION_KEYWORDS = [
        'pricing model', 'choose pricing', 'select pricing',
        'business policy', 'define policy', 'set policy',
        'refund policy', 'cancellation policy', 'terms of service',
        'privacy policy', 'user policy', 'rate limit policy',
        'quota policy', 'set limits', 'define tier'
    ]
    
    # Palabras clave que indican integración compleja
    COMPLEX_INTEGRATION_KEYWORDS = [
        'legacy system', 'legacy integration', 'no documentation',
        'private api', 'internal system', 'third party',
        'external system', 'manual configuration',
        'requires access', 'needs credentials', 'needs permission'
    ]
    
    # Palabras clave que indican debugging profundo
    DEEP_DEBUGGING_KEYWORDS = [
        'production error', 'production debugging',
        'intermittent error', 'hard to reproduce',
        'performance issue', 'concurrency issue',
        'race condition', 'deadlock', 'memory leak'
    ]
    
    # Palabras clave que indican coordinación multi-sistema
    MULTI_SYSTEM_KEYWORDS = [
        'multiple systems', 'coordinate', 'coordination',
        'rollout plan', 'maintenance window',
        'downtime', 'zero downtime', 'blue green',
        'affects multiple', 'cross system'
    ]
    
    def __init__(self):
        self.detection_rules = [
            (self.ARCHITECTURE_KEYWORDS, 'ARCHITECTURE_DECISION', 
             'Requires architectural decision'),
            (self.BUSINESS_DECISION_KEYWORDS, 'BUSINESS_DECISION',
             'Requires business decision'),
            (self.COMPLEX_INTEGRATION_KEYWORDS, 'COMPLEX_INTEGRATION',
             'Requires external access/configuration'),
            (self.DEEP_DEBUGGING_KEYWORDS, 'DEEP_DEBUGGING',
             'Requires production debugging'),
            (self.MULTI_SYSTEM_KEYWORDS, 'MULTI_SYSTEM',
             'Requires coordination between systems')
        ]
    
    def requires_intervention(self, ticket: Dict) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Determina si un ticket requiere intervención humana
        
        Returns:
            (requires_intervention, intervention_type, reason)
        """
        # Combinar todo el texto del ticket
        ticket_text = ' '.join([
            ticket.get('Title', ''),
            ticket.get('Description', ''),
            ticket.get('Solution', ''),
            ticket.get('Step_By_Step_Instructions', '')
        ]).lower()
        
        # Verificar cada regla
        for keywords, intervention_type, reason in self.detection_rules:
            if any(keyword in ticket_text for keyword in keywords):
                logger.info(f"⚠️ Ticket requiere intervención: {intervention_type}")
                return True, intervention_type, reason
        
        # No requiere intervención
        return False, None, None
    
    def get_intervention_details(self, ticket: Dict, intervention_type: str) -> Dict:
        """Obtener detalles sobre qué necesita intervención"""
        details = {
            'ticket_id': ticket.get('Ticket_ID'),
            'title': ticket.get('Title'),
            'intervention_type': intervention_type,
            'can_generate_code': True,
            'waiting_for': None,
            'options': [],
            'recommendation': None
        }
        
        if intervention_type == 'ARCHITECTURE_DECISION':
            details['waiting_for'] = 'Architectural decision'
            details['options'] = self._extract_architecture_options(ticket)
            details['recommendation'] = 'Review options and choose based on scalability needs'
        
        elif intervention_type == 'BUSINESS_DECISION':
            details['waiting_for'] = 'Business decision'
            details['options'] = self._extract_business_options(ticket)
            details['recommendation'] = 'Review options and choose based on business model'
        
        elif intervention_type == 'COMPLEX_INTEGRATION':
            details['waiting_for'] = 'External access/credentials'
            details['options'] = ['Provide API access', 'Provide credentials', 'Configure manually']
            details['recommendation'] = 'System can generate integration code, but needs access'
        
        elif intervention_type == 'DEEP_DEBUGGING':
            details['waiting_for'] = 'Production logs/context'
            details['options'] = ['Provide production logs', 'Provide error context', 'Debug together']
            details['recommendation'] = 'System can generate diagnostic tools, but needs production context'
        
        elif intervention_type == 'MULTI_SYSTEM':
            details['waiting_for'] = 'Coordination approval'
            details['options'] = ['Approve rollout plan', 'Schedule maintenance window', 'Coordinate with teams']
            details['recommendation'] = 'System can generate migration code, but needs coordination approval'
        
        return details
    
    def _extract_architecture_options(self, ticket: Dict) -> List[str]:
        """Extraer opciones arquitectónicas del ticket"""
        # Buscar patrones como "Option A vs Option B"
        text = ticket.get('Solution', '') + ' ' + ticket.get('Description', '')
        options = []
        
        # Buscar opciones mencionadas
        option_patterns = [
            r'option\s+[a-z]:\s*([^\.]+)',
            r'alternative\s+\d+:\s*([^\.]+)',
            r'(?:use|choose|select)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        for pattern in option_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            options.extend(matches)
        
        if not options:
            options = ['Review ticket for architectural options']
        
        return options[:5]  # Máximo 5 opciones
    
    def _extract_business_options(self, ticket: Dict) -> List[str]:
        """Extraer opciones de negocio del ticket"""
        # Similar a architecture options pero para decisiones de negocio
        text = ticket.get('Solution', '') + ' ' + ticket.get('Description', '')
        options = []
        
        # Buscar modelos de precios, políticas, etc.
        if 'pricing' in text.lower():
            options = ['Free tier', 'Pay per use', 'Subscription', 'Freemium']
        elif 'policy' in text.lower():
            options = ['Strict policy', 'Moderate policy', 'Flexible policy']
        else:
            options = ['Review ticket for business options']
        
        return options
    
    def generate_intervention_report(self, ticket: Dict) -> Dict:
        """Generar reporte completo de intervención"""
        requires, intervention_type, reason = self.requires_intervention(ticket)
        
        if not requires:
            return {
                'requires_intervention': False,
                'can_proceed_automatically': True
            }
        
        details = self.get_intervention_details(ticket, intervention_type)
        
        return {
            'requires_intervention': True,
            'can_proceed_automatically': False,
            'intervention_type': intervention_type,
            'reason': reason,
            'details': details,
            'next_steps': [
                f'Review {intervention_type}',
                'Make decision/provide access',
                'Update ticket with decision',
                'System will continue automatically'
            ]
        }

