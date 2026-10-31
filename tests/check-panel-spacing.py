"""Measure panel-frame gaps in actual SVG output; no third-party Python modules."""
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def frames(svg):
    result = []

    def visit(element, y=0):
        transform = element.get('transform', '')
        match = re.fullmatch(r'matrix\(1 0 0 1 ([\d.e+-]+) ([\d.e+-]+)\)', transform)
        if match:
            y += float(match[2])
        if element.get('stroke') == '#252525':
            path = element.attrib['d']
            radius = float(re.search(r'm ([\d.]+) 0', path)[1])
            height = float(re.search(r' v ([\d.]+)', path)[1]) + 2 * radius
            result.append((y, height))
        for child in element:
            visit(child, y)

    visit(ET.parse(svg).getroot())
    return result


def check():
    with tempfile.TemporaryDirectory(prefix='_spacing-', dir=ROOT / 'tests') as folder:
        for mode in ['roteiro', 'editorial', 'producao']:
            for setting, default in [('', 72 / 2.54), (', espaco-quadros: 3mm', 72 / 25.4 * 3)]:
                source = Path(folder) / 'case.typ'
                output = Path(folder) / 'case.svg'
                source.write_text('''#import "../../lib.typ" as hq
#set page(width: 180mm, height: 500mm, margin: 10mm)
#hq.renderizar(hq.pagina(1,
  hq.linha(hq.quadro[Cena], hq.quadro[Cena],
    hq.quadro(espaco-antes: 2cm)[Cena], hq.quadro(espaco-antes: 0pt)[Cena]),
  hq.linha(hq.quadro[Cena]),
), modo: "''' + mode + '"' + setting + ')', encoding='utf-8')
                subprocess.run(['typst', 'compile', '--root', str(ROOT), str(source), str(output)], check=True, capture_output=True)
                boxes = frames(output)
                assert len(boxes) == 5, boxes
                gaps = [b[0] - a[0] - a[1] for a, b in zip(boxes, boxes[1:])]
                expected = [default, 2 * 72 / 2.54, 0, default]
                assert all(abs(a - b) < .01 for a, b in zip(gaps, expected)), (mode, setting, gaps)
    print('Panel spacing: default, global override, local override, zero and row boundary passed in all three text views.')


if __name__ == '__main__':
    check()
