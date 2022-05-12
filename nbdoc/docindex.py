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
# #default_exp docindex

# %% [markdown]
# # docindex
# > Generate an index related to all entities rendered with `ShowDoc`

# %% tags=["active-ipynb-py"]
#export
from functools import partial
import re
from pprint import pformat
import json
from nbdev.export import nbglob, get_config
from fastcore.utils import Path, urlread
from fastcore.basics import merge
from fastcore.script import call_parse, Param, store_false

_re_name = re.compile(r'<DocSection type="(?!decorator)\S+" name="(\S+)"')
_re_decname = re.compile(r'<DocSection type="decorator" name="(\S+)"')
_re_slug = re.compile(r'---.*slug: (\S+).*---', flags=re.DOTALL)

# %% tags=["active-ipynb"]
# #hide
# from nbdoc.showdoc import ShowDoc
# import test_lib.example as ex
# from fastcore.test import test_eq

# %% tags=["active-ipynb"]
# #hide
#
# #This creates a test file #1 
# p = Path('test_files/_md_files/test_docs.md')
# p.write_text(ShowDoc(ex.function_with_types_in_docstring).jsx)
#
#
# #This creates a test file #2
# frontmatter = """---
# key2: value2
# slug: custom/pathfor/site
# key: value
# ---
# """
# p = Path('test_files/_md_files/front_matter_test_docs.md')
# p.write_text(frontmatter + ShowDoc(ex.function_with_pep484_type_annotations).jsx);

# %% tags=["active-ipynb-py"]
#export

mdglob = partial(nbglob, recursive=True, extension='.md', config_key='doc_path')

def _add_at(s): 
    if s: return s if s.startswith('@') else '@'+s

def _get_md_path(path):
    cfg = get_config() 
    if path: return Path(path)
    else: return Path(cfg.get('doc_path', '.'))

def _get_md_files(path): return mdglob(_get_md_path(path))


# %% tags=["active-ipynb-py"]
#export
def build_index(path=None):
    "Build an index of names generated with `ShowDoc` to document paths."
    path = _get_md_path(path)
    cfg = get_config() 
    doc_host = cfg['doc_host']
    base_url = cfg['doc_baseurl']
    
    if doc_host.endswith('/'): doc_host = doc_host[:-1]
    if not base_url.startswith('/'): base_url = '/' + base_url
    if not base_url.endswith('/'): base_url += '/'
    doc_url = doc_host + base_url
    
    reverse_idx = {}
    for f in _get_md_files(path):
        txt = f.read_text()
        decnames = [_add_at(s) for s in _re_decname.findall(txt)]
        names = _re_name.findall(txt)
        slug_match = _re_slug.search(txt)
        
        if slug_match: 
            doc_path = slug_match.group(1)
        else:
            doc_path = str(f.relative_to(path).with_suffix(''))

        for n in names+decnames: reverse_idx[n] = doc_url + doc_path + f'#{n}'
    
    if reverse_idx:
        (cfg.config_path/'_nbdoc_index.json').write_text(f'{json.dumps(reverse_idx, indent=4)}')
    return reverse_idx


# %% [markdown]
# `build_index` will build an index to names generated with `ShowDoc` to document paths that we can later use to construct links for documentation.
#
# Consider the follwing two markdown files, `test_docs.md` and `front_matter_with_test_docs.md`:

# %% tags=["active-ipynb"]
# _p1 = Path('test_files/_md_files/test_docs.md')
# print(_p1.read_text())

# %% tags=["active-ipynb"]
# _p2 = Path('test_files/_md_files/front_matter_test_docs.md')
# print(_p2.read_text())

# %% [markdown]
# Notice that for `front_matter_test_docs.md`, the front matter has a `slug`, which is used for the path rather than the directory in which the document resides.

# %% tags=["active-ipynb"]
# #hide
# _res = build_index('test_files/')
# test_eq(len(_res), 11)
# test_eq(_res['function_with_pep484_type_annotations'], 'https://outerbounds.github.io/nbdoc/custom/pathfor/site#function_with_pep484_type_annotations')
# test_eq(_res['function_with_types_in_docstring'], 'https://outerbounds.github.io/nbdoc/_md_files/test_docs#function_with_types_in_docstring')

