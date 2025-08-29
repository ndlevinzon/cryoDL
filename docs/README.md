# cryoDL Documentation

This directory contains the Sphinx documentation for the cryoDL project.

## Quick Start

### Building Documentation

1. **Install documentation dependencies:**
   ```bash
   pip install -r docs/requirements.txt
   ```

2. **Build HTML documentation:**
   ```bash
   sphinx-build -b html docs docs/_build/html
   ```

3. **View documentation:**
   ```bash
   sphinx-build -b serve docs docs/_build/serve
   ```
   Then open http://localhost:8000 in your browser.

### Full Build Process

For a complete documentation build:

```bash
cd docs
sphinx-build -b full docs docs/_build/html
```

This will:
- Install all dependencies
- Update API documentation
- Build HTML documentation

## Documentation Structure

```
docs/
├── conf.py              # Sphinx configuration
├── index.rst            # Main documentation page
├── installation.rst     # Installation guide
├── quickstart.rst       # Quick start guide
├── cli_commands.rst     # CLI commands reference
├── configuration.rst    # Configuration guide
├── topaz_integration.rst # Topaz integration guide
├── model_angelo_integration.rst # ModelAngelo integration guide
├── analysis.rst         # Analysis documentation
├── slurm_integration.rst # SLURM integration guide
├── api_reference.rst    # API reference (auto-generated)
├── examples.rst         # Usage examples
├── troubleshooting.rst  # Troubleshooting guide
├── contributing.rst     # Contributing guide
├── _static/             # Static files (CSS, images)
│   └── custom.css       # Custom styling
├── _templates/          # Custom templates
├── Makefile             # Build automation
└── requirements.txt     # Documentation dependencies
```

## Available Make Targets

- `html` - Build HTML documentation
- `pdf` - Build PDF documentation
- `all` - Build all documentation formats
- `clean` - Clean build directory
- `serve` - Serve documentation locally
- `linkcheck` - Check for broken links
- `spelling` - Run spell check
- `api` - Update API documentation
- `full` - Complete build process

## Configuration

The documentation is configured in `conf.py` with the following key settings:

- **Theme**: Read the Docs theme
- **Extensions**: autodoc, napoleon, viewcode, intersphinx, etc.
- **Project Info**: cryoDL, version, author
- **Custom CSS**: Applied from `_static/custom.css`

## API Documentation

API documentation is automatically generated from docstrings in the source code:

- `src/config_manager.py` - Configuration management
- `src/cli.py` - Interactive CLI
- `src/topaz_analysis.py` - Analysis functions

To update API documentation:

```bash
cd docs
sphinx-build -b api docs docs/_build/html
```

## Customization

### Styling

Custom CSS is in `_static/custom.css` and includes:

- Custom color scheme
- Command example styling
- Warning/info/success boxes
- Responsive design
- Print styles

### Templates

Custom templates can be added to `_templates/` directory.

### Extensions

Additional Sphinx extensions can be added to `conf.py`:

```python
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    # Add your extensions here
]
```

## Read the Docs Integration

The documentation is configured for Read the Docs deployment:

1. **Configuration**: `conf.py` includes RTD-specific settings
2. **Requirements**: `requirements.txt` lists all dependencies
3. **Build**: `Makefile` includes RTD build target

To deploy to Read the Docs:

1. Connect your GitHub repository to Read the Docs
2. Configure the documentation directory as `docs/`
3. Set the Python interpreter version
4. Build will happen automatically on commits

## Local Development

### Development Server

For development, use the local server:

```bash
make serve
```

This starts a local HTTP server on port 8000.

### Auto-reload

For automatic rebuilding during development:

```bash
sphinx-autobuild . _build/html
```

### Spell Checking

To check spelling:

```bash
sphinx-build -b spelling docs docs/_build/html
```

### Link Checking

To check for broken links:

```bash
sphinx-build -b linkcheck docs docs/_build/html
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the source code is in the Python path
2. **Missing Dependencies**: Install all requirements from `requirements.txt`
3. **Build Errors**: Check the Sphinx build log for specific errors
4. **Theme Issues**: Verify sphinx-rtd-theme is installed

### Debug Mode

For verbose output during builds:

```bash
make html SPHINXOPTS="-v"
```

### Clean Build

If you encounter build issues:

```bash
sphinx-build -b clean
sphinx-build -b html
```

## Contributing to Documentation

1. **Edit RST files** in the docs directory
2. **Update API docs** by modifying docstrings in source code
3. **Test changes** with `sphinx-build -b html`
4. **Check links** with `sphinx-build -b linkcheck`
5. **Submit pull request** with documentation changes

### Documentation Standards

- Use clear, concise language
- Include code examples
- Add cross-references between pages
- Keep API documentation up to date
- Test all code examples

## Deployment

### GitHub Pages

To deploy to GitHub Pages:

1. Build documentation: `sphinx-build -b html`
2. Copy `_build/html/` contents to `docs/` branch
3. Configure GitHub Pages to serve from `docs/` branch

### Read the Docs

1. Connect repository to Read the Docs
2. Configure build settings
3. Documentation will build automatically

### Manual Deployment

For manual deployment to any web server:

1. Build documentation: `sphinx-build -b html`
2. Upload `_build/html/` contents to web server
3. Configure web server to serve static files

## Support

For documentation issues:

1. Check the troubleshooting guide
2. Review Sphinx documentation
3. Open an issue on the GitHub repository
4. Check the build logs for specific errors
