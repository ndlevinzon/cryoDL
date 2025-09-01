Tutorial 1: Using Model-Angelo with cryoDL FastaBuilder
================

In this tutorial, we will walk through the process of using the Model-Angelo tool integrated within cryoDL to build and refine protein structures from cryo-EM maps. This tutorial assumes you have a basic understanding of cryo-EM data processing and are familiar with command-line interfaces.

.. note::
   Model-Angelo is a powerful stand-alone tool for automated model building and refinement. This tutorial will guide you through its integration with cryoDL, allowing for streamlined workflows in structural biology. Please refer to the official Model-Angelo citation and documentation for more detailed information on its capabilities and usage.


------------

Before starting this tutorial, make sure you have:

* cryoDL installed and configured (see :ref:`installation`)
* Have Model-Angelo installed (see `Model-Angelo GitHub)
* Access to cryo-EM maps (.mrc) and corresponding sequence data (PDB or UniProt IDs)

Learning Objectives
------------------

By the end of this tutorial, you will be able to:

* Build FASTA files using cryoDL's FastaBuilder, using either PDB or UniProt IDs
* Run Model-Angelo through cryoDL to generate protein models from cryo-EM maps
* Annotate the generated models with sequence information

Step 1: Building a FASTA File
--------------------------

Before running Model-Angelo, you need to create a FASTA file containing the sequences of the proteins you want to model. You can do this using cryoDL's FastaBuilder.

First, CD into the directory containing your Cryo-EM maps. We will build our FASTA at this same directory.

**Using the command line:**

.. code-block:: bash

   $ cd /path/to/your/cryoem/maps

We are now in the directory where our cryo-EM maps are located. This is important because we will be running Model-Angelo in this directory later.

Next, we will launch cryoDL and use the FastaBuilder command to create a FASTA file. You can provide either PDB IDs or UniProt IDs. In this example, we will use both methods with the --multiple flag.

**Using the command line:**

.. code-block:: text

    $ cryoDL
    cryoDL> fasta --multiple 4B2T Q8N3Y1
    INFO:cryodl_interactive:Command: fasta --multiple 4B2T Q8N3Y1
    Processing multiple identifiers: 4B2T, Q8N3Y1
    Output file: combined_protein.fasta
    INFO:src.build_fasta:Processing PDB ID: 4B2T
    INFO:src.build_fasta:Processing UniProt ID: Q8N3Y1
    Successfully created FASTA file: combined_protein.fasta | Successfully processed: PDB:4B2T, UniProt:Q8N3Y1
    INFO:cryodl_interactive:Output: Successfully created FASTA file: combined_protein.fasta

We now have a FASTA file named `combined_protein.fasta` in our current directory, which contains the sequences for the proteins with PDB ID 4B2T and UniProt ID Q8N3Y1.

Step 2: Running Model-Angelo
---------------------------

Once you have your FASTA file ready, you can run Model-Angelo to build models from your cryo-EM maps.

**Using the cryoDL command line:**

.. code-block:: text

    cryoDL> model-angelo
    INFO:cryodl_interactive:Command: fasta --multiple 4B2T Q8N3Y1
    Processing multiple identifiers: 4B2T, Q8N3Y1
    Output file: combined_protein.fasta
    INFO:src.build_fasta:Processing PDB ID: 4B2T
    INFO:src.build_fasta:Processing UniProt ID: Q8N3Y1
    Successfully created FASTA file: combined_protein.fasta | Successfully processed: PDB:4B2T, UniProt:Q8N3Y1
    INFO:cryodl_interactive:Output: Successfully created FASTA file: combined_protein.fasta

**What these do:**

Explain the purpose of each command.

**Expected results:**

Describe what should happen after running these commands.

Step 3: [Third Step Title]
--------------------------

Continue with additional steps as needed.

**Interactive prompts:**

If the command prompts for input, show the interaction:

.. code-block:: bash

   cryoDL> topaz preprocess --local
   Enter path to micrographs: /path/to/micrographs
   Enter path to particles file: /path/to/particles.txt
   Enter output directory: output_dir
   Enter pixel size: 1.0

**File structure created:**

Show what files and directories should be created:

.. code-block:: text

   output_dir/
   ├── preprocessed/
   │   ├── micrographs.mrcs
   │   └── particles.txt
   ├── logs/
   │   └── preprocessing.log
   └── config.json

Verification
-----------

How to verify that everything worked correctly:

.. code-block:: bash

   # Check that files were created
   cryoDL> ls output_dir/

   # Validate the results
   cryoDL> [validation command]

**Expected verification output:**

.. code-block:: text

   [Show what successful verification looks like]

Advanced Options
---------------

Optional advanced configurations or variations:

.. code-block:: bash

   # Advanced option 1
   cryoDL> [command] --advanced-flag

   # Advanced option 2
   cryoDL> [command] --custom-parameter value

**When to use advanced options:**

Explain when and why you might want to use these advanced features.

Troubleshooting
--------------

Common issues and their solutions:

**Issue 1: [Common Problem]**

.. code-block:: text

   Error: [error message]

**Solution:**

.. code-block:: bash

   # Fix command
   cryoDL> [fix command]

**Issue 2: [Another Common Problem]**

.. code-block:: text

   Error: [error message]

**Solution:**

.. code-block:: bash

   # Fix command
   cryoDL> [fix command]

**Getting Help:**

If you're still having issues:

.. code-block:: bash

   # Get help for the command
   cryoDL> help [command_name]

   # Check the logs
   cryoDL> ls *.log

Next Steps
----------

What to do after completing this tutorial:

* [Link to related tutorial or documentation]
* [Link to advanced usage guide]
* [Link to troubleshooting guide]

**Related Documentation:**

* :ref:`cli_commands` - Complete command reference
* :ref:`api_reference` - Python API documentation
* :ref:`configuration` - Configuration options

**Practice Exercises:**

Optional exercises to reinforce learning:

1. **Exercise 1**: [Description of practice exercise]
   * Try [specific task]
   * Expected outcome: [what should happen]

2. **Exercise 2**: [Another practice exercise]
   * Try [specific task]
   * Expected outcome: [what should happen]

Summary
-------

Brief summary of what was accomplished in this tutorial.

**Key takeaways:**

* [Key point 1]
* [Key point 2]
* [Key point 3]

**Commands learned:**

* ``[command1]`` - [what it does]
* ``[command2]`` - [what it does]
* ``[command3]`` - [what it does]

---

.. note::
   **Template Usage**: When creating a new tutorial from this template:

   1. Copy this file and rename it to ``tutorial_[topic].rst``
   2. Replace all placeholder text in [brackets] with actual content
   3. Remove any sections that aren't relevant to your tutorial
   4. Add the tutorial to the main documentation index
   5. Test all commands and examples to ensure they work correctly

**Template Sections to Customize:**

* **Title and Description**: Replace with your tutorial's specific topic
* **Prerequisites**: List what users need before starting
* **Learning Objectives**: What users will learn
* **Steps**: Replace with your actual tutorial steps
* **Commands**: Use real cryoDL commands with actual examples
* **Output**: Show real expected output
* **Troubleshooting**: Address common issues for your specific topic
* **Next Steps**: Link to relevant documentation
