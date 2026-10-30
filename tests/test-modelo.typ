#import "../lib.typ" as hq
#import "../src/validacao.typ": contar-palavras, avisos-quadro
#import "../src/apresentacoes/esquema.typ": medidas-esquema

#let q = hq.quadro(
  id: "quadro-estavel",
  textos: (
    hq.legenda[No dia seguinte.],
    hq.fala("Alex", modo: "pensamento")[Que *lugar* estranho.],
    hq.som[CRASH!],
  ),
)[Uma porta se abre.]
#let p = hq.pagina(9, hq.linha(q), hq.linha(peso: 3, hq.quadro[Uma oficina.]))

// Tipos semânticos e ordem de leitura preservados como dados.
#assert(type(p) == dictionary)
#assert(p.linhas.at(0).quadros.at(0).textos.map(t => t.tipo) == ("legenda", "fala", "som"))
#assert(p.linhas.at(1).peso == 3)
#assert(hq.validar(p) == (p,))
#assert(hq.validar((p,)) == (p,))
#assert(hq.quadro[Silêncio.].peso == 1)

// Mover o mesmo quadro altera sua posição, preservando ID e conteúdo.
#let movida = hq.pagina(10, hq.linha(hq.quadro[Outro quadro.], q))
#assert(hq.validar(movida).at(0).linhas.at(0).quadros.at(1).id == "quadro-estavel")

#assert(contar-palavras(q) == 7)
#assert(avisos-quadro(q, limite-palavras: 7) == ())
#assert(avisos-quadro(q, limite-palavras: 6).len() == 1)
#assert(avisos-quadro(q, limite-palavras: none) == ())
#assert(avisos-quadro(hq.quadro[]).len() == 1)
#assert(hq.nota("categoria-inventada")[Texto.].categoria == "categoria-inventada")
#assert(hq.nota("ideia", estado: "descartada")[Texto.].estado == "descartada")

// Geometria desconta sarjetas antes de distribuir pesos horizontais e verticais.
#let geometria = hq.pagina(1,
  hq.linha(hq.quadro[A]),
  hq.linha(peso: 3, hq.quadro(peso: 2)[B], hq.quadro[C]),
)
#let medidas = medidas-esquema(geometria, 153mm, 203mm)
#assert(medidas.at(0).altura == 50mm)
#assert(medidas.at(1).altura == 150mm)
#assert(medidas.at(1).larguras == (100mm, 50mm))

Testes do modelo concluídos.
