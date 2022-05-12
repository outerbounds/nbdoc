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
# #default_exp mdx

# %% [markdown]
# # Preprocessors For MDX
#
# > Custom preprocessors that help convert notebook content into MDX
#
# This module defines [nbconvert.Custom Preprocessors](https://nbconvert.readthedocs.io/en/latest/nbconvert_library.html#Custom-Preprocessors) that facilitate transforming notebook content into MDX, which is a variation of markdown.

# %% [markdown]
# ## Cell Tag Cheatsheet
#
# These preprocessors allow you to make special comments to enable/disable them.  Here is a list of all special comments:
#
# All comments start with `#meta` or `#cell_meta`, which are both aliases for the same thing.  For brevity, we will use `#meta` in this cheatsheet.
#
# ### Black code formatting
#
# `#meta:tag=black` will apply black code formatting.
#
# ### Show/Hide Cells
#
# 1. Remvoe entire cells:  `#meta:tag=remove_cell` or `#meta:tag=hide`
# 2. Remove output: `#meta:tag=remove_output` or `#meta:tag=remove_output` or `#meta:tag=hide_outputs` or `#meta:tag=hide_output`
# 3. Remove input: same as above, except `input` instead of `output`.
#
#
# ### Selecting Metaflow Steps
#
# You can selectively show meataflow steps in the output logs:
#
# 1. Show one step: `#meta:show_steps=<step_name>`
# 2. Show multiple steps: `#meta:show_steps=<step1_name>,<step2_name>`

# %% tags=["active-ipynb"]
# # export
# from nbconvert.preprocessors import Preprocessor
# from nbconvert import MarkdownExporter
# from nbconvert.preprocessors import TagRemovePreprocessor
# from nbdev.imports import get_config
# from traitlets.config import Config
# from pathlib import Path
# import re, uuid
# from fastcore.basics import AttrDict
# from nbdoc.media import ImagePath, ImageSave, HTMLEscape
# from black import format_str, Mode

# %% tags=["active-ipynb"]
# #hide
# from nbdev.export import read_nb
# from nbconvert import NotebookExporter
# from nbdoc.test_utils import run_preprocessor, show_plain_md
# from nbdoc.run import _gen_nb
# import json
#
# __file__ = str(get_config().path("lib_path")/'preproc.py')

# %% tags=["active-ipynb-py"]
#export
_re_meta= r'^\s*#(?:cell_meta|meta):\S+\s*[\n\r]'


# %% [markdown]
# ## Injecting Metadata Into Cells -

# %% tags=["active-ipynb-py"]
#export
class InjectMeta(Preprocessor):
    """
    Allows you to inject metadata into a cell for further preprocessing with a comment.
    """
    pattern = r'(^\s*#(?:cell_meta|meta):)(\S+)(\s*[\n\r])'
    
    def preprocess_cell(self, cell, resources, index):
        if cell.cell_type == 'code' and re.search(_re_meta, cell.source, flags=re.MULTILINE):
            cell_meta = re.findall(self.pattern, cell.source, re.MULTILINE)
            d = cell.metadata.get('nbdoc', {})
            for _, m, _ in cell_meta:
                if '=' in m:
                    k,v = m.split('=')
                    d[k] = v
                else: print(f"Warning cell_meta:{m} does not have '=' will be ignored.")
            cell.metadata['nbdoc'] = d
        return cell, resources


# %% [markdown]
# To inject metadata make a comment in a cell with the following pattern: `#cell_meta:{key=value}`. Note that `#meta` is an alias for `#cell_meta`
#
# For example, consider the following code:

# %% tags=["active-ipynb"]
#
# _test_file = 'test_files/hello_world.ipynb'
# first_cell = read_nb(_test_file)['cells'][0]
# print(first_cell['source'])

# %% [markdown]
# At the moment, this cell has no metadata:

# %% tags=["active-ipynb"]
# print(first_cell['metadata'])

# %% [markdown]
# However, after we process this notebook with `InjectMeta`, the appropriate metadata will be injected:

# %% tags=["active-ipynb"]
# c = Config()
# c.NotebookExporter.preprocessors = [InjectMeta]
# exp = NotebookExporter(config=c)
# cells, _ = exp.from_filename(_test_file)
# first_cell = json.loads(cells)['cells'][0]
#
# assert first_cell['metadata'] == {'nbdoc': {'show_steps': 'start,train'}}
# first_cell['metadata']

