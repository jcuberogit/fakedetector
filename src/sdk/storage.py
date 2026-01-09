"""
Universal Fraud Detection SDK Storage Service
Python implementation of secure storage operations
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
import os
import tempfile
from pathlib import Path

from .models import UserInfo, DeviceInfo
from .interfaces import IStorage


class SecureStorageService(IStorage):
    """Secure storage service implementation using file system with encryption"""
    
    def __init__(
        self,
        storage_path: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.logger = logger or logging.getLogger(__name__)
        self.storage_path = Path(storage_path) if storage_path else Path(tempfile.gettempdir()) / "fraud_sdk_storage"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._known_keys: set = set()
        self._load_known_keys()
    
    def _load_known_keys(self):
        """Load known keys from storage directory"""
        try:
            if self.storage_path.exists():
                for file_path in self.storage_path.iterdir():
                    if file_path.is_file():
                        self._known_keys.add(file_path.stem)
        except Exception as ex:
            self.logger.warning(f"Failed to load known keys: {ex}")
    
    def _get_file_path(self, key: str) -> Path:
        """Get file path for a key"""
        # Sanitize key to prevent directory traversal
        safe_key = "".join(c for c in key if c.isalnum() or c in "._-")
        return self.storage_path / f"{safe_key}.json"
    
    async def set_async(self, key: str, value: str) -> None:
        """Store a value securely"""
        if not key.strip():
            raise ValueError("Key cannot be null or empty")
        
        if value is None:
            raise ValueError("Value cannot be null")
        
        try:
            file_path = self._get_file_path(key)
            
            # Encrypt the value (simple base64 encoding for demo)
            import base64
            encrypted_value = base64.b64encode(value.encode('utf-8')).decode('utf-8')
            
            # Store with metadata
            data = {
                "value": encrypted_value,
                "timestamp": asyncio.get_event_loop().time(),
                "key": key
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f)
            
            self._known_keys.add(key)
            self.logger.debug(f"Successfully stored value for key: {key}")
        
        except Exception as ex:
            self.logger.error(f"Failed to store value for key: {key}: {ex}")
            raise
    
    async def get_async(self, key: str) -> Optional[str]:
        """Retrieve a value from secure storage"""
        if not key.strip():
            raise ValueError("Key cannot be null or empty")
        
        try:
            file_path = self._get_file_path(key)
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Decrypt the value
            import base64
            encrypted_value = data.get("value", "")
            decrypted_value = base64.b64decode(encrypted_value.encode('utf-8')).decode('utf-8')
            
            self.logger.debug(f"Retrieved value for key: {key}")
            return decrypted_value
        
        except Exception as ex:
            self.logger.error(f"Failed to retrieve value for key: {key}: {ex}")
            raise
    
    async def remove_async(self, key: str) -> bool:
        """Remove a value from secure storage"""
        if not key.strip():
            raise ValueError("Key cannot be null or empty")
        
        try:
            file_path = self._get_file_path(key)
            
            if file_path.exists():
                file_path.unlink()
                self._known_keys.discard(key)
                self.logger.debug(f"Removed key: {key}")
                return True
            
            return False
        
        except Exception as ex:
            self.logger.error(f"Failed to remove key: {key}: {ex}")
            raise
    
    async def remove_all_async(self) -> None:
        """Remove all values from secure storage"""
        try:
            for key in list(self._known_keys):
                await self.remove_async(key)
            
            self.logger.info("Cleared all secure storage")
        
        except Exception as ex:
            self.logger.error(f"Failed to clear all secure storage: {ex}")
            raise
    
    async def has_key_async(self, key: str) -> bool:
        """Check if a key exists in secure storage"""
        if not key.strip():
            raise ValueError("Key cannot be null or empty")
        
        try:
            file_path = self._get_file_path(key)
            return file_path.exists()
        
        except Exception as ex:
            self.logger.error(f"Failed to check key existence: {key}: {ex}")
            return False
    
    async def get_all_keys_async(self) -> List[str]:
        """Get all keys in secure storage"""
        return list(self._known_keys)
    
    async def set_token_async(self, token_type: str, token: str) -> None:
        """Store authentication token"""
        if not token_type.strip():
            raise ValueError("Token type cannot be null or empty")
        
        if not token:
            raise ValueError("Token cannot be null")
        
        try:
            await self.set_async(token_type, token)
            self.logger.info(f"Stored token of type: {token_type}")
        
        except Exception as ex:
            self.logger.error(f"Failed to store token of type: {token_type}: {ex}")
            raise
    
    async def get_token_async(self, token_type: str) -> Optional[str]:
        """Retrieve authentication token"""
        if not token_type.strip():
            raise ValueError("Token type cannot be null or empty")
        
        try:
            token = await self.get_async(token_type)
            self.logger.debug(f"Retrieved token of type: {token_type} (exists: {token is not None})")
            return token
        
        except Exception as ex:
            self.logger.error(f"Failed to retrieve token of type: {token_type}: {ex}")
            raise
    
    async def remove_token_async(self, token_type: str) -> bool:
        """Remove authentication token"""
        if not token_type.strip():
            raise ValueError("Token type cannot be null or empty")
        
        try:
            removed = await self.remove_async(token_type)
            self.logger.info(f"Removed token of type: {token_type} (success: {removed})")
            return removed
        
        except Exception as ex:
            self.logger.error(f"Failed to remove token of type: {token_type}: {ex}")
            raise
    
    async def set_user_info_async(self, user_info: UserInfo) -> None:
        """Store user information"""
        if not user_info:
            raise ValueError("User info cannot be null")
        
        try:
            json_data = user_info.json(by_alias=True)
            await self.set_async("user_info", json_data)
            self.logger.info(f"Stored user info for user: {user_info.user_id}")
        
        except Exception as ex:
            self.logger.error(f"Failed to store user info: {ex}")
            raise
    
    async def get_user_info_async(self) -> Optional[UserInfo]:
        """Retrieve user information"""
        try:
            json_data = await self.get_async("user_info")
            if not json_data:
                return None
            
            user_info = UserInfo.parse_raw(json_data)
            self.logger.debug("Retrieved user info")
            return user_info
        
        except json.JSONDecodeError as ex:
            self.logger.error(f"Failed to deserialize user info - invalid JSON: {ex}")
            return None
        except Exception as ex:
            self.logger.error(f"Failed to retrieve user info: {ex}")
            raise
    
    async def set_device_info_async(self, device_info: DeviceInfo) -> None:
        """Store device information"""
        if not device_info:
            raise ValueError("Device info cannot be null")
        
        try:
            json_data = device_info.json(by_alias=True)
            await self.set_async("device_info", json_data)
            self.logger.info(f"Stored device info for device: {device_info.device_id}")
        
        except Exception as ex:
            self.logger.error(f"Failed to store device info: {ex}")
            raise
    
    async def get_device_info_async(self) -> Optional[DeviceInfo]:
        """Retrieve device information"""
        try:
            json_data = await self.get_async("device_info")
            if not json_data:
                return None
            
            device_info = DeviceInfo.parse_raw(json_data)
            self.logger.debug("Retrieved device info")
            return device_info
        
        except json.JSONDecodeError as ex:
            self.logger.error(f"Failed to deserialize device info - invalid JSON: {ex}")
            return None
        except Exception as ex:
            self.logger.error(f"Failed to retrieve device info: {ex}")
            raise


class MockStorageService(IStorage):
    """Mock storage service for testing"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._storage: Dict[str, str] = {}
        self._user_info: Optional[UserInfo] = None
        self._device_info: Optional[DeviceInfo] = None
    
    async def set_async(self, key: str, value: str) -> None:
        """Mock store value"""
        self._storage[key] = value
    
    async def get_async(self, key: str) -> Optional[str]:
        """Mock retrieve value"""
        return self._storage.get(key)
    
    async def remove_async(self, key: str) -> bool:
        """Mock remove value"""
        if key in self._storage:
            del self._storage[key]
            return True
        return False
    
    async def remove_all_async(self) -> None:
        """Mock remove all values"""
        self._storage.clear()
        self._user_info = None
        self._device_info = None
    
    async def has_key_async(self, key: str) -> bool:
        """Mock check key existence"""
        return key in self._storage
    
    async def get_all_keys_async(self) -> List[str]:
        """Mock get all keys"""
        return list(self._storage.keys())
    
    async def set_token_async(self, token_type: str, token: str) -> None:
        """Mock store token"""
        await self.set_async(token_type, token)
    
    async def get_token_async(self, token_type: str) -> Optional[str]:
        """Mock retrieve token"""
        return await self.get_async(token_type)
    
    async def remove_token_async(self, token_type: str) -> bool:
        """Mock remove token"""
        return await self.remove_async(token_type)
    
    async def set_user_info_async(self, user_info: UserInfo) -> None:
        """Mock store user info"""
        self._user_info = user_info
    
    async def get_user_info_async(self) -> Optional[UserInfo]:
        """Mock retrieve user info"""
        return self._user_info
    
    async def set_device_info_async(self, device_info: DeviceInfo) -> None:
        """Mock store device info"""
        self._device_info = device_info
    
    async def get_device_info_async(self) -> Optional[DeviceInfo]:
        """Mock retrieve device info"""
        return self._device_info


