import os
import sys

import sphinx_wagtail_theme

from willow import __version__

sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------

project = "Willow"
copyright = "2014-present, Torchbox"
author = "Torchbox"
release = __version__
version = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinxcontrib.spelling",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}

templates_path = ["_templates"]
exclude_patterns = ["_build", ".DS_Store"]

html_theme = "sphinx_wagtail_theme"
html_theme_path = [sphinx_wagtail_theme.get_html_theme_path()]
html_theme_options = {
    "project_name": "Willow",
    # "logo": "",
    "github_url": "https://github.com/wagtail/Willow/tree/main/docs/",
    "footer_links": "",
}
html_last_updated_fmt = "%b %d, %Y"

html_static_path = ["_static"]

pygments_style = None  # covered by sphinx_wagtail_theme

spelling_lang = "en_GB"
spelling_word_list_filename = "spelling_wordlist.txt"

# -- Misc --------------------------------------------------------------------

epub_show_urls = "footnote"
man_pages = [("index", "wagtail", "Willow Documentation", ["Torchbox"], 1)]
texinfo_documents = [
    (
        "index",
        "Willow",
        "Willow Documentation",
        "Torchbox",
        "Willow",
        "A Python image library that sits on top of Pillow, Wand and OpenCV",
        "Imaging",
    ),
]