# %% [markdown]
# ## Strip Ansi Characters From Output -

# %% tags=["active-ipynb-py"]
#export
_re_ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

class StripAnsi(Preprocessor):
    """Strip Ansi Characters."""
    
    def preprocess_cell(self, cell, resources, index):
        for o in cell.get('outputs', []):
            if o.get('name') and o.name == 'stdout': 
                o['text'] = _re_ansi_escape.sub('', o.text)
        return cell, resources


# %% [markdown]
# Gets rid of colors that are streamed from standard out, which can interfere with static site generators:

# %% tags=["active-ipynb"]
# c, _ = run_preprocessor([StripAnsi], 'test_files/run_flow.ipynb')
# assert not _re_ansi_escape.findall(c)

# %% tags=["active-ipynb"]
# # export
# def _get_cell_id(id_length=36):
#     "generate random id for artifical notebook cell"
#     return uuid.uuid4().hex[:id_length]
#
# def _get_md_cell(content="{/* WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! Instead, edit the notebook w/the location & name as this file.*/}"):
#     "generate markdown cell with content"
#     cell = AttrDict({'cell_type': 'markdown',
#                      'id': f'{_get_cell_id()}',
#                      'metadata': {},
#                      'source': f'{content}'})
#     return cell

# %% [markdown]
# ## Insert Warning Into Markdown -

# %% tags=["active-ipynb"]
# # export
# class InsertWarning(Preprocessor):
#     """Insert Autogenerated Warning Into Notebook after the first cell."""
#     def preprocess(self, nb, resources):
#         nb.cells = nb.cells[:1] + [_get_md_cell()] + nb.cells[1:]
#         return nb, resources

# %% [markdown]
# This preprocessor inserts a warning in the markdown destination that the file is autogenerated.  This warning is inserted in the second cell so we do not interfere with front matter.

# %% tags=["active-ipynb"]
# c, _ = run_preprocessor([InsertWarning], 'test_files/hello_world.ipynb', display_results=True)
# assert "{/* WARNING: THIS FILE WAS AUTOGENERATED!" in c

# %% [markdown]
# ## Remove Empty Code Cells -

# %% tags=["active-ipynb"]
# # export
# def _emptyCodeCell(cell):
#     "Return True if cell is an empty Code Cell."
#     if cell['cell_type'] == 'code':
#         if not cell.source or not cell.source.strip(): return True
#     else: return False
#
#
# class RmEmptyCode(Preprocessor):
#     """Remove empty code cells."""
#     def preprocess(self, nb, resources):
#         new_cells = [c for c in nb.cells if not _emptyCodeCell(c)]
#         nb.cells = new_cells
#         return nb, resources

# %% [markdown]
# Notice how this notebook has an empty code cell at the end:

# %% tags=["active-ipynb"]
# show_plain_md('test_files/hello_world.ipynb')

# %% [markdown]
# With `RmEmptyCode` these empty code cells are stripped from the markdown:

# %% tags=["active-ipynb"]
# c, _ = run_preprocessor([RmEmptyCode], 'test_files/hello_world.ipynb', display_results=True)
# assert len(re.findall('```python',c)) == 1

# %% [markdown]
# ## Truncate Metaflow Output -

# %% tags=["active-ipynb-py"]
#export
class MetaflowTruncate(Preprocessor):
    """Remove the preamble and timestamp from Metaflow output."""
    _re_pre = re.compile(r'([\s\S]*Metaflow[\s\S]*Validating[\s\S]+The graph[\s\S]+)(\n[\s\S]+Workflow starting[\s\S]+)')
    _re_time = re.compile('\d{4}-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}.\d{3}')
    
    def preprocess_cell(self, cell, resources, index):
        if re.search('\s*python.+run.*', cell.source) and 'outputs' in cell:
            for o in cell.outputs:
                if o.name == 'stdout':
                    o['text'] = self._re_time.sub('', self._re_pre.sub(r'\2', o.text)).strip()
        return cell, resources


