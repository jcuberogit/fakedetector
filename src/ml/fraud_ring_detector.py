"""
Fraud Ring Detection using Graph Neural Networks (GNN)
Identifies coordinated fraud campaigns by analyzing network patterns
"""

import numpy as np
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
from datetime import datetime, timedelta
import hashlib
import json

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    print("⚠️  NetworkX not installed. Run: pip install networkx")


class FraudRingDetector:
    """
    Detects fraud rings using graph-based analysis.
    Identifies clusters of related scam accounts based on behavioral patterns.
    """
    
    def __init__(self, db_service=None):
        self.db = db_service
        self.graph = nx.Graph() if NETWORKX_AVAILABLE else None
        self.similarity_threshold = 0.7
        self.min_ring_size = 2
    
    def anonymize_identifier(self, identifier: str) -> str:
        """Create anonymized hash of email/profile identifier."""
        return hashlib.sha256(identifier.encode()).hexdigest()[:32]
    
    def extract_behavioral_signature(self, features: Dict) -> str:
        """
        Extract behavioral signature from message features.
        Similar scam messages will have similar signatures.
        """
        # Key features that indicate similar scam patterns
        signature_features = [
            features.get('recruiter_keywords_count', 0),
            features.get('location_inquiry', 0),
            features.get('experience_inquiry', 0),
            features.get('gmail_recruiter_combo', 0),
            features.get('vague_address_pattern', 0),
            features.get('financial_phishing_keywords_count', 0),
            features.get('urgency_keywords_count', 0),
            features.get('money_keywords_count', 0),
            int(features.get('message_length', 0) / 50),  # Bucketed length
            features.get('link_count', 0)
        ]
        
        # Create signature string
        signature = '-'.join(str(f) for f in signature_features)
        return hashlib.md5(signature.encode()).hexdigest()[:16]
    
    def calculate_similarity(self, features1: Dict, features2: Dict) -> float:
        """
        Calculate similarity between two feature sets.
        Returns value between 0 (completely different) and 1 (identical).
        """
        # Extract key features for comparison
        key_features = [
            'recruiter_keywords_count', 'location_inquiry', 'experience_inquiry',
            'gmail_recruiter_combo', 'vague_address_pattern',
            'financial_phishing_keywords_count', 'urgency_keywords_count',
            'money_keywords_count', 'credential_keywords_count'
        ]
        
        # Calculate feature-wise similarity
        similarities = []
        for feature in key_features:
            val1 = features1.get(feature, 0)
            val2 = features2.get(feature, 0)
            
            # Binary features: exact match
            if val1 in [0, 1] and val2 in [0, 1]:
                similarities.append(1.0 if val1 == val2 else 0.0)
            # Numeric features: inverse distance
            else:
                max_val = max(val1, val2, 1)
                similarity = 1.0 - abs(val1 - val2) / max_val
                similarities.append(similarity)
        
        # Average similarity
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def add_scam_report(self, sender_identifier: str, features: Dict, 
                       timestamp: datetime, is_scam: bool):
        """
        Add a scam report to the fraud ring detection graph.
        Only processes confirmed scams (is_scam=True).
        """
        if not NETWORKX_AVAILABLE or not is_scam:
            return
        
        # Anonymize sender
        anon_id = self.anonymize_identifier(sender_identifier)
        
        # Extract behavioral signature
        signature = self.extract_behavioral_signature(features)
        
        # Add node to graph
        if not self.graph.has_node(anon_id):
            self.graph.add_node(anon_id, 
                              first_seen=timestamp,
                              last_seen=timestamp,
                              message_count=1,
                              signatures={signature},
                              features=features)
        else:
            # Update existing node
            node_data = self.graph.nodes[anon_id]
            node_data['last_seen'] = timestamp
            node_data['message_count'] += 1
            node_data['signatures'].add(signature)
        
        # Find similar nodes and create edges
        for other_id in self.graph.nodes():
            if other_id == anon_id:
                continue
            
            other_features = self.graph.nodes[other_id]['features']
            similarity = self.calculate_similarity(features, other_features)
            
            # Create edge if similarity is high
            if similarity >= self.similarity_threshold:
                if self.graph.has_edge(anon_id, other_id):
                    # Strengthen existing edge
                    self.graph[anon_id][other_id]['weight'] += 1
                    self.graph[anon_id][other_id]['similarity'] = max(
                        self.graph[anon_id][other_id]['similarity'], 
                        similarity
                    )
                else:
                    # Create new edge
                    self.graph.add_edge(anon_id, other_id, 
                                      weight=1, 
                                      similarity=similarity)
    
    def detect_fraud_rings(self) -> List[Dict]:
        """
        Detect fraud rings using community detection algorithms.
        Returns list of detected rings with metadata.
        """
        if not NETWORKX_AVAILABLE or self.graph.number_of_nodes() < self.min_ring_size:
            return []
        
        rings = []
        
        # Use connected components to find clusters
        for component in nx.connected_components(self.graph):
            if len(component) < self.min_ring_size:
                continue
            
            # Extract subgraph for this component
            subgraph = self.graph.subgraph(component)
            
            # Calculate ring metrics
            members = list(component)
            edge_count = subgraph.number_of_edges()
            avg_similarity = np.mean([
                data['similarity'] 
                for _, _, data in subgraph.edges(data=True)
            ]) if edge_count > 0 else 0.0
            
            # Determine pattern type based on common features
            pattern_type = self._identify_pattern_type(subgraph)
            
            # Calculate confidence score
            confidence = self._calculate_ring_confidence(subgraph)
            
            # Get temporal info
            first_seen = min(self.graph.nodes[m]['first_seen'] for m in members)
            last_seen = max(self.graph.nodes[m]['last_seen'] for m in members)
            
            ring = {
                'ring_id': hashlib.md5(
                    ''.join(sorted(members)).encode()
                ).hexdigest()[:16],
                'member_count': len(members),
                'members': members,
                'pattern_type': pattern_type,
                'confidence_score': confidence,
                'avg_similarity': avg_similarity,
                'first_seen': first_seen,
                'last_seen': last_seen,
                'is_active': (datetime.now() - last_seen).days < 7
            }
            
            rings.append(ring)
        
        # Sort by confidence score
        rings.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        return rings
    
    def _identify_pattern_type(self, subgraph) -> str:
        """Identify the type of scam pattern used by the ring."""
        # Aggregate features from all members
        feature_counts = defaultdict(int)
        
        for node in subgraph.nodes():
            features = self.graph.nodes[node]['features']
            
            if features.get('gmail_recruiter_combo', 0) > 0:
                feature_counts['rachel_good'] += 1
            if features.get('financial_phishing_keywords_count', 0) > 2:
                feature_counts['financial_phishing'] += 1
            if features.get('credential_keywords_count', 0) > 2:
                feature_counts['credential_phishing'] += 1
            if features.get('money_keywords_count', 0) > 2:
                feature_counts['advance_fee'] += 1
        
        # Return most common pattern
        if not feature_counts:
            return 'unknown'
        
        return max(feature_counts.items(), key=lambda x: x[1])[0]
    
    def _calculate_ring_confidence(self, subgraph) -> float:
        """
        Calculate confidence score for fraud ring detection.
        Higher score = more confident this is a coordinated fraud ring.
        """
        member_count = subgraph.number_of_nodes()
        edge_count = subgraph.number_of_edges()
        
        # Density: how connected are the members?
        max_edges = member_count * (member_count - 1) / 2
        density = edge_count / max_edges if max_edges > 0 else 0
        
        # Average similarity
        avg_similarity = np.mean([
            data['similarity'] 
            for _, _, data in subgraph.edges(data=True)
        ]) if edge_count > 0 else 0.0
        
        # Temporal clustering: are messages sent close together?
        timestamps = [self.graph.nodes[n]['last_seen'] for n in subgraph.nodes()]
        time_span = (max(timestamps) - min(timestamps)).days + 1
        temporal_score = 1.0 / (1.0 + time_span / 7.0)  # Decay over weeks
        
        # Combined confidence score
        confidence = (
            0.4 * density +           # Connection density
            0.4 * avg_similarity +    # Behavioral similarity
            0.2 * temporal_score      # Temporal clustering
        )
        
        return min(confidence, 1.0)
    
    def save_rings_to_database(self, rings: List[Dict]):
        """Save detected fraud rings to database."""
        if not self.db:
            return
        
        for ring in rings:
            # Check if ring already exists
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT id FROM fraud_rings WHERE ring_identifier = %s",
                (ring['ring_id'],)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing ring
                cursor.execute("""
                    UPDATE fraud_rings 
                    SET member_count = %s, confidence_score = %s, 
                        status = %s, notes = %s
                    WHERE ring_identifier = %s
                """, (
                    ring['member_count'],
                    ring['confidence_score'],
                    'active' if ring['is_active'] else 'inactive',
                    f"Pattern: {ring['pattern_type']}, Similarity: {ring['avg_similarity']:.2f}",
                    ring['ring_id']
                ))
                ring_db_id = existing[0]
            else:
                # Insert new ring
                cursor.execute("""
                    INSERT INTO fraud_rings 
                    (ring_identifier, member_count, confidence_score, 
                     pattern_type, status, notes)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    ring['ring_id'],
                    ring['member_count'],
                    ring['confidence_score'],
                    ring['pattern_type'],
                    'active' if ring['is_active'] else 'inactive',
                    f"Similarity: {ring['avg_similarity']:.2f}"
                ))
                ring_db_id = cursor.fetchone()[0]
            
            # Update ring members
            for member_id in ring['members']:
                cursor.execute("""
                    INSERT INTO fraud_ring_members 
                    (ring_id, anonymized_identifier, last_seen, message_count)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (ring_id, anonymized_identifier) 
                    DO UPDATE SET 
                        last_seen = EXCLUDED.last_seen,
                        message_count = fraud_ring_members.message_count + 1
                """, (
                    ring_db_id,
                    member_id,
                    ring['last_seen'],
                    self.graph.nodes[member_id]['message_count']
                ))
            
            self.db.conn.commit()
            cursor.close()
            
            print(f"💍 Saved fraud ring: {ring['ring_id']} ({ring['member_count']} members)")
    
    def get_ring_statistics(self) -> Dict:
        """Get statistics about detected fraud rings."""
        if not NETWORKX_AVAILABLE:
            return {}
        
        rings = self.detect_fraud_rings()
        
        return {
            'total_rings': len(rings),
            'active_rings': sum(1 for r in rings if r['is_active']),
            'total_members': sum(r['member_count'] for r in rings),
            'avg_ring_size': np.mean([r['member_count'] for r in rings]) if rings else 0,
            'pattern_distribution': self._get_pattern_distribution(rings),
            'high_confidence_rings': sum(1 for r in rings if r['confidence_score'] > 0.8)
        }
    
    def _get_pattern_distribution(self, rings: List[Dict]) -> Dict[str, int]:
        """Get distribution of pattern types across rings."""
        distribution = defaultdict(int)
        for ring in rings:
            distribution[ring['pattern_type']] += 1
        return dict(distribution)
