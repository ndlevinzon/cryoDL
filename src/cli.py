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

    prompt = "cryodl> "

    def __init__(self, config_manager: ConfigManager, log_file: str = "cryodl.log"):
        super().__init__()
        self.config_manager = config_manager
        self.log_file = log_file
        self.setup_logging()
        self.intro = self.load_banner()

    def load_banner(self):
        """Load and return the ASCII banner."""
        try:
            banner_path = Path(__file__).parent / "resources" / "big_ascii_banner.txt"
            if banner_path.exists():
                with open(banner_path, 'r', encoding='utf-8') as f:
                    banner = f.read().strip()
                return f"""
{banner}

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

    def do_quit(self, arg):
        """Exit the interactive shell."""
        self.log_command("quit", arg)

        # Display random quote
        quote = self.load_random_quote()
        if quote:
            print(f"\nCryoDL Reminds You: \"{quote}\"")

        print("Goodbye!")
        return True

    def do_exit(self, arg):
        """Exit the interactive shell."""
        self.log_command("exit", arg)

        # Display random quote
        quote = self.load_random_quote()
        if quote:
            print(f"\nCryoDL Reminds You: \"{quote}\"")

        print("Goodbye!")
        return True

    def do_EOF(self, arg):
        """Handle Ctrl+D (EOF)."""
        print()  # New line after Ctrl+D
        self.log_command("EOF", arg)

        # Display random quote
        quote = self.load_random_quote()
        if quote:
            print(f"\nCryoDL Reminds You: \"{quote}\"")

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
