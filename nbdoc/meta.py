# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/meta.ipynb (unless otherwise specified).

__all__ = ['get_meta', 'meta_list', 'chk_desc', 'chk_img', 'chk_len', 'chk_desc_len']

# Cell
from fastcore.utils import globtastic, Path, merge
from fastcore.script import call_parse
import re
import yaml
import json
import sys

# Cell
_re_fm = re.compile(r'^---\s*(.*?)---\s*$', flags=re.DOTALL | re.MULTILINE)


def _load_yml(yml): return yaml.load(yml, Loader=yaml.FullLoader)

def get_meta(fname:str):
    "get metadata and front matter from `fname`."
    txt = Path(fname).read_text()
    fm = _re_fm.findall(txt)
    n_words = len(_re_fm.sub('', txt).split())
    return merge(dict(fname=fname, n_words=n_words), _load_yml(fm[0]) if fm else {})

# Cell
def meta_list(srcdir:str):
    "Get list of all metadata for markdown files in `srcdir`."
    docs = globtastic(srcdir, file_glob='*.md',
                      skip_folder_re='^[.]',
                      skip_file_re='^[_.]')
    return docs.map(get_meta)

# Cell
def _checker(func, msg:str, srcdir:str):
    fnames = meta_list(srcdir).filter(func).attrgot('fname')
    files = '\n\t'.join(fnames)
    if fnames: raise Exception(f"The following files {msg}:\n\t{files}")

# Cell
def _has_no_desc(d): return 'description' not in d

@call_parse
def chk_desc(srcdir:str='.', #directory of files to check
            ):
    "Check if docs do not have the field `description` in their front matter."
    return _checker(_has_no_desc, "do not have the field `description` in their front matter", srcdir)


# Cell
def _has_no_img(d): return 'image' not in d

@call_parse
def chk_img(srcdir:str='.', #directory of files to check
            ):
    "Check if docs do not have the image `description` in their front matter."
    return _checker(_has_no_img, "do not have the image `description` in their front matter", srcdir)

# Cell
def _lt_50(d): return d['n_words'] < 50

@call_parse
def chk_len(srcdir:str='.', #directory of files to check
            ):
    "Check if docs contain less than 50 words."
    return _checker(_lt_50, "contain less than 50 words", srcdir)

# Cell
def _desc_len(d):
    desc = d.get('description', None)
    if desc: return len(desc) >= 55 and len(desc) <=300
    else: return True

@call_parse
def chk_desc_len(srcdir:str='.', #directory of files to check
            ):
    "Check if docs have a description that is not between 55 and 300 characters."
    return _checker(_desc_len, "have a description that is not between 55 and 300 characters", srcdir)