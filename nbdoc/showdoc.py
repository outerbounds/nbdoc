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
# #default_exp showdoc

# %% [markdown]
# # JSX Representations Of Objects
# > Render JSX representations of python classes and functions interactively.
#
# This module is modeled after [nbdev's](https://github.com/fastai/nbdev) showdoc functionality, but is instead [Numpy Docstring](https://numpydoc.readthedocs.io/en/latest/format.html) compliant.

# %% tags=["active-ipynb-py"]
#export
from numpydoc.docscrape import ClassDoc, FunctionDoc, Parameter
from fastcore.xtras import get_source_link
from xml.etree import ElementTree as et
import inspect, warnings
from nbdev.showdoc import get_config
from functools import partial

# %% tags=["active-ipynb"]
# #hide
# import test_lib.example as ex
# from fastcore.test import test_eq, test

# %% tags=["active-ipynb-py"]
#export
_ATTRS_PARAMS=['Parameters', 'Attributes', 'Returns', 'Yields', 'Raises'] # These have parameters
_ATTRS_STR_LIST=['Summary', 'Extended Summary'] # These are lists of strings
def _is_func(obj): return inspect.isfunction(obj)


# %% tags=["active-ipynb-py"]
#export
def is_valid_xml(xml:str):
    "Determine if xml is valid or not."
    try: et.fromstring(xml)
    except et.ParseError as e: 
        print(f"WARNING: xml not does not parse:{e}")
        return False
    return True


# %% [markdown]
# You can use `is_valid_xml` to determine if JSX is valid:

# %% tags=["active-ipynb"]
# _valid = "<Foo></Foo>" # valid jsx
# assert is_valid_xml(_valid)

# %% [markdown]
# If you pass invalid JSX to `is_valid_xml`, a warning will be printed:

# %% tags=["active-ipynb"]
# _invalid1 = "<Foo><Foo>"
# _invalid2 = "<Foo></Bar>"
#
# assert not is_valid_xml(_invalid1)
# assert not is_valid_xml(_invalid2)

# %% tags=["active-ipynb-py"]
#export
def param2JSX(p:Parameter):
    "Format a numpydoc.docscrape.Parameters as JSX components"
    prefix = "<Parameter"
    suffix = " />"
    for a in ['name', 'type', 'desc']:
        val = getattr(p, a)
        if val:
            if a == 'desc': 
                desc = '\n'.join(val).encode('unicode_escape').decode('utf-8')
                prefix += f' {a}="{desc}"'
            else: prefix += f' {a}="{val}"'
    return prefix.strip() + suffix


# %% tags=["active-ipynb"]
# _fd = FunctionDoc(ex.function_with_types_in_docstring)
# _p = _fd['Parameters'][0]
#
# test_eq(param2JSX(_p), '<Parameter name="param1" type="int" desc="The first parameter. something something\\nsecond line. foo" />')
# assert is_valid_xml(param2JSX(_p))

# %% tags=["active-ipynb-py"]
#export
def np2jsx(obj):
    "Turn Numpy Docstrings Into JSX components"
    if inspect.isclass(obj): doc = ClassDoc(obj)
    elif _is_func(obj): doc = FunctionDoc(obj)
    else: raise ValueError(f'You can only generate parameters for classes and functions but got: {type(obj)}')
    desc_list = []
    for a in _ATTRS_STR_LIST:
        nm = a.replace(' ', '_').lower()
        desc = '\n'.join(doc[a]).encode('unicode_escape').decode('utf-8')
        if doc[a]: desc_list.append(f' {nm}="{desc}"')
    desc_props = ''.join(desc_list)
    desc_component = f'<Description{desc_props} />' if desc_props else ''
    
    jsx_sections = []
    for a in _ATTRS_PARAMS:
        params = doc[a]
        if params:
            jsx_params = '\t' + '\n\t'.join([param2JSX(p) for p in params])
            jsx_block = f'<ParamSection name="{a}">\n{jsx_params}\n</ParamSection>'
            jsx_sections.append(jsx_block)
    
    return desc_component+ '\n' + '\n'.join(jsx_sections)


# %% [markdown]
# Below are some examples of docstrings and resulting JSX that comes out of them. This one is of a class:

# %% tags=["active-ipynb"]
# print(inspect.getdoc(ex.ExampleClass))

# %% tags=["active-ipynb"]
# _res = np2jsx(ex.ExampleClass)
# assert '<Parameter name="attr1" type="str" desc="Description of `attr1`." />' in _res
# assert 'extended_summary="If the class has public attributes' in _res
# assert '</ParamSection>' in _res
# print(_res)

