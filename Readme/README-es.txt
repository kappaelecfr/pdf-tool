PDF Tool — guía rápida
==========================================================

Un editor de PDF que funciona en tu propio ordenador. Sin internet,
sin cuenta. Ningún archivo sale de esta máquina.


ABRIR UN ARCHIVO — tres maneras
-------------------------------
  * el botón «Abrir PDF», arriba a la izquierda
  * arrastra un PDF directamente a la ventana
  * arrastra un PDF sobre el icono «PDF Tool.exe»


LAS CUATRO PESTAÑAS, A LA DERECHA
---------------------------------
  Páginas   unir, dividir, girar, borrar, reordenar. Elige páginas
            haciendo clic en las miniaturas de la izquierda, o
            escribe un intervalo:  1-3, 7, 10-

  Añadir    marca de agua, numeración, y una imagen, firma o sello
            que colocas con un clic

  Editar    cambiar el texto del PDF, buscar y reemplazar, y la
            redacción definitiva

  Extraer   texto, tablas en .csv, imágenes, páginas en PNG, OCR y
            compresión


EDITAR TEXTO — LEE ESTO
-----------------------
Un PDF no guarda texto editable como Word. El texto está dibujado en
posiciones fijas de la página.

Lo que hace la aplicación: tapa el texto viejo con el color del fondo
(que detecta sola) y escribe el nuevo encima, con una tipografía
parecida y el mismo tamaño.

  Va bien para    fechas, nombres, importes, palabras cortas
  No sirve para   reescribir párrafos enteros — las líneas de
                  alrededor no se recolocan

Pulsa «Activar modo edición» y todas las zonas de texto de la página
se ponen azules, así ves exactamente dónde puedes hacer clic. Haz clic
en una, cámbiala en la caja de la derecha y pulsa «Aplicar el cambio».
Ctrl+Z deshace cualquier cosa.

El texto nuevo se asienta justo en la línea donde estaba el viejo. Para
moverlo, agárralo con el ratón y arrástralo: dos líneas muestran dónde
va a caer, y en cuanto se acerca a la línea de un texto vecino se
engancha a ella. Las flechas del teclado lo mueven a pasitos, para
cuando no quieres alinearte con nada.


BORRAR UNA ZONA — CÓDIGO QR, LOGOTIPO, SELLO
--------------------------------------------
Un código QR no es texto ni imagen: está trazado con miles de rasgos
pequeños. Por eso no lo quitan ni «Ocultar definitivamente» ni el borrado
de una imagen.

En la pestaña Editar, abajo del todo, pulsa «Elegir una zona que borrar» y
arrastra un rectángulo por encima en la vista previa. Todo lo que queda
dentro — texto, imágenes y dibujos — sale del archivo; no queda solo
tapado.

Lo que solo roza el borde del rectángulo queda intacto, así que los marcos
de la página y las líneas de las tablas no se rompen. Toma la zona 2-3 mm
más ancha que el código.
COPIAR UNA ZONA DE UN PDF A OTRO
--------------------------------
Tienes un membrete de empresa, una firma o una tabla en un PDF y lo
quieres en otro. No lo fotografíes: cópialo.

En la pestaña Añadir, abajo, pulsa «Copiar una zona» y arrastra un
rectángulo sobre lo que te interesa. Luego abre el PDF donde lo quieres,
pulsa «Pegar haciendo clic en la página» y haz clic donde toca.

La zona se va con su texto: sigue siendo texto, se puede buscar y
seleccionar después de pegarla. El archivo crece unos kilobytes, no
cientos.

Si aun así quieres una imagen — para que nadie pueda copiar el texto de
ahí, por ejemplo — marca «Pegar como imagen». El tamaño sale entonces del
ajuste de calidad de la pestaña Extraer.

Solo se copia lo que está dentro del rectángulo. El resto de la página de
origen se queda.




ZOOM Y DESPLAZAMIENTO
---------------------
Debajo de la página: los botones  -  y  +  , el porcentaje actual, y
«Ajustar», que devuelve la página al tamaño de la ventana.

  Ctrl + rueda      acercar y alejar
  rueda             desplazar arriba y abajo
  Mayús + rueda     desplazar izquierda y derecha
  arrastrar         mover la página cuando está ampliada


IDIOMA
------
La lista de arriba a la derecha. La interfaz cambia al momento, sin
cerrar tu documento, y se recuerda tu elección.


OCR — PARA DOCUMENTOS ESCANEADOS
--------------------------------
Si el PDF es un escaneo (una foto del papel), el texto no se puede
seleccionar. El OCR lee las letras de la imagen.

Los botones de OCR siguen en gris hasta que instales Tesseract, que
es gratuito:

  1. Descarga el instalador para Windows de
     https://github.com/UB-Mannheim/tesseract/wiki
  2. Ejecútalo. En el paso de los idiomas («Additional language
     data») marca los idiomas que necesites.
  3. Deja la carpeta por defecto.
  4. Cierra y vuelve a abrir PDF Tool. Los botones se activan solos.

Todo lo demás funciona perfectamente sin Tesseract.


TECLADO
-------
  Ctrl+O   abrir           Ctrl+Z   deshacer
  Ctrl+S   guardar         Ctrl+Y   rehacer
  Ctrl+Mayús+S  guardar como   Ctrl+A  seleccionar todas las páginas
  Supr     borrar las páginas seleccionadas
  Re Pág / Av Pág          página anterior / siguiente
  Esc      salir del modo edición o de la colocación de imagen

  Mayús+clic en una miniatura selecciona todo el intervalo.


SEGURIDAD
---------
Cuando guardas encima del archivo original, se conserva una copia al
lado con .bak añadido al nombre. Si algo sale mal, quita «.bak» del
nombre y tienes de vuelta el archivo inicial.

«Ocultar definitivamente» quita el texto del archivo de verdad.
Después de guardar no hay vuelta atrás.
