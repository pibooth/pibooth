# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import sys
import os.path as osp

sys.path.insert(0, osp.dirname(osp.dirname(osp.abspath(__file__))))
import pibooth

# -- Project information -----------------------------------------------------

project = 'Pibooth'
copyright = '2024, Vincent Verdeil, Antoine Rousseaux'
author = 'Vincent Verdeil, Antoine Rousseaux'

# The full version, including alpha/beta/rc tags
release = pibooth.__version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.viewcode',
    'sphinx.ext.autodoc',
    'sphinx_copybutton'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The documentation uses the same "darkroom" look as the pibooth.org website:
# the palette, the fonts and the card/hairline treatment are taken from
# https://github.com/werdeil/pibooth_pages (src/styles/tokens.css). Furo is
# used because it exposes that whole palette as CSS variables, and ships the
# light/dark switch the website also has.
html_theme = 'furo'

# Palette from pibooth_pages/src/styles/tokens.css. The website is dark-first,
# the light variant is the one below: Furo picks the right one from the
# visitor's system preference and from the theme switch in the sidebar.
_LIGHT_VARIABLES = {
    # --surface-*
    'color-background-primary': '#fbf6ec',
    'color-background-secondary': '#f2ead9',
    'color-background-hover': '#f2ead9ff',
    'color-background-hover--transparent': '#f2ead900',
    'color-background-border': 'rgba(36, 29, 24, 0.12)',
    # --text-on-paper / --text-on-paper-dim
    'color-foreground-primary': '#241d18',
    'color-foreground-secondary': '#4c4038',
    'color-foreground-muted': '#6b5d4f',
    'color-foreground-border': 'rgba(36, 29, 24, 0.2)',
    # --accent-red / --accent-red-deep / --accent-gold
    'color-brand-primary': '#8a2619',
    'color-brand-content': '#b23324',
    'color-brand-visited': '#8a2619',
    'color-announcement-background': '#b23324',
    'color-announcement-text': '#ffffff',
    # sidebar
    'color-sidebar-background': '#f2ead9',
    'color-sidebar-background-border': 'rgba(36, 29, 24, 0.12)',
    'color-sidebar-brand-text': '#241d18',
    'color-sidebar-caption-text': '#a66f2e',
    'color-sidebar-link-text': '#6b5d4f',
    'color-sidebar-link-text--top-level': '#241d18',
    'color-sidebar-search-background': '#fbf6ec',
    'color-sidebar-search-border': 'rgba(36, 29, 24, 0.2)',
    'color-sidebar-item-background--hover': '#fbf6ec',
    # right-hand table of contents
    'color-toc-item-text': '#6b5d4f',
    'color-toc-item-text--hover': '#241d18',
    'color-toc-item-text--active': '#b23324',
    # blocks
    'color-admonition-background': '#f2ead9',
    'color-inline-code-background': '#f2ead9',
    'color-code-background': '#f2ead9',
    'color-code-foreground': '#241d18',
    'color-card-background': '#ffffff',
    'color-card-border': 'rgba(36, 29, 24, 0.1)',
    'color-card-marginals-background': '#f2ead9',
    'color-table-header-background': '#f2ead9',
    'color-table-border': 'rgba(36, 29, 24, 0.14)',
    'color-highlight-on-target': '#f6e7c8',
    'color-guilabel-background': '#f2ead9',
    'color-guilabel-border': 'rgba(36, 29, 24, 0.2)',
    'color-guilabel-text': '#241d18',
    # mobile header
    'color-header-background': '#f2ead9',
    'color-header-border': 'rgba(36, 29, 24, 0.12)',
    'color-header-text': '#241d18',
    # Most diagrams here are transparent PNGs drawn with black ink; on the
    # light theme the page itself is the paper they need.
    'pibooth-artwork-backing': 'transparent',
}

