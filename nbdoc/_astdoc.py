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
# #default_exp astdoc

# %% [markdown]
# # Staticly Parse Python For Documentation (Deprecated)
#
# > Parse python modules and extract components (signatures, docstrings, etc) from the AST.
#
# Given a folder to a python module, we want walk all of the python files and extract the relevant apis into a structured format.  The structured format can then be extracted in a format like JSX that allows custom styling of various components such as signatures, functions, methods, etc.

# %% tags=["active-ipynb-py"]
#export
from fastcore.all import Path, L, risinstance, test_eq
import ast, re


# %% tags=["active-ipynb-py"]
#export
#hide

class Parsed:
    "Base class for Parsed objects used to store structured data about an AST."
    def __init__(self, tree):
        self.tree = tree
        self.docstring = ast.get_docstring(tree)

    def __getattr__(self, a):
        return getattr(self.tree, a)


# %% tags=["active-ipynb-py"]
#export
class ParsedFunc(Parsed):
    "Parse a function in a way that is amenable to show in the docs."
    def __init__(self, tree):
        assert isinstance(tree, ast.FunctionDef), f"Cannot parse non-function type: {type(tree)}."
        super().__init__(tree)
        self.dirty_ds = ast.get_docstring(tree, clean=False)
        self.args = ast.unparse(tree.args)
        _returns = getattr(tree, 'returns')
        self.returns = ast.unparse(_returns) if _returns else None
        self.body = self.get_body()
        self.decorators = [ast.unparse(d) for d in tree.decorator_list]
    
    def get_body(self):
        body = ast.unparse(self.tree.body).encode('utf-8').decode('unicode_escape')
        docstring = f"'{ast.get_docstring(self.tree, clean=False)}'\n"
        return body.replace(docstring, '')

    @property
    def include(self):
        "If this function should be shown in the docs or not."
        return self.name == '__init__' or (not self.name.startswith('_') and 'property' not in self.decorators)


# %% [markdown]
# Let's take the below function as an example.  We can parse it and get its constituent parts:

# %% tags=["active-ipynb"]
# _t = ast.parse(Path('test_files/test_lib/script.py').read_text())
# _f = _t.body[1]
#
# print(ast.unparse(_t.body[1]))

# %% [markdown]
# When we parse the above function we get a number of useful attributes:

# %% tags=["active-ipynb"]
# _pm = ParsedFunc(_f)
# test_eq(_pm.args, 'ms')
# test_eq(_pm.name, 'func')
# test_eq(_pm.body, "global current_metadata\ninfos = ms.split('@', 1)\nreturn get_metadata()") #docstring is stripped out
# test_eq(_pm.returns, 'str')
# test_eq(_pm.decorators, [])
# assert _pm.docstring.startswith('Switch Metadata')

# %% tags=["active-ipynb-py"]
#export
class ParsedClass(Parsed):
    "Parse Python Classes and associated methods."
    def __init__(self, tree):
        assert isinstance(tree, ast.ClassDef), f"Cannot parse non-class type: {type(tree)}."
        super().__init__(tree)
        self.docstring = ast.get_docstring(tree)
        self._methods = self.get_funcs()
        self.methods = []
        for m in self._methods:
            if m.name != '__init__': 
                self.methods.append(m)
            elif m.name == '__init__':
                self._init_method = m
                self.signature = m.args
        
    @property
    def include(self):
        return not self.name.startswith('_') and bool(self._methods)
        
    
    def get_funcs(self):
        _funcs = L(self.tree.body).filter(risinstance(ast.FunctionDef)).map(lambda x: ParsedFunc(x))
        return _funcs.filter(lambda x: x.include)


# %% [markdown]
# Similarly, let's parse the below class:

# %% tags=["active-ipynb"]
# _c = _t.body[6]
# print(ast.unparse(_c))

# %% [markdown]
# When we parse this class, we similarly get useful attributes:

# %% tags=["active-ipynb"]
# _pc = ParsedClass(_c)
# _pc.name == 'Flow'
# test_eq(_pc.methods, []) # only method is __init__ which is stored seperately, and properties do not count
# test_eq(_pc.signature, 'self, foo, *args, **kwargs') # the signature is pulled from __init__
# assert _pc.docstring.startswith("A Flow represents all existing flows") # The class-level docstring

# %% tags=["active-ipynb-py"]
#export
class ParsedModule(Parsed):
    "Parse python modules given a `basedir` and `filepath`"
    def __init__(self, basedir:str, filepath:str):
        fp = Path(filepath)
        bd = Path(basedir)
        assert filepath.startswith(basedir), f"`filepath`: {filepath} must start with `basedir`: {basedir}" 
        assert fp.exists(), f'File does not exist: {str(fp)}'
        assert fp.suffix == '.py', f'Only python files can be parsed.  Got: f{str(fp)}'
        
        
        tree = ast.parse(fp.read_text())
        super().__init__(tree)
        
        self.stem = fp.stem
        self.source_dir = re.sub(r'^/', '', str(fp.parent).replace(str(bd), ''))
        self.dest_dir = f"{self.source_dir}/{self.stem}"
        
        assert isinstance(tree, ast.Module), f"Cannot parse non-Module type: {type(tree)}."
        self.funcs = L()
        self.classes = L()
        for o in L(tree.body).filter(risinstance((ast.FunctionDef, ast.ClassDef))):
            if isinstance(o, ast.FunctionDef):
                f = ParsedFunc(o)
                if f.include: self.funcs.append(f)
            if isinstance(o, ast.ClassDef):
                c = ParsedClass(o)
                if c.include: self.classes.append(c)
        
    @property
    def include(self):
        return self.funcs or self.classes
    
    @property
    def func_names(self): return self.funcs.attrgot('name')

    @property
    def class_names(self): return self.classes.attrgot('name')

# %% [markdown]
# `ParsedModule` parses python modules:

# %% tags=["active-ipynb"]
# _basedir='test_files/'
# _file_path = 'test_files/test_lib/script.py'
# _pm = ParsedModule(_basedir, _file_path)

# %% [markdown]
# The reason we pass `basedir` and `filepath` so we can calculate various paths for writing markdown files:

# %% tags=["active-ipynb"]
# test_eq(_pm.source_dir, 'test_lib') # need this to link back to GitHub from the docs
# test_eq(_pm.dest_dir, 'test_lib/script') # this is the directory that markdown from this module would be written into
# test_eq(_pm.stem, 'script') # This is the stem of the python file

# %% [markdown]
# We have access to useful attributes:

# %% tags=["active-ipynb"]
# test_eq(_pm.class_names, ['Metaflow','MetaflowObject','MetaflowData','Flow'])
# test_eq(_pm.func_names, ['func','get_metadata'])

# %% [markdown]
# We can access methods from classes as well:

# %% tags=["active-ipynb"]
# for c in _pm.classes:
#     if c.name == 'MetaflowObject':
#         # the signature, or __init__ of `MetaflowObject` in our test data
#         test_eq(c.signature, 'self, pathspec=None, attempt=None, _object=None, _parent=None, _namespace_check=True')
#         _tst_methods = c.methods
#         
# test_eq(len(_tst_methods), 1) # there is only one method we want to show from the MetaflowObject besides __init__
# test_eq(_tst_methods[0].name, 'is_in_namespace') # the name of this method is `is_in_namespace`
# assert _tst_methods[0].docstring.startswith("Returns whether this object is in the current namespace.")

# %% tags=["active-ipynb"]
# #hide
#
# # from fastcore.all import globtastic
# # files = globtastic('../../metaflow/metaflow/', 
# #                     file_glob='*.py', 
# #                     skip_folder_re='^[_.]')
