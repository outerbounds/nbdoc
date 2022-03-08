# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/run.ipynb (unless otherwise specified).

__all__ = ['nbrun', 'nbupdate', 'parallel_nbupdate', 'nbdoc_update']

# Cell
from os import sys
import nbformat
import jupyter_client
from nbformat.notebooknode import NotebookNode
from nbclient.exceptions import CellExecutionError
from nbdev.test import NoExportPreprocessor
from nbdev.export import nbglob
from typing import Union
from fastcore.all import Path, parallel, call_parse, L

# Cell
def _get_kernel(nb):
    "Sees if kernelname exists otherwise uses the default of `python3`"
    nb_ks = nb.metadata.kernelspec.name
    K = jupyter_client.kernelspec.KernelSpecManager()
    ks = K.find_kernel_specs()
    return nb_ks if nb_ks in ks else 'python3'

# Cell
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

# Cell
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

# Cell
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

# Cell
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