"""Compilação, erros esperados e comportamento das saídas (sem dependências Python)."""

from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def executar():
    for ferramenta in ("typst", "pdftotext"):
        if not shutil.which(ferramenta):
            raise SystemExit(f"Instale {ferramenta} para executar esta verificação.")

    total = 0
    with tempfile.TemporaryDirectory(prefix="_casos-", dir=ROOT / "tests") as fontes:
        with tempfile.TemporaryDirectory(prefix="comicscript-") as saidas:

            def compilar(codigo, erro=None):
                nonlocal total
                total += 1
                origem = Path(fontes) / f"caso-{total}.typ"
                destino = Path(saidas) / f"caso-{total}.pdf"
                origem.write_text(
                    '#import "../../lib.typ" as hq\n'
                    '#set page(paper: "a4", margin: 20mm)\n'
                    '#set text(size: 11pt, lang: "pt")\n' + codigo,
                    encoding="utf-8",
                )
                resultado = subprocess.run(
                    ["typst", "compile", "--root", str(ROOT), str(origem), str(destino)],
                    capture_output=True, text=True,
                )
                if erro:
                    assert resultado.returncode != 0, f"Caso {total} deveria falhar."
                    assert erro in resultado.stderr, resultado.stderr
                    return ""
                assert resultado.returncode == 0, resultado.stderr
                assert not resultado.stderr.strip(), resultado.stderr
                return subprocess.check_output(["pdftotext", str(destino), "-"], text=True)

            invalidos = (
                ('#hq.pagina(0, hq.linha(hq.quadro[A]))', "inteiro positivo"),
                ('#hq.pagina(1.5, hq.linha(hq.quadro[A]))', "inteiro positivo"),
                ('#hq.pagina(1)', "pelo menos uma linha"),
                ('#hq.linha()', "pelo menos um quadro"),
                ('#hq.linha(hq.fala("Alex")[A])', "elemento quadro"),
                ('#hq.pagina(1, hq.quadro[A])', "elemento linha"),
                ('#hq.quadro(peso: 0)[A]', "maior que zero"),
                ('#hq.linha(peso: -1, hq.quadro[A])', "maior que zero"),
                ('#hq.quadro(peso: true)[A]', "maior que zero"),
                ('#hq.quadro(peso: float("inf"))[A]', "número finito"),
                ('#hq.quadro(id: " ")[A]', "string não vazia"),
                ('#hq.nota("problema", estado: "pendente")[A]', "Estado da nota"),
                ('#hq.quadro(textos: (hq.nota("ideia")[A],))[B]', "fala, legenda ou som"),
                ('#hq.quadro(notas: (hq.fala("Alex")[A],))[B]', "elemento nota"),
                ('#hq.pagina(1, hq.linha(hq.quadro[A]), linhas: ())', "Campo desconhecido"),
                ('#hq.linha(hq.quadro[A], altura: 2)', "Campo desconhecido"),
                ('#hq.renderizar((), modo: "inexistente")', "Modo desconhecido"),
                ('#hq.renderizar((hq.linha(hq.quadro[A]),))', "elemento pagina"),
                ('#hq.renderizar(hq.pagina(1, hq.linha(hq.quadro[A])), modo: "editorial", limite-palavras: 0)', "inteiro positivo ou none"),
                ('#hq.renderizar(hq.pagina(1, hq.linha(hq.quadro[A])), modo: "editorial", estados-notas: ("pendente",))', "estados-notas aceita"),
                ('#hq.renderizar(hq.pagina(1, hq.linha(id: "igual", hq.quadro(id: "igual")[A])))', "ID explícito duplicado: igual"),
                ('#hq.renderizar((hq.pagina(1, hq.linha(hq.quadro(id: "igual")[A])), hq.pagina(2, hq.linha(hq.quadro(id: "igual")[B]))))', "ID explícito duplicado: igual"),
                ('#hq.renderizar(hq.pagina(1, hq.linha(hq.quadro[A])), modo: "esquema", largura-esquema: 0mm)', "comprimentos positivos"),
                ('#hq.renderizar(hq.pagina(1, hq.linha(hq.quadro[A])), modo: "esquema", resumos-esquema: "sim")', "true ou false"),
                ('#hq.note("idea", status: "pending")[A]', "Estado da nota"),
                ('#hq.render((), mode: "unknown")', "Modo desconhecido"),
                ('#hq.render((), note-statuses: "open")', "note-statuses must be an array"),
                ('#hq.page(1, hq.row(hq.panel[A]), unknown: 1)', "Campo desconhecido"),
            )
            for codigo, erro in invalidos:
                compilar(codigo, erro=erro)

            # Mesma fonte: preservar ordem e ocultar apenas material editorial.
            dados = '''
#let p = hq.pagina(42,
  objetivo: [OBJETIVO_TOKEN], estado: [ESTADO_TOKEN],
  notas: (hq.nota("ideia")[PAGINA_TOKEN],),
  hq.linha(notas: (hq.nota("ideia")[LINHA_TOKEN],),
    hq.quadro(textos: (
      hq.legenda[LEGENDA_TOKEN],
      hq.fala("Alex", modo: "pensamento")[PENSAMENTO_TOKEN],
      hq.som[SOM_TOKEN],
    ), notas: (
      hq.nota("inventada")[ABERTA_TOKEN],
      hq.nota("ideia", estado: "resolvida")[RESOLVIDA_TOKEN],
      hq.nota("ideia", estado: "descartada")[DESCARTADA_TOKEN],
    ))[VISUAL_TOKEN],
    hq.quadro[],
  ),
)
'''
            limpo = compilar(dados + '#hq.renderizar(p)')
            editorial = compilar(dados + '#hq.renderizar(p, modo: "editorial", limite-palavras: 2)')
            abertas = compilar(dados + '#hq.renderizar(p, modo: "editorial", estados-notas: ("aberta",))')
            sem_limiar = compilar(dados + '#hq.renderizar(p, modo: "editorial", limite-palavras: none)')
            for token in ("VISUAL_TOKEN", "LEGENDA_TOKEN", "PENSAMENTO_TOKEN", "SOM_TOKEN"):
                assert token in limpo and token in editorial
            assert limpo.index("LEGENDA_TOKEN") < limpo.index("PENSAMENTO_TOKEN") < limpo.index("SOM_TOKEN")
            for token in ("OBJETIVO_TOKEN", "ESTADO_TOKEN", "PAGINA_TOKEN", "LINHA_TOKEN", "ABERTA_TOKEN", "RESOLVIDA_TOKEN", "DESCARTADA_TOKEN"):
                assert token not in limpo and token in editorial
            assert "ABERTA_TOKEN" in abertas
            assert "RESOLVIDA_TOKEN" not in abertas and "DESCARTADA_TOKEN" not in abertas
            assert "Sem descrição visual" in editorial and "Aviso editorial" not in limpo
            assert "limiar editorial" in editorial and "limiar editorial" not in sem_limiar

            # English options produce the same text as their Portuguese counterparts.
            for en, pt in (("script", "roteiro"), ("editorial", "editorial"), ("layout", "esquema"), ("production", "producao")):
                english = compilar(dados + f'''#hq.render(p, mode: "{en}",
  note-statuses: ("open",), word-limit: 2,
  layout-width: 110mm, layout-height: 140mm, layout-summaries: false)''')
                portuguese = compilar(dados + f'''#hq.renderizar(p, modo: "{pt}",
  estados-notas: ("aberta",), limite-palavras: 2,
  largura-esquema: 110mm, altura-esquema: 140mm, resumos-esquema: false)''')
                assert english == portuguese, en
            assert compilar(dados + '#hq.render(p)') == compilar(dados + '#hq.renderizar(p)')
            for en, pt in (
                ('hq.narrative-map(p)', 'hq.mapa-narrativo(p)'),
                ('hq.pending-notes(p)', 'hq.pendencias(p)'),
                ('hq.dialogues(p, character: "Alex")', 'hq.dialogos(p, personagem: "Alex")'),
                ('hq.text-report(p, word-limit: 2)', 'hq.relatorio-textos(p, limite-palavras: 2)'),
            ):
                assert compilar(dados + '#' + en) == compilar(dados + '#' + pt), en

            # The README quick start is executable, not just illustrative syntax.
            readme = (ROOT / "README.md").read_text(encoding="utf-8")
            quick_start = readme.split("```typst\n", 1)[1].split("```", 1)[0]
            quick_start = quick_start.replace('#import "lib.typ" as hq', '')
            quick_start = quick_start.replace('#import "@preview/comicscript:0.3.0" as hq', '')
            assert "Shall we?" in compilar(quick_start)

            # Relatórios selecionam os dados certos e preservam a ordem de leitura.
            mapa = compilar(dados + '#hq.mapa-narrativo(p)')
            assert "OBJETIVO_TOKEN" in mapa and "ESTADO_TOKEN" in mapa
            assert "VISUAL_TOKEN" not in mapa and "ABERTA_TOKEN" not in mapa
            pendencias = compilar(dados + '#hq.pendencias(p)')
            for token in ("PAGINA_TOKEN", "LINHA_TOKEN", "ABERTA_TOKEN"):
                assert token in pendencias
            for token in ("RESOLVIDA_TOKEN", "DESCARTADA_TOKEN", "VISUAL_TOKEN", "OBJETIVO_TOKEN"):
                assert token not in pendencias
            falas = compilar(dados + '#hq.dialogos(p, personagem: "Alex")')
            assert "PENSAMENTO_TOKEN" in falas
            for token in ("VISUAL_TOKEN", "LEGENDA_TOKEN", "SOM_TOKEN", "ABERTA_TOKEN"):
                assert token not in falas
            assert "Nenhuma fala encontrada" in compilar(dados + '#hq.dialogos(p, personagem: "Sam")')
            contagem = compilar(dados + '#hq.relatorio-textos(p, limite-palavras: 2)')
            assert "Revisar" in contagem and "Silencioso" in contagem
            assert "Revisar" not in compilar(dados + '#hq.relatorio-textos(p, limite-palavras: none)')

            # Produção inclui orientações técnicas nos três níveis, sem notas privadas.
            arte = compilar('''
#let p = hq.pagina(8, objetivo: [PRIVADO_OBJETIVO], estado: [PRIVADO_ESTADO],
  notas: (hq.nota("tecnica")[TECNICA_PAGINA], hq.nota("subtexto")[PRIVADO_PAGINA]),
  hq.linha(notas: (hq.nota("continuidade")[TECNICA_LINHA], hq.nota("alternativa")[PRIVADO_LINHA]),
    hq.quadro(textos: (hq.fala("Alex")[FALA_ARTE],), referencias: ([REFERENCIA_ARTE],), notas: (
      hq.nota("composicao", estado: "resolvida")[TECNICA_QUADRO],
      hq.nota("tecnica", estado: "descartada")[PRIVADO_DESCARTADA],
      hq.nota("problema")[PRIVADO_QUADRO],
    ))[VISUAL_ARTE],
  ),
)
#hq.renderizar(p, modo: "producao")
''')
            for token in ("TECNICA_PAGINA", "TECNICA_LINHA", "TECNICA_QUADRO", "FALA_ARTE", "REFERENCIA_ARTE", "VISUAL_ARTE"):
                assert token in arte
            assert "PRIVADO" not in arte

            # Texto extenso não altera a composição nem cria folhas extras no esquema.
            esquema = compilar('''
#let p = hq.pagina(9,
  hq.linha(hq.quadro[RESUMO_CURTO #lorem(900) FINAL_LONGO]),
  hq.linha(peso: 3, hq.quadro(peso: 2)[Maior.], hq.quadro[Menor.]),
)
#hq.renderizar(p, modo: "esquema")
''')
            assert esquema.count("\f") == 1
            assert "RESUMO_CURTO" in esquema and "FINAL_LONGO" not in esquema
            sem_resumo = compilar(dados + '#hq.renderizar(p, modo: "esquema", resumos-esquema: false)')
            assert "VISUAL_TOKEN" not in sem_resumo and "PENSAMENTO_TOKEN" not in sem_resumo
            assert "Q1" in sem_resumo and "Q2" in sem_resumo

            # Um quadro curto deve levar descrição e fala juntos para a próxima folha.
            junto = compilar('''
#v(490pt)
#hq.renderizar(hq.pagina(1, hq.linha(hq.quadro(
  textos: (hq.fala("Alex")[FALA_JUNTA #lorem(35)],),
)[VISUAL_JUNTO #lorem(55)])), modo: "producao")
''')
            folhas = junto.split("\f")
            assert junto.count("\f") > 1
            assert next(i for i, f in enumerate(folhas) if "VISUAL_JUNTO" in f) == next(i for i, f in enumerate(folhas) if "FALA_JUNTA" in f)

            # Um quadrinho e sua nota podem ultrapassar uma folha sem perder texto.
            longo = compilar('''
#hq.renderizar(hq.pagina(7, hq.linha(hq.quadro(
  notas: (hq.nota("ideia")[INICIO_NOTA #lorem(900) FIM_NOTA],),
)[INICIO_VISUAL #lorem(900) FIM_VISUAL])), modo: "editorial")
''')
            assert longo.count("\f") > 2
            for token in ("INICIO_VISUAL", "FIM_VISUAL", "INICIO_NOTA", "FIM_NOTA"):
                assert token in longo

    print(f"{total} casos de compilação passaram; visibilidade, ordem, filtros e quebra de página verificados.")


if __name__ == "__main__":
    executar()