# %% [markdown]
# This next one is of a top-level function:

# %% tags=["active-ipynb"]
# print(inspect.getdoc(ex.function_with_types_in_docstring))

# %% tags=["active-ipynb"]
# _res = np2jsx(ex.function_with_types_in_docstring)
# assert 'extended_summary="`PEP 484`_ type annotations are supported' in _res
# assert '<Parameter name="param2" type="str" desc="The second parameter." />' in _res
# assert '<ParamSection name="Returns">' in _res
# print(_res)

# %% tags=["active-ipynb-py"]
#export
def fmt_sig_param(p:inspect.Parameter):
    "Format inspect.Parameters as JSX components."
    name = str(p) if str(p).startswith('*') else p.name
    prefix = f'<SigArg name="{name}" '
    
    if p.annotation != inspect._empty:
        prefix += f'type="{p.annotation.__name__}" '
    if p.default != inspect._empty:
        prefix += f'default="{p.default}" '

    return prefix + "/>"


# %% [markdown]
# `fmt_sig_param` converts individual parameters in signatures to JSX.  Let's take the complex signature below, for example:

# %% tags=["active-ipynb"]
# _sig = inspect.signature(ex.Bar)
# _sig

# %% [markdown]
# Each of these parameters are then converted to JSX components

# %% tags=["active-ipynb"]
# _ps = _sig.parameters
# test_eq(fmt_sig_param(_ps['a']), '<SigArg name="a" type="int" />')
# test_eq(fmt_sig_param(_ps['b']), '<SigArg name="b" type="str" default="foo" />')
# test_eq(fmt_sig_param(_ps['args']), '<SigArg name="*args" />')
# test_eq(fmt_sig_param(_ps['tags']), '<SigArg name="**tags" />')
# assert is_valid_xml(fmt_sig_param(_ps['b']))

# %% tags=["active-ipynb-py"]
#export
def get_sig_section(obj, spoofstr=None):
    "Get JSX section from the signature of a class or function consisting of all of the argument. Optionally replace signature with `spoofstr`"
    if not spoofstr:
        if not inspect.isclass(obj) and not _is_func(obj):
            raise ValueError(f'You can only generate parameters for classes and functions but got: {type(obj)}')
        try: 
            sig = inspect.signature(obj)
        except: 
            return ''
        params = sig.parameters.items()
        jsx_params = [fmt_sig_param(p) for _, p in params]
    else:
        jsx_params = [f'<SigArg name="{spoofstr}" />']
    return "<SigArgSection>\n" + ''.join(jsx_params) +"\n</SigArgSection>"


# %% [markdown]
# Let's take the class Bar, for example:

# %% tags=["active-ipynb"]
# inspect.signature(ex.Bar)

# %% [markdown]
# The signature will get converted to JSX components, like so:

# %% tags=["active-ipynb"]
# _ex_result="""<SigArgSection>
# <SigArg name="a" type="int" /><SigArg name="b" type="str" default="foo" /><SigArg name="c" type="float" default="0.1" /><SigArg name="*args" /><SigArg name="**tags" />
# </SigArgSection>
# """.strip()
#
# _gen_result = get_sig_section(ex.Bar)
# assert is_valid_xml(_gen_result) # make sure its valid xml
# test_eq(_gen_result, _ex_result)
# print(_gen_result)

# %% tags=["active-ipynb"]
# #hide
# assert '<SigArg name="..." />' in get_sig_section(ex.Bar, spoofstr='...')

# %% tags=["active-ipynb"]
# #hide
# from fastcore.all import AttrDict
# test_eq(get_sig_section(AttrDict), '') # this object has no signature

# %% tags=["active-ipynb-py"]
#export
def get_type(obj):
    "Return type of object as a either 'method', 'function', 'class' or `None`."
    typ = None
    if inspect.ismethod(obj): return 'method'
    if _is_func(obj):
        try: 
            sig = inspect.signature(obj)
            if 'self' in sig.parameters: typ = 'method'
            else: typ = 'function'
        except ValueError:
            return 'function'
    elif inspect.isclass(obj): typ = 'class'
    return typ


# %% tags=["active-ipynb"]
# test_eq(get_type(ex.function_with_types_in_docstring),'function')
# test_eq(get_type(ex.ExampleClass), 'class')
# test_eq(get_type(ex.ExampleClass.example_method), 'method')

