PDF Tool — guia rápido
==========================================================

Um editor de PDF que corre no seu próprio computador. Sem internet,
sem conta. Nenhum ficheiro sai desta máquina.


ABRIR UM FICHEIRO — três formas
-------------------------------
  * o botão «Abrir PDF», em cima à esquerda
  * arraste um PDF directamente para a janela
  * arraste um PDF para cima do ícone «PDF Tool.exe»


OS QUATRO SEPARADORES, À DIREITA
--------------------------------
  Páginas      juntar, dividir, rodar, apagar, reordenar. Escolha as
               páginas clicando nas miniaturas à esquerda, ou escreva
               um intervalo:  1-3, 7, 10-

  Acrescentar  marca de água, numeração, e uma imagem, assinatura ou
               carimbo que coloca com um clique

  Editar       alterar o texto do PDF, procurar e substituir, e a
               tarja definitiva

  Extrair      texto, tabelas em .csv, imagens, páginas em PNG, OCR
               e compressão


EDITAR TEXTO — LEIA ISTO
------------------------
Um PDF não guarda texto editável como o Word. O texto está desenhado
em posições fixas na página.

O que a aplicação faz: tapa o texto antigo com a cor do fundo (que
detecta sozinha) e escreve o novo por cima, com um tipo de letra
parecido e o mesmo tamanho.

  Serve para       datas, nomes, valores, palavras curtas
  Não serve para   reescrever parágrafos inteiros — as linhas à
                   volta não são reorganizadas

Carregue em «Activar o modo de edição» e todas as zonas de texto da
página ficam azuis, para ver exactamente onde pode clicar. Clique numa,
altere-a na caixa à direita e carregue em «Aplicar a alteração».
Ctrl+Z desfaz tudo.

O texto novo assenta exatamente na linha onde estava o antigo. Se um tipo
de letra substituto o deixar ainda assim um fio ao lado, pode alinhá-lo:
as setas por baixo da caixa deslocam-no um quarto de ponto, ou agarra-o
com o rato e arrasta-o para o sítio.


APAGAR UMA ZONA — CÓDIGO QR, LOGÓTIPO, CARIMBO
----------------------------------------------
Um código QR não é texto nem imagem: é traçado a partir de milhares de
pequenos riscos. Por isso não o tiram nem «Ocultar definitivamente» nem
apagar uma imagem.

No separador Editar, mesmo em baixo, prima «Escolher uma zona a apagar» e
arraste um retângulo por cima na pré-visualização. Tudo o que fica dentro
— texto, imagens e desenhos — sai do ficheiro; não fica apenas tapado.

O que apenas toca a margem do retângulo fica intacto, para que as molduras
da página e os filetes das tabelas não se partam. Tome a zona 2-3 mm mais
larga do que o código.


ZOOM E DESLOCAÇÃO
-----------------
Por baixo da página: os botões  -  e  +  , a percentagem actual, e
«Ajustar», que repõe a página no tamanho da janela.

  Ctrl + roda       aproximar e afastar
  roda              deslocar para cima e para baixo
  Shift + roda      deslocar para a esquerda e para a direita
  arrastar          mover a página quando está ampliada


LÍNGUA
------
A lista em cima à direita. A interface muda de imediato, sem fechar o
documento, e a sua escolha fica guardada.


OCR — PARA DOCUMENTOS DIGITALIZADOS
-----------------------------------
Se o PDF for uma digitalização (uma fotografia do papel), o texto não
pode ser seleccionado. O OCR lê as letras a partir da imagem.

Os botões de OCR ficam cinzentos até instalar o Tesseract, que é
gratuito:

  1. Descarregue o instalador para Windows de
     https://github.com/UB-Mannheim/tesseract/wiki
  2. Execute-o. No passo das línguas («Additional language data»)
     marque as línguas de que precisa.
  3. Deixe a pasta predefinida.
  4. Feche e volte a abrir o PDF Tool. Os botões activam-se sozinhos.

Tudo o resto funciona muito bem sem o Tesseract.


TECLADO
-------
  Ctrl+O   abrir           Ctrl+Z   anular
  Ctrl+S   guardar         Ctrl+Y   refazer
  Ctrl+Shift+S  guardar como    Ctrl+A  seleccionar todas as páginas
  Delete   apagar as páginas seleccionadas
  Page Up / Page Down      página anterior / seguinte
  Escape   sair do modo de edição ou da colocação de imagem

  Shift+clique numa miniatura selecciona todo o intervalo.


SEGURANÇA
---------
Quando guarda por cima do ficheiro original, fica ao lado uma cópia de
segurança com .bak acrescentado ao nome. Se algo correr mal, tire
«.bak» do nome e tem de volta o ficheiro inicial.

«Ocultar definitivamente» retira mesmo o texto do ficheiro. Depois de
guardar não há volta.
