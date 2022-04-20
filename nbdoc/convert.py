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
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% tags=["active-ipynb"]
# #default_exp convert

# %% tags=["active-ipynb-py"]
#export
import os, sys
from nbdoc.mdx import get_mdx_exporter
from typing import Union
from nbdev.export import nbglob
from nbconvert.exporters import Exporter
from fastcore.all import Path, parallel, call_parse, bool_arg


# %% [markdown]
# # Convert Notebooks To Markdown
#
# > Utilities that help you go from .ipynb -> .md

# %% tags=["active-ipynb-py"]
#export
def nb2md(fname:Union[str, Path], exp:Exporter):
    "Convert a notebook in `fname` to a markdown file."
    file = Path(fname)
    assert file.name.endswith('.ipynb'), f'{str(fname)} is not a notebook.'
    assert file.is_file(), f'file {str(fname)} not found.'
    print(f"converting: {str(file)}")
    try:
        o,r = exp.from_filename(fname)
        file.with_suffix('.md').write_text(o)
        return True
    except Exception as e:
        print(e)
        return False


# %% [markdown]
# We can use `nb2md` to convert a notebook to a markdown file with an `Exporter`.  Below, we use the exporter given to us by `nbdoc.mdx.get_mdx_exporter` and use that to create a markdown file from a notebook.

# %% tags=["active-ipynb"]
# _test_fname = Path('test_files/example_input.ipynb')
# _test_dest = Path('test_files/example_input.md')
# _test_dest.unlink(missing_ok=True)
# assert not _test_dest.exists() # make sure the markdown file doesn't exist
#
# nb2md(fname=_test_fname, exp = get_mdx_exporter()) # create the markdown file
# assert _test_dest.exists() # make sure the markdown file does exist
# assert len(_test_dest.readlines()) > 10

# %% tags=["active-ipynb"]
# !cat {_test_dest}

# %% tags=["active-ipynb-py"]
#export
def parallel_nb2md(basedir:Union[Path,str], exp:Exporter, recursive=True, force_all=False, n_workers=None, pause=0):
    "Convert all notebooks in `dir` to markdown files."
    files = nbglob(basedir, recursive=recursive).filter(lambda x: not x.name.startswith('Untitled'))
    if len(files)==1:
        force_all = True
        if n_workers is None: n_workers=0
    if not force_all:
        # only rebuild modified files
        files,_files = [],files.copy()
        for fname in _files:
            fname_out = fname.with_suffix('.md')
            if not fname_out.exists() or os.path.getmtime(fname) >= os.path.getmtime(fname_out):
                files.append(fname)
    if len(files)==0: print("No notebooks were modified.")
    else:
        if sys.platform == "win32": n_workers = 0
        passed = parallel(nb2md, files, n_workers=n_workers, exp=exp,  pause=pause)
        if not all(passed):
            msg = "Conversion failed on the following:\n"
            print(msg + '\n'.join([f.name for p,f in zip(passed,files) if not p]))


# %% [markdown]
# You can use `parallel_nb2md` to recursively convert a directory of notebooks to markdown files.

# %% tags=["active-ipynb"]
# _test_nbs =  nbglob('test_files/')

# %% tags=["active-ipynb"]
# #hide
# for f in _test_nbs: f.with_suffix('.md').unlink(missing_ok=True)

# %% tags=["active-ipynb"]
# parallel_nb2md('test_files/', exp=get_mdx_exporter(), recursive=True)

# %% tags=["active-ipynb"]
# for f in _test_nbs:
#     assert f.with_suffix('.md').exists(), f'{str(f)} does not exist.'

# %% [markdown]
# The modified times of notebooks are introspected such notebooks that haven't changed after markdown files have been created will not be converted:

# %% tags=["active-ipynb"]
# parallel_nb2md('test_files/', exp=get_mdx_exporter(), recursive=True)

# %% [markdown]
# However, you can set `force_all` = `True` to force notebooks to convert:

# %% tags=["active-ipynb"]
# parallel_nb2md('test_files/', exp=get_mdx_exporter(), recursive=True, force_all=True)

# %% tags=["active-ipynb"]
# #hide
# for f in _test_nbs: f.with_suffix('.md').unlink(missing_ok=True)

# %% tags=["active-ipynb-py"]
#export
@call_parse
def nbdoc_build(
    srcdir:str=None,  # A directory of notebooks to convert to docs recursively, can also be a filename.
    force_all:bool_arg=False, # Rebuild even notebooks that havent changed
    n_workers:int=None,  # Number of workers to use
    pause:float=0.5  # Pause time (in secs) between notebooks to avoid race conditions
):
    "Build the documentation by converting notebooks in `srcdir` to markdown"
    parallel_nb2md(basedir=srcdir, 
                   exp=get_mdx_exporter(), 
                   recursive=True, 
                   force_all=force_all, 
                   n_workers=n_workers, 
                   pause=pause)