# %% [markdown]
# When you run a metaflow Flow, you are presented with a fair amount of boilerpalte before the job starts running that is not necesary to show in the documentation:

# %% tags=["active-ipynb"]
# show_plain_md('test_files/run_flow.ipynb')

# %% [markdown]
# We don't need to see the beginning part that validates the graph, and we don't need the time-stamps either.  We can remove these with the `MetaflowTruncate` preprocessor:

# %% tags=["active-ipynb"]
# c, _ = run_preprocessor([MetaflowTruncate], 'test_files/run_flow.ipynb', display_results=True)
# assert 'Validating your flow...' not in c

# %% [markdown]
# ## Turn Metadata into Cell Tags -

# %% tags=["foo", "active-ipynb-py"]
#export
class UpdateTags(Preprocessor):
    """
    Create cell tags based upon comment `#cell_meta:tags=<tag>`
    """
    
    def preprocess_cell(self, cell, resources, index):
        root = cell.metadata.get('nbdoc', {})
        tags = root.get('tags', root.get('tag')) # allow the singular also
        if tags: cell.metadata['tags'] = cell.metadata.get('tags', []) + tags.split(',')
        return cell, resources


# %% [markdown]
# Consider this python notebook prior to processing.  The comments can be used configure the visibility of cells. 
#
# - `#cell_meta:tags=remove_output` will just remove the output
# - `#cell_meta:tags=remove_input` will just remove the input
# - `#cell_meta:tags=remove_cell` will remove both the input and output
#
# Note that you can use `#cell_meta:tag` or `#cell_meta:tags` as they are both aliases for the same thing.  Here is a notebook before preprocessing:

# %% tags=["active-ipynb"]
# show_plain_md('test_files/visibility.ipynb')

# %% [markdown]
# `UpdateTags` is meant to be used with `InjectMeta` and `TagRemovePreprocessor` to configure the visibility of cells in rendered docs.  Here you can see what the notebook looks like after pre-processing:

# %% tags=["active-ipynb"]
# # Configure an exporter from scratch
# _test_file = 'test_files/visibility.ipynb'
# c = Config()
# c.TagRemovePreprocessor.remove_cell_tags = ("remove_cell",)
# c.TagRemovePreprocessor.remove_all_outputs_tags = ('remove_output',)
# c.TagRemovePreprocessor.remove_input_tags = ('remove_input',)
# c.MarkdownExporter.preprocessors = [InjectMeta, UpdateTags, TagRemovePreprocessor]
# exp = MarkdownExporter(config=c)
# result = exp.from_filename(_test_file)[0]
#
# # show the results
# assert 'you will not be able to see this cell at all either' not in result
# print(result)

# %% [markdown]
# ## Selecting Metaflow Steps In Output -

# %% tags=["active-ipynb-py"]
#export
class MetaflowSelectSteps(Preprocessor):
    """
    Hide Metaflow steps in output based on cell metadata.
    """
    re_step = r'.*\d+/{0}/\d+\s\(pid\s\d+\).*'
    
    def preprocess_cell(self, cell, resources, index):
        root = cell.metadata.get('nbdoc', {})
        steps = root.get('show_steps', root.get('show_step'))
        if re.search('\s*python.+run.*', cell.source) and 'outputs' in cell and steps:
            for o in cell.outputs:
                if o.name == 'stdout':
                    final_steps = []
                    for s in steps.split(','):
                        found_steps = re.compile(self.re_step.format(s)).findall(o['text'])
                        if found_steps: 
                            final_steps += found_steps + ['...']
                    o['text'] = '\n'.join(['...'] + final_steps)
        return cell, resources


# %% [markdown]
# `MetaflowSelectSteps` is meant to be used with `InjectMeta` to only show specific steps in the output logs from Metaflow.  
#
# For example, if you want to only show the `start` and `train` steps in your flow, you would annotate your cell with the following pattern: `#cell_meta:show_steps=<step_name>`
#
# Note that `show_step` and `show_steps` are aliases for convenience, so you don't need to worry about the `s` at the end.
#
# In the below example, `#cell_meta:show_steps=start,train` shows the `start` and `train` steps, whereas `#cell_meta:show_steps=train` only shows the `train` step:

