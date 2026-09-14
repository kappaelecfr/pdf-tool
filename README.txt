PDF Tool — quick guide
==========================================================

A PDF editor that runs on your own computer. No internet, no account.
No file ever leaves this machine.


OPENING A FILE — three ways
---------------------------
  * the "Open PDF" button, top left
  * drag a PDF straight into the window
  * drag a PDF onto the "PDF Tool.exe" icon


THE FOUR TABS, ON THE RIGHT
---------------------------
  Pages     merge, split, rotate, delete, reorder. Pick pages by
            clicking the thumbnails on the left, or type a range
            such as  1-3, 7, 10-

  Add       watermark, page numbers, and an image, signature or
            stamp that you place with a click

  Edit      change the text inside the PDF, find and replace,
            and permanent redaction

  Extract   text, tables as .csv, images, pages as PNG, OCR,
            and compression


EDITING TEXT — PLEASE READ
--------------------------
A PDF does not store editable text the way Word does. The text is
painted at fixed positions on the page.

What the app does: it covers the old text with the background colour
(which it detects by itself) and writes the new text over it, in a
similar font and the same size.

  Works well for   dates, names, amounts, short words
  Not meant for    rewriting whole paragraphs — the surrounding
                   lines are not reflowed

Press "Start edit mode" and every text area on the page turns blue,
so you can see exactly what is clickable. Click one, change it in the
box on the right, press "Apply change". Ctrl+Z undoes anything.

The new text lands on the very line the old text sat on. To move it,
take hold of it with the mouse and drag: two lines show where it will
land, and when it comes near the line of a neighbouring text it snaps
onto it. The arrow keys move it in small steps, for when you do not
want to align with anything.


ERASING AN AREA — QR CODE, LOGO, STAMP
--------------------------------------
A QR code is neither text nor an image: it is drawn from thousands of
small strokes. That is why neither "Hide permanently" nor deleting an
image will remove it.

In the Edit tab, right at the bottom, press "Choose an area to erase" and
drag a rectangle over it in the preview. Everything inside — text, images
and drawings alike — leaves the file; it is not merely covered up.

Whatever only touches the edge of the rectangle stays whole, so page
borders and table rules do not break. Take the area 2-3 mm wider than the
code.


ZOOM AND MOVING AROUND
----------------------
Under the page: the  -  and  +  buttons, the current percentage, and
"Fit" which brings the page back to the window size.

  Ctrl + wheel     zoom in and out
  wheel            scroll up and down
  Shift + wheel    scroll left and right
  drag with mouse  move the page when it is zoomed in


LANGUAGE
--------
The list at the top right. The interface changes at once, without
closing your document, and your choice is remembered.


OCR — FOR SCANNED DOCUMENTS
---------------------------
If the PDF is a scan (a photo of paper), the text cannot be selected.
OCR reads the letters out of the image.

The OCR buttons stay grey until you install Tesseract, which is free:

  1. Download the Windows installer from
     https://github.com/UB-Mannheim/tesseract/wiki
  2. Run it. At the language step ("Additional language data") tick
     the languages you need.
  3. Keep the default folder.
  4. Close and reopen PDF Tool. The buttons enable themselves.

Everything else works fine without Tesseract.


KEYBOARD
--------
  Ctrl+O   open            Ctrl+Z   undo
  Ctrl+S   save            Ctrl+Y   redo
  Ctrl+Shift+S  save as    Ctrl+A   select every page
  Delete   remove the selected pages
  Page Up / Page Down      previous / next page
  Escape   leave edit mode or image placing

  Shift+click on a thumbnail selects the whole range.


SAFETY
------
When you save over the original file, a backup is kept next to it with
.bak added to the name. If something goes wrong, remove ".bak" from
the name and you have the original back.

"Hide permanently" really does remove the text from the file. After
saving there is no way back.
