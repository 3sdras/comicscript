#import "../src/apresentacoes/blocos.typ": estilos-internos, dispor-bloco

// Frequências 3, 2, 1, 1: empate não cria uma redução adicional.
#let estilos = estilos-internos(("nota", "fala", "nota", "plano", "nota", "fala", "composicao"))
#assert(estilos.nota.reducao == 0cm)
#assert(estilos.fala.reducao == 1cm)
#assert(estilos.plano.reducao == 2cm)
#assert(estilos.composicao.reducao == 2cm)
#assert(estilos.fala.posicao == left)
#assert(estilos.plano.posicao == center)
#assert(estilos.composicao.posicao == right)
#assert(estilos-internos(()) == (:))

// A ordem das ocorrências não muda a apresentação de cada tipo.
#let outros = estilos-internos(("composicao", "fala", "plano", "nota", "fala", "nota", "nota"))
#assert(outros == estilos)

// Confere a largura efetivamente recebida pelo conteúdo, inclusive em área estreita.
#block(width: 40mm)[
  #dispor-bloco("raro", estilos: (raro: (reducao: 9cm, posicao: right)))[
    #layout(tamanho => metadata((teste: "estreito", largura: tamanho.width)))
    Bloco estreito.
  ]
]
#block(width: 100mm)[
  #dispor-bloco("fala", estilos: estilos)[
    #layout(tamanho => metadata((teste: "passo", largura: tamanho.width)))
    Bloco com redução de um centímetro.
  ]
]
#context {
  let valores = query(metadata).map(m => m.value)
  let estreito = valores.find(v => v.teste == "estreito")
  let passo = valores.find(v => v.teste == "passo")
  assert(calc.abs(estreito.largura - 24mm) < 0.01pt)
  assert(calc.abs(passo.largura - 90mm) < 0.01pt)
}
