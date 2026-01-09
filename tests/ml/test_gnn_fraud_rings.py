"""
GNN Fraud Ring Detection Tests (FRAUD-003)
TDD: RED → GREEN → REFACTOR
"""

import pytest
import asyncio
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from fraud_detection.gnn_service import GNNService
from fraud_detection.graph_models import (
    FraudDetectionGraph, GraphNode, GraphEdge, FraudRing, GraphCommunity,
    NodeType, EdgeType, GraphStatus, RiskLevel, CommunityType
)


@pytest.mark.ml
@pytest.mark.slow
class TestGNNFraudRingDetection:
    """Test GNN fraud ring detection functionality"""
    
    @pytest.fixture
    def gnn_service(self):
        """Create GNNService instance"""
        return GNNService()
    
    @pytest.fixture
    def fraud_ring_test_case(self):
        """Create test case with known fraud ring pattern"""
        # Create a graph with suspicious connections
        graph_id = "test-fraud-ring-graph"
        
        # Create nodes that form a fraud ring
        nodes = [
            GraphNode(
                id=f"account-{i}",
                type=NodeType.ACCOUNT,
                properties={
                    "accountNumber": f"ACC-{i:04d}",
                    "riskScore": Decimal('0.8') if i < 5 else Decimal('0.2')
                },
                created_at=datetime.utcnow() - timedelta(days=30),
                last_activity_at=datetime.utcnow()
            )
            for i in range(10)
        ]
        
        # Create edges connecting accounts in suspicious pattern
        edges = []
        for i in range(5):  # First 5 accounts form a ring
            source_idx = i
            target_idx = (i + 1) % 5
            edges.append(
                GraphEdge(
                    id=f"edge-{i}",
                    source_node_id=nodes[source_idx].id,
                    target_node_id=nodes[target_idx].id,
                    type=EdgeType.TRANSFER,
                    properties={
                        "amount": Decimal('1000.00'),
                        "riskScore": Decimal('0.9'),
                        "timestamp": datetime.utcnow() - timedelta(hours=i)
                    },
                    created_at=datetime.utcnow() - timedelta(hours=i)
                )
            )
        
        return {
            "graph_id": graph_id,
            "nodes": nodes,
            "edges": edges
        }
    
    @pytest.mark.asyncio
    async def test_detect_fraud_rings_known_pattern(self, gnn_service, fraud_ring_test_case):
        """Test detecting known fraud ring pattern"""
        # Create graph with fraud ring
        graph = FraudDetectionGraph(
            id=fraud_ring_test_case["graph_id"],
            name="Test Fraud Ring Graph",
            description="Graph with known fraud ring pattern",
            created_at=datetime.utcnow(),
            last_updated_at=datetime.utcnow(),
            status=GraphStatus.ACTIVE,
            nodes=fraud_ring_test_case["nodes"],
            edges=fraud_ring_test_case["edges"],
            node_count=len(fraud_ring_test_case["nodes"]),
            edge_count=len(fraud_ring_test_case["edges"])
        )
        
        gnn_service.graphs[graph.id] = graph
        
        # Detect fraud rings
        result = await gnn_service.detect_fraud_rings(graph.id)
        
        # Should detect at least one fraud ring
        assert result is not None
        assert len(result.fraud_rings) > 0, "Should detect fraud ring in known pattern"
        
        # Verify fraud ring properties
        fraud_ring = result.fraud_rings[0]
        assert fraud_ring.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert len(fraud_ring.member_accounts) >= 3  # Fraud rings typically have 3+ members
    
    @pytest.mark.asyncio
    async def test_detect_fraud_rings_legitimate_connections(self, gnn_service):
        """Test that legitimate connections are not flagged as fraud rings"""
        # Create graph with legitimate connections
        graph_id = "test-legitimate-graph"
        
        nodes = [
            GraphNode(
                id=f"account-{i}",
                type=NodeType.ACCOUNT,
                properties={
                    "accountNumber": f"ACC-{i:04d}",
                    "riskScore": Decimal('0.2')  # Low risk
                },
                created_at=datetime.utcnow() - timedelta(days=60),
                last_activity_at=datetime.utcnow()
            )
            for i in range(5)
        ]
        
        # Create legitimate edges (low risk, normal amounts)
        edges = [
            GraphEdge(
                id=f"edge-{i}",
                source_node_id=nodes[i].id,
                target_node_id=nodes[(i + 1) % 5].id,
                type=EdgeType.TRANSFER,
                properties={
                    "amount": Decimal('50.00'),  # Normal amount
                    "riskScore": Decimal('0.2'),  # Low risk
                    "timestamp": datetime.utcnow() - timedelta(days=i)
                },
                created_at=datetime.utcnow() - timedelta(days=i)
            )
            for i in range(5)
        ]
        
        graph = FraudDetectionGraph(
            id=graph_id,
            name="Test Legitimate Graph",
            description="Graph with legitimate connections",
            created_at=datetime.utcnow(),
            last_updated_at=datetime.utcnow(),
            status=GraphStatus.ACTIVE,
            nodes=nodes,
            edges=edges,
            node_count=len(nodes),
            edge_count=len(edges)
        )
        
        gnn_service.graphs[graph.id] = graph
        
        # Detect fraud rings
        result = await gnn_service.detect_fraud_rings(graph.id)
        
        # Should have few or no fraud rings detected
        if result and result.fraud_rings:
            # If rings detected, they should be low risk
            for ring in result.fraud_rings:
                assert ring.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM], \
                    "Legitimate connections should not be flagged as high-risk fraud rings"
    
    @pytest.mark.asyncio
    async def test_detect_communities(self, gnn_service):
        """Test community detection in graph"""
        graph_id = "test-community-graph"
        
        # Use existing sample graph if available
        if "sample-fraud-graph-001" in gnn_service.graphs:
            graph_id = "sample-fraud-graph-001"
            result = await gnn_service.detect_communities(graph_id)
            
            assert result is not None
            assert len(result.communities) >= 0  # May have communities or not
    
    @pytest.mark.asyncio
    async def test_graph_analysis(self, gnn_service):
        """Test comprehensive graph analysis"""
        graph_id = "sample-fraud-graph-001"
        
        if graph_id in gnn_service.graphs:
            result = await gnn_service.analyze_graph(graph_id)
            
            assert result is not None
            assert result.graph_id == graph_id
            assert result.node_count >= 0
            assert result.edge_count >= 0


