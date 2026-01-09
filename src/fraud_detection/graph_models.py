#!/usr/bin/env python3
"""
Graph Neural Network Models for Fraud Detection
Python equivalent of C# GraphML and GNN models
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from decimal import Decimal
from enum import Enum


class NodeType(str, Enum):
    """Node types in the fraud detection graph"""
    USER = "User"
    DEVICE = "Device"
    IP = "IP"
    MERCHANT = "Merchant"
    LOCATION = "Location"
    ACCOUNT = "Account"
    TRANSACTION = "Transaction"
    CARD = "Card"
    BANK = "Bank"
    PHONE = "Phone"
    EMAIL = "Email"
    ADDRESS = "Address"
    COMPANY = "Company"
    DOCUMENT = "Document"
    OTHER = "Other"


class EdgeType(str, Enum):
    """Edge types representing relationships between nodes"""
    USES = "Uses"
    LOCATED_AT = "LocatedAt"
    TRANSACTS_WITH = "TransactsWith"
    OWNS = "Owns"
    ASSOCIATED_WITH = "AssociatedWith"
    SHARES = "Shares"
    CONNECTED_TO = "ConnectedTo"
    BELONGS_TO = "BelongsTo"
    WORKS_FOR = "WorksFor"
    LIVES_AT = "LivesAt"
    CALLS = "Calls"
    EMAILS = "Emails"
    VISITS = "Visits"
    TRANSFER = "Transfer"
    LOGIN = "Login"
    DEVICE = "Device"
    LOCATION = "Location"
    OTHER = "Other"


class GraphNodeType(str, Enum):
    """Types of nodes in the fraud detection graph"""
    USER = "User"
    DEVICE = "Device"
    IP_ADDRESS = "IpAddress"
    MERCHANT = "Merchant"
    LOCATION = "Location"
    PAYMENT_METHOD = "PaymentMethod"
    ACCOUNT = "Account"
    TRANSACTION = "Transaction"
    EMAIL = "Email"
    PHONE_NUMBER = "PhoneNumber"


class GraphEdgeType(str, Enum):
    """Types of edges in the fraud detection graph"""
    USER_TO_DEVICE = "UserToDevice"
    USER_TO_ACCOUNT = "UserToAccount"
    USER_TO_LOCATION = "UserToLocation"
    DEVICE_TO_LOCATION = "DeviceToLocation"
    DEVICE_TO_IP_ADDRESS = "DeviceToIpAddress"
    TRANSACTION_TO_MERCHANT = "TransactionToMerchant"
    TRANSACTION_TO_PAYMENT_METHOD = "TransactionToPaymentMethod"
    ACCOUNT_TO_PAYMENT_METHOD = "AccountToPaymentMethod"
    USER_TO_MERCHANT = "UserToMerchant"
    DEVICE_TO_MERCHANT = "DeviceToMerchant"
    IP_TO_LOCATION = "IpToLocation"
    SHARED_DEVICE = "SharedDevice"
    SHARED_IP_ADDRESS = "SharedIpAddress"
    SHARED_MERCHANT = "SharedMerchant"
    SHARED_LOCATION = "SharedLocation"
    SIMILAR_TRANSACTION = "SimilarTransaction"


class CommunityType(str, Enum):
    """Types of communities in the graph"""
    FRAUD_RING = "FraudRing"
    LEGITIMATE_GROUP = "LegitimateGroup"
    SUSPICIOUS_CLUSTER = "SuspiciousCluster"
    UNKNOWN = "Unknown"


class GraphStatus(str, Enum):
    """Graph status"""
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PROCESSING = "Processing"
    ERROR = "Error"


class RiskLevel(str, Enum):
    """Risk levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class GraphNodeMetadata(BaseModel):
    """Additional metadata for graph nodes"""
    label: str = Field(default="", description="Node label")
    centrality: float = Field(default=0.0, description="Node centrality")
    clustering_coefficient: int = Field(default=0, description="Clustering coefficient")
    community_ids: List[str] = Field(default_factory=list, description="Community IDs")
    metrics: Dict[str, float] = Field(default_factory=dict, description="Node metrics")
    is_suspicious: bool = Field(default=False, description="Is suspicious")
    tags: List[str] = Field(default_factory=list, description="Node tags")


