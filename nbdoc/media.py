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
# #default_exp media

# %% [markdown]
# # Convert HTML and Images to MDX
# > Make allowances for plots and dataframes in MDX

# %% tags=["active-ipynb-py"]
#export
from nbconvert.preprocessors import Preprocessor
from fastcore.xtras import Path
from html.parser import HTMLParser


# %% tags=["active-ipynb"]
# #hide
# from nbdoc.test_utils import run_preprocessor

# %% tags=["active-ipynb-py"]
#export
class HTMLdf(HTMLParser):
    """HTML Parser that finds a dataframe."""
    df = False
    scoped = False
    
    def handle_starttag(self, tag, attrs):
        if tag == 'style':
            for k,v in attrs:
                if k == 'scoped': self.scoped=True

    def handle_data(self, data):
        if '.dataframe' in data and self.scoped:
            self.df=True
        
    def handle_endtag(self, tag):
        if tag == 'style': self.scoped=False
                
    @classmethod
    def search(cls, x):
        parser = cls()
        parser.feed(x)
        return parser.df


# %% tags=["active-ipynb"]
# _test_html = """<div>
# <style scoped>
#     .dataframe tbody tr th:only-of-type {
#         vertical-align: middle;
#     }
#
#     .dataframe tbody tr th {
#         vertical-align: top;
#     }
#
#     .dataframe thead th {
#         text-align: right;
#     }
# </style>"""
#
# assert HTMLdf.search(_test_html)
# assert not HTMLdf.search('<div></div>')

# %% tags=["active-ipynb-py"]
#export
class HTMLEscape(Preprocessor):
    """
    Place HTML in a codeblock and surround it with a <HTMLOutputBlock> component.
    """    
    def preprocess_cell(self, cell, resources, index):
        if cell.cell_type =='code':
            outputs = []
            for o in cell.outputs:
                if o.get('data') and o['data'].get('text/html'):
                    cell.metadata.html_output = True
                    html = o['data']['text/html']
                    cell.metadata.html_center = False if HTMLdf.search(html) else True
                    o['data']['text/html'] = '```html\n'+html.strip()+'\n```'
        return cell, resources


# %% [markdown]
# By default, HTML is incompatible with MDX.  We place HTML in a code block and wrap it with the a custom component so that the static site generator can render it.

# %% tags=["active-ipynb"]
# c, _ = run_preprocessor([HTMLEscape], 'test_files/pandas.ipynb', display_results=True)
# assert '<HTMLOutputBlock' in c and '</HTMLOutputBlock>' in c and 'center' not in c
# assert '```html\n<div>' in c and '</div>\n```' in c

# %% tags=["active-ipynb"]
# #hide
# c, _ = run_preprocessor([HTMLEscape], 'test_files/altair.ipynb')
# assert 'center' in c

# %% tags=["active-ipynb-py"]
#export
class ImageSave(Preprocessor):
    "Saves images stored as bytes in notebooks to disk."
    def preprocess(self, nb, resources):
        meta = resources.get('metadata', {})
        nb_name = meta.get('name')
        nb_path = meta.get('path')
        outfiles = resources.get('outputs')
        if nb_name and outfiles:
            resources['fmap'] = {}
            for k,v in outfiles.items():
                dest = Path(nb_path)/f'_{nb_name}_files/{k}'
                dest.parent.mkdir(exist_ok=True)
                dest.write_bytes(v)
                resources['fmap'][f'{k}'] = f'_{nb_name}_files/{k}'       
        return nb, resources

class ImagePath(Preprocessor):
    "Changes the image path to the location where `ImageSave` saved the files."
    def preprocess_cell(self, cell, resources, index): 
        fmap = resources.get('fmap')
        if fmap:
            for o in cell.get('outputs', []):
                fnames = o.get('metadata', {}).get('filenames', {})
                for k,v in fnames.items():
                    fnames[k] = fmap.get(v,v)
        return cell, resources

# %% [markdown]
# `ImageSave` and `ImagePath` must be used together to extract and save images from notebooks and change the path.  This is necessary to enable compatiblity with certain types of plotting libraries like matplotlib.

# %% tags=["active-ipynb"]
# c, _ = run_preprocessor([ImageSave, ImagePath], 'test_files/matplotlib.ipynb', display_results=True)
# assert '![png](_matplotlib_files/output_0_1.png)' in c

# %% tags=["active-ipynb"]
# c, _ = run_preprocessor([ImageSave, ImagePath], 'test_files/altair_jpeg.ipynb')
# assert '![svg](_altair_jpeg_files/output_0_0.svg' in c
