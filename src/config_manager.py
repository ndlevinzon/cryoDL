import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging


class ConfigManager:
    """
    Configuration manager for cryoDL project.
    Handles creation, reading, and updating of config.json with global variables
    and dependency paths.
    """

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialize the configuration manager.

        Args:
            config_path: Path to config.json file. If None, uses default location.
        """
        self.project_root = Path(__file__).parent.parent
        self.config_path = Path(config_path) if config_path else self.project_root / "config.json"

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Default configuration structure
        self.default_config = {
            "project_info": {
                "name": "cryoDL",
                "version": "0.1.0",
                "description": "Python wrapper for cryo-EM software"
            },
            "paths": {
                "project_root": str(self.project_root),
                "src_dir": str(self.project_root / "src"),
                "docs_dir": str(self.project_root / "docs"),
                "output_dir": str(self.project_root / "output"),
                "temp_dir": str(self.project_root / "temp")
            },
            "dependencies": {
                "relion": {
                    "path": "",
                    "version": "",
                    "enabled": False
                },
                "cryosparc": {
                    "path": "",
                    "version": "",
                    "enabled": False
                },
                "eman2": {
                    "path": "",
                    "version": "",
                    "enabled": False
                },
                "cisTEM": {
                    "path": "",
                    "version": "",
                    "enabled": False
                }
            },
            "settings": {
                "max_threads": 4,
                "memory_limit_gb": 16,
                "gpu_enabled": False,
                "debug_mode": False,
                "log_level": "INFO"
            },
            "api_keys": {
                "cryosparc_license": "",
                "relion_license": ""
            }
        }

        # Load or create configuration
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or create default if not exists.

        Returns:
            Dictionary containing configuration
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                self.logger.info(f"Configuration loaded from {self.config_path}")
                return config
            except (json.JSONDecodeError, IOError) as e:
                self.logger.warning(f"Error loading config: {e}. Creating new config.")
                return self.create_default_config()
        else:
            self.logger.info("Config file not found. Creating default configuration.")
            return self.create_default_config()

    def create_default_config(self) -> Dict[str, Any]:
        """
        Create and save default configuration.

        Returns:
            Dictionary containing default configuration
        """
        # Create necessary directories
        for path_key, path_value in self.default_config["paths"].items():
            if path_key != "project_root" and path_key != "src_dir" and path_key != "docs_dir":
                Path(path_value).mkdir(exist_ok=True)

        # Save default config
        self.save_config(self.default_config)
        return self.default_config

    def save_config(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Save configuration to file.

        Args:
            config: Configuration to save. If None, saves current config.
        """
        if config is None:
            config = self.config

        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4, sort_keys=True)
            self.logger.info(f"Configuration saved to {self.config_path}")
        except IOError as e:
            self.logger.error(f"Error saving config: {e}")
            raise

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation (e.g., 'paths.output_dir').

        Args:
            key: Configuration key in dot notation
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.

        Args:
            key: Configuration key in dot notation
            value: Value to set
        """
        keys = key.split('.')
        config = self.config

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value
        self.logger.info(f"Set config key '{key}' to '{value}'")

    def update_dependency_path(self, dependency: str, path: str, version: str = "") -> None:
        """
        Update dependency path and version.

        Args:
            dependency: Name of the dependency (e.g., 'relion', 'cryosparc')
            path: Path to the dependency executable or directory
            version: Version of the dependency
        """
        if dependency not in self.config["dependencies"]:
            self.logger.warning(f"Unknown dependency: {dependency}")
            return

        self.config["dependencies"][dependency]["path"] = path
        self.config["dependencies"][dependency]["version"] = version
        self.config["dependencies"][dependency]["enabled"] = bool(path)

        self.save_config()
        self.logger.info(f"Updated {dependency} path: {path}")

    def validate_dependency_path(self, dependency: str) -> bool:
        """
        Validate if a dependency path exists and is accessible.

        Args:
            dependency: Name of the dependency

        Returns:
            True if path is valid, False otherwise
        """
        if dependency not in self.config["dependencies"]:
            return False

        path = self.config["dependencies"][dependency]["path"]
        if not path:
            return False

        return Path(path).exists()

    def list_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all configured dependencies.

        Returns:
            Dictionary of dependencies with their paths and status
        """
        return self.config["dependencies"]

    def get_enabled_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """
        Get only enabled dependencies.

        Returns:
            Dictionary of enabled dependencies
        """
        return {
            name: info for name, info in self.config["dependencies"].items()
            if info.get("enabled", False)
        }

    def reset_config(self) -> None:
        """
        Reset configuration to default values.
        """
        self.config = self.default_config.copy()
        self.save_config()
        self.logger.info("Configuration reset to defaults")

    def export_config(self, export_path: Union[str, Path]) -> None:
        """
        Export configuration to a different location.

        Args:
            export_path: Path where to export the configuration
        """
        export_path = Path(export_path)
        try:
            with open(export_path, 'w') as f:
                json.dump(self.config, f, indent=4, sort_keys=True)
            self.logger.info(f"Configuration exported to {export_path}")
        except IOError as e:
            self.logger.error(f"Error exporting config: {e}")
            raise

    def import_config(self, import_path: Union[str, Path]) -> None:
        """
        Import configuration from a file.

        Args:
            import_path: Path to the configuration file to import
        """
        import_path = Path(import_path)
        try:
            with open(import_path, 'r') as f:
                new_config = json.load(f)
            self.config = new_config
            self.save_config()
            self.logger.info(f"Configuration imported from {import_path}")
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Error importing config: {e}")
            raise


def main():
    """
    Example usage of the ConfigManager.
    """
    # Initialize config manager
    config_manager = ConfigManager()

    # Example: Set some configuration values
    config_manager.set("settings.max_threads", 8)
    config_manager.set("settings.gpu_enabled", True)

    # Example: Update dependency paths
    config_manager.update_dependency_path("relion", "/usr/local/relion/bin/relion", "4.0")
    config_manager.update_dependency_path("cryosparc", "/opt/cryosparc", "4.0.0")

    # Example: Get configuration values
    print(f"Project root: {config_manager.get('paths.project_root')}")
    print(f"Max threads: {config_manager.get('settings.max_threads')}")
    print(f"Enabled dependencies: {list(config_manager.get_enabled_dependencies().keys())}")

    # Example: Validate dependency paths
    for dep_name in config_manager.config["dependencies"]:
        is_valid = config_manager.validate_dependency_path(dep_name)
        print(f"{dep_name} path valid: {is_valid}")


if __name__ == "__main__":
    main()