class GraphEdgeMetadata(BaseModel):
    """Additional metadata for graph edges"""
    label: str = Field(default="", description="Edge label")
    strength: float = Field(default=1.0, description="Edge strength")
    frequency: int = Field(default=1, description="Interaction frequency")
    last_interaction: datetime = Field(default_factory=datetime.utcnow, description="Last interaction")
    is_suspicious: bool = Field(default=False, description="Is suspicious")
    tags: List[str] = Field(default_factory=list, description="Edge tags")


class GraphNode(BaseModel):
    """Graph node representing an entity in the fraud detection graph"""
    id: str = Field(..., description="Node identifier")
    type: NodeType = Field(..., description="Node type")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Node properties")
    features: Dict[str, Any] = Field(default_factory=dict, description="Node features")
    embeddings: Dict[str, Decimal] = Field(default_factory=dict, description="Node embeddings")
    risk_score: Decimal = Field(default=Decimal('0'), description="Risk score")
    first_seen: datetime = Field(default_factory=datetime.utcnow, description="First seen")
    last_seen: datetime = Field(default_factory=datetime.utcnow, description="Last seen")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    last_activity_at: datetime = Field(default_factory=datetime.utcnow, description="Last activity")
    transaction_count: int = Field(default=0, description="Transaction count")
    total_amount: Decimal = Field(default=Decimal('0'), description="Total amount")
    source: str = Field(default="", description="Data source")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class GraphEdge(BaseModel):
    """Graph edge representing a relationship between nodes"""
    id: str = Field(..., description="Edge identifier")
    source_node_id: str = Field(..., description="Source node ID")
    target_node_id: str = Field(..., description="Target node ID")
    type: EdgeType = Field(..., description="Edge type")
    weight: Decimal = Field(default=Decimal('1'), description="Edge weight")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Edge properties")
    features: Dict[str, Any] = Field(default_factory=dict, description="Edge features")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    last_seen: datetime = Field(default_factory=datetime.utcnow, description="Last seen")
    interaction_count: int = Field(default=0, description="Interaction count")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class GraphMetadata(BaseModel):
    """Graph metadata and statistics"""
    version: str = Field(default="1.0.0", description="Graph version")
    domain: str = Field(default="Banking", description="Domain")
    risk_level: RiskLevel = Field(default=RiskLevel.LOW, description="Risk level")
    last_analysis_at: datetime = Field(default_factory=datetime.utcnow, description="Last analysis")
    total_nodes: int = Field(default=0, description="Total nodes")
    total_edges: int = Field(default=0, description="Total edges")
    average_risk_score: Decimal = Field(default=Decimal('0'), description="Average risk score")
    max_risk_score: Decimal = Field(default=Decimal('0'), description="Max risk score")
    min_risk_score: Decimal = Field(default=Decimal('0'), description="Min risk score")
    graph_density: Decimal = Field(default=Decimal('0'), description="Graph density")
    clustering_coefficient: Decimal = Field(default=Decimal('0'), description="Clustering coefficient")
    node_type_distribution: Dict[str, int] = Field(default_factory=dict, description="Node type distribution")
    edge_type_distribution: Dict[str, int] = Field(default_factory=dict, description="Edge type distribution")
    last_analysis_date: datetime = Field(default_factory=datetime.utcnow, description="Last analysis date")


class FraudDetectionGraph(BaseModel):
    """Fraud detection graph containing nodes and edges"""
    id: str = Field(..., description="Graph identifier")
    name: str = Field(..., description="Graph name")
    description: str = Field(..., description="Graph description")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    last_updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    status: GraphStatus = Field(default=GraphStatus.ACTIVE, description="Graph status")
    nodes: List[GraphNode] = Field(default_factory=list, description="Graph nodes")
    edges: List[GraphEdge] = Field(default_factory=list, description="Graph edges")
    node_count: int = Field(default=0, description="Node count")
    edge_count: int = Field(default=0, description="Edge count")
    metadata: GraphMetadata = Field(default_factory=GraphMetadata, description="Graph metadata")


