# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import re

sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------

project = 'cryoDL'
copyright = '2025, cryoDL Team'
author = 'cryoDL Team'

# The full version, including alpha/beta/rc tags
release = '0.1.0'


# -- General configuration ---------------------------------------------------

# --- Autodoc hook: turn "Usage:" and "Examples:" text into code blocks automatically -------
def _usage_examples_to_codeblock(app, what, name, obj, options, lines):
    """
    Convert 'Usage:' and 'Examples:' sections in raw Google-style docstrings into proper code blocks.
    """
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        line_lower = line.strip().lower()

        if line_lower in ["usage:", "examples:"]:
            # Keep the original section header
            out.append(line)
            out.append("")
            i += 1

            # Collect following non-empty lines until a blank line or a new section header
            code_lines = []
            while i < len(lines):
                nxt = lines[i]
                if not nxt.strip():
                    break
                if re.match(r"^[A-Z][A-Za-z0-9 _-]*:\s*$", nxt.strip()):  # next section
                    break
                code_lines.append(nxt.rstrip())
                i += 1

            # If we have code lines, format them as a code block
            if code_lines:
                out.append(".. code-block:: bash")
                out.append("")
                for code_line in code_lines:
                    out.append("    " + code_line)
                out.append("")
            continue

        out.append(line)
        i += 1

    lines[:] = out


# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.githubpages',
    'sphinx_rtd_theme',
    'sphinx_copybutton',
    'sphinx.ext.autosummary',
    'myst_parser',  # Enable MyST parser for Markdown support
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    'navigation_depth': 4,
    'titles_only': False,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'logo_only': False,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'style_nav_header_background': '#2980B9',
    'canonical_url': '',
    'analytics_id': '',
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
        'donate.html',
    ]
}

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'cryoDLdoc'

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    'papersize': 'a4paper',

    # The font size ('10pt', '11pt' or '12pt').
    'pointsize': '11pt',

    # Additional stuff for the LaTeX preamble.
    'preamble': '',

    # Latex figure (float) alignment
    'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'cryoDL.tex', 'cryoDL Documentation',
     'cryoDL Team', 'manual'),
]

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'cryodl', 'cryoDL Documentation',
     [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'cryoDL', 'cryoDL Documentation',
     author, 'cryoDL', 'A Python manager for cryo-EM software wrappers.',
     'Miscellaneous'),
]

# -- Extension configuration -------------------------------------------------

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False  # Don't use admonitions for examples
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True
napoleon_preprocess_types = True
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Custom sections for Napoleon
napoleon_custom_sections = [
    ("Usage", "Examples"),
    ("Example", "Examples"),
]

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
    'typing': ('https://docs.python.org/3/library/typing.html', None),
}

# Todo settings
todo_include_todos = True

# Autosummary settings
autosummary_generate = True


# Pydoctor configuration - commented out due to integration issues
# extensions += ["pydoctor.sphinx_ext.build_apidocs"]

# pydoctor_args = [
#     "--project-name=cryoDL",
#     "--docformat=google",
#     "--add-package=../src/",
#     "--html-output=api",
#     "--theme=readthedocs",
#     "--intersphinx=https://docs.python.org/3/objects.inv",
# ]

# -- Custom CSS for better styling -------------------------------------------

def setup(app):
    app.add_css_file('custom.css')
    # Enable the docstring transformer for Usage and Examples sections:
    app.connect('autodoc-process-docstring', _usage_examples_to_codeblock)