_DARK_VARIABLES = {
    'color-background-primary': '#1a1512',
    'color-background-secondary': '#241d18',
    'color-background-hover': '#262019ff',
    'color-background-hover--transparent': '#26201900',
    'color-background-border': 'rgba(239, 230, 211, 0.14)',
    'color-foreground-primary': '#efe6d3',
    'color-foreground-secondary': '#cdbfa8',
    'color-foreground-muted': '#b9ab94',
    'color-foreground-border': 'rgba(239, 230, 211, 0.2)',
    # --accent-red lightened: the website uses it on buttons only, here it has
    # to carry body-sized links, which needs more contrast on the dark ground.
    'color-brand-primary': '#e8705c',
    'color-brand-content': '#e8705c',
    'color-brand-visited': '#e8705c',
    'color-announcement-background': '#c63b2a',
    'color-announcement-text': '#ffffff',
    'color-sidebar-background': '#241d18',
    'color-sidebar-background-border': 'rgba(239, 230, 211, 0.12)',
    'color-sidebar-brand-text': '#efe6d3',
    'color-sidebar-caption-text': '#c68a3d',
    'color-sidebar-link-text': '#b9ab94',
    'color-sidebar-link-text--top-level': '#efe6d3',
    'color-sidebar-search-background': '#1a1512',
    'color-sidebar-search-border': 'rgba(239, 230, 211, 0.2)',
    'color-sidebar-item-background--hover': '#262019',
    'color-toc-item-text': '#b9ab94',
    'color-toc-item-text--hover': '#efe6d3',
    'color-toc-item-text--active': '#e8705c',
    'color-admonition-background': '#262019',
    'color-inline-code-background': '#262019',
    'color-code-background': '#14100e',
    'color-code-foreground': '#efe6d3',
    'color-card-background': '#262019',
    'color-card-border': 'rgba(239, 230, 211, 0.12)',
    'color-card-marginals-background': '#1a1512',
    'color-table-header-background': '#262019',
    'color-table-border': 'rgba(239, 230, 211, 0.14)',
    'color-highlight-on-target': '#3a2d1c',
    'color-guilabel-background': '#262019',
    'color-guilabel-border': 'rgba(239, 230, 211, 0.2)',
    'color-guilabel-text': '#efe6d3',
    'color-header-background': '#241d18',
    'color-header-border': 'rgba(239, 230, 211, 0.12)',
    'color-header-text': '#efe6d3',
    # ...on the dark theme they have to bring their own paper.
    'pibooth-artwork-backing': '#fbf6ec',
}


def _admonition_colors(palette):
    """Expand [(kinds, '#rrggbb')] into the Furo admonition variable pairs."""
    variables = {}
    for kinds, color in palette:
        red, green, blue = (int(color[i:i + 2], 16) for i in (1, 3, 5))
        for kind in kinds:
            variables['color-admonition-title--' + kind] = color
            variables['color-admonition-title-background--' + kind] = \
                'rgba({}, {}, {}, 0.18)'.format(red, green, blue)
    return variables


# Furo ships bright material-design admonition colors, which fight with the
# warm palette. These keep every kind distinguishable, in the same range of
# hues as the website.
_LIGHT_VARIABLES.update(_admonition_colors([
    (('danger', 'error', 'attention'), '#b23324'),
    (('warning', 'caution'), '#c2701f'),
    (('important',), '#a66f2e'),
    (('note', 'seealso'), '#2f7d84'),
    (('tip', 'hint'), '#5f8757'),
    (('admonition-todo',), '#6b5d4f'),
]))

_DARK_VARIABLES.update(_admonition_colors([
    (('danger', 'error', 'attention'), '#e8705c'),
    (('warning', 'caution'), '#dd9440'),
    (('important',), '#c68a3d'),
    (('note', 'seealso'), '#58a8b0'),
    (('tip', 'hint'), '#85b479'),
    (('admonition-todo',), '#b9ab94'),
]))