class GraphStatistics(BaseModel):
    """Statistical information about the fraud graph"""
    node_count: int = Field(default=0, description="Node count")
    edge_count: int = Field(default=0, description="Edge count")
    density: float = Field(default=0.0, description="Graph density")
    average_clustering_coefficient: float = Field(default=0.0, description="Average clustering coefficient")
    average_path_length: float = Field(default=0.0, description="Average path length")
    connected_components: int = Field(default=0, description="Connected components")
    node_type_distribution: Dict[str, int] = Field(default_factory=dict, description="Node type distribution")
    edge_type_distribution: Dict[str, int] = Field(default_factory=dict, description="Edge type distribution")
    top_central_nodes: List[str] = Field(default_factory=list, description="Top central nodes")
    graph_diameter: float = Field(default=0.0, description="Graph diameter")
    last_calculated: datetime = Field(default_factory=datetime.utcnow, description="Last calculated")


class GraphConfiguration(BaseModel):
    """Configuration settings for the fraud graph"""
    max_nodes: int = Field(default=10000, description="Maximum nodes")
    max_edges: int = Field(default=50000, description="Maximum edges")
    enable_community_detection: bool = Field(default=True, description="Enable community detection")
    enable_fraud_ring_detection: bool = Field(default=True, description="Enable fraud ring detection")
    risk_threshold: Decimal = Field(default=Decimal('0.7'), description="Risk threshold")
    update_frequency_minutes: int = Field(default=60, description="Update frequency in minutes")
    retention_days: int = Field(default=90, description="Data retention in days")


class FraudRing(BaseModel):
    """Represents a detected fraud ring"""
    id: str = Field(..., description="Fraud ring identifier")
    name: str = Field(..., description="Fraud ring name")
    description: str = Field(..., description="Fraud ring description")
    node_ids: List[str] = Field(default_factory=list, description="Node IDs in the ring")
    edge_ids: List[str] = Field(default_factory=list, description="Edge IDs in the ring")
    risk_score: Decimal = Field(default=Decimal('0'), description="Risk score")
    confidence: Decimal = Field(default=Decimal('0'), description="Detection confidence")
    ring_type: str = Field(default="", description="Ring type")
    detected_at: datetime = Field(default_factory=datetime.utcnow, description="Detection time")
    is_active: bool = Field(default=True, description="Is active")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class GraphCommunity(BaseModel):
    """Represents a community in the graph"""
    id: str = Field(..., description="Community identifier")
    name: str = Field(..., description="Community name")
    type: CommunityType = Field(..., description="Community type")
    node_ids: List[str] = Field(default_factory=list, description="Node IDs in community")
    size: int = Field(default=0, description="Community size")
    density: float = Field(default=0.0, description="Community density")
    risk_score: Decimal = Field(default=Decimal('0'), description="Risk score")
    detected_at: datetime = Field(default_factory=datetime.utcnow, description="Detection time")
    is_suspicious: bool = Field(default=False, description="Is suspicious")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class FraudRingResult(BaseModel):
    """Result of fraud ring detection"""
    id: str = Field(..., description="Result identifier")
    ring_id: str = Field(..., description="Fraud ring identifier")
    detection_method: str = Field(..., description="Detection method")
    confidence: Decimal = Field(..., description="Detection confidence")
    risk_score: Decimal = Field(..., description="Risk score")
    affected_nodes: List[str] = Field(default_factory=list, description="Affected nodes")
    affected_edges: List[str] = Field(default_factory=list, description="Affected edges")
    detection_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Detection time")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class GNNModelConfig(BaseModel):
    """GNN model configuration"""
    id: str = Field(..., description="Model identifier")
    name: str = Field(..., description="Model name")
    model_type: str = Field(..., description="Model type (GraphSAGE, GCN, etc.)")
    version: str = Field(default="1.0.0", description="Model version")
    status: str = Field(default="Trained", description="Model status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    last_updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    hyperparameters: Dict[str, Any] = Field(default_factory=dict, description="Model hyperparameters")
    performance: Dict[str, float] = Field(default_factory=dict, description="Model performance")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class GraphAnalysisResult(BaseModel):
    """Result of graph analysis"""
    analysis_id: str = Field(..., description="Analysis identifier")
    graph_id: str = Field(..., description="Graph identifier")
    analysis_type: str = Field(..., description="Analysis type")
    results: Dict[str, Any] = Field(default_factory=dict, description="Analysis results")
    fraud_rings: List[FraudRing] = Field(default_factory=list, description="Detected fraud rings")
    communities: List[GraphCommunity] = Field(default_factory=list, description="Detected communities")
    risk_assessment: Dict[str, Decimal] = Field(default_factory=dict, description="Risk assessment")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analysis time")
    processing_time_ms: float = Field(default=0.0, description="Processing time")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
