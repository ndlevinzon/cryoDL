CLI Commands Reference
=====================

This page provides a comprehensive reference for all available commands in the cryoDL interactive shell.

Configuration Commands
---------------------

init
~~~~

Initialize default configuration.

**Usage:**
.. code-block:: bash

   init [--force]

**Examples:**
.. code-block:: bash

   cryoDL> init
   cryoDL> init --force

**Description:**
Creates a new `config.json` file with default settings. Use `--force` to overwrite existing configuration.

get
~~~

Get configuration value.

**Usage:**
.. code-block:: bash

   get <key>

**Examples:**
.. code-block:: bash

   cryoDL> get dependencies.topaz.path
   cryoDL> get slurm.nodes
   cryoDL> get settings.max_threads

**Description:**
Retrieves and displays the value of a configuration key using dot notation.

set
~~~

Set configuration value.

**Usage:**
.. code-block:: bash

   set <key> <value>

**Examples:**
.. code-block:: bash

   cryoDL> set settings.max_threads 8
   cryoDL> set slurm.time "24:00:00"
   cryoDL> set dependencies.topaz.version "0.2.5"

**Description:**
Sets a configuration value. The key uses dot notation for nested configuration.

show
~~~~

Show full configuration.

**Usage:**
.. code-block:: bash

   show

**Description:**
Displays the complete configuration in JSON format.

reset
~~~~~

Reset configuration to defaults.

**Usage:**
.. code-block:: bash

   reset

**Description:**
Resets all configuration values to their defaults.

Dependency Management
--------------------

add_dependency
~~~~~~~~~~~~~

Add or update dependency path.

**Usage:**
.. code-block:: bash

   add_dependency <name> <path> [version]

**Examples:**
.. code-block:: bash

   cryoDL> add_dependency topaz /usr/local/bin/topaz 0.2.5
   cryoDL> add_dependency model_angelo /opt/model-angelo/bin/model-angelo
   cryoDL> add_dependency relion /usr/local/relion/bin/relion 4.0

**Description:**
Adds or updates a dependency with its path and optional version.

list_dependencies
~~~~~~~~~~~~~~~~

List all configured dependencies.

**Usage:**
.. code-block:: bash

   list_dependencies

**Description:**
Displays all configured dependencies with their paths, versions, and status.

validate_dependencies
~~~~~~~~~~~~~~~~~~~~

Validate all dependency paths.

**Usage:**
.. code-block:: bash

   validate_dependencies

**Description:**
Checks that all configured dependency paths exist and are executable.

Configuration Import/Export
--------------------------

export
~~~~~~

Export configuration to file.

**Usage:**
.. code-block:: bash

   export <path>

**Examples:**
.. code-block:: bash

   cryoDL> export config_backup.json
   cryoDL> export /path/to/config.json

**Description:**
Saves the current configuration to a JSON file.

import
~~~~~~

Import configuration from file.

**Usage:**
.. code-block:: bash

   import <path>

**Examples:**
.. code-block:: bash

   cryoDL> import config_backup.json
   cryoDL> import /path/to/config.json

**Description:**
Loads configuration from a JSON file.

SLURM Commands
--------------

slurm_show
~~~~~~~~~~

Show SLURM configuration.

**Usage:**
.. code-block:: bash

   slurm_show

**Description:**
Displays current SLURM configuration settings.

slurm_update
~~~~~~~~~~~

Update SLURM configuration.

**Usage:**
.. code-block:: bash

   slurm_update [--job-name <name>] [--nodes <n>] [--ntasks <n>] [--cpus-per-task <n>] [--gres-gpu <n>] [--time <time>] [--partition <partition>] [--qos <qos>] [--account <account>] [--mem <mem>] [--output <pattern>] [--error <pattern>]

**Examples:**
.. code-block:: bash

   cryoDL> slurm_update --nodes 2 --gres-gpu 2 --time 12:00:00
   cryoDL> slurm_update --partition notchpeak-gpu --mem 96G
   cryoDL> slurm_update --job-name default --cpus-per-task 8

**Description:**
Updates SLURM configuration parameters. Only specified parameters are updated.

slurm_generate
~~~~~~~~~~~~~

Generate SLURM header.

**Usage:**
.. code-block:: bash

   slurm_generate [--job-name <name>] [--output <file>] [--nodes <n>] [--ntasks <n>] [--cpus-per-task <n>] [--gres-gpu <n>] [--time <time>] [--mem <mem>]

**Examples:**
.. code-block:: bash

   cryoDL> slurm_generate --job-name model_angelo --nodes 2 --gres-gpu 2
   cryoDL> slurm_generate --output my_job.slurm --time 24:00:00

**Description:**
Generates a SLURM header with specified parameters. Use `--output` to save to a file.

Software Integration Commands
----------------------------

model_angelo
~~~~~~~~~~~

Run ModelAngelo for protein structure prediction.

**Usage:**
.. code-block:: bash

   model_angelo [--local]

**Examples:**
.. code-block:: bash

   cryoDL> model_angelo --local
   cryoDL> model_angelo

**Description:**
Runs ModelAngelo for protein structure prediction. Use `--local` to run directly, otherwise submits to SLURM.

**Prompts:**
- MRC file path
- FASTA file path

topaz
~~~~~

Run Topaz for particle picking and analysis.

**Usage:**
.. code-block:: bash

   topaz <command> [--local]

