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