html_theme_options = {
    'light_css_variables': _LIGHT_VARIABLES,
    'dark_css_variables': _DARK_VARIABLES,
    # The sidebar brand (booth icon + "Pibooth" in Amatic SC, like the website
    # header) is built by docs/_templates/sidebar/brand.html.
    'sidebar_hide_name': True,
    'footer_icons': [
        {
            'name': 'pibooth.org',
            'url': 'https://www.pibooth.org',
            'html': '<svg stroke="currentColor" fill="currentColor" stroke-width="0" '
                    'viewBox="0 0 512 512"><path d="M352 256C352 278.2 350.8 299.6 348.7 320H163.3C161.2 '
                    '299.6 159.1 278.2 159.1 256C159.1 233.8 161.2 212.4 163.3 192H348.7C350.8 212.4 352 '
                    '233.8 352 256zM503.9 192C509.2 212.5 512 233.9 512 256C512 278.1 509.2 299.5 503.9 '
                    '320H380.8C382.9 299.4 384 277.1 384 256C384 234 382.9 212.6 380.8 192H503.9zM493.4 '
                    '160H376.7C366.7 96.14 346.9 42.62 321.4 8.442C399.8 29.09 463.4 85.94 493.4 '
                    '160zM344.3 160H167.7C173.8 123.6 183.2 91.38 194.7 65.35C205.2 41.74 216.9 24.61 '
                    '228.2 13.81C239.4 3.178 248.7 0 256 0C263.3 0 272.6 3.178 283.8 13.81C295.1 24.61 '
                    '306.8 41.74 317.3 65.35C328.8 91.38 338.2 123.6 344.3 160H344.3zM18.61 160C48.59 '
                    '85.94 112.2 29.09 190.6 8.442C165.1 42.62 145.3 96.14 135.3 160H18.61zM131.2 '
                    '192C129.1 212.6 127.1 234 127.1 256C127.1 277.1 129.1 299.4 131.2 320H8.065C2.8 '
                    '299.5 0 278.1 0 256C0 233.9 2.8 212.5 8.065 192H131.2zM194.7 446.6C183.2 420.6 '
                    '173.8 388.4 167.7 352H344.3C338.2 388.4 328.8 420.6 317.3 446.6C306.8 470.3 295.1 '
                    '487.4 283.8 498.2C272.6 508.8 263.3 512 255.1 512C248.7 512 239.4 508.8 228.2 '
                    '498.2C216.9 487.4 205.2 470.3 194.7 446.6H194.7zM190.6 503.6C112.2 482.9 48.59 '
                    '426.1 18.61 352H135.3C145.3 415.9 165.1 469.4 190.6 503.6V503.6zM321.4 503.6C346.9 '
                    '469.4 366.7 415.9 376.7 352H493.4C463.4 426.1 399.8 482.9 321.4 503.6V503.6z">'
                    '</path></svg>',
            'class': '',
        },
        {
            'name': 'GitHub',
            'url': 'https://github.com/pibooth/pibooth',
            'html': '<svg stroke="currentColor" fill="currentColor" stroke-width="0" '
                    'viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 '
                    '2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69'
                    '-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 '
                    '1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59'
                    '.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 '
                    '.27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 '
                    '3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55'
                    '.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path></svg>',
            'class': '',
        },
    ],
    # "Edit this page" links, the website links to GitHub everywhere too.
    'source_repository': 'https://github.com/pibooth/pibooth/',
    'source_branch': 'master',
    'source_directory': 'docs/',
}

# Shown in the browser tab and in the mobile header.
html_title = f"Pibooth {release}"

# This value selects if automatically documented members are sorted alphabetical
# (value 'alphabetical'), by member type (value 'groupwise') or by source order
# (value 'bysource'). The default is alphabetical.
autodoc_member_order = 'bysource'

add_module_names = False

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Typography, spacing and the card treatment of pibooth.org, applied on top of
# the colors declared above.
html_css_files = ['pibooth.css']

# No `html_logo`: the sidebar brand is rendered by _templates/sidebar/brand.html
# so that it matches the website header (icon + name in the display font). The
# `pibooth.png` / `pibooth-dark.png` wordmarks are used by index.rst.

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = '_static/favicon.ico'

# If false, no index is generated.
html_use_index = True

# If true, the index is split into individual pages for each letter.
html_split_index = False

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = False

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = True
