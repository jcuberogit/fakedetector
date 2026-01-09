#!/usr/bin/env python3
"""
Graph Neural Network Service for Fraud Detection
Python equivalent of C# GNNService.cs
"""

import asyncio
import logging
import uuid
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
import networkx as nx
import numpy as np
from collections import defaultdict, Counter

from .graph_models import (
    FraudDetectionGraph, GraphNode, GraphEdge, GraphMetadata, GraphStatistics,
    GraphConfiguration, FraudRing, GraphCommunity, FraudRingResult,
    GraphAnalysisResult, GNNModelConfig, NodeType, EdgeType, GraphStatus,
    RiskLevel, CommunityType
)

logger = logging.getLogger(__name__)


class GNNService:
    """
    Graph Neural Network service for fraud detection
    
    Python equivalent of C# GNNService with NetworkX for graph analysis,
    community detection, and fraud ring identification.
    """
    
    def __init__(self):
        self.graphs: Dict[str, FraudDetectionGraph] = {}
        self.models: Dict[str, GNNModelConfig] = {}
        self.analysis_results: Dict[str, GraphAnalysisResult] = {}
        
        # Initialize sample data
        self._initialize_sample_data()
        
        logger.info("GNNService initialized with sample data")
    
    def _initialize_sample_data(self):
        """Initialize sample fraud detection graph and model"""
        
        # Create sample fraud detection graph
        sample_graph = FraudDetectionGraph(
            id="sample-fraud-graph-001",
            name="Sample Banking Fraud Detection Graph",
            description="Graph for detecting fraud patterns in banking transactions",
            created_at=datetime.utcnow(),
            last_updated_at=datetime.utcnow(),
            status=GraphStatus.ACTIVE,
            node_count=0,
            edge_count=0,
            metadata=GraphMetadata(
                version="1.0.0",
                domain="Banking",
                risk_level=RiskLevel.MEDIUM,
                last_analysis_at=datetime.utcnow()
            )
        )
        
        # Add sample nodes
        account_node = GraphNode(
            id="account-001",
            type=NodeType.ACCOUNT,
            properties={
                "accountNumber": "1234567890",
                "accountType": "Checking",
                "balance": Decimal('5000.00'),
                "riskScore": Decimal('0.3')
            },
            created_at=datetime.utcnow() - timedelta(days=30),
            last_activity_at=datetime.utcnow()
        )
        
        transaction_node = GraphNode(
            id="transaction-001",
            type=NodeType.TRANSACTION,
            properties={
                "transactionId": "TXN-001",
                "amount": Decimal('150.00'),
                "merchant": "Starbucks",
                "location": "San Francisco, CA",
                "riskScore": Decimal('0.7')
            },
            created_at=datetime.utcnow() - timedelta(hours=2),
            last_activity_at=datetime.utcnow() - timedelta(hours=2)
        )
        
        device_node = GraphNode(
            id="device-001",
            type=NodeType.DEVICE,
            properties={
                "deviceId": "DEV-001",
                "deviceType": "Mobile",
                "os": "iOS 17.0",
                "riskScore": Decimal('0.2')
            },
            created_at=datetime.utcnow() - timedelta(days=60),
            last_activity_at=datetime.utcnow() - timedelta(hours=1)
        )
        
        # Add sample edges
        transfer_edge = GraphEdge(
            id="edge-001",
            source_node_id="account-001",
            target_node_id="transaction-001",
            type=EdgeType.TRANSFER,
            properties={
                "amount": Decimal('150.00'),
                "timestamp": datetime.utcnow() - timedelta(hours=2),
                "riskScore": Decimal('0.6')
            },
            created_at=datetime.utcnow() - timedelta(hours=2)
        )
        
        login_edge = GraphEdge(
            id="edge-002",
            source_node_id="account-001",
            target_node_id="device-001",
            type=EdgeType.LOGIN,
            properties={
                "timestamp": datetime.utcnow() - timedelta(hours=1),
                "ipAddress": "192.168.1.100",
                "riskScore": Decimal('0.4')
            },
            created_at=datetime.utcnow() - timedelta(hours=1)
        )
        
        # Add nodes and edges to graph
        sample_graph.nodes = [account_node, transaction_node, device_node]
        sample_graph.edges = [transfer_edge, login_edge]
        sample_graph.node_count = len(sample_graph.nodes)
        sample_graph.edge_count = len(sample_graph.edges)
        
        self.graphs[sample_graph.id] = sample_graph
        
        # Create sample model
        sample_model = GNNModelConfig(
            id="model-001",
            name="Sample Fraud Detection Model",
            model_type="GraphSAGE",
            version="1.0.0",
            status="Trained",
            created_at=datetime.utcnow() - timedelta(days=7),
            last_updated_at=datetime.utcnow() - timedelta(days=1),
            hyperparameters={
                "hiddenDimensions": 128,
                "numLayers": 3,
                "learningRate": 0.001,
                "batchSize": 32
            },
            performance={
                "accuracy": 0.92,
                "precision": 0.89,
                "recall": 0.94,
                "f1_score": 0.91,
                "auc": 0.95
            }
        )
        
        self.models[sample_model.id] = sample_model
        
        logger.info(f"GNN Service initialized with sample data: "
                   f"{len(self.graphs)} graphs, {len(self.models)} models")
    
    # Graph construction and management
    
    async def create_graph_async(self, name: str, description: str) -> FraudDetectionGraph:
        """Create a new fraud detection graph"""
        graph_id = f"graph-{uuid.uuid4().hex[:8]}"
        
        graph = FraudDetectionGraph(
            id=graph_id,
            name=name,
            description=description,
            created_at=datetime.utcnow(),
            last_updated_at=datetime.utcnow(),
            status=GraphStatus.ACTIVE,
            nodes=[],
            edges=[],
            node_count=0,
            edge_count=0,
            metadata=GraphMetadata(
                version="1.0.0",
                domain="Banking",
                risk_level=RiskLevel.LOW,
                last_analysis_at=datetime.utcnow()
            )
        )
        
        self.graphs[graph_id] = graph
        logger.info(f"Created new fraud detection graph: {graph_id}")
        
        return graph
    
    async def get_graph_async(self, graph_id: str) -> FraudDetectionGraph:
        """Get graph by ID"""
        if graph_id not in self.graphs:
            raise KeyError(f"Graph with ID {graph_id} not found")
        
        return self.graphs[graph_id]
    
    async def get_all_graphs_async(self) -> List[FraudDetectionGraph]:
        """Get all graphs"""
        return list(self.graphs.values())
    
    async def update_graph_async(self, graph_id: str, graph: FraudDetectionGraph) -> FraudDetectionGraph:
        """Update graph"""
        if graph_id not in self.graphs:
            raise KeyError(f"Graph with ID {graph_id} not found")
        
        graph.last_updated_at = datetime.utcnow()
        self.graphs[graph_id] = graph
        
        return graph
    
    async def delete_graph_async(self, graph_id: str) -> bool:
        """Delete graph"""
        if graph_id in self.graphs:
            del self.graphs[graph_id]
            logger.info(f"Deleted fraud detection graph: {graph_id}")
            return True
        return False
    
    # Node management
    
    async def add_node_async(self, graph_id: str, node: GraphNode) -> GraphNode:
        """Add node to graph"""
        if graph_id not in self.graphs:
            raise KeyError(f"Graph with ID {graph_id} not found")
        
        graph = self.graphs[graph_id]
        
        if not node.id:
            node.id = f"node-{uuid.uuid4().hex[:8]}"
        
        node.created_at = datetime.utcnow()
        node.last_activity_at = datetime.utcnow()
        
        graph.nodes.append(node)
        graph.node_count = len(graph.nodes)
        graph.last_updated_at = datetime.utcnow()
        
        logger.info(f"Added node {node.id} to graph {graph_id}")
        
        return node
    
    async def get_node_async(self, graph_id: str, node_id: str) -> GraphNode:
        """Get node by ID"""
        if graph_id not in self.graphs:
            raise KeyError(f"Graph with ID {graph_id} not found")
        
        graph = self.graphs[graph_id]
        for node in graph.nodes:
            if node.id == node_id:
                return node
        
        raise KeyError(f"Node with ID {node_id} not found in graph {graph_id}")
    
    async def get_all_nodes_async(self, graph_id: str) -> List[GraphNode]:
        """Get all nodes in graph"""
        if graph_id not in self.graphs:
            raise KeyError(f"Graph with ID {graph_id} not found")
        
        return self.graphs[graph_id].nodes
    
    async def update_node_async(self, graph_id: str, node_id: str, node: GraphNode) -> GraphNode:
        """Update node"""
        if graph_id not in self.graphs:
            raise KeyError(f"Graph with ID {graph_id} not found")
        
        graph = self.graphs[graph_id]
        for i, existing_node in enumerate(graph.nodes):
            if existing_node.id == node_id:
                node.last_activity_at = datetime.utcnow()
                graph.nodes[i] = node
                graph.last_updated_at = datetime.utcnow()
                return node
        
        raise KeyError(f"Node with ID {node_id} not found in graph {graph_id}")
    
    async def delete_node_async(self, graph_id: str, node_id: str) -> bool:
        """Delete node"""
        if graph_id not in self.graphs:
            raise KeyError(f"Graph with ID {graph_id} not found")
        
        graph = self.graphs[graph_id]
        for i, node in enumerate(graph.nodes):
            if node.id == node_id:
                del graph.nodes[i]
                graph.node_count = len(graph.nodes)
                graph.last_updated_at = datetime.utcnow()
                
                # Remove associated edges
                graph.edges = [edge for edge in graph.edges 
                              if edge.source_node_id != node_id and edge.target_node_id != node_id]
                graph.edge_count = len(graph.edges)
                
                logger.info(f"Deleted node {node_id} from graph {graph_id}")
                return True
        
        return False
    
    # Edge management
    
    async def add_edge_async(self, graph_id: str, edge: GraphEdge) -> GraphEdge:
        """Add edge to graph"""
        if graph_id not in self.graphs:
            raise KeyError(f"Graph with ID {graph_id} not found")
        
        graph = self.graphs[graph_id]
        
        if not edge.id:
            edge.id = f"edge-{uuid.uuid4().hex[:8]}"
        
        edge.created_at = datetime.utcnow()
        
        graph.edges.append(edge)
        graph.edge_count = len(graph.edges)
        graph.last_updated_at = datetime.utcnow()
        
        logger.info(f"Added edge {edge.id} to graph {graph_id}")
        
        return edge
    
    async def get_edge_async(self, graph_id: str, edge_id: str) -> GraphEdge:
        """Get edge by ID"""
        if graph_id not in self.graphs:
            raise KeyError(f"Graph with ID {graph_id} not found")
        
        graph = self.graphs[graph_id]
        for edge in graph.edges:
            if edge.id == edge_id:
                return edge
        
        raise KeyError(f"Edge with ID {edge_id} not found in graph {graph_id}")
    
    async def get_all_edges_async(self, graph_id: str) -> List[GraphEdge]:
        """Get all edges in graph"""
        if graph_id not in self.graphs:
            raise KeyError(f"Graph with ID {graph_id} not found")
        
        return self.graphs[graph_id].edges
    
    # Graph analysis methods
    
    async def analyze_graph_async(self, graph_id: str) -> GraphAnalysisResult:
        """Perform comprehensive graph analysis"""
        start_time = time.time()
        
        try:
            if graph_id not in self.graphs:
                raise KeyError(f"Graph with ID {graph_id} not found")
            
            graph = self.graphs[graph_id]
            
            # Convert to NetworkX graph for analysis
            nx_graph = self._convert_to_networkx(graph)
            
            # Perform various analyses
            statistics = self._calculate_graph_statistics(nx_graph, graph)
            fraud_rings = await self._detect_fraud_rings_async(nx_graph, graph)
            communities = await self._detect_communities_async(nx_graph, graph)
            risk_assessment = self._assess_graph_risk(graph, fraud_rings, communities)
            
            processing_time = (time.time() - start_time) * 1000
            
            analysis_id = f"analysis_{uuid.uuid4().hex[:8]}"
            
            result = GraphAnalysisResult(
                analysis_id=analysis_id,
                graph_id=graph_id,
                analysis_type="comprehensive",
                results={
                    "statistics": statistics.dict(),
                    "node_count": len(graph.nodes),
                    "edge_count": len(graph.edges),
                    "density": statistics.density,
                    "clustering_coefficient": statistics.average_clustering_coefficient
                },
                fraud_rings=fraud_rings,
                communities=communities,
                risk_assessment=risk_assessment,
                recommendations=self._generate_recommendations(fraud_rings, communities, risk_assessment),
                analysis_timestamp=datetime.utcnow(),
                processing_time_ms=processing_time
            )
            
            self.analysis_results[analysis_id] = result
            
            logger.info(f"Graph analysis completed for {graph_id}: "
                       f"{len(fraud_rings)} fraud rings, {len(communities)} communities, "
                       f"Time: {processing_time:.1f}ms")
            
            return result
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error analyzing graph {graph_id}: {e}")
            raise
    
    async def detect_fraud_rings_async(self, graph_id: str) -> List[FraudRing]:
        """Detect fraud rings in the graph"""
        try:
            if graph_id not in self.graphs:
                raise KeyError(f"Graph with ID {graph_id} not found")
            
            graph = self.graphs[graph_id]
            nx_graph = self._convert_to_networkx(graph)
            
            fraud_rings = await self._detect_fraud_rings_async(nx_graph, graph)
            
            logger.info(f"Fraud ring detection completed for {graph_id}: "
                       f"Found {len(fraud_rings)} fraud rings")
            
            return fraud_rings
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error detecting fraud rings for {graph_id}: {e}")
            raise
    
    async def detect_communities_async(self, graph_id: str) -> List[GraphCommunity]:
        """Detect communities in the graph"""
        try:
            if graph_id not in self.graphs:
                raise KeyError(f"Graph with ID {graph_id} not found")
            
            graph = self.graphs[graph_id]
            nx_graph = self._convert_to_networkx(graph)
            
            communities = await self._detect_communities_async(nx_graph, graph)
            
            logger.info(f"Community detection completed for {graph_id}: "
                       f"Found {len(communities)} communities")
            
            return communities
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error detecting communities for {graph_id}: {e}")
            raise
    
    # Private helper methods
    
    def _convert_to_networkx(self, graph: FraudDetectionGraph) -> nx.Graph:
        """Convert FraudDetectionGraph to NetworkX graph"""
        nx_graph = nx.Graph()
        
        # Add nodes
        for node in graph.nodes:
            nx_graph.add_node(
                node.id,
                type=node.type.value,
                risk_score=float(node.risk_score),
                properties=node.properties
            )
        
        # Add edges
        for edge in graph.edges:
            nx_graph.add_edge(
                edge.source_node_id,
                edge.target_node_id,
                type=edge.type.value,
                weight=float(edge.weight),
                properties=edge.properties
            )
        
        return nx_graph
    
    def _calculate_graph_statistics(self, nx_graph: nx.Graph, graph: FraudDetectionGraph) -> GraphStatistics:
        """Calculate graph statistics"""
        if nx_graph.number_of_nodes() == 0:
            return GraphStatistics()
        
        # Basic statistics
        node_count = nx_graph.number_of_nodes()
        edge_count = nx_graph.number_of_edges()
        density = nx.density(nx_graph)
        
        # Clustering coefficient
        clustering_coeffs = nx.clustering(nx_graph)
        avg_clustering = sum(clustering_coeffs.values()) / len(clustering_coeffs) if clustering_coeffs else 0.0
        
        # Path length (only for connected components)
        try:
            avg_path_length = nx.average_shortest_path_length(nx_graph)
        except nx.NetworkXError:
            avg_path_length = 0.0
        
        # Connected components
        connected_components = nx.number_connected_components(nx_graph)
        
        # Node type distribution
        node_type_dist = {}
        for node_id in nx_graph.nodes():
            node_type = nx_graph.nodes[node_id].get('type', 'Unknown')
            node_type_dist[node_type] = node_type_dist.get(node_type, 0) + 1
        
        # Edge type distribution
        edge_type_dist = {}
        for edge in nx_graph.edges(data=True):
            edge_type = edge[2].get('type', 'Unknown')
            edge_type_dist[edge_type] = edge_type_dist.get(edge_type, 0) + 1
        
        # Top central nodes (by degree centrality)
        centrality = nx.degree_centrality(nx_graph)
        top_central_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        top_central_node_ids = [node_id for node_id, _ in top_central_nodes]
        
        # Graph diameter
        try:
            diameter = nx.diameter(nx_graph)
        except nx.NetworkXError:
            diameter = 0.0
        
        return GraphStatistics(
            node_count=node_count,
            edge_count=edge_count,
            density=density,
            average_clustering_coefficient=avg_clustering,
            average_path_length=avg_path_length,
            connected_components=connected_components,
            node_type_distribution=node_type_dist,
            edge_type_distribution=edge_type_dist,
            top_central_nodes=top_central_node_ids,
            graph_diameter=diameter,
            last_calculated=datetime.utcnow()
        )
    
    async def _detect_fraud_rings_async(self, nx_graph: nx.Graph, graph: FraudDetectionGraph) -> List[FraudRing]:
        """Detect fraud rings using graph analysis"""
        fraud_rings = []
        
        if nx_graph.number_of_nodes() < 3:
            return fraud_rings
        
        # Detect suspicious subgraphs (simplified algorithm)
        suspicious_nodes = []
        for node_id in nx_graph.nodes():
            node_data = nx_graph.nodes[node_id]
            risk_score = node_data.get('risk_score', 0.0)
            
            if risk_score > 0.7:  # High risk threshold
                suspicious_nodes.append(node_id)
        
        # Find connected components of suspicious nodes
        suspicious_subgraph = nx_graph.subgraph(suspicious_nodes)
        
        for component in nx.connected_components(suspicious_subgraph):
            if len(component) >= 3:  # Minimum ring size
                ring_id = f"ring_{uuid.uuid4().hex[:8]}"
                
                # Calculate ring metrics
                subgraph = nx_graph.subgraph(component)
                ring_density = nx.density(subgraph)
                
                # Calculate risk score for the ring
                ring_risk_scores = [nx_graph.nodes[node_id].get('risk_score', 0.0) 
                                  for node_id in component]
                avg_risk_score = sum(ring_risk_scores) / len(ring_risk_scores)
                
                # Get edges within the ring
                ring_edges = []
                for edge in graph.edges:
                    if (edge.source_node_id in component and 
                        edge.target_node_id in component):
                        ring_edges.append(edge.id)
                
                fraud_ring = FraudRing(
                    id=ring_id,
                    name=f"Fraud Ring {len(fraud_rings) + 1}",
                    description=f"Suspicious activity ring with {len(component)} nodes",
                    node_ids=list(component),
                    edge_ids=ring_edges,
                    risk_score=Decimal(str(avg_risk_score)),
                    confidence=Decimal(str(min(ring_density * 2, 1.0))),
                    ring_type="suspicious_cluster",
                    detected_at=datetime.utcnow(),
                    is_active=True,
                    metadata={
                        "density": ring_density,
                        "size": len(component),
                        "detection_method": "risk_based_clustering"
                    }
                )
                
                fraud_rings.append(fraud_ring)
        
        return fraud_rings
    
    async def _detect_communities_async(self, nx_graph: nx.Graph, graph: FraudDetectionGraph) -> List[GraphCommunity]:
        """Detect communities using graph analysis"""
        communities = []
        
        if nx_graph.number_of_nodes() < 2:
            return communities
        
        try:
            # Use NetworkX community detection algorithms
            # Try different algorithms and pick the best result
            
            # Algorithm 1: Greedy modularity communities
            try:
                greedy_communities = nx.community.greedy_modularity_communities(nx_graph)
                for i, community in enumerate(greedy_communities):
                    if len(community) >= 2:  # Minimum community size
                        community_id = f"community_{uuid.uuid4().hex[:8]}"
                        
                        # Calculate community metrics
                        subgraph = nx_graph.subgraph(community)
                        density = nx.density(subgraph)
                        
                        # Calculate risk score for the community
                        community_risk_scores = [nx_graph.nodes[node_id].get('risk_score', 0.0) 
                                                for node_id in community]
                        avg_risk_score = sum(community_risk_scores) / len(community_risk_scores)
                        
                        # Determine community type
                        community_type = CommunityType.LEGITIMATE_GROUP
                        if avg_risk_score > 0.7:
                            community_type = CommunityType.FRAUD_RING
                        elif avg_risk_score > 0.4:
                            community_type = CommunityType.SUSPICIOUS_CLUSTER
                        
                        graph_community = GraphCommunity(
                            id=community_id,
                            name=f"Community {i + 1}",
                            type=community_type,
                            node_ids=list(community),
                            size=len(community),
                            density=density,
                            risk_score=Decimal(str(avg_risk_score)),
                            detected_at=datetime.utcnow(),
                            is_suspicious=avg_risk_score > 0.5,
                            metadata={
                                "detection_algorithm": "greedy_modularity",
                                "modularity": nx.community.modularity(nx_graph, greedy_communities)
                            }
                        )
                        
                        communities.append(graph_community)
            
            except (ValueError, TypeError, AttributeError) as e:
                logger.warning(f"Greedy modularity community detection failed: {e}")
            
            # Algorithm 2: Label propagation (fallback)
            if not communities:
                try:
                    label_communities = nx.community.label_propagation_communities(nx_graph)
                    for i, community in enumerate(label_communities):
                        if len(community) >= 2:
                            community_id = f"community_{uuid.uuid4().hex[:8]}"
                            
                            subgraph = nx_graph.subgraph(community)
                            density = nx.density(subgraph)
                            
                            community_risk_scores = [nx_graph.nodes[node_id].get('risk_score', 0.0) 
                                                    for node_id in community]
                            avg_risk_score = sum(community_risk_scores) / len(community_risk_scores)
                            
                            community_type = CommunityType.LEGITIMATE_GROUP
                            if avg_risk_score > 0.7:
                                community_type = CommunityType.FRAUD_RING
                            elif avg_risk_score > 0.4:
                                community_type = CommunityType.SUSPICIOUS_CLUSTER
                            
                            graph_community = GraphCommunity(
                                id=community_id,
                                name=f"Community {i + 1}",
                                type=community_type,
                                node_ids=list(community),
                                size=len(community),
                                density=density,
                                risk_score=Decimal(str(avg_risk_score)),
                                detected_at=datetime.utcnow(),
                                is_suspicious=avg_risk_score > 0.5,
                                metadata={
                                    "detection_algorithm": "label_propagation"
                                }
                            )
                            
                            communities.append(graph_community)
                
                except (ValueError, TypeError, AttributeError) as e:
                    logger.warning(f"Label propagation community detection failed: {e}")
        
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Community detection failed: {e}")
        
        return communities
    
    def _assess_graph_risk(self, graph: FraudDetectionGraph, fraud_rings: List[FraudRing], 
                          communities: List[GraphCommunity]) -> Dict[str, Decimal]:
        """Assess overall graph risk"""
        risk_assessment = {}
        
        # Overall risk score
        if graph.nodes:
            node_risk_scores = [node.risk_score for node in graph.nodes]
            overall_risk = sum(node_risk_scores) / len(node_risk_scores)
        else:
            overall_risk = Decimal('0')
        
        risk_assessment['overall_risk'] = overall_risk
        
        # Fraud ring risk
        if fraud_rings:
            ring_risk_scores = [ring.risk_score for ring in fraud_rings]
            fraud_ring_risk = sum(ring_risk_scores) / len(ring_risk_scores)
        else:
            fraud_ring_risk = Decimal('0')
        
        risk_assessment['fraud_ring_risk'] = fraud_ring_risk
        
        # Community risk
        suspicious_communities = [comm for comm in communities if comm.is_suspicious]
        if suspicious_communities:
            community_risk_scores = [comm.risk_score for comm in suspicious_communities]
            community_risk = sum(community_risk_scores) / len(community_risk_scores)
        else:
            community_risk = Decimal('0')
        
        risk_assessment['community_risk'] = community_risk
        
        # Combined risk score
        combined_risk = max(overall_risk, fraud_ring_risk, community_risk)
        risk_assessment['combined_risk'] = combined_risk
        
        return risk_assessment
    
    def _generate_recommendations(self, fraud_rings: List[FraudRing], communities: List[GraphCommunity], 
                                risk_assessment: Dict[str, Decimal]) -> List[str]:
        """Generate recommendations based on analysis results"""
        recommendations = []
        
        # Fraud ring recommendations
        if fraud_rings:
            recommendations.append(f"Investigate {len(fraud_rings)} detected fraud rings")
            high_risk_rings = [ring for ring in fraud_rings if ring.risk_score > Decimal('0.8')]
            if high_risk_rings:
                recommendations.append(f"Immediate attention required for {len(high_risk_rings)} high-risk fraud rings")
        
        # Community recommendations
        suspicious_communities = [comm for comm in communities if comm.is_suspicious]
        if suspicious_communities:
            recommendations.append(f"Monitor {len(suspicious_communities)} suspicious communities")
        
        # Risk-based recommendations
        combined_risk = risk_assessment.get('combined_risk', Decimal('0'))
        if combined_risk > Decimal('0.8'):
            recommendations.append("High risk detected - consider enhanced monitoring")
        elif combined_risk > Decimal('0.5'):
            recommendations.append("Medium risk detected - continue regular monitoring")
        else:
            recommendations.append("Low risk - standard monitoring sufficient")
        
        # General recommendations
        recommendations.append("Regular graph analysis recommended")
        recommendations.append("Update fraud detection models based on new patterns")
        
        return recommendations
