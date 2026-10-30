#!/usr/bin/env python3
"""Check the selected font's actual cmap against supplied canonical lyric characters."""
import argparse
import json
from pathlib import Path
from input_contracts import lyric_lines, sha


def inspect_font(font,document):
    from fontTools.ttLib import TTFont
    f=TTFont(font,fontNumber=0)
    try:
        cmap=f.getBestCmap() or {}
        chars=sorted({c for line in lyric_lines(json.loads(Path(document).read_text(encoding='utf-8'))) for c in line['text'] if not c.isspace()})
        missing=[{'character':c,'codepoint':f'U+{ord(c):04X}'} for c in chars if ord(c) not in cmap or cmap[ord(c)]=='.notdef']
        family=next((n.toUnicode() for n in f['name'].names if n.nameID==16),None) or next(n.toUnicode() for n in f['name'].names if n.nameID==1)
        return {'schema_version':1,'font_sha256':sha(font),'text_document_sha256':sha(document),'family':family,'checked_characters':len(chars),'missing':missing,'ok':not missing,'scope':'Actual font cmap coverage only; inspect rendered glyph shapes, size, contrast and reading time separately.'}
    finally:f.close()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--font',type=Path,required=True);p.add_argument('--lyrics',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():p.error('output exists; previous glyph evidence preserved')
    try:
        result=inspect_font(a.font,a.lyrics);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n', encoding='utf-8');print(json.dumps(result,ensure_ascii=False));return 0 if result['ok'] else 2
    except ImportError:p.error('fontTools is required for the selected glyph check; see requirements-media.txt')
    except (OSError,ValueError,KeyError) as exc:p.error(str(exc))


if __name__ == '__main__':
    import sys
    for _stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(_stream, 'reconfigure'):
            _stream.reconfigure(encoding='utf-8')
    raise SystemExit(main())
