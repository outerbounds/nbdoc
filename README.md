# nbdoc
> Generate beautiful, testable documentation with Jupyter Notebooks


[![CI](https://github.com/outerbounds/nbdoc/actions/workflows/main.yml/badge.svg)](https://github.com/outerbounds/nbdoc/actions/workflows/main.yml) [![](https://img.shields.io/pypi/v/nbdoc)](https://pypi.org/project/nbdoc/)
[![](https://img.shields.io/static/v1?label=fastai&message=nbdev&color=57aeac&labelColor=black&style=flat&logo=data:image/png;base64,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)](https://github.com/fastai/nbdev)

## Install

`pip install nbdoc`

## Usage

This library consists of two cli tools as noted below.

### Converting Notebooks To Markdown


```python
! nbdoc_build --help
```

    usage: nbdoc_build [-h] [--srcdir SRCDIR] [--force_all FORCE_ALL]
                       [--n_workers N_WORKERS] [--pause PAUSE]
    
    Build the documentation by converting notebooks in `srcdir` to markdown
    
    optional arguments:
      -h, --help             show this help message and exit
      --srcdir SRCDIR        A directory of notebooks to convert to docs
                             recursively, can also be a filename.
      --force_all FORCE_ALL  Rebuild even notebooks that havent changed (default:
                             False)
      --n_workers N_WORKERS  Number of workers to use
      --pause PAUSE          Pause time (in secs) between notebooks to avoid race
                             conditions (default: 0.5)


### Run and Save Notebooks Inplace

```python
! nbdoc_update -h
```

    usage: nbdoc_update [-h] [--srcdir SRCDIR] [--flags FLAGS]
                        [--n_workers N_WORKERS] [--pause PAUSE]
    
    Refresh all notebooks in `srcdir` by running them and saving them in place.
    
    optional arguments:
      -h, --help             show this help message and exit
      --srcdir SRCDIR        A directory of notebooks to refresh recursively, can
                             also be a filename.
      --flags FLAGS          Space separated list of flags (tst_flags in
                             settings.ini) to NOT ignore while running notebooks.
                             Otherwise, those cells are ignored.
      --n_workers N_WORKERS  Number of workers to use
      --pause PAUSE          Pause time (in secs) between notebooks to avoid race
                             conditions (default: 0.5)


### Testing Notebooks

`nbdoc_test` is just an alias of `nbdev_test_nbs` from [nbdev](https://github.com/fastai/nbdev), and is a lightweight way to test notebooks.

```python
! nbdoc_test --help
```

    usage: nbdoc_test [-h] [--fname FNAME] [--flags FLAGS] [--n_workers N_WORKERS]
                      [--verbose VERBOSE] [--timing] [--pause PAUSE]
    
    Test in parallel the notebooks matching `fname`, passing along `flags`
    
    optional arguments:
      -h, --help             show this help message and exit
      --fname FNAME          A notebook name or glob to convert
      --flags FLAGS          Space separated list of flags
      --n_workers N_WORKERS  Number of workers to use
      --verbose VERBOSE      Print errors along the way (default: True)
      --timing               Timing each notebook to see the ones are slow (default:
                             False)
      --pause PAUSE          Pause time (in secs) between notebooks to avoid race
                             conditions (default: 0.5)


## Automatically Attach Links To APIs in Backticks

```python
! nbdoc_linkify --help
```

    usage: nbdoc_linkify [-h] [--local] [--md_path MD_PATH]
    
    Convert names in `backticks` in markdown files that have been documented with
    nbdoc.showdoc.ShowDoc to appropriate links.
    
    optional arguments:
      -h, --help         show this help message and exit
      --local            Whether or not to build an index based on local documents
                         (default: True)
      --md_path MD_PATH  Root path to search recursively containing markdown files
                         to linkify


## Documentation

Documentation [can be found here](https://outerbounds.github.io/nbdoc/).

## References

nbdoc is built with [nbdev](https://github.com/fastai/nbdev).  Furthermore, much of the code in this project is re-purposed from nbdev directly.
