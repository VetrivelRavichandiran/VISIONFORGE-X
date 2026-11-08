"""Application settings and configuration management for VISIONFORGE X."""
import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class DeviceConfig:
    """Device connection configuration."""
    mode: str = "simulation"  # simulation | hardware
    board_ip: str = "192.168.1.100"
    tcp_port: int = 5000
    udp_port: int = 5001
    comm_timeout: float = 5.0
    heartbeat_timeout: float = 10.0
    reconnect_enabled: bool = True
    reconnect_delay: float = 2.0


@dataclass
class CameraConfig:
    """Camera configuration."""
    preview_resolution: str = "640x480"
    target_fps: int = 30
    processing_mode: str = "balanced"  # quality | balanced | performance
    source: str = "simulation"  # simulation | webcam | file
    source_path: str = ""


@dataclass
class AIConfig:
    """AI model configuration."""
    model_path: str = ""
    model_type: str = "classification"  # classification | detection | anomaly
    confidence_threshold: float = 0.5
    inference_interval: int = 1  # run every N frames
    device: str = "cpu"  # cpu | cuda


@dataclass
class StorageConfig:
    """Storage configuration."""
    base_path: str = "./storage"
    dataset_path: str = "./datasets"
    log_path: str = "./logs"
    db_path: str = "./storage/visionforge.db"
    data_retention_days: int = 90


@dataclass
class ThemeConfig:
    """Theme configuration."""
    name: str = "Dark Industrial"
    accent_color: str = "#00E5FF"
    warning_color: str = "#FFB300"
    error_color: str = "#FF1744"
    success_color: str = "#00E676"


@dataclass
class AppConfig:
    """Main application configuration."""
    device: DeviceConfig = field(default_factory=DeviceConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    theme: ThemeConfig = field(default_factory=ThemeConfig)
    adaptive_enabled: bool = True
    overlays_enabled: bool = True
    last_window_geometry: str = ""
    last_window_state: str = ""


class SettingsManager:
    """Manages application settings with file persistence."""

    DEFAULT_CONFIG_PATH = "config/app_config.json"

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = AppConfig()

    def load(self) -> AppConfig:
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                self._apply_dict(data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config: {e}")
        return self.config

    def save(self) -> bool:
        """Save configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(asdict(self.config), f, indent=2)
            return True
        except (IOError, OSError) as e:
            print(f"Error saving config: {e}")
            return False

    def _apply_dict(self, data: dict):
        """Apply dictionary data to config."""
        if 'device' in data:
            for k, v in data['device'].items():
                if hasattr(self.config.device, k):
                    setattr(self.config.device, k, v)
        if 'camera' in data:
            for k, v in data['camera'].items():
                if hasattr(self.config.camera, k):
                    setattr(self.config.camera, k, v)
        if 'ai' in data:
            for k, v in data['ai'].items():
                if hasattr(self.config.ai, k):
                    setattr(self.config.ai, k, v)
        if 'storage' in data:
            for k, v in data['storage'].items():
                if hasattr(self.config.storage, k):
                    setattr(self.config.storage, k, v)
        if 'theme' in data:
            for k, v in data['theme'].items():
                if hasattr(self.config.theme, k):
                    setattr(self.config.theme, k, v)
        for k in ['adaptive_enabled', 'overlays_enabled', 'last_window_geometry', 'last_window_state']:
            if k in data:
                setattr(self.config, k, data[k])

    def export(self, path: str) -> bool:
        """Export configuration to specified path."""
        try:
            with open(path, 'w') as f:
                json.dump(asdict(self.config), f, indent=2)
            return True
        except (IOError, OSError):
            return False

    def import_config(self, path: str) -> bool:
        """Import configuration from specified path."""
        if not os.path.exists(path):
            return False
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            self._apply_dict(data)
            return True
        except (json.JSONDecodeError, IOError):
            return False

    def reset(self):
        """Reset to default configuration."""
        self.config = AppConfig()
