#!/usr/bin/env python3
"""
Command-line interface for cryoDL configuration manager.
"""

import argparse
import sys
from pathlib import Path
from config_manager import ConfigManager


def main():
    parser = argparse.ArgumentParser(
        description="cryoDL Configuration Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py init                    # Initialize default configuration
  python cli.py get paths.project_root  # Get project root path
  python cli.py set settings.max_threads 8  # Set max threads to 8
  python cli.py add-dependency relion /usr/local/relion/bin/relion 4.0
  python cli.py list-dependencies       # List all dependencies
  python cli.py validate-dependencies   # Validate all dependency paths
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize default configuration')
    init_parser.add_argument('--force', action='store_true', help='Force overwrite existing config')

    # Get command
    get_parser = subparsers.add_parser('get', help='Get configuration value')
    get_parser.add_argument('key', help='Configuration key (e.g., paths.project_root)')

    # Set command
    set_parser = subparsers.add_parser('set', help='Set configuration value')
    set_parser.add_argument('key', help='Configuration key (e.g., settings.max_threads)')
    set_parser.add_argument('value', help='Value to set')

    # Add dependency command
    dep_parser = subparsers.add_parser('add-dependency', help='Add or update dependency path')
    dep_parser.add_argument('name', help='Dependency name (e.g., relion, cryosparc)')
    dep_parser.add_argument('path', help='Path to dependency executable or directory')
    dep_parser.add_argument('version', nargs='?', default='', help='Dependency version')

    # List dependencies command
    subparsers.add_parser('list-dependencies', help='List all configured dependencies')

    # Validate dependencies command
    subparsers.add_parser('validate-dependencies', help='Validate all dependency paths')

    # Show config command
    subparsers.add_parser('show', help='Show full configuration')

    # Reset command
    subparsers.add_parser('reset', help='Reset configuration to defaults')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export configuration to file')
    export_parser.add_argument('path', help='Export file path')

    # Import command
    import_parser = subparsers.add_parser('import', help='Import configuration from file')
    import_parser.add_argument('path', help='Import file path')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize config manager
    config_manager = ConfigManager()

    try:
        if args.command == 'init':
            if args.force or not config_manager.config_path.exists():
                config_manager.create_default_config()
                print(f"Configuration initialized at {config_manager.config_path}")
            else:
                print("Configuration already exists. Use --force to overwrite.")

        elif args.command == 'get':
            value = config_manager.get(args.key)
            if value is not None:
                print(value)
            else:
                print(f"Key '{args.key}' not found", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'set':
            config_manager.set(args.key, args.value)
            print(f"Set {args.key} = {args.value}")

        elif args.command == 'add-dependency':
            config_manager.update_dependency_path(args.name, args.path, args.version)
            print(f"Updated {args.name} dependency")

        elif args.command == 'list-dependencies':
            deps = config_manager.list_dependencies()
            print("\nConfigured Dependencies:")
            print("-" * 50)
            for name, info in deps.items():
                status = "✓ Enabled" if info.get('enabled') else "✗ Disabled"
                path = info.get('path', 'Not set')
                version = info.get('version', 'Unknown')
                print(f"{name:12} {status:12} {path}")
                if version:
                    print(f"{'':12} {'':12} Version: {version}")
                print()

        elif args.command == 'validate-dependencies':
            print("\nDependency Path Validation:")
            print("-" * 40)
            all_valid = True
            for dep_name in config_manager.config["dependencies"]:
                is_valid = config_manager.validate_dependency_path(dep_name)
                status = "✓ Valid" if is_valid else "✗ Invalid"
                path = config_manager.config["dependencies"][dep_name].get("path", "Not set")
                print(f"{dep_name:12} {status:8} {path}")
                if not is_valid and path:
                    all_valid = False

            if all_valid:
                print("\nAll dependency paths are valid!")
            else:
                print("\nSome dependency paths are invalid. Please check the paths.")
                sys.exit(1)

        elif args.command == 'show':
            import json
            print(json.dumps(config_manager.config, indent=4))

        elif args.command == 'reset':
            config_manager.reset_config()
            print("Configuration reset to defaults")

        elif args.command == 'export':
            config_manager.export_config(args.path)
            print(f"Configuration exported to {args.path}")

        elif args.command == 'import':
            config_manager.import_config(args.path)
            print(f"Configuration imported from {args.path}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