# %% tags=["active-ipynb"]
# c, _ = run_preprocessor([InjectMeta, MetaflowSelectSteps], 
#                         'test_files/run_flow_showstep.ipynb', 
#                         display_results=True)
# assert 'end' not in c

# %% [markdown]
# ## Hide Specific Lines of Output With Keywords -

# %% tags=["active-ipynb-py"]
#export
class FilterOutput(Preprocessor):
    """
    Hide Output Based on Keywords.
    """
    def preprocess_cell(self, cell, resources, index):
        root = cell.metadata.get('nbdoc', {})
        words = root.get('filter_words', root.get('filter_word'))
        if 'outputs' in cell and words:
            _re = f"^(?!.*({'|'.join(words.split(','))}))"
            for o in cell.outputs:
                if o.name == 'stdout':
                    filtered_lines = [l for l in o['text'].splitlines() if re.findall(_re, l)]
                    o['text'] = '\n'.join(filtered_lines)
        return cell, resources


# %% [markdown]
# If we want to exclude output with certain keywords, we can use the `#meta:filter_words` comment.  For example, if we wanted to ignore all output that contains the text `FutureWarning` or `MultiIndex` we can use the comment:
#
# `#meta:filter_words=FutureWarning,MultiIndex`
#
# Consider this output below:

# %% tags=["active-ipynb"]
# show_plain_md('test_files/strip_out.ipynb')

# %% [markdown]
# Notice how the lines containing the terms `FutureWarning` or `MultiIndex` are stripped out:

# %% tags=["active-ipynb"]
# c, _ = run_preprocessor([InjectMeta, FilterOutput], 
#                         'test_files/strip_out.ipynb', 
#                         display_results=True)
# assert 'FutureWarning:' not in c and 'from pandas import MultiIndex, Int64Index' not in c

# %% [markdown]
# ## Hide Specific Lines of Code -

# %% tags=["active-ipynb-py"]
#export
class HideInputLines(Preprocessor):
    """
    Hide lines of code in code cells with the comment `#meta_hide_line` at the end of a line of code.
    """
    tok = '#meta_hide_line'
    
    def preprocess_cell(self, cell, resources, index):
        if cell.cell_type == 'code':
            if self.tok in cell.source:
                cell.source = '\n'.join([c for c in cell.source.split('\n') if not c.strip().endswith(self.tok)])
        return cell, resources


# %% [markdown]
# You can use the special comment `#meta_hide_line` to hide a specific line of code in a code cell.  This is what the code looks like before:

# %% tags=["active-ipynb"]
# show_plain_md('test_files/hide_lines.ipynb')

# %% [markdown]
# and after:

# %% tags=["active-ipynb"]
# c, _ = run_preprocessor([InjectMeta, HideInputLines], 
#                         'test_files/hide_lines.ipynb', 
#                         display_results=True)

# %% tags=["active-ipynb"]
# #hide 
# _res = """```python
# def show():
#     a = 2
# ```"""
# assert _res in c

# %% [markdown]
# ## Handle Scripts With `%%writefile` -

# %% tags=["active-ipynb-py"]
#export
class WriteTitle(Preprocessor):
    """Modify the code-fence with the filename upon %%writefile cell magic."""
    pattern = r'(^[\S\s]*%%writefile\s)(\S+)\n'
    
    def preprocess_cell(self, cell, resources, index):
        m = re.match(self.pattern, cell.source)
        if m: 
            filename = m.group(2)
            ext = filename.split('.')[-1]
            cell.metadata.magics_language = f'{ext} title="{filename}"'
            cell.metadata.script = True
            cell.metadata.file_ext = ext
            cell.metadata.filename = filename
            cell.outputs = []
        return cell, resources


# %% [markdown]
# `WriteTitle` creates the proper code-fence with a title in the situation where the `%%writefile` magic is used.
#
# For example, here are contents before pre-processing:

# %% tags=["active-ipynb"]
# show_plain_md('test_files/writefile.ipynb')

# %% [markdown]
# When we use `WriteTitle`, you will see the code-fence will change appropriately:

# %% tags=["active-ipynb"]
# c, _ = run_preprocessor([WriteTitle], 'test_files/writefile.ipynb', display_results=True)
# assert '```py title="myflow.py"' in c and '```txt title="hello.txt"' in c

