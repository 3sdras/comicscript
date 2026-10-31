// Interface pública. Os construtores produzem dados, sem efeitos no documento.
#import "src/modelo.typ": pagina, linha, quadro, fala, legenda, som, nota
#import "src/validacao.typ": validar, exigir-espaco
#import "src/apresentacoes/roteiro.typ": apresentar-roteiro
#import "src/apresentacoes/editorial.typ": validar-opcoes-editoriais
#import "src/apresentacoes/esquema.typ": apresentar-esquema
#import "src/relatorios.typ": mapa-narrativo, pendencias, dialogos, relatorio-textos

#let renderizar(
  paginas,
  modo: "roteiro",
  espaco-quadros: 1cm,
  estados-notas: ("aberta", "resolvida", "descartada"),
  limite-palavras: 60,
  largura-esquema: 140mm,
  altura-esquema: 180mm,
  resumos-esquema: true,
) = {
  assert(modo in ("roteiro", "editorial", "esquema", "producao"), message:
    "Modo desconhecido: " + repr(modo) + ". Use roteiro, editorial, esquema ou producao.")
  exigir-espaco(espaco-quadros)
  let paginas = validar(paginas)
  if modo == "roteiro" {
    apresentar-roteiro(paginas, espaco-quadros: espaco-quadros)
  } else if modo == "editorial" {
    validar-opcoes-editoriais(estados-notas, limite-palavras)
    apresentar-roteiro(paginas, espaco-quadros: espaco-quadros, editorial: true, estados-notas: estados-notas, limite-palavras: limite-palavras)
  } else if modo == "producao" {
    apresentar-roteiro(paginas, espaco-quadros: espaco-quadros, producao: true)
  } else {
    apresentar-esquema(paginas, largura: largura-esquema, altura: altura-esquema, resumos: resumos-esquema)
  }
}

// English authoring aliases. Data keeps the canonical Portuguese field names.
#let _note-statuses = (open: "aberta", resolved: "resolvida", discarded: "descartada")
#let _categories = (problem: "problema", idea: "ideia", alternative: "alternativa",
  continuity: "continuidade", subtext: "subtexto", clue: "pista", reference: "referencia",
  decision: "decisao", composition: "composicao", technical: "tecnica")
#let _speech-modes = (thought: "pensamento", "off-panel": "fora de campo", whisper: "sussurro")
#let _render-modes = (script: "roteiro", editorial: "editorial", layout: "esquema", production: "producao")

#let page(number, title: none, objective: none, status: none, notes: (), ..rows) = pagina(
  number, titulo: title, objetivo: objective, estado: status, notas: notes, ..rows)

#let row(weight: 1, id: none, notes: (), ..panels) = linha(peso: weight, id: id, notas: notes, ..panels)

#let panel(visual, id: none, weight: 1, shot: none, composition: none, texts: (), notes: (), references: (), space-before: none) = quadro(
  visual, id: id, peso: weight, plano: shot, composicao: composition,
  textos: texts, notas: notes, referencias: references, espaco-antes: space-before)

#let speech(character, body, mode: "normal") = fala(
  character, body, modo: _speech-modes.at(mode, default: mode))

#let caption = legenda
#let sound = som

#let note(category, body, status: "open", author: none) = nota(
  _categories.at(category, default: category), body,
  estado: _note-statuses.at(status, default: status), autor: author)

#let validate = validar

#let render(pages, mode: "script", note-statuses: ("open", "resolved", "discarded"), word-limit: 60,
  layout-width: 140mm, layout-height: 180mm, layout-summaries: true, panel-spacing: 1cm) = {
  assert(type(note-statuses) == array, message: "note-statuses must be an array.")
  renderizar(pages, modo: _render-modes.at(mode, default: mode),
    estados-notas: note-statuses.map(s => _note-statuses.at(s, default: s)),
    limite-palavras: word-limit, largura-esquema: layout-width, altura-esquema: layout-height,
    resumos-esquema: layout-summaries, espaco-quadros: panel-spacing)
}

#let narrative-map = mapa-narrativo
#let pending-notes = pendencias

#let dialogues(pages, character: none) = dialogos(pages, personagem: character)

#let text-report(pages, word-limit: 60) = relatorio-textos(pages, limite-palavras: word-limit)
