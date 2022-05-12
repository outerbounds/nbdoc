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

# %% [markdown]
# # Testing Notebooks
# > Testing of notebooks used for documentation

# %% [markdown]
# You can use `nbdev_test_nbs` from [nbdev](https://nbdev.fast.ai/test.html#nbdev_test_nbs) to test notebooks.  No customization is necessary for docs sites.  This is aliased as `nbdoc_test` for convenience:

# %% tags=["active-ipynb"]
# !nbdoc_test --help

# %% [markdown]
# To use `nbdev_test_nbs`, you must also define a `settings.ini` file at the root of the repo.  For documentation based testing, we recommend setting the following variables:
#
# - recursive = True
# - tst_flags = notest
#
# `tst_flags = notest` allow you to make commments on cells like `#notest` to allow tests to skip a specific cell.  This is useful for skipping long-running tests.  You can [read more about this here](https://nbdev.fast.ai/test.html#nbdev_test_nbs).
#
# `recursive = True` sets the default behavior of `nbdev_test_nbs` to `True` which is probably is what you want for a documentation site with many folders nested arbitrarily deep that may contain notebooks.
#
# Here is this project's `settings.ini` (note that the `recursive` flag is set to `False` as this project is not a documentation site):

# %% tags=["active-ipynb"]
# !cat ../settings.ini

# %% tags=["active-ipynb"]
# #notest
# from nbdev.test import nbdev_test_nbs
# nbdev_test_nbs('test_files/example_input.ipynb', n_workers=0)

# %% tags=["active-ipynb"]
# #notest
# nbdev_test_nbs('test_files/', n_workers=0)