# %% [markdown]
# Here is how the index looks:

# %% tags=["active-ipynb"]
# build_index('test_files/')

# %% tags=["active-ipynb-py"]
#export
_re_backticks = re.compile(r'`([^`\s]+)`')
def get_idx(url): return json.loads(urlread(url))

class NbdevLookup:
    "Mapping from symbol names to URLs with docs"
    def __init__(self, local=True, md_path=None):
        self.md_path = md_path
        self.local = local
        self.mdfiles = _get_md_files(md_path)
    
    def build_syms(self):
        cfg = get_config()
        urls = cfg.get('remote_idx', '').split()
        self.syms = merge(*[get_idx(url) for url in urls])

        if self.local:
            build_index(self.md_path)
            idx_file = cfg.config_path/'_nbdoc_index.json'
            if idx_file.exists(): self.syms = merge(self.syms, json.loads(idx_file.read_text()))
        
        
    def _link_sym(self, m):
        l = m.group(1)
        s = self[l]
        if s is None: return m.group(0)
        return rf"[{l}]({s})"

    def _link_line(self, l): return _re_backticks.sub(self._link_sym, l)
    
    def linkify(self, md):
        in_fence=False
        lines = md.splitlines()
        for i,l in enumerate(lines):
            if l.startswith("```"): in_fence=not in_fence
            elif not l.startswith('    ') and not in_fence: lines[i] = self._link_line(l)
        return '\n'.join(lines)

    def __getitem__(self, s): return self.syms.get(s, None)

    def update_markdown(self):
        self.build_syms()
        if self.syms:
            for f in self.mdfiles:
                print(f'Updating: {str(f)}')
                f.write_text(self.linkify(f.read_text()))


# %% [markdown]
# `NbdevLookup` can help you linkify markdown.

# %% tags=["active-ipynb"]
# #hide
#
# # generates backtics.md testing file
# _original_md = """Hey I am going to see what happens when we have things like `@conda` and `@batch`, but you will not convert conda to a link because it isn't in back ticks.
#
# If something isn't in the index like `@lorem`, nothing will happen.
#
# ```py
# In code fences you will not convert links `@conda`
# ```
#
# # Some other md
#
# this is another test: `function_with_types_in_docstring`
# """
# _backticks_file = Path('test_files/_md_files/backticks.md')
#
# _backticks_file.write_text(_original_md);

# %% [markdown]
# Here is an example of a file before linkifying it:

# %% tags=["active-ipynb"]
# print(_backticks_file.read_text())

# %% [markdown]
# And after linkifying it:

# %% tags=["active-ipynb"]
# nl = NbdevLookup(md_path='test_files/_md_files/')
# nl.update_markdown()

# %% tags=["active-ipynb"]
# print(_backticks_file.read_text())

# %% tags=["active-ipynb"]
# #hide
# _correct_res = """Hey I am going to see what happens when we have things like [@conda](https://outerbounds.github.io/nbdoc/decorators#@conda) and [@batch](https://outerbounds.github.io/nbdoc/decorators#@batch), but you will not convert conda to a link because it isn't in back ticks.
#
# If something isn't in the index like `@lorem`, nothing will happen.
#
# ```py
# In code fences you will not convert links `@conda`
# ```
#
# # Some other md
#
# this is another test: [function_with_types_in_docstring](https://outerbounds.github.io/nbdoc/test_docs#function_with_types_in_docstring)"""
# test_eq(_backticks_file.read_text(), _correct_res)

# %% tags=["active-ipynb-py"]
#export
@call_parse
def nbdoc_linkify(
    local:Param('Whether or not to build an index based on local documents', store_false),
    md_path:Param('Root path to search recursively containing markdown files to linkify', str)=None
):
    "Convert names in `backticks` in markdown files that have been documented with nbdoc.showdoc.ShowDoc to appropriate links."
    nl = NbdevLookup(local=local, md_path=md_path)
    nl.update_markdown()
