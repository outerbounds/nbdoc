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
# #default_exp run

# %% [markdown]
# # Run Notebooks
#
# > Lightweight running of notebooks without Papermill

# %% tags=["active-ipynb-py"]
#export
from os import sys
import nbformat
import jupyter_client
from nbformat.notebooknode import NotebookNode
from nbclient.exceptions import CellExecutionError
from nbdev.test import NoExportPreprocessor
from nbdev.export import nbglob
from typing import Union
from fastcore.parallel import parallel
from fastcore.script import call_parse
from fastcore.foundation import L
from fastcore.xtras import Path


# %% tags=["active-ipynb-py"]
#export
def _gen_nb():
    "Generates a temporary notebook for testing."
    p = Path('test_files/exec.txt')
    newP = p.with_suffix('.ipynb')
    text = p.read_text()
    newP.write_text(text)
    return newP


# %% tags=["active-ipynb-py"]
#export
def _get_kernel(nb):
    "Sees if kernelname exists otherwise uses the default of `python3`"
    nb_ks = nb.metadata.kernelspec.name
    K = jupyter_client.kernelspec.KernelSpecManager()
    ks = K.find_kernel_specs()
    return nb_ks if nb_ks in ks else 'python3'


# %% tags=["active-ipynb-py"]
#export
def nbrun(fname:Union[str, Path], flags=None) -> NotebookNode:
    "Execute notebook and skip cells that have flags consistent `tst_flags` in settings.ini"
    file = Path(fname)
    assert file.name.endswith('.ipynb'), f'{str(fname)} is not a notebook.'
    assert file.is_file(), f'file {str(fname)} not found.'
    nb = nbformat.read(file, as_version=4)
    if flags is None: flags = []
    kernel = _get_kernel(nb)
    print(f"running: {str(file)} with kernel: {kernel}")
    exp = NoExportPreprocessor(flags=flags, timeout=1500, kernel_name=kernel)
    pnb,_ = exp.preprocess(nb, resources={'metadata': {'path': file.parent}})
    return pnb


# %% tags=["active-ipynb"]
# _tmp_nb = _gen_nb()
# assert '3157' not in _tmp_nb.read_text() #value does not exist before execution
# _results = str(nbrun(_tmp_nb))
# assert '3157' in _results # value exists after execution
# assert '98343 + 2' in _results and '98345' not in _results # cells with flags do not get executed

# %% tags=["active-ipynb-py"]
#export
def nbupdate(fname:Union[str, Path], flags=None):
    "Run notebooks and update them in place."
    try:
        nb = nbrun(fname, flags=flags)
    except CellExecutionError as e:
        print(f'Error in {str(fname)}:\n{e}')
        return False
    print(f"finished: {str(fname)}")
    nbformat.write(nb, fname)
    return True


# %% tags=["active-ipynb"]
# _tmp_nb = _gen_nb()
# assert '3157' not in _tmp_nb.read_text() # doesn't exist b/c notebook hasn't been run
# nbupdate(_tmp_nb)
# assert '3157' in _tmp_nb.read_text() # exists now b/c notebook has been run

# %% tags=["active-ipynb-py"]
#export
def parallel_nbupdate(basedir:Union[Path,str], flags=None, recursive=True, n_workers=None, pause=0.1):
    "Run all notebooks in `dir` and save them in place."
    files = L(nbglob(basedir, recursive=recursive)).filter(lambda x: not x.name.startswith('Untitled'))
    if len(files)==1:
        if n_workers is None: n_workers=0
    if sys.platform == "win32": n_workers = 0
    passed = parallel(nbupdate, files, flags=flags, n_workers=n_workers, pause=pause)
    if all(passed): print("All notebooks refreshed!")
    else:
        msg = "Notebook Run & Update failed on the following:\n"
        raise Exception(msg + '\n'.join([f.name for p,f in zip(passed,files) if not p]))


# %% tags=["active-ipynb"]
# _test_nb = _gen_nb()
# assert not '3157' in _test_nb.read_text()
# parallel_nbupdate(_test_nb)
# assert '3157' in _test_nb.read_text()

# %% tags=["active-ipynb-py"]
#export
@call_parse
def nbdoc_update(
    srcdir:str=None,  # A directory of notebooks to refresh recursively, can also be a filename.
    flags:str=None,  # Space separated list of flags (tst_flags in settings.ini) to NOT ignore while running notebooks.  Otherwise, those cells are ignored.
    n_workers:int=None,  # Number of workers to use
    pause:float=0.5  # Pause time (in secs) between notebooks to avoid race conditions
):
    "Refresh all notebooks in `srcdir` by running them and saving them in place."
    parallel_nbupdate(basedir=srcdir,
                      flags=flags,
                      recursive=True, 
                      n_workers=n_workers, 
                      pause=pause)
