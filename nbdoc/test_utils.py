# ---
# jupyter:
#   jupytext:
#     comment_out_non_nbdev_exported_cells: true
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.9-dev
#   kernelspec:
#     display_name: Python 3.9.7 ('base')
#     language: python
#     name: python397jvsc74a57bd042fd40e048e0585f88ec242f050f7ef0895cf845a8dd1159352394e5826cd102
# ---

# %% tags=["active-ipynb"]
# #default_exp test_utils

# %% [markdown] tags=[]
# # Internal Testing Utilities
# > Utilities that help to test and display intermediate results of custom Preprocessors

# %% tags=["active-ipynb-py"]
#export
from nbconvert import MarkdownExporter
from traitlets.config import Config
from fastcore.xtras import Path


# %% tags=["active-ipynb-py"]
#export
def run_preprocessor(pp, nbfile, template_file='ob.tpl', display_results=False):
    "Runs a preprocessor with the MarkdownExporter and optionally displays results."
    c = Config()
    c.MarkdownExporter.preprocessors = pp
    tmp_dir = Path(__file__).parent/'templates/'
    tmp_file = tmp_dir/f"{template_file}"
    c.MarkdownExporter.template_file = str(tmp_file)
    exp =  MarkdownExporter(config=c)
    result = exp.from_filename(nbfile)
    if display_results: print(result[0])
    return result


# %% tags=["active-ipynb-py"]
#export
def show_plain_md(nbfile):
    md = MarkdownExporter()
    print(md.from_filename(nbfile)[0])

# %% tags=["active-ipynb"]
# show_plain_md('test_files/hello_world.ipynb')