# %% [markdown]
# ## Clean Flags and Magics -

# %% tags=["active-ipynb-py"]
#export
_tst_flags = get_config()['tst_flags'].split('|')

class CleanFlags(Preprocessor):
    """A preprocessor to remove Flags"""
    patterns = [re.compile(r'^#\s*{0}\s*'.format(f), re.MULTILINE) for f in _tst_flags]
    
    def preprocess_cell(self, cell, resources, index):
        if cell.cell_type == 'code':
            for p in self.patterns:
                cell.source = p.sub('', cell.source).strip()
        return cell, resources


# %% tags=["active-ipynb"]
# c, _ = run_preprocessor([CleanFlags], _gen_nb())
# assert '#notest' not in c

# %% tags=["active-ipynb-py"]
#export
class CleanMagics(Preprocessor):
    """A preprocessor to remove cell magic commands and #cell_meta: comments"""
    pattern = re.compile(r'(^\s*(%%|%).+?[\n\r])|({0})'.format(_re_meta), re.MULTILINE)
    
    def preprocess_cell(self, cell, resources, index):
        if cell.cell_type == 'code': 
            cell.source = self.pattern.sub('', cell.source).strip()
        return cell, resources


# %% [markdown]
# `CleanMagics` strips magic cell commands `%%` so they do not appear in rendered markdown files:

# %% tags=["active-ipynb"]
# c, _ = run_preprocessor([WriteTitle, CleanMagics], 'test_files/writefile.ipynb', display_results=True)
# assert '%%' not in c

# %% [markdown]
# Here is how `CleanMagics` Works on the file with the Metaflow log outputs from earlier, we can see that the `#cell_meta` comments are gone:

# %% tags=["active-ipynb"]
# c, _ = run_preprocessor([InjectMeta, MetaflowSelectSteps, CleanMagics], 
#                         'test_files/run_flow_showstep.ipynb', display_results=True)

# %% tags=["active-ipynb"]
# #hide
# c, _ = run_preprocessor([WriteTitle, CleanMagics], 'test_files/hello_world.ipynb')
# assert '#cell_meta' not in c

# %% [markdown]
# ## Formatting Code With Black -

# %% tags=["active-ipynb-py"]
#export
black_mode = Mode()

class Black(Preprocessor):
    """Format code that has a cell tag `black`"""
    def preprocess_cell(self, cell, resources, index):
        tags = cell.metadata.get('tags', [])
        if cell.cell_type == 'code' and 'black' in tags:
            cell.source = format_str(src_contents=cell.source, mode=black_mode).strip()
        return cell, resources


# %% [markdown]
# `Black` is a preprocessor that will format cells that have the cell tag `black` with [Python black](https://github.com/psf/black) code formatting.  You can apply tags via the notebook interface or with a comment `meta:tag=black`.

# %% [markdown]
# This is how cell formatting looks before [black](https://github.com/psf/black) formatting:

# %% tags=["active-ipynb"]
# show_plain_md('test_files/black.ipynb')

# %% [markdown]
# After black is applied, the code looks like this:

# %% tags=["active-ipynb"]
# c, _ = run_preprocessor([InjectMeta, UpdateTags, CleanMagics, Black], 'test_files/black.ipynb', display_results=True)
# assert '[1, 2, 3]' in c
# assert 'very_important_function(\n    template: str,' in c

# %% [markdown]
# ## Show File Contents -

# %% tags=["active-ipynb-py"]
#export
class CatFiles(Preprocessor):
    """Cat arbitrary files with %cat"""
    pattern = '^\s*!'
    
    def preprocess_cell(self, cell, resources, index):
        if cell.cell_type == 'code' and re.search(self.pattern, cell.source):
            cell.metadata.magics_language = 'bash'
            cell.source = re.sub(self.pattern, '', cell.source).strip()
        return cell, resources


# %% [markdown]
# ## Format Shell Commands -

# %% tags=["active-ipynb-py"]
#export
class BashIdentify(Preprocessor):
    """A preprocessor to identify bash commands and mark them appropriately"""
    pattern = re.compile('^\s*!', flags=re.MULTILINE)
    
    def preprocess_cell(self, cell, resources, index):
        if cell.cell_type == 'code' and self.pattern.search(cell.source):
            cell.metadata.magics_language = 'bash'
            cell.source = self.pattern.sub('', cell.source).strip()
        return cell, resources