**Commands:**
- `preprocess` - Preprocess micrographs
- `cross` - Run cross-validation
- `model` - Train models (not yet implemented)
- `postprocess` - Post-process results (not yet implemented)

**Examples:**
.. code-block:: bash

   cryoDL> topaz preprocess --local
   cryoDL> topaz cross
   cryoDL> topaz preprocess

**Description:**
Runs Topaz commands for particle picking and analysis. Use `--local` to run directly, otherwise submits to SLURM.

**Preprocess Prompts:**
- Raw micrographs directory
- Particle coordinates file (optional)
- Output directory
- Pixel size for downsampling

**Cross-validation Prompts:**
- Raw micrographs directory
- Particle coordinates file
- Output directory
- Pixel size for downsampling
- Number of test micrographs to hold out
- Number of folds for cross-validation
- N values (comma-separated)

Analysis Commands
----------------

analyze_cv
~~~~~~~~~

Analyze cross-validation results.

**Usage:**
.. code-block:: bash

   analyze_cv [cv_directory] [n_values] [k_folds]

**Examples:**
.. code-block:: bash

   cryoDL> analyze_cv saved_models/EMPIAR-10025/cv
   cryoDL> analyze_cv cv_results 250,300,350,400,450,500 5

**Description:**
Analyzes cross-validation results and generates performance plots and recommendations.

**Prompts (if not provided as arguments):**
- Cross-validation directory path
- N values (comma-separated)
- Number of folds

Utility Commands
---------------

clear
~~~~~

Clear the screen.

**Usage:**
.. code-block:: bash

   clear

**Description:**
Clears the terminal screen.

pwd
~~~

Show current working directory.

**Usage:**
.. code-block:: bash

   pwd

**Description:**
Displays the current working directory.

ls
~~

List files in current directory.

**Usage:**
.. code-block:: bash

   ls [path]

**Examples:**
.. code-block:: bash

   cryoDL> ls
   cryoDL> ls output_dir
   cryoDL> ls /path/to/directory

**Description:**
Lists files and directories. If no path is provided, lists current directory.

help
~~~~

Show help for commands.

**Usage:**
.. code-block:: bash

   help [command]

**Examples:**
.. code-block:: bash

   cryoDL> help
   cryoDL> help topaz
   cryoDL> help model_angelo

**Description:**
Shows help information. Without arguments, lists all available commands.

Exit Commands
------------

quit
~~~~

Exit the interactive shell.

**Usage:**
.. code-block:: bash

   quit

**Description:**
Exits the cryoDL shell and displays a random quote.

exit
~~~~

Exit the interactive shell.

**Usage:**
.. code-block:: bash

   exit

**Description:**
Exits the cryoDL shell and displays a random quote.

EOF (Ctrl+D)
~~~~~~~~~~~

Handle Ctrl+D (EOF).

**Usage:**
.. code-block:: bash

   Ctrl+D

**Description:**
Exits the cryoDL shell and displays a random quote.

Command Examples
---------------

Complete Workflow Example
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Start cryoDL
   cryodl

   # Initialize configuration
   cryoDL> init

   # Add dependencies
   cryoDL> add_dependency topaz /usr/local/bin/topaz 0.2.5
   cryoDL> add_dependency model_angelo /opt/model-angelo/bin/model-angelo

   # Validate dependencies
   cryoDL> validate_dependencies

   # Configure SLURM
   cryoDL> slurm_update --partition notchpeak-gpu --mem 96G --time 24:00:00

   # Run Topaz preprocessing
   cryoDL> topaz preprocess --local
   # Enter prompts...

   # Run cross-validation
   cryoDL> topaz cross --local
   # Enter prompts...

   # Analyze results
   cryoDL> analyze_cv output_dir/saved_models/cv

   # Exit
   cryoDL> quit

Configuration Management Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # View current configuration
   cryoDL> show

   # Get specific values
   cryoDL> get dependencies.topaz.path
   cryoDL> get slurm.nodes

   # Update settings
   cryoDL> set settings.max_threads 16
   cryoDL> set slurm.time "48:00:00"

   # Export configuration
   cryoDL> export my_config.json

   # Import configuration
   cryoDL> import backup_config.json

SLURM Management Example
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # View SLURM settings
   cryoDL> slurm_show

   # Update SLURM configuration
   cryoDL> slurm_update --nodes 4 --gres-gpu 4 --time 48:00:00

   # Generate SLURM header
   cryoDL> slurm_generate --job-name my_job --output job.slurm

   # Submit jobs
   cryoDL> topaz preprocess
   cryoDL> model_angelo

Command Line Options
-------------------

Global Options
~~~~~~~~~~~~~

.. code-block:: bash

   cryodl --log-file my.log  # Use custom log file
   cryodl --help             # Show help

Environment Variables
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   export CRYODL_CONFIG_PATH=/path/to/config.json  # Custom config path
   export CRYODL_LOG_LEVEL=DEBUG                   # Set log level

Logging
-------

All commands and their outputs are automatically logged to `cryodl.log` in the current directory. The log includes:

- Command execution timestamps
- Input parameters
- Output messages
- Error messages
- Session information

Example log entry:
.. code-block:: text

   2024-01-15 10:30:45 - INFO - Command: topaz preprocess --local
   2024-01-15 10:30:45 - INFO - Output: Running Topaz preprocess locally
   2024-01-15 10:30:46 - INFO - Output: Topaz preprocess completed successfully
