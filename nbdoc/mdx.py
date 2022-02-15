# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/mdx.ipynb (unless otherwise specified).

__all__ = ['CleanOutput', 'WriteTitle', 'CleanMagics', 'BashIdentify', 'get_mdx_exporter']

# Cell
from nbconvert.preprocessors import Preprocessor
from nbconvert import MarkdownExporter
from nbconvert.preprocessors import TagRemovePreprocessor
from nbdev.imports import get_config
import traitlets
from IPython.display import display, Markdown
from traitlets.config import Config
from pathlib import Path
import re, os

# Cell
class CleanOutput(Preprocessor):
    """Remove the preamble from Metaflow output."""
    pattern = r'([\s\S]*Metaflow[\s\S]*Validating[\s\S]+The graph[\s\S]+)(\n[\s\S]+Workflow starting[\s\S]+)'
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    def preprocess_cell(self, cell, resources, index):
        if re.search('\s*python.+run.*', cell.source) and 'outputs' in cell:
            for o in cell.outputs:
                if o.name == 'stdout':
                    o['text'] = self.ansi_escape.sub('', re.sub(self.pattern, r'\2', o.text)).strip()
        return cell, resources

# Cell
class WriteTitle(Preprocessor):
    """Modify the code-fence with the filename upon %%writefile cell magic."""
    pattern = r'(^[\S\s]*%%writefile\s)(\S+)\n'

    def preprocess_cell(self, cell, resources, index):
        m = re.match(self.pattern, cell.source)
        if m:
            filename = m.group(2)
            ext = filename.split('.')[-1]
            cell.metadata.magics_language = f'{ext} title="{filename}"'
            cell.outputs = []
        return cell, resources

# Cell
class CleanMagics(Preprocessor):
    """A preprocessor to remove cell magic commands"""
    pattern = '^\s*(%%|%).+?[\n\r]'

    def preprocess_cell(self, cell, resources, index):
        if cell.cell_type == 'code':
            cell.source = re.sub(self.pattern, '', cell.source).strip()
        return cell, resources

# Cell
class BashIdentify(Preprocessor):
    """A preprocessor to identify bash commands and mark them appropriately"""
    pattern = '^\s*!'

    def preprocess_cell(self, cell, resources, index):
        if cell.cell_type == 'code' and re.search(self.pattern, cell.source):
            cell.metadata.magics_language = 'bash'
            cell.source = re.sub(self.pattern, '', cell.source).strip()
        return cell, resources

# Cell
def get_mdx_exporter(template_file='ob.tpl'):
    """A mdx notebook exporter which composes many pre-processors together."""
    c = Config()
    c.TagRemovePreprocessor.remove_cell_tags = ("remove_cell",)
    c.TagRemovePreprocessor.remove_all_outputs_tags = ('remove_output',)
    c.TagRemovePreprocessor.remove_input_tags = ('remove_input',)
    c.MarkdownExporter.preprocessors = [WriteTitle, CleanMagics, BashIdentify, CleanOutput]
    tmp_dir = Path(__file__).parent/'templates/'
    tmp_file = tmp_dir/f"{template_file}"
    if not tmp_file.exists(): raise ValueError(f"{tmp_file} does not exist in {tmp_dir}")
    c.MarkdownExporter.template_file = str(tmp_file)
    return MarkdownExporter(config=c)