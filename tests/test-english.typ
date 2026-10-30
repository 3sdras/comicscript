#import "../lib.typ" as hq

#let en-note = hq.note("composition", status: "resolved", author: "Example editor")[Keep the doorway.]
#let pt-note = hq.nota("composicao", estado: "resolvida", autor: "Example editor")[Keep the doorway.]
#assert(en-note == pt-note)
#assert(hq.note("custom-category")[Text.].categoria == "custom-category")
#assert(hq.note("ideia", status: "aberta")[Text.] == hq.nota("ideia")[Text.])
#for (en, pt) in (("open", "aberta"), ("resolved", "resolvida"), ("discarded", "descartada")) {
  assert(hq.note("idea", status: en)[Text.].estado == pt)
}
#for (en, pt) in (("problem", "problema"), ("idea", "ideia"), ("alternative", "alternativa"),
  ("continuity", "continuidade"), ("subtext", "subtexto"), ("clue", "pista"),
  ("reference", "referencia"), ("decision", "decisao"), ("composition", "composicao"), ("technical", "tecnica")) {
  assert(hq.note(en)[Text.].categoria == pt)
}
#assert(hq.caption[Tomorrow.] == hq.legenda[Tomorrow.])
#assert(hq.sound[CRASH!] == hq.som[CRASH!])
#assert(hq.speech("Alex", mode: "thought")[Wait.] == hq.fala("Alex", modo: "pensamento")[Wait.])
#assert(hq.speech("Alex", mode: "off-panel")[Wait.].modo == "fora de campo")
#assert(hq.speech("Alex", mode: "whisper")[Wait.].modo == "sussurro")
#assert(hq.speech("Alex", mode: "custom-mode")[Wait.].modo == "custom-mode")

#let en-panel = hq.panel(id: "door", weight: 2, shot: "wide", composition: [Left.],
  texts: (hq.speech("Alex")[Wait.],), notes: (en-note,), references: ([Study.],))[A door.]
#let pt-panel = hq.quadro(id: "door", peso: 2, plano: "wide", composicao: [Left.],
  textos: (hq.fala("Alex")[Wait.],), notas: (pt-note,), referencias: ([Study.],))[A door.]
#assert(en-panel == pt-panel)
#let en = hq.page(1, title: [Door], objective: [Leave.], status: "draft", notes: (en-note,),
  hq.row(id: "top", weight: 2, notes: (en-note,), en-panel))
#let pt = hq.pagina(1, titulo: [Door], objetivo: [Leave.], estado: "draft", notas: (pt-note,),
  hq.linha(id: "top", peso: 2, notas: (pt-note,), pt-panel))
#assert(en == pt)
#assert(hq.validate(en) == hq.validar(pt))
#assert(hq.page(2, hq.row(hq.quadro[Mixed API.])).linhas.at(0).quadros.len() == 1)

English and Portuguese constructors produce identical data.
