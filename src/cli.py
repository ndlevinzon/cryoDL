#!/usr/bin/env python3
"""
Interactive CLI shell for cryoDL configuration manager.
"""

import argparse
import cmd
import datetime
import logging
import os
import sys
import traceback
from pathlib import Path
from typing import List, Optional

from .config_manager import ConfigManager


class CryoDLShell(cmd.Cmd):
    """Interactive shell for cryoDL configuration management."""

    prompt = "cryoDL> "

    def __init__(self, config_manager: ConfigManager, log_file: str = "cryodl.log"):
        super().__init__()
        self.config_manager = config_manager
        self.log_file = log_file
        self.setup_logging()
        self.intro = self.load_banner()

    def load_banner(self):
        """Load and return the ASCII banner."""
        # Get version info from config manager
        metadata = self.config_manager.get_project_metadata()
        version_info = f"Version {metadata['version']}"
        try:
            banner_path = Path(__file__).parent / "resources" / "big_ascii_banner.txt"
            if banner_path.exists():
                with open(banner_path, 'r', encoding='utf-8') as f:
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
        """Set up logging to file."""
        # Create a custom formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Set up file handler
        file_handler = logging.FileHandler(self.log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        # Set up logger
        self.logger = logging.getLogger('cryodl_interactive')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)

        # Log session start
        self.logger.info("=== cryoDL Interactive Session Started ===")
        self.logger.info(f"Working directory: {os.getcwd()}")

    def log_command(self, command: str, args: str = ""):
        """Log user command."""
        full_command = f"{command} {args}".strip()
        self.logger.info(f"Command: {full_command}")

    def log_output(self, output: str):
        """Log command output."""
        if output.strip():
            self.logger.info(f"Output: {output.strip()}")

    def log_error(self, error: str):
        """Log error messages."""
        self.logger.error(f"Error: {error}")

    def do_init(self, arg):
        """Initialize default configuration.

        Usage: init [--force]
        """
        self.log_command("init", arg)
        try:
            force = "--force" in arg
            if force or not self.config_manager.config_path.exists():
                self.config_manager.create_default_config()
                output = f"Configuration initialized at {self.config_manager.config_path}"
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

        Usage: get <key>
        Example: get paths.project_root
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

        Usage: set <key> <value>
        Example: set settings.max_threads 8
        """
        self.log_command("set", arg)
        try:
            parts = arg.split(None, 1)
            if len(parts) < 2:
                print("Error: Key and value are required. Usage: set <key> <value>", file=sys.stderr)
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

        Usage: add_dependency <name> <path> [version]
        Example: add_dependency relion /usr/local/relion/bin/relion 4.0
        """
        self.log_command("add_dependency", arg)
        try:
            parts = arg.split()
            if len(parts) < 2:
                print("Error: Name and path are required. Usage: add_dependency <name> <path> [version]",
                      file=sys.stderr)
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
        """List all configured dependencies."""
        self.log_command("list_dependencies", arg)
        try:
            deps = self.config_manager.list_dependencies()
            output = "\nConfigured Dependencies:\n" + "-" * 50 + "\n"
            for name, info in deps.items():
                status = "✓ Enabled" if info.get('enabled') else "✗ Disabled"
                path = info.get('path', 'Not set')
                version = info.get('version', 'Unknown')
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
        """Validate all dependency paths."""
        self.log_command("validate_dependencies", arg)
        try:
            output = "\nDependency Path Validation:\n" + "-" * 40 + "\n"
            all_valid = True
            for dep_name in self.config_manager.config["dependencies"]:
                is_valid = self.config_manager.validate_dependency_path(dep_name)
                status = "✓ Valid" if is_valid else "✗ Invalid"
                path = self.config_manager.config["dependencies"][dep_name].get("path", "Not set")
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
        """Show full configuration."""
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
        """Reset configuration to defaults."""
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

        Usage: export <path>
        Example: export config_backup.json
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

        Usage: import <path>
        Example: import config_backup.json
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

        Usage: slurm_generate [--job-name <name>] [--output <file>] [--nodes <n>] [--ntasks <n>] [--cpus-per-task <n>] [--gres-gpu <n>] [--time <time>] [--mem <mem>]
        Example: slurm_generate --job-name model_angelo --nodes 2 --gres-gpu 2
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
                    overrides['nodes'] = int(args[i + 1])
                    i += 2
                elif args[i] == "--ntasks" and i + 1 < len(args):
                    overrides['ntasks'] = int(args[i + 1])
                    i += 2
                elif args[i] == "--cpus-per-task" and i + 1 < len(args):
                    overrides['cpus_per_task'] = int(args[i + 1])
                    i += 2
                elif args[i] == "--gres-gpu" and i + 1 < len(args):
                    overrides['gres_gpu'] = int(args[i + 1])
                    i += 2
                elif args[i] == "--time" and i + 1 < len(args):
                    overrides['time'] = args[i + 1]
                    i += 2
                elif args[i] == "--mem" and i + 1 < len(args):
                    overrides['mem'] = args[i + 1]
                    i += 2
                else:
                    i += 1

            header = self.config_manager.generate_slurm_header(job_name, **overrides)

            if output_file:
                self.config_manager.save_slurm_header(output_file, job_name, **overrides)
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
        """Show SLURM configuration."""
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

        Usage: slurm_update [--job-name <name>] [--nodes <n>] [--ntasks <n>] [--cpus-per-task <n>] [--gres-gpu <n>] [--time <time>] [--partition <partition>] [--qos <qos>] [--account <account>] [--mem <mem>] [--output <pattern>] [--error <pattern>]
        Example: slurm_update --nodes 2 --gres-gpu 2 --time 12:00:00
        """
        self.log_command("slurm_update", arg)
        try:
            # Parse arguments (simplified parsing for interactive mode)
            args = arg.split()
            updates = {}

            i = 0
            while i < len(args):
                if args[i] == "--job-name" and i + 1 < len(args):
                    updates['job_name'] = args[i + 1]
                    i += 2
                elif args[i] == "--nodes" and i + 1 < len(args):
                    updates['nodes'] = int(args[i + 1])
                    i += 2
                elif args[i] == "--ntasks" and i + 1 < len(args):
                    updates['ntasks'] = int(args[i + 1])
                    i += 2
                elif args[i] == "--cpus-per-task" and i + 1 < len(args):
                    updates['cpus_per_task'] = int(args[i + 1])
                    i += 2
                elif args[i] == "--gres-gpu" and i + 1 < len(args):
                    updates['gres_gpu'] = int(args[i + 1])
                    i += 2
                elif args[i] == "--time" and i + 1 < len(args):
                    updates['time'] = args[i + 1]
                    i += 2
                elif args[i] == "--partition" and i + 1 < len(args):
                    updates['partition'] = args[i + 1]
                    i += 2
                elif args[i] == "--qos" and i + 1 < len(args):
                    updates['qos'] = args[i + 1]
                    i += 2
                elif args[i] == "--account" and i + 1 < len(args):
                    updates['account'] = args[i + 1]
                    i += 2
                elif args[i] == "--mem" and i + 1 < len(args):
                    updates['mem'] = args[i + 1]
                    i += 2
                elif args[i] == "--output" and i + 1 < len(args):
                    updates['output'] = args[i + 1]
                    i += 2
                elif args[i] == "--error" and i + 1 < len(args):
                    updates['error'] = args[i + 1]
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

    def do_model_angelo(self, arg):
        """Run ModelAngelo for protein structure prediction.

        Usage: model_angelo [--local]
        Example: model_angelo --local
        """
        self.log_command("model_angelo", arg)
        try:
            # Check if model_angelo is configured
            model_angelo_path = self.config_manager.get("dependencies.model_angelo.path")
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
                    result = subprocess.run(model_angelo_cmd, shell=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        success_msg = f"ModelAngelo completed successfully. Output in: {output_dir}"
                        print(success_msg)
                        self.log_output(success_msg)
                    else:
                        error_msg = f"ModelAngelo failed with return code {result.returncode}"
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
                partition = self.config_manager.get('slurm.partition')
                if partition:
                    slurm_script += f"#SBATCH --partition={partition}\n"

                qos = self.config_manager.get('slurm.qos')
                if qos:
                    slurm_script += f"#SBATCH --qos={qos}\n"

                account = self.config_manager.get('slurm.account')
                if account:
                    slurm_script += f"#SBATCH --account={account}\n"

                gres_gpu = self.config_manager.get('slurm.gres_gpu')
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
                with open(slurm_script_path, 'w') as f:
                    f.write(slurm_script)

                # Show job summary and ask for confirmation
                print(f"\nJob Summary:")
                print(f"  Job Name: {job_name}")
                print(f"  MRC File: {mrc_file}")
                print(f"  FASTA File: {fasta_file}")
                print(f"  Output Directory: {output_dir}")
                print(f"  SLURM Script: {slurm_script_path}")
                print(f"  Time Limit: {self.config_manager.get('slurm.time', '24:00:00')}")
                print(f"  Nodes: {self.config_manager.get('slurm.nodes', 1)}")
                print(f"  CPUs per Task: {self.config_manager.get('slurm.cpus_per_task', 4)}")
                print(f"  Memory: {self.config_manager.get('slurm.mem', '16G')}")

                gres_gpu = self.config_manager.get('slurm.gres_gpu')
                if gres_gpu:
                    print(f"  GPUs: {gres_gpu}")

                partition = self.config_manager.get('slurm.partition')
                if partition:
                    print(f"  Partition: {partition}")

                # Ask for confirmation
                while True:
                    confirm = input("\nSubmit this job to SLURM? (Y/N): ").strip().upper()
                    if confirm in ['Y', 'YES', 'y', 'yes']:
                        break
                    elif confirm in ['N', 'NO', 'n', 'no']:
                        print("Job submission cancelled.")
                        self.log_output("Job submission cancelled by user")
                        return
                    else:
                        print("Please enter Y or N.")

                # Submit job

                try:
                    import subprocess
                    result = subprocess.run(f"sbatch {slurm_script_path}", shell=True, capture_output=True,
                                            text=True)

                    if result.returncode == 0:
                        job_id = result.stdout.strip().split()[-1]  # Extract job ID from sbatch output
                        success_msg = f"ModelAngelo job submitted successfully. Job ID: {job_id}"
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

        Usage: topaz <command> [--local]
        Commands: preprocess, model, postprocess
        Examples:
          topaz preprocess --local
          topaz preprocess
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
                print("Error: Topaz command required. Usage: topaz <command> [--local]")
                print("Available commands: preprocess, model, postprocess")
                self.log_error("Missing topaz command")
                return

            command = args[0]
            is_local = "--local" in args

            if command == "preprocess":
                self._run_topaz_preprocess(topaz_path, is_local)
            elif command == "model":
                print("Topaz model command not yet implemented")
                self.log_output("Topaz model command not yet implemented")
            elif command == "postprocess":
                print("Topaz postprocess command not yet implemented")
                self.log_output("Topaz postprocess command not yet implemented")
            else:
                error_msg = f"Unknown topaz command: {command}"
                print(error_msg, file=sys.stderr)
                print("Available commands: preprocess, model, postprocess")
                self.log_error(error_msg)

        except Exception as e:
            error_msg = f"Error in topaz command: {e}"
            print(error_msg, file=sys.stderr)
            self.log_error(error_msg)

    def _run_topaz_preprocess(self, topaz_path, is_local):
        """Run Topaz preprocess command."""
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
                "Enter path to particle coordinates file (optional, press Enter to skip): ").strip()
            particles_path = None
            if raw_particles:
                particles_path = Path(raw_particles)
                if not particles_path.exists():
                    error_msg = f"Particle coordinates file not found: {raw_particles}"
                    print(error_msg, file=sys.stderr)
                    self.log_error(error_msg)
                    return

            # Get output directory
            output_dir = input("Enter output directory name (default: topaz_preprocess_output): ").strip()
            if not output_dir:
                output_dir = "topaz_preprocess_output"

            # Get pixel size for downsampling
            pixel_size = input("Enter pixel size for downsampling in Å/px (default: 8): ").strip()
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
                    result = subprocess.run(preprocess_cmd, shell=True, capture_output=True, text=True)
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
                        result = subprocess.run(convert_cmd, shell=True, capture_output=True, text=True)
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
                with open(slurm_script_path, 'w') as f:
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
                    confirm = input("\nSubmit this job to SLURM? (Y/N): ").strip().upper()
                    if confirm in ['Y', 'YES', 'y', 'yes']:
                        break
                    elif confirm in ['N', 'NO', 'n', 'no']:
                        print("Job submission cancelled.")
                        self.log_output("Job submission cancelled by user")
                        return
                    else:
                        print("Please enter Y or N.")

                # Submit job
                try:
                    import subprocess
                    result = subprocess.run(f"sbatch {slurm_script_path}", shell=True, capture_output=True,
                                            text=True)

                    if result.returncode == 0:
                        job_id = result.stdout.strip().split()[-1]  # Extract job ID from sbatch output
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

    def _run_topaz_cross(self, topaz_path, is_local):
        """Run Topaz cross-validation command."""
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
            output_dir = input("Enter output directory name (default: topaz_cross_output): ").strip()
            if not output_dir:
                output_dir = "topaz_cross_output"

            # Get pixel size for downsampling
            pixel_size = input("Enter pixel size for downsampling in Å/px (default: 8): ").strip()
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
            test_micrographs = input("Enter number of test micrographs to hold out (default: 10): ").strip()
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
            k_folds = input("Enter number of folds for cross-validation (default: 5): ").strip()
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
                "Enter N values for cross-validation (comma-separated, default: 250,300,350,400,450,500): ").strip()
            if not n_values_input:
                n_values = [250, 300, 350, 400, 450, 500]
            else:
                try:
                    n_values = [int(x.strip()) for x in n_values_input.split(',')]
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
                    result = subprocess.run(preprocess_cmd, shell=True, capture_output=True, text=True)
                    if result.returncode != 0:
                        error_msg = f"Topaz preprocess failed with return code {result.returncode}"
                        print(error_msg, file=sys.stderr)
                        print(f"Error output: {result.stderr}", file=sys.stderr)
                        self.log_error(error_msg)
                        return

                    # Step 2: Convert particle coordinates
                    print("Step 2: Converting particle coordinates...")
                    result = subprocess.run(convert_cmd, shell=True, capture_output=True, text=True)
                    if result.returncode != 0:
                        error_msg = f"Topaz convert failed with return code {result.returncode}"
                        print(error_msg, file=sys.stderr)
                        print(f"Error output: {result.stderr}", file=sys.stderr)
                        self.log_error(error_msg)
                        return

                    # Step 3: Train-test split
                    print("Step 3: Performing train-test split...")
                    result = subprocess.run(split_cmd, shell=True, capture_output=True, text=True)
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
                            result = subprocess.run(train_cmd, shell=True, capture_output=True, text=True)
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
                with open(slurm_script_path, 'w') as f:
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
                    confirm = input("\nSubmit this job to SLURM? (Y/N): ").strip().upper()
                    if confirm in ['Y', 'YES', 'y', 'yes']:
                        break
                    elif confirm in ['N', 'NO', 'n', 'no']:
                        print("Job submission cancelled.")
                        self.log_output("Job submission cancelled by user")
                        return
                    else:
                        print("Please enter Y or N.")

                # Submit job
                try:
                    import subprocess
                    result = subprocess.run(f"sbatch {slurm_script_path}", shell=True, capture_output=True,
                                            text=True)

                    if result.returncode == 0:
                        job_id = result.stdout.strip().split()[-1]  # Extract job ID from sbatch output
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

        Usage: analyze_cv [cv_directory] [n_values] [k_folds]
        Example: analyze_cv saved_models/EMPIAR-10025/cv 250,300,350,400,450,500 5
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
                n_values = [int(x.strip()) for x in n_values_str.split(',')]
            else:
                n_values_input = input("Enter N values (comma-separated, default: 250,300,350,400,450,500): ").strip()
                if n_values_input:
                    n_values = [int(x.strip()) for x in n_values_input.split(',')]
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
                    show_plots=False
                )

                print(f"\n=== Cross-validation Analysis Complete ===")
                print(f"Best N value: {analysis_results['best_n']}")
                print(f"Best number of epochs: {analysis_results['best_epoch']}")
                print(f"Best AUPRC: {analysis_results['best_auprc']:.4f}")
                print(f"Recommendation: {analysis_results['recommendations']['recommendation']}")
                print(f"Analysis results saved to: {cv_dir}")

                self.log_output(
                    f"Cross-validation analysis completed. Best N: {analysis_results['best_n']}, Best epochs: {analysis_results['best_epoch']}")

            except ImportError as e:
                error_msg = f"Could not import analysis module: {e}"
                print(error_msg, file=sys.stderr)
                print("Please install analysis dependencies: pip install numpy pandas matplotlib pillow seaborn")
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
        """Clear the screen."""
        self.log_command("clear", arg)
        os.system('cls' if os.name == 'nt' else 'clear')
        self.log_output("Screen cleared")

    def do_pwd(self, arg):
        """Show current working directory."""
        self.log_command("pwd", arg)
        output = os.getcwd()
        print(output)
        self.log_output(output)

    def do_ls(self, arg):
        """List files in current directory."""
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
        """Show help for commands."""
        self.log_command("help", arg)
        super().do_help(arg)

    def load_random_quote(self):
        """Load and return a random quote from quotes.txt."""
        try:
            quotes_path = Path(__file__).parent / "resources" / "quotes.txt"
            if quotes_path.exists():
                with open(quotes_path, 'r', encoding='utf-8') as f:
                    quotes = [line.strip() for line in f if line.strip()]
                if quotes:
                    import random
                    return random.choice(quotes)
            return None
        except Exception:
            return None

    def do_version(self, arg):
        """Display version information.

        Usage: version
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
        """Exit the interactive shell."""
        self.log_command("quit", arg)

        # Display random quote
        quote = self.load_random_quote()
        if quote:
            print(f"\nCryoDL Reminds You: {quote}")

        print("Goodbye!")
        return True

    def do_exit(self, arg):
        """Exit the interactive shell."""
        self.log_command("exit", arg)

        # Display random quote
        quote = self.load_random_quote()
        if quote:
            print(f"\nCryoDL Reminds You: {quote}")

        print("Goodbye!")
        return True

    def do_EOF(self, arg):
        """Handle Ctrl+D (EOF)."""
        print()  # New line after Ctrl+D
        self.log_command("EOF", arg)

        # Display random quote
        quote = self.load_random_quote()
        if quote:
            print(f"\nCryoDL Reminds You: {quote}")

        print("Goodbye!")
        return True

    def default(self, line):
        """Handle unknown commands."""
        self.log_command("unknown", line)
        print(f"Unknown command: {line}")
        print("Type 'help' for available commands.")
        self.log_error(f"Unknown command: {line}")

    def emptyline(self):
        """Handle empty lines."""
        pass  # Do nothing for empty lines


def main():
    """Main entry point for interactive CLI."""
    parser = argparse.ArgumentParser(
        description="cryoDL Interactive Configuration Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cryodl                    # Start interactive shell
  cryodl --log-file my.log  # Use custom log file
        """
    )

    parser.add_argument(
        '--log-file',
        default='cryodl.log',
        help='Log file path (default: cryodl.log)'
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
