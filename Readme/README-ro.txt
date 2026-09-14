PDF Tool — ghid scurt
==========================================================

Un editor PDF care rulează pe calculatorul tău. Fără internet, fără
cont. Niciun fișier nu pleacă de pe această mașină.


CUM DESCHIZI UN FIȘIER — trei feluri
------------------------------------
  * butonul „Deschide PDF”, stânga sus
  * tragi un PDF direct în fereastră
  * tragi un PDF peste iconița „PDF Tool.exe”


CELE PATRU TABURI, ÎN DREAPTA
-----------------------------
  Pagini    unire, împărțire, rotire, ștergere, reordonare. Alegi
            paginile dând click pe miniaturile din stânga, sau scrii
            un interval, de pildă  1-3, 7, 10-

  Adaugă    filigran, numerotare, și o imagine, semnătură sau
            ștampilă pe care o pui cu un click

  Editare   schimbi textul din PDF, cauți și înlocuiești, sau ascunzi
            definitiv un text

  Extrage   text, tabele în .csv, imagini, pagini ca PNG, OCR și
            comprimare


EDITAREA TEXTULUI — CITEȘTE ASTA
--------------------------------
Un PDF nu păstrează text editabil așa cum o face Word. Textul e
desenat la poziții fixe pe pagină.

Ce face aplicația: acoperă textul vechi cu culoarea fundalului (pe
care o detectează singură) și scrie textul nou peste, cu un font
asemănător și aceeași mărime.

  Merge bine pentru   date, nume, sume, cuvinte scurte
  Nu e pentru         rescris paragrafe întregi — rândurile din jur
                      nu se rearanjează

Apeși „Pornește modul editare” și toate zonele de text din pagină se
colorează în albastru, ca să vezi exact pe ce poți da click. Dai click
pe una, o schimbi în caseta din dreapta, apeși „Aplică modificarea”.
Ctrl+Z anulează orice.

Textul nou se așază exact pe linia pe care stătea cel vechi. Dacă vrei
să-l muți, îl apuci cu mouse-ul și îl tragi: apar două linii care arată
unde ajunge, iar când se apropie de rândul unui text vecin se prinde
singur pe el. Săgețile de pe tastatură îl mută cu pași mici, pentru
când nu vrei să te aliniezi la nimic.


ȘTERGEREA UNEI ZONE — COD QR, SIGLĂ, ȘTAMPILĂ
---------------------------------------------
Un cod QR nu e nici text, nici imagine: e desenat din mii de trăsături
mici. De aceea nu-l scoate nici „Ascunde definitiv”, nici ștergerea unei
imagini.

În fila Editare, jos de tot, apeși „Alege o zonă de șters” și tragi un
dreptunghi peste el în previzualizare. Tot ce e înăuntru — text, imagini
și desene — iese din fișier, nu e doar acoperit.

Ce doar atinge marginea dreptunghiului rămâne întreg, așa că chenarul
paginii și liniile de tabel nu se rup. Ia zona cu 2-3 mm mai largă decât
codul.
COPIAZĂ O ZONĂ DINTR-UN PDF ÎN ALTUL
------------------------------------
Ai un antet de firmă, o semnătură sau un tabel într-un PDF și îl vrei
în altul. Nu-l fotografia: copiază-l.

În fila Adaugă, jos, apeși „Copiază o zonă” și tragi un dreptunghi peste
ce te interesează. Apoi deschizi PDF-ul în care vrei să-l pui, apeși
„Lipește prin click pe pagină” și dai click unde trebuie.

Zona pleacă cu textul ei cu tot: rămâne text, se poate căuta și se poate
selecta după lipire. Fișierul crește cu câteva kilooctete, nu cu sute.

Dacă vrei totuși o poză — de pildă ca nimeni să nu poată copia textul de
acolo — bifezi „Lipește ca poză”. Atunci mărimea se ia din reglajul de
calitate din fila Extrage.

Se copiază numai ce e în dreptunghi. Restul paginii sursă nu pleacă.




ZOOM ȘI DEPLASARE
-----------------
Sub pagină: butoanele  -  și  +  , procentajul curent, și „Încadrează”
care aduce pagina înapoi la mărimea ferestrei.

  Ctrl + rotița     zoom in și zoom out
  rotița            derulezi în sus și în jos
  Shift + rotița    derulezi în stânga și în dreapta
  tragi cu mouse-ul deplasezi pagina, când e mărită


LIMBA
-----
Lista din dreapta sus. Interfața se schimbă pe loc, fără să închizi
documentul, iar alegerea se ține minte.


OCR — PENTRU DOCUMENTE SCANATE
------------------------------
Dacă PDF-ul e o scanare (o poză a hârtiei), textul nu se poate selecta.
OCR-ul citește literele din imagine.

Butoanele de OCR rămân gri până instalezi Tesseract, care e gratuit:

  1. Descarcă instalerul pentru Windows de la
     https://github.com/UB-Mannheim/tesseract/wiki
  2. Rulează-l. La pasul cu limbile („Additional language data”)
     bifează limbile de care ai nevoie.
  3. Lasă folderul implicit.
  4. Închide și redeschide PDF Tool. Butoanele se activează singure.

Restul aplicației merge perfect și fără Tesseract.


TASTATURĂ
---------
  Ctrl+O   deschide        Ctrl+Z   anulează
  Ctrl+S   salvează        Ctrl+Y   refă
  Ctrl+Shift+S  salvează ca    Ctrl+A   selectează toate paginile
  Delete   șterge paginile selectate
  Page Up / Page Down      pagina anterioară / următoare
  Escape   ieși din modul editare sau plasare imagine

  Shift+click pe o miniatură selectează tot intervalul.


SIGURANȚĂ
---------
Când salvezi peste fișierul original, se păstrează o copie alături, cu
.bak adăugat la nume. Dacă ceva merge prost, ștergi „.bak” din nume și
ai înapoi fișierul inițial.

„Ascunde definitiv” chiar scoate textul din fișier. După salvare nu
mai există cale de întoarcere.