class InMemoryStorageService(IStorage):
    """In-memory storage service for development/testing"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._storage: Dict[str, str] = {}
        self._user_info: Optional[UserInfo] = None
        self._device_info: Optional[DeviceInfo] = None
    
    async def set_async(self, key: str, value: str) -> None:
        """Store value in memory"""
        self._storage[key] = value
        self.logger.debug(f"Stored value for key: {key}")
    
    async def get_async(self, key: str) -> Optional[str]:
        """Retrieve value from memory"""
        value = self._storage.get(key)
        self.logger.debug(f"Retrieved value for key: {key} (exists: {value is not None})")
        return value
    
    async def remove_async(self, key: str) -> bool:
        """Remove value from memory"""
        if key in self._storage:
            del self._storage[key]
            self.logger.debug(f"Removed key: {key}")
            return True
        return False
    
    async def remove_all_async(self) -> None:
        """Remove all values from memory"""
        self._storage.clear()
        self._user_info = None
        self._device_info = None
        self.logger.info("Cleared all in-memory storage")
    
    async def has_key_async(self, key: str) -> bool:
        """Check if key exists in memory"""
        return key in self._storage
    
    async def get_all_keys_async(self) -> List[str]:
        """Get all keys in memory"""
        return list(self._storage.keys())
    
    async def set_token_async(self, token_type: str, token: str) -> None:
        """Store token in memory"""
        await self.set_async(token_type, token)
        self.logger.info(f"Stored token of type: {token_type}")
    
    async def get_token_async(self, token_type: str) -> Optional[str]:
        """Retrieve token from memory"""
        token = await self.get_async(token_type)
        self.logger.debug(f"Retrieved token of type: {token_type} (exists: {token is not None})")
        return token
    
    async def remove_token_async(self, token_type: str) -> bool:
        """Remove token from memory"""
        removed = await self.remove_async(token_type)
        self.logger.info(f"Removed token of type: {token_type} (success: {removed})")
        return removed
    
    async def set_user_info_async(self, user_info: UserInfo) -> None:
        """Store user info in memory"""
        self._user_info = user_info
        self.logger.info(f"Stored user info for user: {user_info.user_id}")
    
    async def get_user_info_async(self) -> Optional[UserInfo]:
        """Retrieve user info from memory"""
        self.logger.debug("Retrieved user info")
        return self._user_info
    
    async def set_device_info_async(self, device_info: DeviceInfo) -> None:
        """Store device info in memory"""
        self._device_info = device_info
        self.logger.info(f"Stored device info for device: {device_info.device_id}")
    
    async def get_device_info_async(self) -> Optional[DeviceInfo]:
        """Retrieve device info from memory"""
        self.logger.debug("Retrieved device info")
        return self._device_info
