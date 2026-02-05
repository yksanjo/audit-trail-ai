"""Configuration management for Audit Trail AI."""
from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    app_name: str = "Audit Trail AI"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, alias="DEBUG")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    
    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    
    # Database
    database_url: str = Field(
        default="postgresql://audit:audit@localhost:5432/audit_trail",
        alias="DATABASE_URL"
    )
    database_pool_size: int = 20
    database_max_overflow: int = 10
    
    # Security
    secret_key: str = Field(default="change-me-in-production", alias="SECRET_KEY")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    api_key_header: str = "X-API-Key"
    
    # Blockchain
    ethereum_rpc_url: str = Field(
        default="http://localhost:8545",
        alias="ETHEREUM_RPC_URL"
    )
    blockchain_enabled: bool = Field(default=False, alias="BLOCKCHAIN_ENABLED")
    anchor_contract_address: Optional[str] = Field(
        default=None,
        alias="ANCHOR_CONTRACT_ADDRESS"
    )
    anchor_private_key: Optional[str] = Field(
        default=None,
        alias="ANCHOR_PRIVATE_KEY"
    )
    chain_id: int = Field(default=1, alias="CHAIN_ID")
    
    # Merkle Tree
    merkle_tree_depth: int = 32
    anchor_interval_minutes: int = 60
    
    # Encryption
    encryption_key: Optional[str] = Field(default=None, alias="ENCRYPTION_KEY")
    enable_encryption: bool = True
    
    # GDPR
    gdpr_deletion_retention_days: int = 30
    enable_gdpr_tombstones: bool = True
    
    # Audit Export
    export_format: str = "json"
    max_export_rows: int = 100000
    signed_exports: bool = True
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        alias="CORS_ORIGINS"
    )
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    structured_logging: bool = True
    
    # Compliance
    compliance_standards: List[str] = Field(
        default=["SOC2", "ISO27001", "GDPR"],
        alias="COMPLIANCE_STANDARDS"
    )
    retention_days: int = Field(default=2555, alias="RETENTION_DAYS")  # 7 years
    
    @property
    def database_async_url(self) -> str:
        """Get async database URL."""
        return self.database_url.replace(
            "postgresql://", "postgresql+asyncpg://"
        )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
