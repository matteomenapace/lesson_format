#!/usr/bin/env python
from pandocfilters import toJSONFilter, Str, Para, Image

import shutil
import sys
import os
import cgi
import os.path
import hashlib
import subprocess
from string import Template

from tempfile import mkdtemp

def sha1(x):
  return hashlib.sha1(x).hexdigest()

base = os.path.dirname(__file__)
scratchblocks2 = os.path.join(base, "scratchblocks2")
rasterize = os.path.join(base, "rasterize.js")
jquery = os.path.join(base, "jquery.min.js")

with open(os.path.join(base, "scratch_template.html")) as fh:
    html_template = Template(fh.read())

tempdir = None

def block_to_image(block, lang, output_dir):
    block = block.encode('utf-8')
    lang = lang.encode('utf-8')
    name = sha1(block)
    html_file = os.path.join(tempdir, "%s.html"%(name))
    image_file = os.path.join(output_dir, "%s.png"%(name))

    if not os.path.exists(image_file):
        with open(html_file,"wb") as fh:
            raw = html_template.substitute(block=cgi.escape(block), lang=lang)
            fh.write(raw)

        subprocess.check_call(['phantomjs', rasterize, html_file, image_file])
    return image_file
    
    
def render_blocks(key, value, format, meta):
    lang = meta.get("language")
    if lang:
        lang = lang["c"][0]["c"]
    else:
        lang = meta.get("lang")
        if lang: 
            lang = lang["c"]
    if key == "CodeBlock":
        [[ident,classes,keyvals], code] = value

        if u"blocks" in classes or u"scratch" in classes:
            image = block_to_image(code, lang, os.getcwd())
            alt = Str(code)
            return Para([Image([alt], [os.path.basename(image),""])])


def log(*a):
    for x in a:
        print >> sys.stderr, x,
    print >> sys.stderr, ""

if __name__ == '__main__':
    try:
        tempdir = mkdtemp()
        shutil.copytree(scratchblocks2, os.path.join(tempdir, "scratchblocks2"))
        shutil.copy(jquery, tempdir)

        toJSONFilter(render_blocks)

    finally:
        shutil.rmtree(tempdir)