# %% [markdown]
# When we issue a shell command in a notebook with `!`, we need to change the code-fence from `python` to `bash` and remove the `!`:

# %% tags=["active-ipynb"]
# c, _ = run_preprocessor([MetaflowTruncate, CleanMagics, BashIdentify], 'test_files/run_flow.ipynb', display_results=True)
# assert "```bash" in c and '!python' not in c

# %% [markdown]
# ## Remove `ShowDoc` Input Cells -

# %% tags=["active-ipynb-py"]
#export
_re_showdoc = re.compile(r'^ShowDoc', re.MULTILINE)


def _isShowDoc(cell):
    "Return True if cell contains ShowDoc."
    if cell['cell_type'] == 'code':
        if _re_showdoc.search(cell.source): return True
    else: return False


class CleanShowDoc(Preprocessor):
    """Ensure that ShowDoc output gets cleaned in the associated notebook."""
    _re_html = re.compile(r'<HTMLRemove>.*</HTMLRemove>', re.DOTALL)
    
    def preprocess_cell(self, cell, resources, index):
        "Convert cell to a raw cell with just the stripped portion of the output."
        if _isShowDoc(cell):
            all_outs = [o['data'] for o in cell.outputs if 'data' in o]
            html_outs = [o['text/html'] for o in all_outs if 'text/html' in o]
            if len(html_outs) != 1:
                return cell, resources
            cleaned_html = self._re_html.sub('', html_outs[0])
            cell = AttrDict({'cell_type':'raw', 'id':cell.id, 'metadata':cell.metadata, 'source':cleaned_html})
                    
        return cell, resources


# %% tags=["active-ipynb"]
# _result, _ = run_preprocessor([CleanShowDoc], 'test_files/doc.ipynb')
# assert '<HTMLRemove>' not in _result
# print(_result)

# %% [markdown]
# ## Composing Preprocessors Into A Pipeline
#
# Lets see how you can compose all of these preprocessors together to process notebooks appropriately:

# %% tags=["active-ipynb-py"]
#export
def get_mdx_exporter(template_file='ob.tpl'):
    """A mdx notebook exporter which composes many pre-processors together."""
    c = Config()
    c.TagRemovePreprocessor.remove_cell_tags = ("remove_cell", "hide")
    c.TagRemovePreprocessor.remove_all_outputs_tags = ("remove_output", "remove_outputs", "hide_output", "hide_outputs")
    c.TagRemovePreprocessor.remove_input_tags = ('remove_input', 'remove_inputs', "hide_input", "hide_inputs")
    pp = [InjectMeta, WriteTitle, CleanMagics, BashIdentify, MetaflowTruncate,
          MetaflowSelectSteps, UpdateTags, InsertWarning, TagRemovePreprocessor, CleanFlags, CleanShowDoc, RmEmptyCode, 
          StripAnsi, HideInputLines, FilterOutput, Black, ImageSave, ImagePath, HTMLEscape]
    c.MarkdownExporter.preprocessors = pp
    tmp_dir = Path(__file__).parent/'templates/'
    tmp_file = tmp_dir/f"{template_file}"
    if not tmp_file.exists(): raise ValueError(f"{tmp_file} does not exist in {tmp_dir}")
    c.MarkdownExporter.template_file = str(tmp_file)
    return MarkdownExporter(config=c)

# %% [markdown]
# `get_mdx_exporter` combines all of the previous preprocessors, along with the built in `TagRemovePreprocessor` to allow for hiding cell inputs/outputs based on cell tags.  Here is an example of markdown generated from a notebook with the default preprocessing:

# %% tags=["active-ipynb"]
# show_plain_md('test_files/example_input.ipynb')

# %% [markdown]
# Here is the same notebook, but with all of the preprocessors that we defined in this module.  Additionally, we hide the input of the last cell which prints `hello, you should not see the print statement...` by using the built in `TagRemovePreprocessor`:

# %% tags=["active-ipynb"]
# exp = get_mdx_exporter()
# print(exp.from_filename('test_files/example_input.ipynb')[0])