# %% tags=["active-ipynb"]
# #hide
# from fastcore.all import AttrDict
# test_eq(get_type(AttrDict), 'class')

# %% tags=["active-ipynb-py"]
#export
def get_base_urls(warn=False, param='module_baseurls') -> dict:
    "Get baseurls from config file"
    cfg = get_config()
    if param not in cfg:
        if warn: warnings.warn(f"Did not find `{param}` setting in {cfg.config_file}")
        return {}
    return dict([b.split('=', 1) for b in cfg.module_baseurls.split('\n')])


# %% [markdown]
# This project has a settings.ini which defines the `module_baseurls` parameter.  `get_base_urls` will return a dictionary of all the baseurls defined there.  This is useful used to construct URLs to source code in documentation. 
#
# Here is how the relevant parts of this project's `settings.ini` file is defined:
#
# ```
# module_baseurls = metaflow=https://github.com/Netflix/metaflow/tree/master/
# 	nbdev=https://github.com/fastai/nbdev/tree/master
# 	fastcore=https://github.com/fastcore/tree/master
#
# ```

# %% tags=["active-ipynb"]
# _base_urls = get_base_urls()
# assert len(_base_urls.keys()) == 3
# _base_urls

# %% tags=["active-ipynb-py"]
#export
#hide
def _get_name(var):
    try:
        callers_local_vars = inspect.currentframe().f_back.f_back.f_back.f_locals.items()
        return [var_name for var_name, var_val in callers_local_vars if var_val is var][0]
    except:
        return None


# %% tags=["active-ipynb-py"]
#export
#hide
def _get_mf_obj(obj):
    "Get decorator partials for Metaflow."
    if type(obj) == partial and hasattr(obj, 'args'):
        args=getattr(obj, 'args')
        if args:
            arg = args[0]
            if hasattr(arg, '__name__'):
                nm = arg.__name__
                if nm and 'decorator' in nm.lower():
                    newnm = _get_name(obj)
                    arg.__newname__ = newnm if newnm else nm
                    arg.__ismfdecorator__ = True
                    return arg
        else:
            return obj.func
    else:
        return obj


# %% tags=["active-ipynb"]
# #hide
# def _func(a,b): pass
# def _adecorator(): pass
# _bar = partial(_func, _adecorator)
# _bar2 = partial(_func, a=1)

# %% tags=["active-ipynb"]
# #hide
# def _run_get_obj(obj): return _get_mf_obj(obj)
# test_eq(_run_get_obj(_bar).__name__, '_adecorator')
# test_eq(_run_get_obj(_bar).__newname__, '_bar')
# test_eq(_run_get_obj(_bar2).__name__, '_func') # gets the function from the partial, since no decorator

