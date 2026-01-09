"""
Data Stream Models for Fraud Detection Agent

This module contains Pydantic models for data stream analysis and fraud detection,
mirroring the C# DataStreamModels.cs functionality.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class DataType(str, Enum):
    """Represents different types of data streams that can be analyzed for fraud"""
    UNKNOWN = "unknown"
    JSON = "json"
    XML = "xml"
    FORM_DATA = "form_data"
    MULTIPART_FORM = "multipart_form"
    QUERY_STRING = "query_string"
    TEXT = "text"
    BINARY = "binary"


class DataStream(BaseModel):
    """Represents a data stream captured from HTTP requests for fraud analysis"""
    id: str = Field(default="", description="Unique identifier for the data stream")
    type: DataType = Field(default=DataType.UNKNOWN, description="Type of data stream")
    content: str = Field(default="", description="Content of the data stream")
    headers: Dict[str, str] = Field(default_factory=dict, description="HTTP headers")
    method: str = Field(default="", description="HTTP method")
    path: str = Field(default="", description="Request path")
    query_string: str = Field(default="", description="Query string parameters")
    content_type: str = Field(default="", description="Content type")
    user_agent: str = Field(default="", description="User agent string")
    remote_ip_address: str = Field(default="", description="Remote IP address")
    user_id: Optional[str] = Field(default=None, description="User ID if available")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when stream was captured")


class FraudAnalysis(BaseModel):
    """Data stream fraud analysis result for comprehensive monitoring"""
    risk_score: Decimal = Field(default=Decimal('0.0'), description="Risk score (0.0-1.0)")
    is_suspicious: bool = Field(default=False, description="Whether the stream is suspicious")
    risk_factors: List[str] = Field(default_factory=list, description="List of risk factors")
    analysis_type: str = Field(default="", description="Type of analysis performed")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow, description="When analysis was performed")
    confidence_level: str = Field(default="Medium", description="Confidence level of analysis")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AppMessage(BaseModel):
    """Complete message containing data stream and fraud analysis for centralized collection"""
    data_stream: DataStream = Field(default_factory=DataStream, description="Data stream information")
    fraud_analysis: FraudAnalysis = Field(default_factory=FraudAnalysis, description="Fraud analysis result")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    source: str = Field(default="", description="Source of the message")
    correlation_id: Optional[str] = Field(default=None, description="Correlation ID for tracking")


class DataStreamSettings(BaseModel):
    """Configuration settings for data stream fraud detection"""
    enable_real_time_analysis: bool = Field(default=True, description="Enable real-time analysis")
    suspicious_threshold: Decimal = Field(default=Decimal('0.7'), description="Threshold for suspicious activity")
    max_content_length: int = Field(default=10000, description="Maximum content length to analyze")
    buffer_size: int = Field(default=100, description="Buffer size for processing")
    flush_interval_minutes: int = Field(default=5, description="Flush interval in minutes")
    excluded_paths: List[str] = Field(default_factory=lambda: ["/health", "/swagger"], description="Paths to exclude from analysis")
    analyze_binary_content: bool = Field(default=False, description="Whether to analyze binary content")


class DataStreamStats(BaseModel):
    """Statistics for data stream monitoring"""
    total_streams_analyzed: int = Field(default=0, description="Total number of streams analyzed")
    suspicious_streams: int = Field(default=0, description="Number of suspicious streams")
    data_type_breakdown: Dict[str, int] = Field(default_factory=dict, description="Breakdown by data type")
    average_risk_score: float = Field(default=0.0, description="Average risk score")
    last_analysis_time: datetime = Field(default_factory=datetime.utcnow, description="Last analysis time")
    monitoring_duration_hours: float = Field(default=0.0, description="Monitoring duration in hours")


class DataStreamAnalysisRequest(BaseModel):
    """Request to analyze a data stream"""
    data_stream: DataStream = Field(description="Data stream to analyze")
    analysis_settings: Optional[DataStreamSettings] = Field(default=None, description="Analysis settings")
    user_context: Optional[Dict[str, Any]] = Field(default=None, description="User context information")


class DataStreamAnalysisResponse(BaseModel):
    """Response from data stream analysis"""
    success: bool = Field(description="Whether analysis was successful")
    fraud_analysis: FraudAnalysis = Field(description="Fraud analysis result")
    processing_time_ms: float = Field(description="Processing time in milliseconds")
    warnings: List[str] = Field(default_factory=list, description="Any warnings during analysis")
    errors: List[str] = Field(default_factory=list, description="Any errors during analysis")


class DataStreamBatchRequest(BaseModel):
    """Request to analyze multiple data streams in batch"""
    data_streams: List[DataStream] = Field(description="List of data streams to analyze")
    analysis_settings: Optional[DataStreamSettings] = Field(default=None, description="Analysis settings")
    batch_id: Optional[str] = Field(default=None, description="Batch identifier")


class DataStreamBatchResponse(BaseModel):
    """Response from batch data stream analysis"""
    success: bool = Field(description="Whether batch analysis was successful")
    batch_id: str = Field(description="Batch identifier")
    total_streams: int = Field(description="Total number of streams processed")
    successful_analyses: int = Field(description="Number of successful analyses")
    failed_analyses: int = Field(description="Number of failed analyses")
    analyses: List[DataStreamAnalysisResponse] = Field(description="Individual analysis results")
    processing_time_ms: float = Field(description="Total processing time in milliseconds")
    warnings: List[str] = Field(default_factory=list, description="Any warnings during batch analysis")
    errors: List[str] = Field(default_factory=list, description="Any errors during batch analysis")
