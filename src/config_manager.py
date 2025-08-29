import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging

try:
    import tomllib
except ImportError:
    import tomli as tomllib


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

        # Load project metadata from pyproject.toml
        self.project_metadata = self._load_project_metadata()

        # Default configuration structure
        self.default_config = {
            "project_info": {
                "name": self.project_metadata["name"],
                "version": self.project_metadata["version"],
                "description": self.project_metadata["description"]
            },
            "paths": {
                "project_root": str(self.project_root),
                "src_dir": str(self.project_root / "src"),
                "docs_dir": str(self.project_root / "docs"),
                "output_dir": str(self.project_root / "output"),
                "temp_dir": str(self.project_root / "temp")
            },
            "dependencies": {
                "topaz": {
                    "path": "/uufs/chpc.utah.edu/sys/installdir/r8/topaz/0.3.7/bin/topaz",
                    "version": "3.0.7",
                    "enabled": True
                },
                "model_angelo": {
                    "path": "/uufs/chpc.utah.edu/sys/installdir/model-angelo/1.0.1/bin/model_angelo",
                    "version": "1.0.1",
                    "enabled": True
                }
            },
            "settings": {
                "max_threads": 4,
                "memory_limit_gb": 16,
                "gpu_enabled": False,
                "debug_mode": False,
                "log_level": "INFO"
            },
            "slurm": {
                "job_name": "cryodl_job",
                "nodes": 1,
                "ntasks": 1,
                "cpus_per_task": 4,
                "gres_gpu": 1,
                "time": "06:00:00",
                "partition": "notchpeak-gpu",
                "qos": "notchpeak-gpu",
                "account": "notchpeak-gpu",
                "mem": "96G",
                "output": "slurm-%j.out-%N",
                "error": "slurm-%j.err-%N",
                "mail_type": "",
                "mail_user": "",
                "exclude": "",
                "dependency": "",
                "array": "",
                "comment": "SLURM job configuration for cryoDL workflows"
            }
        }

        # Load or create configuration
        self.config = self.load_config()

    def _load_project_metadata(self) -> Dict[str, Any]:
        """Load project metadata from pyproject.toml file.

        Reads the project name, version, and description from the pyproject.toml
        file located in the project root directory. If the file is not found or
        cannot be read, returns default values.

        Returns:
            Dict[str, Any]: Dictionary containing project metadata with keys:
                - name (str): Project name
                - version (str): Project version
                - description (str): Project description

        Example:
            >>> metadata = config_manager._load_project_metadata()
            >>> print(metadata['version'])
            '0.3.0'
        """
        pyproject_path = self.project_root / "pyproject.toml"

        if not pyproject_path.exists():
            self.logger.warning(f"pyproject.toml not found at {pyproject_path}")
            return {
                "name": "cryoDL",
                "version": "0.1.0",
                "description": "Python wrapper for cryo-EM software"
            }

        try:
            with open(pyproject_path, 'rb') as f:
                pyproject_data = tomllib.load(f)

            project_data = pyproject_data.get('project', {})

            metadata = {
                "name": project_data.get('name', 'cryoDL'),
                "version": project_data.get('version', '0.1.0'),
                "description": project_data.get('description', 'Python wrapper for cryo-EM software')
            }

            self.logger.info(f"Loaded project metadata from pyproject.toml: {metadata}")
            return metadata

        except Exception as e:
            self.logger.error(f"Error reading pyproject.toml: {e}")
            return {
                "name": "cryoDL",
                "version": "0.1.0",
                "description": "Python wrapper for cryo-EM software"
            }

    def get_project_metadata(self) -> Dict[str, Any]:
        """Get the current project metadata from pyproject.toml.

        Returns a copy of the project metadata that was loaded during initialization.
        This includes the project name, version, and description from pyproject.toml.

        Returns:
            Dict[str, Any]: Dictionary containing project metadata with keys:
                - name (str): Project name
                - version (str): Project version
                - description (str): Project description

        Example:
            >>> metadata = config_manager.get_project_metadata()
            >>> print(f"Version: {metadata['version']}")
            Version: 0.3.0
        """
        return self.project_metadata.copy()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default if not exists.

        Attempts to load the configuration from the config.json file. If the file
        doesn't exist or is corrupted, creates a new default configuration file.

        Returns:
            Dict[str, Any]: Dictionary containing the loaded or created configuration
                with sections for project_info, paths, dependencies, settings, and slurm.

        Example:
            >>> config = config_manager.load_config()
            >>> print(config['project_info']['version'])
            '0.3.0'
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
        """Create and save default configuration.

        Creates the necessary directories and saves a default configuration file
        with project metadata, paths, dependencies, settings, and SLURM configuration.

        Returns:
            Dict[str, Any]: Dictionary containing the default configuration structure
                with all required sections initialized.

        Example:
            >>> config = config_manager.create_default_config()
            >>> print(config['settings']['max_threads'])
            4
        """
        # Create necessary directories
        for path_key, path_value in self.default_config["paths"].items():
            if path_key != "project_root" and path_key != "src_dir" and path_key != "docs_dir":
                Path(path_value).mkdir(exist_ok=True)

        # Save default config
        self.save_config(self.default_config)
        return self.default_config

    def save_config(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Save configuration to file.

        Saves the configuration dictionary to the config.json file in JSON format
        with proper indentation. If no config is provided, saves the current
        configuration.

        Args:
            config (Optional[Dict[str, Any]]): Configuration dictionary to save.
                If None, saves the current configuration.

        Raises:
            IOError: If the file cannot be written to.

        Example:
            >>> config_manager.save_config()
            >>> # Or save a specific config
            >>> custom_config = {'settings': {'max_threads': 8}}
            >>> config_manager.save_config(custom_config)
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
        """Get configuration value using dot notation.

        Retrieves a configuration value using dot notation to access nested
        dictionary keys. If the key doesn't exist, returns the default value.

        Args:
            key (str): Configuration key in dot notation (e.g., 'paths.output_dir').
            default (Any): Default value to return if key is not found.

        Returns:
            Any: The configuration value if found, otherwise the default value.

        Example:
            >>> config_manager.get('settings.max_threads')
            4
            >>> config_manager.get('nonexistent.key', 'default')
            'default'
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
        """Set configuration value using dot notation.

        Sets a configuration value using dot notation to access nested dictionary
        keys. Creates intermediate dictionaries if they don't exist.

        Args:
            key (str): Configuration key in dot notation (e.g., 'settings.max_threads').
            value (Any): Value to set for the configuration key.

        Example:
            >>> config_manager.set('settings.max_threads', 8)
            >>> config_manager.set('new_section.new_key', 'new_value')
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
        """Update dependency path and version.

        Updates the path and version for a specified dependency in the configuration.
        If the dependency doesn't exist in the configuration, logs a warning.
        The dependency is automatically enabled if a path is provided.

        Args:
            dependency (str): Name of the dependency (e.g., 'topaz', 'model_angelo').
            path (str): Path to the dependency executable or directory.
            version (str, optional): Version of the dependency. Defaults to empty string.

        Example:
            >>> config_manager.update_dependency_path('topaz', '/usr/local/bin/topaz', '0.3.7')
            >>> config_manager.update_dependency_path('model_angelo', '/path/to/model_angelo')
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
        """Validate if a dependency path exists and is accessible.

        Checks if the specified dependency exists in the configuration and if its
        path points to an existing file or directory.

        Args:
            dependency (str): Name of the dependency to validate.

        Returns:
            bool: True if the dependency path exists and is accessible, False otherwise.

        Example:
            >>> config_manager.validate_dependency_path('topaz')
            True
            >>> config_manager.validate_dependency_path('nonexistent')
            False
        """
        if dependency not in self.config["dependencies"]:
            return False

        path = self.config["dependencies"][dependency]["path"]
        if not path:
            return False

        return Path(path).exists()

    def list_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """Get all configured dependencies.

        Returns a dictionary containing all dependencies configured in the system,
        including their paths, versions, and enabled status.

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary where keys are dependency names and
                values are dictionaries containing:
                - path (str): Path to the dependency
                - version (str): Version of the dependency
                - enabled (bool): Whether the dependency is enabled

        Example:
            >>> deps = config_manager.list_dependencies()
            >>> print(deps['topaz']['path'])
            '/usr/local/bin/topaz'
        """
        return self.config["dependencies"]

    def get_enabled_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """Get only enabled dependencies.

        Returns a filtered dictionary containing only the dependencies that are
        currently enabled in the configuration.

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary containing only enabled dependencies
                with their configuration details (path, version, enabled status).

        Example:
            >>> enabled_deps = config_manager.get_enabled_dependencies()
            >>> print(list(enabled_deps.keys()))
            ['topaz', 'model_angelo']
        """
        return {
            name: info for name, info in self.config["dependencies"].items()
            if info.get("enabled", False)
        }

    def reset_config(self) -> None:
        """Reset configuration to default values.

        Resets the current configuration to the default values and saves the
        changes to the configuration file. This will overwrite any custom
        settings that have been made.

        Example:
            >>> config_manager.reset_config()
            >>> # Configuration is now reset to defaults
        """
        self.config = self.default_config.copy()
        self.save_config()
        self.logger.info("Configuration reset to defaults")

    def export_config(self, export_path: Union[str, Path]) -> None:
        """Export configuration to a different location.

        Exports the current configuration to a specified file path in JSON format.
        This is useful for backing up configurations or sharing them between
        different environments.

        Args:
            export_path (Union[str, Path]): Path where to export the configuration file.

        Raises:
            IOError: If the file cannot be written to.

        Example:
            >>> config_manager.export_config('config_backup.json')
            >>> config_manager.export_config(Path('backups/config_2024.json'))
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
        """Import configuration from a file.

        Imports a configuration from a specified file path and replaces the current
        configuration. The imported configuration is then saved to the main
        configuration file.

        Args:
            import_path (Union[str, Path]): Path to the configuration file to import.

        Raises:
            IOError: If the file cannot be read.
            json.JSONDecodeError: If the file contains invalid JSON.

        Example:
            >>> config_manager.import_config('config_backup.json')
            >>> config_manager.import_config(Path('backups/config_2024.json'))
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

    def generate_slurm_header(self, job_name: Optional[str] = None, **kwargs) -> str:
        """Generate SLURM header from configuration.

        Generates a SLURM job script header using the current SLURM configuration
        settings. Allows overriding specific parameters for the job.

        Args:
            job_name (Optional[str]): Override job name if provided. If None, uses
                the default job name from configuration.
            **kwargs: Additional SLURM parameters to override. Valid parameters include:
                - nodes (int): Number of nodes
                - ntasks (int): Number of tasks
                - cpus_per_task (int): CPUs per task
                - gres_gpu (int): Number of GPUs
                - time (str): Time limit (HH:MM:SS)
                - partition (str): Partition name
                - qos (str): Quality of service
                - account (str): Account name
                - mem (str): Memory limit
                - output (str): Output file pattern
                - error (str): Error file pattern

        Returns:
            str: Complete SLURM header as a string with all directives.

        Example:
            >>> header = config_manager.generate_slurm_header('my_job', nodes=2, gres_gpu=2)
            >>> print(header)
            #!/bin/bash
            #SBATCH --job-name=my_job
            #SBATCH --nodes=2
            #SBATCH --gres=gpu:2
            ...
        """
        slurm_config = self.config.get("slurm", {}).copy()

        # Override with provided parameters
        if job_name:
            slurm_config["job_name"] = job_name

        for key, value in kwargs.items():
            if key in slurm_config:
                slurm_config[key] = value

        # Build SLURM header
        header_lines = ["#!/bin/bash"]

        # Add SLURM directives
        directives = [
            ("job-name", slurm_config.get("job_name", "cryodl_job")),
            ("nodes", slurm_config.get("nodes", 1)),
            ("ntasks", slurm_config.get("ntasks", 1)),
            ("cpus-per-task", slurm_config.get("cpus_per_task", 4)),
            ("gres", f"gpu:{slurm_config.get('gres_gpu', 1)}" if slurm_config.get("gres_gpu", 0) > 0 else None),
            ("time", slurm_config.get("time", "06:00:00")),
            ("partition", slurm_config.get("partition", "notchpeak-gpu")),
            ("qos", slurm_config.get("qos", "notchpeak-gpu")),
            ("account", slurm_config.get("account", "notchpeak-gpu")),
            ("mem", slurm_config.get("mem", "96G")),
            ("output", slurm_config.get("output", "slurm-%j.out-%N")),
            ("error", slurm_config.get("error", "slurm-%j.err-%N")),
        ]

        # Add optional directives
        optional_directives = [
            ("mail-type", slurm_config.get("mail_type")),
            ("mail-user", slurm_config.get("mail_user")),
            ("exclude", slurm_config.get("exclude")),
            ("dependency", slurm_config.get("dependency")),
            ("array", slurm_config.get("array")),
        ]

        # Add required directives
        for directive, value in directives:
            if value is not None:
                header_lines.append(f"#SBATCH --{directive}={value}")

        # Add optional directives (only if they have values)
        for directive, value in optional_directives:
            if value:
                header_lines.append(f"#SBATCH --{directive}={value}")

        # Add comment if provided
        comment = slurm_config.get("comment", "")
        if comment:
            header_lines.append(f"# {comment}")

        return "\n".join(header_lines)

    def update_slurm_config(self, **kwargs) -> None:
        """Update SLURM configuration parameters.

        Updates the SLURM configuration section with new parameter values and
        saves the changes to the configuration file.

        Args:
            **kwargs: SLURM parameters to update. Valid parameters include:
                - job_name (str): Default job name
                - nodes (int): Number of nodes
                - ntasks (int): Number of tasks
                - cpus_per_task (int): CPUs per task
                - gres_gpu (int): Number of GPUs
                - time (str): Time limit (HH:MM:SS)
                - partition (str): Partition name
                - qos (str): Quality of service
                - account (str): Account name
                - mem (str): Memory limit
                - output (str): Output file pattern
                - error (str): Error file pattern
                - mail_type (str): Mail notification type
                - mail_user (str): Mail notification user
                - exclude (str): Nodes to exclude
                - dependency (str): Job dependencies
                - array (str): Array job specification
                - comment (str): Comment for the configuration

        Example:
            >>> config_manager.update_slurm_config(nodes=2, gres_gpu=2, time='12:00:00')
            >>> config_manager.update_slurm_config(partition='gpu', account='my_account')
        """
        if "slurm" not in self.config:
            self.config["slurm"] = {}

        for key, value in kwargs.items():
            self.config["slurm"][key] = value

        self.save_config()
        self.logger.info(f"Updated SLURM configuration: {list(kwargs.keys())}")

    def get_slurm_config(self) -> Dict[str, Any]:
        """Get current SLURM configuration.

        Returns the current SLURM configuration dictionary containing all
        SLURM-related settings.

        Returns:
            Dict[str, Any]: Dictionary containing all SLURM configuration parameters
                including job_name, nodes, ntasks, cpus_per_task, gres_gpu, time,
                partition, qos, account, mem, output, error, and other SLURM settings.

        Example:
            >>> slurm_config = config_manager.get_slurm_config()
            >>> print(slurm_config['nodes'])
            1
            >>> print(slurm_config['time'])
            '06:00:00'
        """
        return self.config.get("slurm", {})

    def save_slurm_header(self, output_path: Union[str, Path], job_name: Optional[str] = None, **kwargs) -> None:
        """Save SLURM header to a file.

        Generates a SLURM header using the current configuration and saves it to
        a specified file path. This is useful for creating SLURM job scripts.

        Args:
            output_path (Union[str, Path]): Path where to save the SLURM header file.
            job_name (Optional[str]): Override job name if provided. If None, uses
                the default job name from configuration.
            **kwargs: Additional SLURM parameters to override. See generate_slurm_header
                for valid parameters.

        Raises:
            IOError: If the file cannot be written to.

        Example:
            >>> config_manager.save_slurm_header('my_job.slurm', 'my_job', nodes=2)
            >>> config_manager.save_slurm_header(Path('jobs/batch_job.slurm'))
        """
        output_path = Path(output_path)
        header_content = self.generate_slurm_header(job_name, **kwargs)

        try:
            with open(output_path, 'w') as f:
                f.write(header_content)
            self.logger.info(f"SLURM header saved to {output_path}")
        except IOError as e:
            self.logger.error(f"Error saving SLURM header: {e}")
            raise


def main():
    """Example usage of the ConfigManager.

    Demonstrates basic usage of the ConfigManager class including setting
    configuration values, updating dependency paths, and validating dependencies.

    Example:
        >>> python config_manager.py
        Project root: /path/to/project
        Max threads: 8
        Enabled dependencies: ['topaz', 'model_angelo']
        topaz path valid: True
        model_angelo path valid: False
    """
    # Initialize config manager
    config_manager = ConfigManager()

    # Example: Set some configuration values
    config_manager.set("settings.max_threads", 8)
    config_manager.set("settings.gpu_enabled", True)

    # Example: Update dependency paths
    config_manager.update_dependency_path("topaz", "/path/to/topaz", "0.2.5")
    config_manager.update_dependency_path("model_angelo", "/path/to/model_angelo", "1.0.0")

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