# %% tags=["active-ipynb-py"]
#export
class ShowDoc:
    def __init__(self, obj, 
                 hd_lvl=None, # override heading level
                 name=None, # override name of object ex: '@mydecorator'
                 objtype=None, # override type of object. ex: 'decorator'
                 module_nm=None, #override module name. ex: 'fastai.vision'
                 decorator=False #same as setting `objtype` = 'decorator'
                ):
        "Construct the html and JSX representation for a particular object."
        if decorator: objtype = 'decorator'
        self.obj = _get_mf_obj(obj)
        #special handling for metaflow decorators
        if hasattr(self.obj, '__ismfdecorator__'):
            decorator = True
            objtype = 'decorator'
            name = self.obj.__newname__
        self.decorator = decorator
        self.typ = get_type(self.obj) if not objtype else objtype
        if not self.typ: raise ValueError(f'Can only parse a class or a function, but got a {type(self.obj)}')
        self.npdocs = np2jsx(self.obj)
            
        default_nm = self.obj.__qualname__ if self.typ == 'method' else self.obj.__name__
        self.objnm = default_nm if not name else name
            
        self.modnm = inspect.getmodule(self.obj).__name__ if not module_nm else module_nm
        
        if hd_lvl: self.hd_lvl = hd_lvl
        elif self.typ == 'method': self.hd_lvl = 4
        else: self.hd_lvl = 3
        self.link_suffix = get_source_link(self.obj)
        
    def _repr_html_(self):
        "This method controls what is displayed in Jupyter Notebooks."
        return f'<HTMLRemove>\n{self.nbhtml}\n</HTMLRemove>\n{self.jsx}'
    
    @property
    def nbhtml(self): 
        "HTML to be shown in the notebook"
        name=self.objnm
        if self.decorator and not name.startswith('@'):name = '@' + name
        hd_prefix = f'<h{self.hd_lvl}> <code>{self.typ}</code> <span style="color:Brown">{name}</span> <em>{self._html_signature}</em>'
        if self.src_link: hd_prefix += f'<a href="{self.src_link}" style="float:right">[source]</a>'
        hd_prefix += f'</h{self.hd_lvl}>'
        hd_prefix += f'<strong>{self.modnm}</strong>'
        if self._html_docstring: hd_prefix += f'<p>{self._html_docstring}</p>'
        return hd_prefix
    
    @property
    def _html_docstring(self):
        "Docstrings in HTML format"
        doc = inspect.getdoc(self.obj)
        if not doc: return ''
        return '<blockquote>'+doc.replace(' ', '&nbsp;').replace('\n', '<br>').strip()+'</blockquote>'
        
    @property
    def _html_signature(self):
        if self.decorator: sig = '(...)'
        else:
            try: sig = str(inspect.signature(self.obj))
            except: sig = ''
        return sig
    
    @property
    def jsx(self):
        "Returns the JSX components."
        nm = f'<DocSection type="{self.typ}" name="{self.objnm}" module="{self.modnm}" heading_level="{self.hd_lvl}"{self._src_link_attr}>'
        spoof = '...' if self.decorator else None
        sp = get_sig_section(self.obj, spoofstr=spoof)
        return f'{nm}\n{sp}\n{self.npdocs}\n</DocSection>'
    
    @property
    def src_link(self):
        "Construct the full link if it can be found."
        base_url = get_base_urls().get(self.modnm.split('.')[0])
        if base_url: return base_url + self.link_suffix
        else: return None
    
    @property
    def _src_link_attr(self):
        "JSX attribute if full link is found, otherwhise empty string."
        if not self.src_link: return ''
        else: return f' link="{self.src_link}"'

# %% [markdown]
# `ShowDoc` will render the function signature as well as other info that may help you author documentation for a function, method, or class in a notebook:
#
# Below, we render the docs for a class:

# %% tags=["active-ipynb"]
# ShowDoc(ex.ExampleClass)

# %% [markdown]
# There is a special override for decorators:

# %% tags=["active-ipynb"]
# ShowDoc(ex.ExampleClass, decorator=True, name='example')

# %% [markdown]
# There is also a special override for the module name:

# %% tags=["active-ipynb"]
# ShowDoc(ex.ExampleClass, decorator=True, name='example', module_nm='mymodule.foo')

# %% tags=["active-ipynb"]
# #hide
# _res = ShowDoc(ex.ExampleClass, decorator=True, name='example').jsx
# _res
# assert 'type="decorator" name="example"' in  _res
# assert '<SigArg name="..." />' in _res
#
# _res = ShowDoc(ex.ExampleClass, decorator=True, name='example', module_nm='mymod.foo').jsx
# assert 'module="mymod.foo"' in _res

# %% [markdown]
# Below, we render docs for method.  Note that you will receive an warning if your docstrings are not able to be parsed according to the numpy format:

# %% tags=["active-ipynb"]
# ShowDoc(ex.ExampleClass.example_method)

# %% tags=["active-ipynb"]
# #hide
# _res = ShowDoc(ex.ExampleClass.example_method).jsx
# assert 'ExampleClass.example_method' in _res # for methods, we put the class name in there as well.

# %% tags=["active-ipynb"]
# #hide
# _res = ShowDoc(ex.ExampleClass.example_method).jsx
# assert 'heading_level="4"' in _res

# %% [markdown]
# Finally, we can also show docs for a function.  If the module associated with the object has a baseurl specified in your project's `settings.ini` file as described in `get_base_urls`, you will also see a link to the source code:

# %% tags=["active-ipynb"]
# ShowDoc(test_eq)

# %% [markdown]
# As a debugging tool, `ShowDoc.jsx` extracts JSX Markup about an object so that you can use it for code documentation.  Here are some examples:

# %% tags=["active-ipynb"]
# #hide
# _result = ShowDoc(test_eq).jsx
# assert is_valid_xml(_result)
# assert 'link' in _result

# %% tags=["active-ipynb"]
# _result = ShowDoc(ex.ExampleClass).jsx
# assert is_valid_xml(_result)
# print(_result)

# %% tags=["active-ipynb"]
# _result = ShowDoc(ex.Foo).jsx
# assert is_valid_xml(_result)
# assert 'link' not in _result
# print(_result)
