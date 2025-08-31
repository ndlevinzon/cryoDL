#!/usr/bin/env python3
"""
Interactive CLI shell for cryoDL configuration manager.
"""

import argparse
import cmd
import datetime
import logging
import subprocess
import os
import sys
import traceback
from pathlib import Path
from typing import List, Optional

from .config_manager import ConfigManager


class CryoDLShell(cmd.Cmd):
    """Interactive shell for cryoDL configuration management.

    A command-line interface that provides an interactive environment for managing
    cryoDL configuration, dependencies, and running cryo-EM software workflows.
    Supports both local execution and SLURM job submission for computational tasks.

    Attributes:
        prompt (str): The command prompt displayed to users.
        config_manager (ConfigManager): The configuration manager instance.
        log_file (str): Path to the log file for recording all interactions.
        logger (logging.Logger): Logger instance for recording commands and outputs.
    """

    prompt = "cryoDL> "

    def __init__(self, config_manager: ConfigManager, log_file: str = "cryodl.log"):
        """Initialize the CryoDLShell.

        Sets up the interactive shell with configuration management, logging,
        and displays the ASCII banner with version information.

        Args:
            config_manager (ConfigManager): The configuration manager instance
                to use for managing settings and dependencies.
            log_file (str, optional): Path to the log file for recording all
                interactions. Defaults to "cryodl.log".

        Example:
            config_manager = ConfigManager()
            shell = CryoDLShell(config_manager, "my_session.log")
        """
        super().__init__()
        self.config_manager = config_manager
        self.log_file = log_file
        self.setup_logging()
        self.intro = self.load_banner()

    def load_banner(self):
        """Load and return the ASCII banner.

        Loads the ASCII art banner from the resources directory and combines it
        with version information from the configuration manager. If the banner
        file is not found, returns a simple text banner.

        Returns:
            str: The formatted banner string with version information and
                instructions for using the CLI.

        Example:
            banner = shell.load_banner()
            print(banner)
            [ASCII art banner with version info]
        """
        # Get version info from config manager
        metadata = self.config_manager.get_project_metadata()
        version_info = f"Version {metadata['version']}"
        try:
            banner_path = Path(__file__).parent / "resources" / "big_ascii_banner.txt"
            if banner_path.exists():
                with open(banner_path, "r", encoding="utf-8") as f:
                    banner = f.read().strip()
                return f"""
{banner}
{version_info}

Type 'help' for available commands, 'quit' to exit.
All interactions are logged to {self.log_file} in the current directory.
"""
            else:
                return """
=== cryoDL Interactive Configuration Manager ===
Type 'help' for available commands, 'quit' to exit.
All interactions are logged to cryodl.log in the current directory.
"""
        except Exception:
            return """
=== cryoDL Interactive Configuration Manager ===
Type 'help' for available commands, 'quit' to exit.
All interactions are logged to cryodl.log in the current directory.
"""

    def setup_logging(self):
        """Set up logging to file.

        Configures logging to write all commands, outputs, and errors to a log file.
        Uses a custom formatter with timestamps and creates a file handler that
        appends to the log file.

        Example:
            shell.setup_logging()
            # All subsequent commands will be logged to the log file
        """
        # Create a custom formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Set up file handler
        file_handler = logging.FileHandler(self.log_file, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        # Set up logger
        self.logger = logging.getLogger("cryodl_interactive")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)

        # Log session start
        self.logger.info("=== cryoDL Interactive Session Started ===")
        self.logger.info(f"Working directory: {os.getcwd()}")

    def log_command(self, command: str, args: str = ""):
        """Log user command.

        Records a user command with its arguments to the log file.

        Args:
            command (str): The command name that was executed.
            args (str, optional): The arguments passed to the command.
                Defaults to empty string.

        Example:
            shell.log_command("get", "settings.max_threads")
            # Logs: "Command: get settings.max_threads"
        """
        full_command = f"{command} {args}".strip()
        self.logger.info(f"Command: {full_command}")

    def log_output(self, output: str):
        """Log command output.

        Records the output of a command to the log file.

        Args:
            output (str): The output text to log.

        Example:
            shell.log_output("Configuration loaded successfully")
            # Logs: "Output: Configuration loaded successfully"
        """
        if output.strip():
            self.logger.info(f"Output: {output.strip()}")

    def log_error(self, error: str):
        """Log error messages.

        Records error messages to the log file with error level.

        Args:
            error (str): The error message to log.

        Example:
            shell.log_error("Configuration file not found")
            # Logs: "Error: Configuration file not found"
        """
        self.logger.error(f"Error: {error}")

    def do_init(self, arg):
        """Initialize default configuration.

        Creates a new configuration file with default settings. If a configuration
        file already exists, it will not be overwritten unless the --force flag
        is used.

        Args:
            arg (str): Command arguments. Use --force to overwrite existing config.

        Usage:
            init [--force]

        Example:
            init
            init --force
        """
        self.log_command("init", arg)
        try:
            force = "--force" in arg
            if force or not self.config_manager.config_path.exists():
                self.config_manager.create_default_config()
                output = (
                    f"Configuration initialized at {self.config_manager.config_path}"
                )
                print(output)
                self.log_output(output)
            else:
                output = "Configuration already exists. Use --force to overwrite."
                print(output)
                self.log_output(output)
        except Exception as e:
            error_msg = f"Error initializing configuration: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def do_get(self, arg):
        """Get configuration value.

        Retrieves a configuration value using dot notation to access nested
        configuration keys.

        Args:
            arg (str): The configuration key in dot notation.

        Usage:
            get <key>

        Example:
            get paths.project_root
            get settings.max_threads
            get dependencies.topaz.path
        """
        self.log_command("get", arg)
        try:
            if not arg.strip():
                print("Error: Key is required. Usage: get <key>", file=sys.stderr)
                self.log_error("Missing key argument")
                return

            value = self.config_manager.get(arg.strip())
            if value is not None:
                print(value)
                self.log_output(str(value))
            else:
                error_msg = f"Key '{arg.strip()}' not found"
                print(error_msg, file=sys.stderr)
                self.log_error(error_msg)
        except Exception as e:
            error_msg = f"Error getting configuration: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def do_set(self, arg):
        """Set configuration value.

        Sets a configuration value using dot notation. Creates intermediate
        dictionaries if they don't exist.

        Args:
            arg (str): The configuration key and value in format "key value".

        Usage:
            .. code-block:: bash

                set <key> <value>

        Example:
            .. code-block:: bash

                set settings.max_threads 8
                set settings.gpu_enabled true
                set new_section.new_key new_value
        """
        self.log_command("set", arg)
        try:
            parts = arg.split(None, 1)
            if len(parts) < 2:
                print(
                    "Error: Key and value are required. Usage: set <key> <value>",
                    file=sys.stderr,
                )
                self.log_error("Missing key or value argument")
                return

            key, value = parts
            self.config_manager.set(key, value)
            output = f"Set {key} = {value}"
            print(output)
            self.log_output(output)
        except Exception as e:
            error_msg = f"Error setting configuration: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def do_add_dependency(self, arg):
        """Add or update dependency path.

        Updates the path and version for a specified dependency in the configuration.
        The dependency is automatically enabled if a path is provided.

        Args:
            arg (str): Dependency name, path, and optional version.

        Usage:
            add_dependency <name> <path> [version]

        Example:
            add_dependency topaz /usr/local/bin/topaz 0.3.7
            add_dependency model_angelo /path/to/model_angelo 1.0.1
            add_dependency relion /usr/local/relion/bin/relion
        """
        self.log_command("add_dependency", arg)
        try:
            parts = arg.split()
            if len(parts) < 2:
                print(
                    "Error: Name and path are required. Usage: add_dependency <name> <path> [version]",
                    file=sys.stderr,
                )
                self.log_error("Missing name or path argument")
                return

            name = parts[0]
            path = parts[1]
            version = parts[2] if len(parts) > 2 else ""

            self.config_manager.update_dependency_path(name, path, version)
            output = f"Updated {name} dependency"
            print(output)
            self.log_output(output)
        except Exception as e:
            error_msg = f"Error adding dependency: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def do_list_dependencies(self, arg):
        """List all configured dependencies.

        Displays a formatted list of all dependencies configured in the system,
        including their paths, versions, and enabled status.

        Args:
            arg (str): Not used.

        Example:
            list_dependencies
            # Shows all dependencies with their status
        """
        self.log_command("list_dependencies", arg)
        try:
            deps = self.config_manager.list_dependencies()
            output = "\nConfigured Dependencies:\n" + "-" * 50 + "\n"
            for name, info in deps.items():
                status = "✓ Enabled" if info.get("enabled") else "✗ Disabled"
                path = info.get("path", "Not set")
                version = info.get("version", "Unknown")
                output += f"{name:12} {status:12} {path}\n"
                if version:
                    output += f"{'':12} {'':12} Version: {version}\n"
                output += "\n"
            print(output)
            self.log_output(output)
        except Exception as e:
            error_msg = f"Error listing dependencies: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def do_validate_dependencies(self, arg):
        """Validate all dependency paths.

        Checks if all configured dependency paths exist and are accessible.
        Displays the validation status for each dependency.

        Args:
            arg (str): Not used.

        Example:
            validate_dependencies
            # Shows validation status for all dependencies
        """
        self.log_command("validate_dependencies", arg)
        try:
            output = "\nDependency Path Validation:\n" + "-" * 40 + "\n"
            all_valid = True
            for dep_name in self.config_manager.config["dependencies"]:
                is_valid = self.config_manager.validate_dependency_path(dep_name)
                status = "✓ Valid" if is_valid else "✗ Invalid"
                path = self.config_manager.config["dependencies"][dep_name].get(
                    "path", "Not set"
                )
                output += f"{dep_name:12} {status:8} {path}\n"
                if not is_valid and path:
                    all_valid = False

            if all_valid:
                output += "\nAll dependency paths are valid!"
            else:
                output += "\nSome dependency paths are invalid. Please check the paths."

            print(output)
            self.log_output(output)

            if not all_valid:
                self.log_error("Some dependency paths are invalid")
        except Exception as e:
            error_msg = f"Error validating dependencies: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def do_show(self, arg):
        """Show full configuration.

        Displays the complete configuration in JSON format.

        Args:
            arg (str): Not used.

        Example:
            show
            # Displays the entire configuration as JSON
        """
        self.log_command("show", arg)
        try:
            import json

            output = json.dumps(self.config_manager.config, indent=4)
            print(output)
            self.log_output(output)
        except Exception as e:
            error_msg = f"Error showing configuration: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def do_reset(self, arg):
        """Reset configuration to defaults.

        Resets the current configuration to the default values and saves the
        changes. This will overwrite any custom settings that have been made.

        Args:
            arg (str): Not used.

        Example:
            reset
            # Configuration is reset to default values
        """
        self.log_command("reset", arg)
        try:
            self.config_manager.reset_config()
            output = "Configuration reset to defaults"
            print(output)
            self.log_output(output)
        except Exception as e:
            error_msg = f"Error resetting configuration: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def do_export(self, arg):
        """Export configuration to file.

        Exports the current configuration to a specified file path in JSON format.
        This is useful for backing up configurations or sharing them between
        different environments.

        Args:
            arg (str): The file path where to export the configuration.

        Usage:
            export <path>

        Example:
            export config_backup.json
            export backups/config_2024.json
        """
        self.log_command("export", arg)
        try:
            if not arg.strip():
                print("Error: Path is required. Usage: export <path>", file=sys.stderr)
                self.log_error("Missing path argument")
                return

            self.config_manager.export_config(arg.strip())
            output = f"Configuration exported to {arg.strip()}"
            print(output)
            self.log_output(output)
        except Exception as e:
            error_msg = f"Error exporting configuration: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def do_import(self, arg):
        """Import configuration from file.

        Imports a configuration from a specified file path and replaces the current
        configuration. The imported configuration is then saved to the main
        configuration file.

        Args:
            arg (str): The file path of the configuration to import.

        Usage:
            import <path>

        Example:
            import config_backup.json
            import backups/config_2024.json
        """
        self.log_command("import", arg)
        try:
            if not arg.strip():
                print("Error: Path is required. Usage: import <path>", file=sys.stderr)
                self.log_error("Missing path argument")
                return

            self.config_manager.import_config(arg.strip())
            output = f"Configuration imported from {arg.strip()}"
            print(output)
            self.log_output(output)
        except Exception as e:
            error_msg = f"Error importing configuration: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def do_slurm_generate(self, arg):
        """Generate SLURM header.

        Generates a SLURM job script header using the current SLURM configuration
        settings. Allows overriding specific parameters for the job.

        Args:
            arg (str): SLURM parameters to override. Available options:
                --job-name <name>: Override job name
                --output <file>: Save header to file
                --nodes <n>: Number of nodes
                --ntasks <n>: Number of tasks
                --cpus-per-task <n>: CPUs per task
                --gres-gpu <n>: Number of GPUs
                --time <time>: Time limit (HH:MM:SS)
                --mem <mem>: Memory limit

        Usage:
            slurm_generate [--job-name <name>] [--output <file>] [--nodes <n>] [--ntasks <n>] [--cpus-per-task <n>] [--gres-gpu <n>] [--time <time>] [--mem <mem>]

        Example:
            slurm_generate --job-name model_angelo --nodes 2 --gres-gpu 2
            slurm_generate --output my_job.slurm --time 12:00:00
        """
        self.log_command("slurm_generate", arg)
        try:
            # Parse arguments (simplified parsing for interactive mode)
            args = arg.split()
            overrides = {}
            job_name = None
            output_file = None

            i = 0
            while i < len(args):
                if args[i] == "--job-name" and i + 1 < len(args):
                    job_name = args[i + 1]
                    i += 2
                elif args[i] == "--output" and i + 1 < len(args):
                    output_file = args[i + 1]
                    i += 2
                elif args[i] == "--nodes" and i + 1 < len(args):
                    overrides["nodes"] = int(args[i + 1])
                    i += 2
                elif args[i] == "--ntasks" and i + 1 < len(args):
                    overrides["ntasks"] = int(args[i + 1])
                    i += 2
                elif args[i] == "--cpus-per-task" and i + 1 < len(args):
                    overrides["cpus_per_task"] = int(args[i + 1])
                    i += 2
                elif args[i] == "--gres-gpu" and i + 1 < len(args):
                    overrides["gres_gpu"] = int(args[i + 1])
                    i += 2
                elif args[i] == "--time" and i + 1 < len(args):
                    overrides["time"] = args[i + 1]
                    i += 2
                elif args[i] == "--mem" and i + 1 < len(args):
                    overrides["mem"] = args[i + 1]
                    i += 2
                else:
                    i += 1

            header = self.config_manager.generate_slurm_header(job_name, **overrides)

            if output_file:
                self.config_manager.save_slurm_header(
                    output_file, job_name, **overrides
                )
                output = f"SLURM header saved to {output_file}"
                print(output)
                self.log_output(output)
            else:
                print(header)
                self.log_output(header)
        except Exception as e:
            error_msg = f"Error generating SLURM header: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def do_slurm_show(self, arg):
        """Show SLURM configuration.

        Displays the current SLURM configuration settings in a formatted table.

        Args:
            arg (str): Not used.

        Example:
            slurm_show
            # Shows all SLURM configuration parameters
        """
        self.log_command("slurm_show", arg)
        try:
            slurm_config = self.config_manager.get_slurm_config()
            output = "\nSLURM Configuration:\n" + "-" * 30 + "\n"
            for key, value in slurm_config.items():
                output += f"{key:20}: {value}\n"
            print(output)
            self.log_output(output)
        except Exception as e:
            error_msg = f"Error showing SLURM configuration: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def do_slurm_update(self, arg):
        """Update SLURM configuration.

        Updates the SLURM configuration section with new parameter values and
        saves the changes to the configuration file.

        Args:
            arg (str): SLURM parameters to update. Available options:
                --job-name <name>: Default job name
                --nodes <n>: Number of nodes
                --ntasks <n>: Number of tasks
                --cpus-per-task <n>: CPUs per task
                --gres-gpu <n>: Number of GPUs
                --time <time>: Time limit (HH:MM:SS)
                --partition <partition>: Partition name
                --qos <qos>: Quality of service
                --account <account>: Account name
                --mem <mem>: Memory limit
                --output <pattern>: Output file pattern
                --error <pattern>: Error file pattern

        Usage:
            slurm_update [--job-name <name>] [--nodes <n>] [--ntasks <n>] [--cpus-per-task <n>] [--gres-gpu <n>] [--time <time>] [--partition <partition>] [--qos <qos>] [--account <account>] [--mem <mem>] [--output <pattern>] [--error <pattern>]

        Example:
            slurm_update --nodes 2 --gres-gpu 2 --time 12:00:00
            slurm_update --partition gpu --account my_account
        """
        self.log_command("slurm_update", arg)
        try:
            # Parse arguments (simplified parsing for interactive mode)
            args = arg.split()
            updates = {}

            i = 0
            while i < len(args):
                if args[i] == "--job-name" and i + 1 < len(args):
                    updates["job_name"] = args[i + 1]
                    i += 2
                elif args[i] == "--nodes" and i + 1 < len(args):
                    updates["nodes"] = int(args[i + 1])
                    i += 2
                elif args[i] == "--ntasks" and i + 1 < len(args):
                    updates["ntasks"] = int(args[i + 1])
                    i += 2
                elif args[i] == "--cpus-per-task" and i + 1 < len(args):
                    updates["cpus_per_task"] = int(args[i + 1])
                    i += 2
                elif args[i] == "--gres-gpu" and i + 1 < len(args):
                    updates["gres_gpu"] = int(args[i + 1])
                    i += 2
                elif args[i] == "--time" and i + 1 < len(args):
                    updates["time"] = args[i + 1]
                    i += 2
                elif args[i] == "--partition" and i + 1 < len(args):
                    updates["partition"] = args[i + 1]
                    i += 2
                elif args[i] == "--qos" and i + 1 < len(args):
                    updates["qos"] = args[i + 1]
                    i += 2
                elif args[i] == "--account" and i + 1 < len(args):
                    updates["account"] = args[i + 1]
                    i += 2
                elif args[i] == "--mem" and i + 1 < len(args):
                    updates["mem"] = args[i + 1]
                    i += 2
                elif args[i] == "--output" and i + 1 < len(args):
                    updates["output"] = args[i + 1]
                    i += 2
                elif args[i] == "--error" and i + 1 < len(args):
                    updates["error"] = args[i + 1]
                    i += 2
                else:
                    i += 1

            if updates:
                self.config_manager.update_slurm_config(**updates)
                output = "SLURM configuration updated"
                print(output)
                self.log_output(output)
            else:
                output = "No SLURM parameters provided for update"
                print(output)
                self.log_output(output)
        except Exception as e:
            error_msg = f"Error updating SLURM configuration: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def do_fasta(self, arg):
        """Build FASTA files from PDB IDs using RCSB PDB.

        Retrieves FASTA sequences from the RCSB PDB database and saves them to files
        for use in cryo-EM workflows. Supports single and multiple PDB IDs, and
        creating annotated sequences from ModelAngelo CIF output.

        Args:
            arg (str): PDB ID(s) and options. Can include:
                pdb_id: Single PDB ID (e.g., "1ABC")
                --multiple: Process multiple PDB IDs
                --annotate: Create annotated sequences from CIF and FASTA files
                --output filename: Specify output filename

        Usage:
            fasta <pdb_id> [--output filename]
            fasta --multiple <pdb_id1> <pdb_id2> ... [--output filename]
            fasta --annotate <cif_file> <fasta_file> [--output filename]

        Example:
            fasta 1ABC
            fasta 1ABC --output my_protein.fasta
            fasta --multiple 1ABC 2DEF 3GHI --output combined.fasta
            fasta --annotate model.cif protein.fasta --output annotated.fasta
        """
        self.log_command("fasta", arg)
        try:
            # Import the FastaBuilder
            try:
                from .build_fasta import FastaBuilder
            except ImportError as e:
                error_msg = f"Could not import FastaBuilder module: {e}"
                print(error_msg, file=sys.stderr)
                print("Please install network dependencies: pip install requests")
                self.log_error(error_msg)
                return

            # Parse arguments
            args = arg.split()
            if not args:
                print("FASTA command - Build FASTA files from PDB IDs using RCSB PDB")
                print()
                print("Usage:")
                print("  fasta <pdb_id> [--output filename]")
                print("  fasta --multiple <pdb_id1> <pdb_id2> ... [--output filename]")
                print("  fasta --annotate <cif_file> <fasta_file> [--output filename]")
                print()
                print("Use 'fasta --help' for detailed information")
                self.log_error("Missing PDB ID argument")
                return

            # Check for help first
            if args[0] in ["--help", "-h", "help"]:
                print(self.do_fasta.__doc__)
                return

            if args[0] == "--annotate":
                if len(args) < 3:
                    print("Error: CIF file and FASTA file required for --annotate option")
                    print("Usage: fasta --annotate <cif_file> <fasta_file> [--output filename]")
                    self.log_error("Missing CIF or FASTA file for --annotate option")
                    return

                cif_file = args[1]
                fasta_file = args[2]
                output_file = "annotated_sequence.fasta"

                # Check for output file option
                if len(args) >= 5 and args[3] == "--output":
                    output_file = args[4]

                print(f"Creating annotated sequence from CIF: {cif_file}")
                print(f"Using FASTA file: {fasta_file}")
                print(f"Output file: {output_file}")

                builder = FastaBuilder()
                success, message = builder.create_annotated_sequence(cif_file, fasta_file, output_file)

                if success:
                    print(message)
                    self.log_output(f"Successfully created annotated FASTA file: {output_file}")
                else:
                    print(f"Error: {message}", file=sys.stderr)
                    self.log_error(f"Failed to create annotated FASTA file: {message}")

                return

            elif args[0] == "--multiple":
                if len(args) < 2:
                    print("Error: At least one PDB ID required for --multiple option")
                    self.log_error("Missing PDB IDs for --multiple option")
                    return

                # Extract PDB IDs and output file
                pdb_ids = []
                output_file = "combined_protein.fasta"

                i = 1
                while i < len(args):
                    if args[i] == "--output" and i + 1 < len(args):
                        output_file = args[i + 1]
                        i += 2
                    else:
                        pdb_ids.append(args[i].upper())
                        i += 1

                if not pdb_ids:
                    print("Error: No PDB IDs provided")
                    self.log_error("No PDB IDs provided for --multiple option")
                    return

                print(f"Processing multiple PDB IDs: {', '.join(pdb_ids)}")
                print(f"Output file: {output_file}")

                builder = FastaBuilder()
                success, message = builder.build_fasta_from_multiple_pdbs(
                    pdb_ids, output_file
                )

                if success:
                    print(message)
                    self.log_output(f"Successfully created FASTA file: {output_file}")
                else:
                    print(f"Error: {message}", file=sys.stderr)
                    self.log_error(f"Failed to create FASTA file: {message}")

                return

            else:
                # Single PDB ID mode
                pdb_id = args[0].upper()
                output_file = f"{pdb_id}_protein.fasta"

                # Check for output file option
                if len(args) >= 3 and args[1] == "--output":
                    output_file = args[2]

                print(f"Fetching FASTA sequence for PDB ID: {pdb_id}")
                print(f"Output file: {output_file}")

                builder = FastaBuilder()
                success, message = builder.build_fasta_from_pdb(pdb_id, output_file)

                if success:
                    print(message)
                    self.log_output(f"Successfully created FASTA file: {output_file}")
                else:
                    print(f"Error: {message}", file=sys.stderr)
                    self.log_error(f"Failed to create FASTA file: {message}")

        except Exception as e:
            error_msg = f"Error in fasta command: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def do_model_angelo(self, arg):
        """Run ModelAngelo for protein structure prediction.

        Executes ModelAngelo for protein structure prediction from cryo-EM data.
        Prompts for input files (.mrc and FASTA) and can run either locally or
        submit to SLURM queue.

        Args:
            arg (str): Command arguments. Use --local to run locally instead of SLURM.

        Usage:
            model_angelo [--local]

        Example:
            model_angelo
            model_angelo --local
        """
        self.log_command("model_angelo", arg)
        try:
            # Check if model_angelo is configured
            model_angelo_path = self.config_manager.get(
                "dependencies.model_angelo.path"
            )
            if not model_angelo_path:
                error_msg = "ModelAngelo path not configured. Use 'add_dependency model_angelo <path>' first."
                print(error_msg, file=sys.stderr)
                self.log_error(error_msg)
                return

            # Validate model_angelo path
            if not self.config_manager.validate_dependency_path("model_angelo"):
                error_msg = f"ModelAngelo not found at: {model_angelo_path}"
                print(error_msg, file=sys.stderr)
                self.log_error(error_msg)
                return

            # Parse arguments
            args = arg.split()

            # Check for help first
            if args and args[0] in ["--help", "-h", "help"]:
                print(self.do_model_angelo.__doc__)
                return

            is_local = "--local" in args

            # Prompt for input files
            print("ModelAngelo Setup:")
            print("-" * 20)

            # Get MRC file path
            mrc_file = input("Enter path to .mrc file: ").strip()
            if not mrc_file:
                error_msg = "MRC file path is required"
                print(error_msg, file=sys.stderr)
                self.log_error(error_msg)
                return

            # Validate MRC file exists
            mrc_path = Path(mrc_file)
            if not mrc_path.exists():
                error_msg = f"MRC file not found: {mrc_file}"
                print(error_msg, file=sys.stderr)
                self.log_error(error_msg)
                return

            # Get FASTA file path
            fasta_file = input("Enter path to protein FASTA file: ").strip()
            if not fasta_file:
                error_msg = "FASTA file path is required"
                print(error_msg, file=sys.stderr)
                self.log_error(error_msg)
                return

            # Validate FASTA file exists
            fasta_path = Path(fasta_file)
            if not fasta_path.exists():
                error_msg = f"FASTA file not found: {fasta_file}"
                print(error_msg, file=sys.stderr)
                self.log_error(error_msg)
                return

            # Generate output directory name based on MRC file
            mrc_stem = mrc_path.stem
            output_dir = f"model_angelo_output_{mrc_stem}"

            # Build ModelAngelo command
            model_angelo_cmd = f"{model_angelo_path} -v {mrc_file} -pf {fasta_file} -o {output_dir} --device 0"

            if is_local:
                # Run locally
                output = f"Running ModelAngelo locally:\n{model_angelo_cmd}"
                print(output)
                self.log_output(output)

                # Execute the command
                import subprocess

                try:
                    result = subprocess.run(
                        model_angelo_cmd, shell=True, capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        success_msg = f"ModelAngelo completed successfully. Output in: {output_dir}"
                        print(success_msg)
                        self.log_output(success_msg)
                    else:
                        error_msg = (
                            f"ModelAngelo failed with return code {result.returncode}"
                        )
                        print(error_msg, file=sys.stderr)
                        print(f"Error output: {result.stderr}", file=sys.stderr)
                        self.log_error(error_msg)
                except Exception as e:
                    error_msg = f"Error running ModelAngelo: {e}"
                    print(error_msg, file=sys.stderr)
                    self.log_error(error_msg)
            else:
                # Generate and submit SLURM job
                job_name = f"model_angelo_{mrc_stem}"

                # Create SLURM script content
                slurm_script = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --output={job_name}_%j.out
#SBATCH --error={job_name}_%j.err
#SBATCH --time={self.config_manager.get('slurm.time', '24:00:00')}
#SBATCH --nodes={self.config_manager.get('slurm.nodes', 1)}
#SBATCH --ntasks={self.config_manager.get('slurm.ntasks', 1)}
#SBATCH --cpus-per-task={self.config_manager.get('slurm.cpus_per_task', 4)}
#SBATCH --mem={self.config_manager.get('slurm.mem', '16G')}
    """

                # Add optional SLURM parameters if configured
                partition = self.config_manager.get("slurm.partition")
                if partition:
                    slurm_script += f"#SBATCH --partition={partition}\n"

                qos = self.config_manager.get("slurm.qos")
                if qos:
                    slurm_script += f"#SBATCH --qos={qos}\n"

                account = self.config_manager.get("slurm.account")
                if account:
                    slurm_script += f"#SBATCH --account={account}\n"

                gres_gpu = self.config_manager.get("slurm.gres_gpu")
                if gres_gpu:
                    slurm_script += f"#SBATCH --gres=gpu:{gres_gpu}\n"

                slurm_script += f"""
set -euo pipefail
set -x

# Load any required modules (uncomment and modify as needed)
module purge
module load model-angelo/1.0.1


# Run ModelAngelo
{model_angelo_cmd}

echo "ModelAngelo job completed"
"""

                # Write SLURM script to file
                slurm_script_path = f"{job_name}.slurm"
                with open(slurm_script_path, "w") as f:
                    f.write(slurm_script)

                # Show job summary and ask for confirmation
                print(f"\nJob Summary:")
                print(f"  Job Name: {job_name}")
                print(f"  MRC File: {mrc_file}")
                print(f"  FASTA File: {fasta_file}")
                print(f"  Output Directory: {output_dir}")
                print(f"  SLURM Script: {slurm_script_path}")
                print(
                    f"  Time Limit: {self.config_manager.get('slurm.time', '24:00:00')}"
                )
                print(f"  Nodes: {self.config_manager.get('slurm.nodes', 1)}")
                print(
                    f"  CPUs per Task: {self.config_manager.get('slurm.cpus_per_task', 4)}"
                )
                print(f"  Memory: {self.config_manager.get('slurm.mem', '16G')}")

                gres_gpu = self.config_manager.get("slurm.gres_gpu")
                if gres_gpu:
                    print(f"  GPUs: {gres_gpu}")

                partition = self.config_manager.get("slurm.partition")
                if partition:
                    print(f"  Partition: {partition}")

                # Ask for confirmation
                while True:
                    confirm = (
                        input("\nSubmit this job to SLURM? (Y/N): ").strip().upper()
                    )
                    if confirm in ["Y", "YES", "y", "yes"]:
                        break
                    elif confirm in ["N", "NO", "n", "no"]:
                        print("Job submission cancelled.")
                        self.log_output("Job submission cancelled by user")
                        return
                    else:
                        print("Please enter Y or N.")

                # Submit job

                try:
                    import subprocess

                    result = subprocess.run(
                        f"sbatch {slurm_script_path}",
                        shell=True,
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode == 0:
                        job_id = result.stdout.strip().split()[
                            -1
                        ]  # Extract job ID from sbatch output
                        success_msg = (
                            f"ModelAngelo job submitted successfully. Job ID: {job_id}"
                        )
                        print(success_msg)
                        self.log_output(success_msg)
                        print(f"SLURM script saved as: {slurm_script_path}")
                        print(f"Job output will be in: {job_name}_<job_id>.out")
                        print(f"Job errors will be in: {job_name}_<job_id>.err")
                    else:
                        error_msg = f"Failed to submit SLURM job: {result.stderr}"
                        print(error_msg, file=sys.stderr)
                        self.log_error(error_msg)
                except Exception as e:
                    error_msg = f"Error submitting SLURM job: {e}"
                    print(error_msg, file=sys.stderr)
                    self.log_error(error_msg)

        except Exception as e:
            error_msg = f"Error in model_angelo command: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def do_topaz(self, arg):
        """Run Topaz for particle picking and analysis.

        Executes Topaz commands for cryo-EM particle picking and analysis workflows.
        Supports preprocessing, model training, postprocessing, and cross-validation.

        Args:
            arg (str): Topaz command and options. Available commands:
                preprocess: Preprocess micrographs and particle coordinates
                denoise: Train and apply denoising models to micrographs
                model: Train particle picking models
                postprocess: Post-process results
                cross: Perform cross-validation analysis
                Use --local to run locally instead of SLURM.

        Usage:
            topaz <command> [--local]

        Commands:
            preprocess, denoise, model, postprocess, cross

        Example:
            topaz preprocess --local
            topaz denoise --local
            topaz preprocess
            topaz cross
        """
        self.log_command("topaz", arg)
        try:
            # Check if topaz is configured
            topaz_path = self.config_manager.get("dependencies.topaz.path")
            if not topaz_path:
                error_msg = "Topaz path not configured. Use 'add_dependency topaz <path>' first."
                print(error_msg, file=sys.stderr)
                self.log_error(error_msg)
                return

            # Validate topaz path
            if not self.config_manager.validate_dependency_path("topaz"):
                error_msg = f"Topaz not found at: {topaz_path}"
                print(error_msg, file=sys.stderr)
                self.log_error(error_msg)
                return

            # Parse arguments
            args = arg.split()
            if not args:
                print("Topaz command - Run Topaz for particle picking and analysis")
                print()
                print("Usage:")
                print("  topaz <command> [--local]")
                print()
                print("Available commands:")
                print("  preprocess  - Preprocess micrographs and particle coordinates")
                print("  denoise     - Train and apply denoising models to micrographs")
                print("  model       - Train particle picking models")
                print("  postprocess - Post-process results")
                print("  cross       - Perform cross-validation analysis")
                print()
                print("Use 'topaz --help' for detailed information")
                self.log_error("Missing topaz command")
                return

            # Check for help first
            if args[0] in ["--help", "-h", "help"]:
                print(self.do_topaz.__doc__)
                return

            command = args[0]
            is_local = "--local" in args

            if command == "preprocess":
                self._run_topaz_preprocess(topaz_path, is_local)
            elif command == "denoise":
                self._run_topaz_denoise(topaz_path, is_local)
            elif command == "model":
                print("Topaz model command not yet implemented")
                self.log_output("Topaz model command not yet implemented")
            elif command == "postprocess":
                print("Topaz postprocess command not yet implemented")
                self.log_output("Topaz postprocess command not yet implemented")
            else:
                error_msg = f"Unknown topaz command: {command}"
                print(error_msg, file=sys.stderr)
                print("Available commands: preprocess, denoise, model, postprocess")
                self.log_error(error_msg)

        except Exception as e:
            error_msg = f"Error in topaz command: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def _run_topaz_preprocess(self, topaz_path, is_local):
        """Run Topaz preprocess command.

        Executes the Topaz preprocess workflow to downsample micrographs and
        scale particle coordinates. Can run locally or generate SLURM scripts.

        Args:
            topaz_path (str): Path to the Topaz executable.
            is_local (bool): If True, run locally; if False, submit to SLURM.

        Example:
            shell._run_topaz_preprocess('/usr/local/bin/topaz', True)
        """
        try:
            print("Topaz Preprocess Setup:")
            print("-" * 25)

            # Prompt for input parameters
            raw_micrographs = input("Enter path to raw micrographs directory: ").strip()
            if not raw_micrographs:
                error_msg = "Raw micrographs directory path is required"
                print(error_msg, file=sys.stderr)
                self.log_error(error_msg)
                return

            # Validate micrographs directory exists
            micrographs_path = Path(raw_micrographs)
            if not micrographs_path.exists():
                error_msg = f"Micrographs directory not found: {raw_micrographs}"
                print(error_msg, file=sys.stderr)
                self.log_error(error_msg)
                return

            # Get particle coordinates file (optional)
            raw_particles = input(
                "Enter path to particle coordinates file (optional, press Enter to skip): "
            ).strip()
            particles_path = None
            if raw_particles:
                particles_path = Path(raw_particles)
                if not particles_path.exists():
                    error_msg = f"Particle coordinates file not found: {raw_particles}"
                    print(error_msg, file=sys.stderr)
                    self.log_error(error_msg)
                    return

            # Get output directory
            output_dir = input(
                "Enter output directory name (default: topaz_preprocess_output): "
            ).strip()
            if not output_dir:
                output_dir = "topaz_preprocess_output"

            # Get pixel size for downsampling
            pixel_size = input(
                "Enter pixel size for downsampling in Å/px (default: 8): "
            ).strip()
            if not pixel_size:
                pixel_size = "8"
            else:
                try:
                    float(pixel_size)  # Validate it's a number
                except ValueError:
                    error_msg = "Pixel size must be a number"
                    print(error_msg, file=sys.stderr)
                    self.log_error(error_msg)
                    return

            # Create output directories
            proc_root = Path(output_dir)
            proc_micrographs = proc_root / "micrographs"
            model_dir = proc_root / "saved_models"
            data_dir = proc_root / "data"

            # Build Topaz preprocess command
            preprocess_cmd = f"{topaz_path} preprocess -v -s {pixel_size} -o {proc_micrographs} {raw_micrographs}/*.mrc"

            # Build convert command if particles file provided
            convert_cmd = None
            if particles_path:
                convert_cmd = f"{topaz_path} convert -s {pixel_size} -o {proc_root}/particles.txt {raw_particles}"

            if is_local:
                # Run locally
                print(f"\nRunning Topaz preprocess locally:")
                print(f"Preprocess command: {preprocess_cmd}")
                if convert_cmd:
                    print(f"Convert command: {convert_cmd}")

                # Create directories
                proc_micrographs.mkdir(parents=True, exist_ok=True)
                model_dir.mkdir(parents=True, exist_ok=True)
                data_dir.mkdir(parents=True, exist_ok=True)

                # Execute preprocess command
                import subprocess

                try:
                    result = subprocess.run(
                        preprocess_cmd, shell=True, capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        success_msg = f"Topaz preprocess completed successfully. Output in: {proc_micrographs}"
                        print(success_msg)
                        self.log_output(success_msg)
                    else:
                        error_msg = f"Topaz preprocess failed with return code {result.returncode}"
                        print(error_msg, file=sys.stderr)
                        print(f"Error output: {result.stderr}", file=sys.stderr)
                        self.log_error(error_msg)
                        return

                    # Execute convert command if provided
                    if convert_cmd:
                        result = subprocess.run(
                            convert_cmd, shell=True, capture_output=True, text=True
                        )
                        if result.returncode == 0:
                            success_msg = f"Topaz convert completed successfully. Output in: {proc_root}/particles.txt"
                            print(success_msg)
                            self.log_output(success_msg)
                        else:
                            error_msg = f"Topaz convert failed with return code {result.returncode}"
                            print(error_msg, file=sys.stderr)
                            print(f"Error output: {result.stderr}", file=sys.stderr)
                            self.log_error(error_msg)

                except Exception as e:
                    error_msg = f"Error running Topaz: {e}"
                    print(error_msg, file=sys.stderr)
                    self.log_error(error_msg)
            else:
                # Generate and submit SLURM job
                job_name = "topaz_preprocess"

                # Create SLURM script content
                slurm_script = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --output={job_name}_%j.out
#SBATCH --error={job_name}_%j.err
#SBATCH --time={self.config_manager.get('slurm.time', '24:00:00')}
#SBATCH --nodes={self.config_manager.get('slurm.nodes', 1)}
#SBATCH --ntasks={self.config_manager.get('slurm.ntasks', 1)}
#SBATCH --cpus-per-task={self.config_manager.get('slurm.cpus_per_task', 4)}
#SBATCH --mem={self.config_manager.get('slurm.mem', '16G')}

set -euo pipefail
set -x

module purge
module load topaz/0.2.5

# Be explicit about threads to avoid oversubscription
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1

cd "${{SLURM_SUBMIT_DIR}}"
echo "WORKDIR: ${{SLURM_SUBMIT_DIR}}"
nvidia-smi || true

# Paths
RAW_MICROS="{raw_micrographs}"
PROC_ROOT="{output_dir}"
PROC_MICROS="${{PROC_ROOT}}/micrographs"
MODEL_DIR="${{PROC_ROOT}}/saved_models"
DATA_DIR="${{PROC_ROOT}}/data"

# Make Directories for Preprocessing, Model, and Data
mkdir -p "${{PROC_MICROS}}" "${{MODEL_DIR}}" "${{DATA_DIR}}"

# Preprocess (downsample to {pixel_size} Å/px)
srun -u {topaz_path} preprocess -v -s {pixel_size} \\
  -o "${{PROC_MICROS}}/" \\
  "${{RAW_MICROS}}"/*.mrc
"""

                # Add convert command if particles file provided
                if particles_path:
                    slurm_script += f"""
# Scale particle coordinates to match downsampling
srun -u {topaz_path} convert -s {pixel_size} \\
  -o "${{PROC_ROOT}}/particles.txt" \\
  "{raw_particles}"
"""

                slurm_script += """
echo "Topaz preprocess job completed"
"""

                # Write SLURM script to file
                slurm_script_path = f"{job_name}.slurm"
                with open(slurm_script_path, "w") as f:
                    f.write(slurm_script)

                # Show job summary and ask for confirmation
                print(f"\nJob Summary:")
                print(f"  Job Name: {job_name}")
                print(f"  Raw Micrographs: {raw_micrographs}")
                if particles_path:
                    print(f"  Particle Coordinates: {raw_particles}")
                print(f"  Output Directory: {output_dir}")
                print(f"  Pixel Size: {pixel_size} Å/px")
                print(f"  SLURM Script: {slurm_script_path}")
                print(f"  Time Limit: 06:00:00")
                print(f"  Nodes: 1")
                print(f"  CPUs per Task: 4")
                print(f"  Memory: 96G")
                print(f"  GPUs: 1")
                print(f"  Partition: notchpeak-gpu")

                # Ask for confirmation
                while True:
                    confirm = (
                        input("\nSubmit this job to SLURM? (Y/N): ").strip().upper()
                    )
                    if confirm in ["Y", "YES", "y", "yes"]:
                        break
                    elif confirm in ["N", "NO", "n", "no"]:
                        print("Job submission cancelled.")
                        self.log_output("Job submission cancelled by user")
                        return
                    else:
                        print("Please enter Y or N.")

                # Submit job
                try:
                    import subprocess

                    result = subprocess.run(
                        f"sbatch {slurm_script_path}",
                        shell=True,
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode == 0:
                        job_id = result.stdout.strip().split()[
                            -1
                        ]  # Extract job ID from sbatch output
                        success_msg = f"Topaz preprocess job submitted successfully. Job ID: {job_id}"
                        print(success_msg)
                        self.log_output(success_msg)
                        print(f"SLURM script saved as: {slurm_script_path}")
                        print(f"Job output will be in: slurm-<job_id>.out-<node>")
                        print(f"Job errors will be in: slurm-<job_id>.err-<node>")
                    else:
                        error_msg = f"Failed to submit SLURM job: {result.stderr}"
                        print(error_msg, file=sys.stderr)
                        self.log_error(error_msg)
                except Exception as e:
                    error_msg = f"Error submitting SLURM job: {e}"
                    print(error_msg, file=sys.stderr)
                    self.log_error(error_msg)

        except Exception as e:
            error_msg = f"Error in topaz preprocess: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def _run_topaz_denoise(self, topaz_path, is_local):
        """Run Topaz denoise command.

        Executes the Topaz denoising workflow to train denoising models and apply them
        to micrographs. Can run locally or generate SLURM scripts.

        Args:
            topaz_path (str): Path to the Topaz executable.
            is_local (bool): If True, run locally; if False, submit to SLURM.

        Example:
            shell._run_topaz_denoise('/usr/local/bin/topaz', True)
        """
        try:
            print("Topaz Denoise Setup:")
            print("-" * 20)

            # Prompt for input parameters
            raw_movies = input("Enter path to raw movie frames directory: ").strip()
            if not raw_movies:
                error_msg = "Raw movie frames directory path is required"
                print(error_msg, file=sys.stderr)
                self.log_error(error_msg)
                return

            # Validate movies directory exists
            movies_path = Path(raw_movies)
            if not movies_path.exists():
                error_msg = f"Movie frames directory not found: {raw_movies}"
                print(error_msg, file=sys.stderr)
                self.log_error(error_msg)
                return

            # Get output directory
            output_dir = input(
                "Enter output directory name (default: topaz_denoise_output): "
            ).strip()
            if not output_dir:
                output_dir = "topaz_denoise_output"

            # Get project name for organization
            project_name = input(
                "Enter project name (e.g., EMPIAR-10025, default: project): "
            ).strip()
            if not project_name:
                project_name = "project"

            # Create output directories
            denoise_root = Path(output_dir)
            denoised_dir = denoise_root / "data" / project_name / "denoised"
            training_data_dir = denoised_dir / "training_data"
            part_a_dir = training_data_dir / "partA"  # odd frames
            part_b_dir = training_data_dir / "partB"  # even frames
            models_dir = denoise_root / "saved_models" / "denoising"

            if is_local:
                # Run locally
                print(f"\nRunning Topaz denoise locally:")
                print(f"Input movies: {raw_movies}")
                print(f"Output directory: {output_dir}")

                # Create directories
                denoised_dir.mkdir(parents=True, exist_ok=True)
                part_a_dir.mkdir(parents=True, exist_ok=True)
                part_b_dir.mkdir(parents=True, exist_ok=True)
                models_dir.mkdir(parents=True, exist_ok=True)

                # Import and run the denoising workflow
                from .topaz_analysis import run_denoising_workflow

                try:
                    run_denoising_workflow(
                        movies_dir=raw_movies,
                        output_dir=str(denoise_root),
                        project_name=project_name,
                        topaz_path=topaz_path
                    )

                    success_msg = f"Topaz denoise completed successfully. Output in: {denoised_dir}"
                    print(success_msg)
                    self.log_output(success_msg)

                    # Run visualization
                    print("\nGenerating visualization...")
                    from .topaz_analysis import visualize_denoising_results
                    visualize_denoising_results(
                        raw_dir=f"data/{project_name}/rawdata/micrographs",
                        denoised_dir=str(denoised_dir),
                        output_dir=str(denoise_root / "visualization")
                    )

                except Exception as e:
                    error_msg = f"Error in denoising workflow: {e}"
                    print(error_msg, file=sys.stderr)
                    self.log_error(error_msg)
                    return

            else:
                # Generate and submit SLURM job
                job_name = "topaz_denoise"

                # Create SLURM script content
                slurm_script = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --nodes={self.config_manager.get('slurm.nodes', 1)}
#SBATCH --ntasks={self.config_manager.get('slurm.ntasks', 1)}
#SBATCH --cpus-per-task={self.config_manager.get('slurm.cpus_per_task', 4)}
#SBATCH --gres=gpu:{self.config_manager.get('slurm.gres_gpu', 1)}
#SBATCH --time={self.config_manager.get('slurm.time', '06:00:00')}
#SBATCH --partition={self.config_manager.get('slurm.partition', 'notchpeak-gpu')}
#SBATCH --qos={self.config_manager.get('slurm.qos', 'notchpeak-gpu')}
#SBATCH --account={self.config_manager.get('slurm.account', 'notchpeak-gpu')}
#SBATCH --mem={self.config_manager.get('slurm.mem', '96G')}
#SBATCH -o {self.config_manager.get('slurm.output', 'slurm-%j.out-%N')}
#SBATCH -e {self.config_manager.get('slurm.error', 'slurm-%j.err-%N')}

set -euo pipefail
set -x

module purge
module load topaz/0.2.5

# Be explicit about threads to avoid oversubscription
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1

cd "${{SLURM_SUBMIT_DIR}}"
echo "WORKDIR: ${{SLURM_SUBMIT_DIR}}"
nvidia-smi || true

# Create directories
mkdir -p "{denoised_dir}"
mkdir -p "{part_a_dir}"
mkdir -p "{part_b_dir}"
mkdir -p "{models_dir}"

# Paths
RAW_MOVIES="{raw_movies}"
PROJECT_NAME="{project_name}"
DENOISE_ROOT="{output_dir}"

# Run the denoising workflow
python -c "
import sys
sys.path.append('{self.project_root}')
from src.topaz_analysis import run_denoising_workflow, visualize_denoising_results

# Run denoising
run_denoising_workflow(
    movies_dir='{raw_movies}',
    output_dir='{output_dir}',
    project_name='{project_name}',
    topaz_path='{topaz_path}'
)

# Run visualization
visualize_denoising_results(
    raw_dir=f'data/{project_name}/rawdata/micrographs',
    denoised_dir='{denoised_dir}',
    output_dir='{output_dir}/visualization'
)
"
"""

                # Write SLURM script to file
                slurm_script_path = f"{job_name}.sh"
                with open(slurm_script_path, "w") as f:
                    f.write(slurm_script)

                # Submit SLURM job
                try:
                    result = subprocess.run(
                        f"sbatch {slurm_script_path}",
                        shell=True,
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode == 0:
                        job_id = result.stdout.strip().split()[-1]
                        success_msg = f"Topaz denoise job submitted successfully. Job ID: {job_id}"
                        print(success_msg)
                        self.log_output(success_msg)
                        print(f"SLURM script saved as: {slurm_script_path}")
                        print(f"Job output will be in: slurm-<job_id>.out-<node>")
                        print(f"Job errors will be in: slurm-<job_id>.err-<node>")
                    else:
                        error_msg = f"Failed to submit SLURM job: {result.stderr}"
                        print(error_msg, file=sys.stderr)
                        self.log_error(error_msg)
                except Exception as e:
                    error_msg = f"Error submitting SLURM job: {e}"
                    print(error_msg, file=sys.stderr)
                    self.log_error(error_msg)

        except Exception as e:
            error_msg = f"Error in topaz denoise: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def _run_topaz_cross(self, topaz_path, is_local):
        """Run Topaz cross-validation command.

        Executes the Topaz cross-validation workflow to train models with different
        hyperparameters and evaluate performance. Can run locally or generate SLURM scripts.

        Args:
            topaz_path (str): Path to the Topaz executable.
            is_local (bool): If True, run locally; if False, submit to SLURM.

        Example:
            shell._run_topaz_cross('/usr/local/bin/topaz', True)
        """
        try:
            print("Topaz Cross-Validation Setup:")
            print("-" * 30)

            # Prompt for input parameters
            raw_micrographs = input("Enter path to raw micrographs directory: ").strip()
            if not raw_micrographs:
                error_msg = "Raw micrographs directory path is required"
                print(error_msg, file=sys.stderr)
                self.log_error(error_msg)
                return

            # Validate micrographs directory exists
            micrographs_path = Path(raw_micrographs)
            if not micrographs_path.exists():
                error_msg = f"Micrographs directory not found: {raw_micrographs}"
                print(error_msg, file=sys.stderr)
                self.log_error(error_msg)
                return

            # Get particle coordinates file (required for cross-validation)
            raw_particles = input("Enter path to particle coordinates file: ").strip()
            if not raw_particles:
                error_msg = "Particle coordinates file is required for cross-validation"
                print(error_msg, file=sys.stderr)
                self.log_error(error_msg)
                return

            particles_path = Path(raw_particles)
            if not particles_path.exists():
                error_msg = f"Particle coordinates file not found: {raw_particles}"
                print(error_msg, file=sys.stderr)
                self.log_error(error_msg)
                return

            # Get output directory
            output_dir = input(
                "Enter output directory name (default: topaz_cross_output): "
            ).strip()
            if not output_dir:
                output_dir = "topaz_cross_output"

            # Get pixel size for downsampling
            pixel_size = input(
                "Enter pixel size for downsampling in Å/px (default: 8): "
            ).strip()
            if not pixel_size:
                pixel_size = "8"
            else:
                try:
                    float(pixel_size)  # Validate it's a number
                except ValueError:
                    error_msg = "Pixel size must be a number"
                    print(error_msg, file=sys.stderr)
                    self.log_error(error_msg)
                    return

            # Get number of test micrographs to hold out
            test_micrographs = input(
                "Enter number of test micrographs to hold out (default: 10): "
            ).strip()
            if not test_micrographs:
                test_micrographs = "10"
            else:
                try:
                    int(test_micrographs)  # Validate it's a number
                except ValueError:
                    error_msg = "Number of test micrographs must be a number"
                    print(error_msg, file=sys.stderr)
                    self.log_error(error_msg)
                    return

            # Get number of folds for cross-validation
            k_folds = input(
                "Enter number of folds for cross-validation (default: 5): "
            ).strip()
            if not k_folds:
                k_folds = "5"
            else:
                try:
                    int(k_folds)  # Validate it's a number
                except ValueError:
                    error_msg = "Number of folds must be a number"
                    print(error_msg, file=sys.stderr)
                    self.log_error(error_msg)
                    return

            # Get N values for cross-validation (comma-separated)
            n_values_input = input(
                "Enter N values for cross-validation (comma-separated, default: 250,300,350,400,450,500): "
            ).strip()
            if not n_values_input:
                n_values = [250, 300, 350, 400, 450, 500]
            else:
                try:
                    n_values = [int(x.strip()) for x in n_values_input.split(",")]
                except ValueError:
                    error_msg = "N values must be comma-separated numbers"
                    print(error_msg, file=sys.stderr)
                    self.log_error(error_msg)
                    return

            # Create output directories
            proc_root = Path(output_dir)
            proc_micrographs = proc_root / "micrographs"
            model_dir = proc_root / "saved_models"
            data_dir = proc_root / "data"
            cross_dir = model_dir / "cv"

            # Build Topaz commands
            preprocess_cmd = f"{topaz_path} preprocess -v -s {pixel_size} -o {proc_micrographs} {raw_micrographs}/*.mrc"
            convert_cmd = f"{topaz_path} convert -s {pixel_size} -o {proc_root}/particles.txt {raw_particles}"
            split_cmd = f"{topaz_path} train_test_split -n {test_micrographs} --image-dir {proc_micrographs}/micrographs/ {proc_root}/particles.txt"

            if is_local:
                # Run locally
                print(f"\nRunning Topaz cross-validation locally:")
                print(f"Preprocess command: {preprocess_cmd}")
                print(f"Convert command: {convert_cmd}")
                print(f"Train-test split command: {split_cmd}")
                print(f"Cross-validation with {k_folds} folds and N values: {n_values}")

                # Create directories
                proc_micrographs.mkdir(parents=True, exist_ok=True)
                model_dir.mkdir(parents=True, exist_ok=True)
                data_dir.mkdir(parents=True, exist_ok=True)
                cross_dir.mkdir(parents=True, exist_ok=True)

                # Execute commands
                import subprocess

                try:
                    # Step 1: Preprocess
                    print("\nStep 1: Preprocessing micrographs...")
                    result = subprocess.run(
                        preprocess_cmd, shell=True, capture_output=True, text=True
                    )
                    if result.returncode != 0:
                        error_msg = f"Topaz preprocess failed with return code {result.returncode}"
                        print(error_msg, file=sys.stderr)
                        print(f"Error output: {result.stderr}", file=sys.stderr)
                        self.log_error(error_msg)
                        return

                    # Step 2: Convert particle coordinates
                    print("Step 2: Converting particle coordinates...")
                    result = subprocess.run(
                        convert_cmd, shell=True, capture_output=True, text=True
                    )
                    if result.returncode != 0:
                        error_msg = (
                            f"Topaz convert failed with return code {result.returncode}"
                        )
                        print(error_msg, file=sys.stderr)
                        print(f"Error output: {result.stderr}", file=sys.stderr)
                        self.log_error(error_msg)
                        return

                    # Step 3: Train-test split
                    print("Step 3: Performing train-test split...")
                    result = subprocess.run(
                        split_cmd, shell=True, capture_output=True, text=True
                    )
                    if result.returncode != 0:
                        error_msg = f"Topaz train_test_split failed with return code {result.returncode}"
                        print(error_msg, file=sys.stderr)
                        print(f"Error output: {result.stderr}", file=sys.stderr)
                        self.log_error(error_msg)
                        return

                    # Step 4: Cross-validation training
                    print("Step 4: Running cross-validation training...")
                    for n in n_values:
                        for fold in range(int(k_folds)):
                            train_cmd = f"{topaz_path} train -n {n} --num-workers=8 --train-images {proc_root}/image_list_train.txt --train-targets {proc_root}/particles_train.txt -k {k_folds} --fold {fold} -o {cross_dir}/model_n{n}_fold{fold}_training.txt"
                            print(f"Training model with N={n}, fold={fold}...")
                            result = subprocess.run(
                                train_cmd, shell=True, capture_output=True, text=True
                            )
                            if result.returncode != 0:
                                error_msg = f"Topaz train failed for N={n}, fold={fold} with return code {result.returncode}"
                                print(error_msg, file=sys.stderr)
                                print(f"Error output: {result.stderr}", file=sys.stderr)
                                self.log_error(error_msg)
                            else:
                                print(f"✓ Completed training for N={n}, fold={fold}")

                    success_msg = f"Topaz cross-validation completed successfully. Output in: {cross_dir}"
                    print(success_msg)
                    self.log_output(success_msg)

                except Exception as e:
                    error_msg = f"Error running Topaz cross-validation: {e}"
                    print(error_msg, file=sys.stderr)
                    self.log_error(error_msg)
            else:
                # Generate and submit SLURM job
                job_name = "topaz_cross"

                # Create SLURM script content
                slurm_script = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --output={job_name}_%j.out
#SBATCH --error={job_name}_%j.err
#SBATCH --time={self.config_manager.get('slurm.time', '24:00:00')}
#SBATCH --nodes={self.config_manager.get('slurm.nodes', 1)}
#SBATCH --ntasks={self.config_manager.get('slurm.ntasks', 1)}
#SBATCH --cpus-per-task={self.config_manager.get('slurm.cpus_per_task', 4)}
#SBATCH --mem={self.config_manager.get('slurm.mem', '16G')}

set -euo pipefail
set -x

module purge
module load topaz/0.2.5

# Be explicit about threads to avoid oversubscription
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1

cd "${{SLURM_SUBMIT_DIR}}"
echo "WORKDIR: ${{SLURM_SUBMIT_DIR}}"
nvidia-smi || true

# Paths
RAW_MICROS="{raw_micrographs}"
RAW_PARTS="{raw_particles}"
PROC_ROOT="{output_dir}"
PROC_MICROS="${{PROC_ROOT}}/micrographs"
MODEL_DIR="${{PROC_ROOT}}/saved_models"
DATA_DIR="${{PROC_ROOT}}/data"
CROSS_DIR="${{MODEL_DIR}}/cv"

# Make Directories for Preprocessing, Model, and Data
mkdir -p "${{PROC_MICROS}}" "${{MODEL_DIR}}" "${{DATA_DIR}}" "${{CROSS_DIR}}"

# Preprocess (downsample to {pixel_size} Å/px)
srun -u {topaz_path} preprocess -v -s {pixel_size} \\
  -o "${{PROC_MICROS}}/" \\
  "${{RAW_MICROS}}"/*.mrc

# Scale particle coordinates to match downsampling
srun -u {topaz_path} convert -s {pixel_size} \\
  -o "${{PROC_ROOT}}/particles.txt" \\
  "${{RAW_PARTS}}"

# Train-test split
srun -u {topaz_path} train_test_split -n {test_micrographs} --image-dir "${{PROC_MICROS}}/micrographs/" \\
  "${{PROC_ROOT}}/particles.txt"

# Cross-validation training
K={k_folds}
N_VALUES=({', '.join(map(str, n_values))})

# iterate possible values of N
for N in "${{N_VALUES[@]}}"; do
    # iterate each fold
    for ((fold=0;fold<K;fold++)); do
        # where to write results
        PATH="${{CROSS_DIR}}/model_n${{N}}_fold${{fold}}_training.txt"
        echo ${{PATH}}
        # run the training command
        srun -u {topaz_path} train -n ${{N}} --num-workers=8 \\
                       --train-images ${{PROC_ROOT}}/image_list_train.txt \\
                       --train-targets ${{PROC_ROOT}}/particles_train.txt \\
                       -k ${{K}} \\
                       --fold ${{fold}} \\
                       -o ${{PATH}}
    done
done

echo "Topaz cross-validation job completed"
"""

                # Write SLURM script to file
                slurm_script_path = f"{job_name}.slurm"
                with open(slurm_script_path, "w") as f:
                    f.write(slurm_script)

                # Show job summary and ask for confirmation
                print(f"\nJob Summary:")
                print(f"  Job Name: {job_name}")
                print(f"  Raw Micrographs: {raw_micrographs}")
                print(f"  Particle Coordinates: {raw_particles}")
                print(f"  Output Directory: {output_dir}")
                print(f"  Pixel Size: {pixel_size} Å/px")
                print(f"  Test Micrographs: {test_micrographs}")
                print(f"  Cross-validation Folds: {k_folds}")
                print(f"  N Values: {n_values}")
                print(f"  SLURM Script: {slurm_script_path}")
                print(f"  Time Limit: 06:00:00")
                print(f"  Nodes: 1")
                print(f"  CPUs per Task: 4")
                print(f"  Memory: 96G")
                print(f"  GPUs: 1")
                print(f"  Partition: notchpeak-gpu")

                # Ask for confirmation
                while True:
                    confirm = (
                        input("\nSubmit this job to SLURM? (Y/N): ").strip().upper()
                    )
                    if confirm in ["Y", "YES", "y", "yes"]:
                        break
                    elif confirm in ["N", "NO", "n", "no"]:
                        print("Job submission cancelled.")
                        self.log_output("Job submission cancelled by user")
                        return
                    else:
                        print("Please enter Y or N.")

                # Submit job
                try:
                    import subprocess

                    result = subprocess.run(
                        f"sbatch {slurm_script_path}",
                        shell=True,
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode == 0:
                        job_id = result.stdout.strip().split()[
                            -1
                        ]  # Extract job ID from sbatch output
                        success_msg = f"Topaz cross-validation job submitted successfully. Job ID: {job_id}"
                        print(success_msg)
                        self.log_output(success_msg)
                        print(f"SLURM script saved as: {slurm_script_path}")
                        print(f"Job output will be in: slurm-<job_id>.out-<node>")
                        print(f"Job errors will be in: slurm-<job_id>.err-<node>")
                    else:
                        error_msg = f"Failed to submit SLURM job: {result.stderr}"
                        print(error_msg, file=sys.stderr)
                        self.log_error(error_msg)
                except Exception as e:
                    error_msg = f"Error submitting SLURM job: {e}"
                    print(error_msg, file=sys.stderr)
                    self.log_error(error_msg)

        except Exception as e:
            error_msg = f"Error in topaz cross-validation: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def do_analyze_cv(self, arg):
        """Analyze cross-validation results.

        Analyzes cross-validation results from Topaz training to determine optimal
        hyperparameters and generate performance plots and recommendations.

        Args:
            arg (str): Cross-validation parameters. Can include:
                cv_directory: Path to cross-validation results directory
                n_values: Comma-separated list of N values used
                k_folds: Number of folds used in cross-validation

        Usage:
            analyze_cv [cv_directory] [n_values] [k_folds]

        Example:
            analyze_cv saved_models/EMPIAR-10025/cv 250,300,350,400,450,500 5
            analyze_cv
            # Prompts for parameters interactively
        """
        self.log_command("analyze_cv", arg)
        try:
            # Parse arguments
            args = arg.split()

            if len(args) >= 1:
                cv_dir = args[0]
            else:
                cv_dir = input("Enter cross-validation directory path: ").strip()

            if len(args) >= 2:
                n_values_str = args[1]
                n_values = [int(x.strip()) for x in n_values_str.split(",")]
            else:
                n_values_input = input(
                    "Enter N values (comma-separated, default: 250,300,350,400,450,500): "
                ).strip()
                if n_values_input:
                    n_values = [int(x.strip()) for x in n_values_input.split(",")]
                else:
                    n_values = [250, 300, 350, 400, 450, 500]

            if len(args) >= 3:
                k_folds = int(args[2])
            else:
                k_folds_input = input("Enter number of folds (default: 5): ").strip()
                k_folds = int(k_folds_input) if k_folds_input else 5

            # Validate inputs
            cv_path = Path(cv_dir)
            if not cv_path.exists():
                error_msg = f"Cross-validation directory not found: {cv_dir}"
                print(error_msg, file=sys.stderr)
                self.log_error(error_msg)
                return

            print(f"Analyzing cross-validation results from: {cv_dir}")
            print(f"N values: {n_values}")
            print(f"K folds: {k_folds}")

            # Run analysis
            try:
                from .topaz_analysis import analyze_cross_validation

                analysis_results = analyze_cross_validation(
                    cv_dir=cv_dir,
                    n_values=n_values,
                    k_folds=k_folds,
                    output_dir=cv_dir,
                    save_plots=True,
                    show_plots=False,
                )

                print(f"\n=== Cross-validation Analysis Complete ===")
                print(f"Best N value: {analysis_results['best_n']}")
                print(f"Best number of epochs: {analysis_results['best_epoch']}")
                print(f"Best AUPRC: {analysis_results['best_auprc']:.4f}")
                print(
                    f"Recommendation: {analysis_results['recommendations']['recommendation']}"
                )
                print(f"Analysis results saved to: {cv_dir}")

                self.log_output(
                    f"Cross-validation analysis completed. Best N: {analysis_results['best_n']}, Best epochs: {analysis_results['best_epoch']}"
                )

            except ImportError as e:
                error_msg = f"Could not import analysis module: {e}"
                print(error_msg, file=sys.stderr)
                print(
                    "Please install analysis dependencies: pip install numpy pandas matplotlib pillow seaborn"
                )
                self.log_error(error_msg)
            except Exception as e:
                error_msg = f"Cross-validation analysis failed: {e}"
                print(error_msg, file=sys.stderr)
                self.log_error(error_msg)

        except Exception as e:
            error_msg = f"Error in analyze_cv command: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def do_clear(self, arg):
        """Clear the screen.

        Clears the terminal screen for better readability.

        Args:
            arg (str): Not used.

        Example:
            clear
        """
        self.log_command("clear", arg)
        os.system("cls" if os.name == "nt" else "clear")
        self.log_output("Screen cleared")

    def do_pwd(self, arg):
        """Show current working directory.

        Displays the current working directory path.

        Args:
            arg (str): Not used.

        Example:
            pwd
            # Shows current working directory
        """
        self.log_command("pwd", arg)
        output = os.getcwd()
        print(output)
        self.log_output(output)

    def do_ls(self, arg):
        """List files in current directory.

        Lists files and directories in the current directory or a specified path.

        Args:
            arg (str): Optional path to list. If empty, lists current directory.

        Usage:
            ls [path]

        Example:
            ls
            ls /path/to/directory
        """
        self.log_command("ls", arg)
        try:
            path = Path(arg.strip()) if arg.strip() else Path(".")
            if path.exists():
                files = list(path.iterdir())
                output = "\n".join([f.name for f in files])
                print(output)
                self.log_output(output)
            else:
                error_msg = f"Path does not exist: {path}"
                print(error_msg, file=sys.stderr)
                self.log_error(error_msg)
        except Exception as e:
            error_msg = f"Error listing files: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def do_help(self, arg):
        """Show help for commands.

        Displays help information for available commands.

        Args:
            arg (str): Optional command name to get help for.

        Usage:
            help [command]

        Example:
            help
            help model_angelo
        """
        self.log_command("help", arg)
        super().do_help(arg)

    def load_random_quote(self):
        """Load and return a random quote from quotes.txt.

        Reads quotes from the quotes.txt file in the resources directory and
        returns a randomly selected quote.

        Returns:
            str: A randomly selected quote, or None if no quotes are available.

        Example:
            quote = shell.load_random_quote()
            print(quote)
            "Some inspiring quote about science..."
        """
        try:
            quotes_path = Path(__file__).parent / "resources" / "quotes.txt"
            if quotes_path.exists():
                with open(quotes_path, "r", encoding="utf-8") as f:
                    quotes = [line.strip() for line in f if line.strip()]
                if quotes:
                    import random

                    return random.choice(quotes)
            return None
        except Exception:
            return None

    def do_version(self, arg):
        """Display version information.

        Shows detailed version information including project name, version,
        and description from the configuration.

        Args:
            arg (str): Not used.

        Usage:
            version

        Example:
            version
            # Shows version information
        """
        self.log_command("version", arg)
        try:
            metadata = self.config_manager.get_project_metadata()
            version_info = f"""
cryoDL Version Information:
Name: {metadata['name']}
Version: {metadata['version']}
Description: {metadata['description']}
    """
            print(version_info)
            self.log_output(version_info)
        except Exception as e:
            error_msg = f"Error getting version info: {e}"
            print(error_msg)
            self.log_error(error_msg)

    def do_quit(self, arg):
        """Exit the interactive shell.

        Exits the interactive shell, displays a random quote, and logs the session end.

        Args:
            arg (str): Not used.

        Usage:
            quit

        Example:
            quit
            # Exits the shell with a farewell message
        """
        self.log_command("quit", arg)

        # Display random quote
        quote = self.load_random_quote()
        if quote:
            print(f"\nCryoDL Reminds You: {quote}")

        print("Goodbye!")
        return True

    def do_exit(self, arg):
        """Exit the interactive shell.

        Exits the interactive shell, displays a random quote, and logs the session end.
        Alias for the quit command.

        Args:
            arg (str): Not used.

        Usage:
            exit

        Example:
            exit
            # Exits the shell with a farewell message
        """
        self.log_command("exit", arg)

        # Display random quote
        quote = self.load_random_quote()
        if quote:
            print(f"\nCryoDL Reminds You: {quote}")

        print("Goodbye!")
        return True

    def do_EOF(self, arg):
        """Handle Ctrl+D (EOF).

        Handles the end-of-file signal (Ctrl+D) by exiting the shell gracefully
        with a farewell message and quote.

        Args:
            arg (str): Not used.

        Example:
            # Press Ctrl+D
            # Exits the shell with a farewell message
        """
        print()  # New line after Ctrl+D
        self.log_command("EOF", arg)

        # Display random quote
        quote = self.load_random_quote()
        if quote:
            print(f"\nCryoDL Reminds You: {quote}")

        print("Goodbye!")
        return True

    def default(self, line):
        """Handle unknown commands.

        Handles commands that are not recognized by the shell by displaying
        an error message and suggesting to use the help command.

        Args:
            line (str): The unrecognized command line.

        Example:
            unknown_command
            # Shows error message and suggests using help
        """
        self.log_command("unknown", line)
        print(f"Unknown command: {line}")
        print("Type 'help' for available commands.")
        self.log_error(f"Unknown command: {line}")

    def emptyline(self):
        """Handle empty lines.

        Handles empty command lines by doing nothing, which allows users
        to press Enter to get a new prompt without executing any command.

        Example:
            [press Enter]
            # Shows new prompt without executing anything
        """
        pass  # Do nothing for empty lines


def main():
    """Main entry point for interactive CLI.

    Parses command-line arguments and starts the interactive cryoDL shell.
    Handles keyboard interrupts and other exceptions gracefully.

    Command-line Arguments:
        --log-file: Specify custom log file path (default: cryodl.log)

    Example:
        python cli.py
        python cli.py --log-file my_session.log

    Raises:
        SystemExit: On successful completion or error conditions.
    """
    parser = argparse.ArgumentParser(
        description="cryoDL Interactive Configuration Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cryodl                    # Start interactive shell
  cryodl --log-file my.log  # Use custom log file
        """,
    )

    parser.add_argument(
        "--log-file", default="cryodl.log", help="Log file path (default: cryodl.log)"
    )

    args = parser.parse_args()

    try:
        # Initialize config manager
        config_manager = ConfigManager()

        # Start interactive shell
        shell = CryoDLShell(config_manager, args.log_file)
        shell.cmdloop()

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
