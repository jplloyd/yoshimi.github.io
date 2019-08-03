#!/usr/bin/env python
# Build script for the yoshimi web site
#
# Do not use this for anything complex,
# learn to use a real static site generator instead.
#

from distutils import file_util, dir_util
import json
from os import getenv, path
from itertools import groupby
from functools import partial
import logging
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

CONF = "site.json"
BUILD_DIR = getenv("BUILD_DIR", "out")


def main():
    try:
        conf_data = json.loads(readfile(CONF))
        gen_site(conf_data)
    except IOError:
        logger.exception("Double check file paths.")
        exit(1)
    except Exception:
        logger.exception("An exception occured!")
        logger.error("Failed to fully generate site!")
        exit(2)


def gen_site(conf_data):
    # Fetch data items from the site config
    src_paths = conf_data["pages"]
    footer_links = conf_data["footer_links"]
    menu_link_list = conf_data["menu_links"]
    template_path = conf_data["template"]
    to_copy = conf_data.get("copy", None)
    template = readfile(template_path)

    tmp_dir = tempfile.mkdtemp()

    def is_divider(i):
        return isinstance(i, list)
    # Split the menu items into groups, for wrapping purposes
    menu_groups = sublist_split(menu_link_list, is_divider)

    # Generate the output for each source in the "pages" section
    for src in src_paths:
        gen_page(
            tmp_dir,
            src["url"], footer_links, menu_groups,
            template, src.get("title", None)
        )

    dir_util.copy_tree(tmp_dir, BUILD_DIR)

    if to_copy:
        copy_files(to_copy)
    # It seems everything worked out
    logger.info(
        'Website files successfully written to "{output_dir}/".'.format(
            output_dir=BUILD_DIR
        )
    )


def gen_page(tmp_dir, src_path, footer_links, menu_groups, template, title):
    src_name = path.basename(src_path)
    src = readfile(src_path)
    menu_rows = gen_menu(src_name, menu_groups)
    footer_iter = map(partial(gen_footer_link, src_name), footer_links)
    title_name = title if title else "Yoshimi"
    output = template.format(
        title=title_name,
        menu_rows=menu_rows,
        content=src,
        footer_links="".join(footer_iter)
    )
    out_path = path.join(tmp_dir, src_name)
    with open(out_path, "w") as outfile:
        outfile.write(output)


def gen_footer_link(src_url, footer_link):
    link_template = '<a href="{url}" {style}>{name}</a>'
    url = footer_link["url"]
    style = 'style="font-weight:bold"' if src_url == url else ''
    return link_template.format(
        url=url,
        name=footer_link["name"],
        style=style,
    )


def gen_menu(src_name, menu_groups):
    row_div = '<div class="menurow">'
    string_parts = []
    for group in menu_groups:
        string_parts.append(row_div)
        string_parts.extend([gen_menu_link(src_name, i) for i in group])
        string_parts.append('</div>')
    return "".join(string_parts)


def gen_menu_link(src_url, link_data):
    link_template = '<a href="{url}" {styling} >{name}</a>'
    url = link_data["url"]
    link_name = link_data["name"]
    styling = 'class="active"' if src_url == url else ''
    return link_template.format(url=url, styling=styling, name=link_name)


# Utility functions

def copy_files(to_copy):
    for src in to_copy:
        name = path.basename(src)
        dst = path.join(BUILD_DIR, name)
        copy = dir_util.copy_tree if path.isdir(src) else file_util.copy_file
        copy(src, dst)


def sublist_split(l, p):
    """Split a list into sublists based on a predicate function
    The predicate should return true for elements representing
    dividers, not the reverse.
    """
    return [list(i[1]) for i in groupby(l, p) if i[0] is False]


def readfile(file_path):
    """Convenience wrapper for reading file data to a string
    """
    with open(file_path) as f:
        return f.read()


# Run site generation

if __name__ == '__main__':
    logger.info("Trying to generate site!")
    main()