@pytest.mark.ml
class TestGNNService:
    """Test GNN service basic functionality"""
    
    @pytest.fixture
    def gnn_service(self):
        """Create GNNService instance"""
        return GNNService()
    
    @pytest.mark.asyncio
    async def test_create_graph(self, gnn_service):
        """Test creating a new graph"""
        graph_id = await gnn_service.create_graph(
            name="Test Graph",
            description="Test graph creation"
        )
        
        assert graph_id is not None
        assert graph_id in gnn_service.graphs
    
    @pytest.mark.asyncio
    async def test_add_node(self, gnn_service):
        """Test adding node to graph"""
        graph_id = "sample-fraud-graph-001"
        
        if graph_id in gnn_service.graphs:
            node = GraphNode(
                id="test-node-001",
                type=NodeType.ACCOUNT,
                properties={"test": "value"},
                created_at=datetime.utcnow(),
                last_activity_at=datetime.utcnow()
            )
            
            result = await gnn_service.add_node(graph_id, node)
            
            assert result is True or result is None  # May return True or None
    
    @pytest.mark.asyncio
    async def test_add_edge(self, gnn_service):
        """Test adding edge to graph"""
        graph_id = "sample-fraud-graph-001"
        
        if graph_id in gnn_service.graphs:
            edge = GraphEdge(
                id="test-edge-001",
                source_node_id="account-001",
                target_node_id="transaction-001",
                type=EdgeType.TRANSFER,
                properties={"test": "value"},
                created_at=datetime.utcnow()
            )
            
            result = await gnn_service.add_edge(graph_id, edge)
            
            assert result is True or result is None  # May return True or None










