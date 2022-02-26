# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/showdoc.ipynb (unless otherwise specified).

__all__ = ['is_valid_xml', 'param2JSX', 'np2jsx', 'fmt_sig_param', 'get_sig_section', 'get_type', 'get_base_urls',
           'ShowDoc']

# Cell
from numpydoc.docscrape import NumpyDocString,ClassDoc, FunctionDoc, Parameter
from fastcore.all import test_eq, get_source_link, test
from xml.etree import ElementTree as et
import inspect, functools, warnings
from nbdev.showdoc import get_config

# Cell
_ATTRS_PARAMS=['Parameters', 'Attributes', 'Returns', 'Yields', 'Raises'] # These have parameters
_ATTRS_STR_LIST=['Summary', 'Extended Summary'] # These are lists of strings
def _is_func(obj): return inspect.isfunction(obj)

# Cell
def is_valid_xml(xml:str):
    "Determine if xml is valid or not."
    try: et.fromstring(xml)
    except et.ParseError as e:
        print(f"WARNING: xml not does not parse:{e}")
        return False
    return True

# Cell
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

# Cell
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

# Cell
def fmt_sig_param(p:inspect.Parameter):
    "Format inspect.Parameters as JSX components"
    name = str(p) if str(p).startswith('*') else p.name
    prefix = f'<SigArg name="{name}" '
    if p.annotation != inspect._empty:
        prefix += f'type="{p.annotation.__name__}" '
    if p.default != inspect._empty:
        prefix += f'default="{p.default}" '
    return prefix + "/>"

# Cell
def get_sig_section(obj):
    "Get JSX section from the signature of a class or function consisting of all of the argument."
    if not inspect.isclass(obj) and not _is_func(obj):
        raise ValueError(f'You can only generate parameters for classes and functions but got: {type(obj)}')
    params = inspect.signature(obj).parameters.items()
    jsx_params = [fmt_sig_param(p) for _, p in params]
    return "<SigArgSection>\n" + ''.join(jsx_params) +"\n</SigArgSection>"

# Cell
def get_type(obj):
    "Return type of object as a either 'method', 'function', 'class' or `None`."
    typ = None
    if _is_func(obj):
        if 'self' in inspect.signature(obj).parameters: typ = 'method'
        else: typ = 'function'
    elif inspect.isclass(obj): typ = 'class'
    return typ

# Cell
def get_base_urls(warn=False, param='module_baseurls') -> dict:
    "Get baseurls from config file"
    cfg = get_config()
    if param not in cfg:
        if warn: warnings.warn(f"Did not find `{param}` setting in {cfg.config_file}")
        return {}
    return dict([b.split('=', 1) for b in cfg.module_baseurls.split('\n')])

# Cell
class ShowDoc:
    def __init__(self, obj, hd_lvl=None):
        "Construct the html and JSX representation for a particular object."
        self.obj = obj
        self.typ = get_type(obj)
        if not self.typ: raise ValueError(f'Can only parse a class or a function, but got a {type(obj)}')
        self.npdocs = np2jsx(obj)
        self.objnm = obj.__name__
        self.modnm = inspect.getmodule(obj).__name__

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
        hd_prefix = f'<h{self.hd_lvl}> <code>{self.typ}</code> <span style="color:Brown">{self.objnm}</span> <em>{self._html_signature}</em>'
        if self.src_link: hd_prefix += f'<a href="{self.src_link}" style="float:right">[source]</a>'
        hd_prefix += f'</h{self.hd_lvl}>'
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
        return str(inspect.signature(self.obj))

    @property
    def jsx(self):
        "Returns the JSX components."
        nm = f'<DocSection type="{self.typ}" name="{self.objnm}" module="{self.modnm}"{self._src_link_attr}>'
        sp = get_sig_section(self.obj)
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