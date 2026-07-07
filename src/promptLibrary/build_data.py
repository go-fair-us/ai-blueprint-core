#!/usr/bin/env python3
"""Walk an OKF v0.1 bundle and emit a data.json for the Prompt Library web UI.

The bundle (default: ./okf-bundle) is the editable source of truth; this script
regenerates the data.json that app.js fetches. See README/SPEC in this directory.

Mapping (OKF -> data.json):
  root index.md frontmatter        -> meta {title, description, version, lastUpdated, source}
  each subdirectory (its index.md) -> a category node {id, title, description, children?}
  each concept *.md file           -> a prompt leaf {id, title, description, prompt}

Ordering follows the link order inside each index.md (not directory glob), so the
curated order in the bundle is preserved. Stdlib only -- no PyYAML dependency.
"""

import argparse
import json
import os
import re
import sys

# A markdown list item linking to a child: "* [text](target) - description"
LINK_RE = re.compile(
    r'^\s*[-*]\s*\[(?P<text>[^\]]+)\]\((?P<target>[^)]+)\)\s*(?:-\s*(?P<desc>.*\S))?\s*$'
)
H1_RE = re.compile(r'^#\s+(.*\S)\s*$')


def split_frontmatter(text):
    """Return (frontmatter_dict, body). Frontmatter is an optional leading
    '---' delimited YAML block; only simple `key: value` scalars are parsed."""
    fm = {}
    body = text
    if text.startswith('---'):
        end = text.find('\n---', 3)
        if end != -1:
            block = text[3:end]
            body = text[end + 4:]
            for line in block.splitlines():
                line = line.strip()
                if not line or line.startswith('#') or ':' not in line:
                    continue
                key, _, val = line.partition(':')
                fm[key.strip()] = _unquote(val.strip())
    return fm, body.lstrip('\n')


def _unquote(val):
    if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
        return val[1:-1]
    return val


def read(path):
    with open(path, encoding='utf-8') as fh:
        return fh.read()


def extract_title(body, fallback):
    for line in body.splitlines():
        m = H1_RE.match(line)
        if m:
            return m.group(1)
    return fallback


def extract_links(body):
    """Ordered list of (text, target, description) for every list-item link."""
    out = []
    for line in body.splitlines():
        m = LINK_RE.match(line)
        if m:
            out.append((m.group('text'), m.group('target'), m.group('desc') or ''))
    return out


def extract_prompt(body):
    """The prompt text: everything after a leading '# Prompt' heading, or the
    body minus a single leading heading line if no '# Prompt' section exists."""
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if re.match(r'^#{1,6}\s+prompt\s*$', line.strip(), re.IGNORECASE):
            return '\n'.join(lines[i + 1:]).strip()
    # Fallback: drop a leading heading line if present.
    trimmed = body.lstrip('\n').splitlines()
    if trimmed and trimmed[0].lstrip().startswith('#'):
        trimmed = trimmed[1:]
    return '\n'.join(trimmed).strip()


def rel_id(bundle_root, path):
    """Bundle-relative id without the .md extension; '/index' stripped."""
    rel = os.path.relpath(path, bundle_root).replace(os.sep, '/')
    if rel.endswith('/index.md'):
        rel = rel[:-len('/index.md')]
    elif rel.endswith('.md'):
        rel = rel[:-len('.md')]
    return rel


def build_prompt_node(bundle_root, path):
    fm, body = split_frontmatter(read(path))
    node = {
        'id': rel_id(bundle_root, path),
        'title': fm.get('title', os.path.basename(path)[:-3]),
    }
    if fm.get('description'):
        node['description'] = fm['description']
    node['prompt'] = extract_prompt(body)
    return node


def build_category(bundle_root, index_path, title, description):
    """Build a category node from a directory's index.md, following its link
    order. Directory links become child categories; *.md links become prompts."""
    _, body = split_frontmatter(read(index_path))
    dir_path = os.path.dirname(index_path)
    node = {'id': rel_id(bundle_root, index_path), 'title': title}
    if description:
        node['description'] = description

    children, prompts = [], []
    for text, target, desc in extract_links(body):
        target_path = os.path.normpath(os.path.join(dir_path, target))
        if target.endswith('/index.md') or target.endswith('/') or os.path.isdir(target_path):
            child_index = target_path if target_path.endswith('index.md') \
                else os.path.join(target_path, 'index.md')
            child_title = extract_title(read(child_index), text)
            children.append(build_category(bundle_root, child_index, child_title, desc))
        elif target.endswith('.md'):
            prompts.append(build_prompt_node(bundle_root, target_path))
        else:
            print(f'  warning: skipping unrecognized link -> {target}', file=sys.stderr)

    if children:
        node['children'] = children
    if prompts:
        node['prompts'] = prompts
    return node


def build(bundle_root):
    root_index = os.path.join(bundle_root, 'index.md')
    fm, body = split_frontmatter(read(root_index))
    meta = {}
    for key in ('title', 'description', 'version', 'lastUpdated', 'source'):
        if fm.get(key):
            meta[key] = fm[key]

    categories = []
    dir_path = os.path.dirname(root_index)
    for text, target, desc in extract_links(body):
        if not (target.endswith('/index.md') or target.endswith('/')):
            continue
        child_index = os.path.normpath(os.path.join(dir_path, target))
        if not child_index.endswith('index.md'):
            child_index = os.path.join(child_index, 'index.md')
        title = extract_title(read(child_index), text)
        categories.append(build_category(bundle_root, child_index, title, desc))

    return {'meta': meta, 'categories': categories}


def count_prompts(nodes):
    total = 0
    for n in nodes:
        total += len(n.get('prompts', []))
        total += count_prompts(n.get('children', []))
    return total


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--bundle', default=os.path.join(here, 'okf-bundle'),
                    help='Path to the OKF bundle root (default: ./okf-bundle)')
    ap.add_argument('--output', default=os.path.join(here, 'data.json'),
                    help='Path to write data.json (default: ./data.json)')
    args = ap.parse_args()

    data = build(args.bundle)
    with open(args.output, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write('\n')

    print(f'Wrote {args.output}')
    print(f'  categories: {len(data["categories"])}')
    print(f'  prompts:    {count_prompts(data["categories"])}')


if __name__ == '__main__':
    main()
