Tutorial Template
================

This is a template for creating tutorials in the cryoDL documentation. Copy this template and customize it for your specific tutorial.

.. note::
   This is a template file. When creating a new tutorial, copy this file and rename it to something like ``tutorial_my_topic.rst``, then customize the content.

Tutorial Title
-------------

Brief description of what this tutorial will teach users.

Prerequisites
------------

Before starting this tutorial, make sure you have:

* cryoDL installed and configured (see :ref:`installation`)
* Basic familiarity with command line interfaces
* [Add any other prerequisites specific to this tutorial]

*Optional prerequisites:*

* [Add any optional software or knowledge that would be helpful]

Learning Objectives
------------------

By the end of this tutorial, you will be able to:

* [Objective 1]
* [Objective 2]
* [Objective 3]

Overview
--------

Brief overview of what the tutorial covers and why it's useful.

.. note::
   You can add notes, warnings, or tips using admonitions like this.

.. warning::
   Use warnings for important safety information or potential pitfalls.

.. tip::
   Use tips for helpful hints and best practices.

Step 1: [First Step Title]
--------------------------

Description of the first step.

**Command to run:**

.. code-block:: bash

   cryoDL> [your command here]

**What this does:**

Explain what the command does and why it's necessary.

**Expected output:**

.. code-block:: text

   [Show expected output or response]

**Troubleshooting:**

If you encounter issues:

* **Problem**: [Describe the problem]
  **Solution**: [Provide the solution]

* **Problem**: [Another common issue]
  **Solution**: [Another solution]

Step 2: [Second Step Title]
---------------------------

Description of the second step.

**Commands to run:**

.. code-block:: bash

   cryoDL> [first command]
   cryoDL> [second command]

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
