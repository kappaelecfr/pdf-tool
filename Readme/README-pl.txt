PDF Tool — krótki przewodnik
==========================================================

Edytor PDF, który działa na twoim komputerze. Bez internetu, bez
konta. Żaden plik nie opuszcza tej maszyny.


OTWIERANIE PLIKU — trzy sposoby
-------------------------------
  * przycisk „Otwórz PDF” w lewym górnym rogu
  * przeciągnij PDF wprost do okna
  * przeciągnij PDF na ikonę „PDF Tool.exe”


CZTERY ZAKŁADKI, PO PRAWEJ
--------------------------
  Strony     scalanie, dzielenie, obracanie, usuwanie, zmiana
             kolejności. Strony wybierasz klikając miniatury po
             lewej, albo wpisujesz zakres:  1-3, 7, 10-

  Dodaj      znak wodny, numerowanie, oraz obraz, podpis lub
             pieczątkę, którą stawiasz kliknięciem

  Edycja     zmiana tekstu w PDF, znajdź i zamień, oraz trwałe
             zaczernienie

  Wyciągnij  tekst, tabele w .csv, obrazy, strony jako PNG, OCR i
             kompresja


EDYCJA TEKSTU — PRZECZYTAJ TO
-----------------------------
PDF nie przechowuje edytowalnego tekstu tak jak Word. Tekst jest
narysowany w stałych miejscach na stronie.

Co robi program: zakrywa stary tekst kolorem tła (który sam wykrywa) i
pisze nowy tekst na wierzchu, podobnym krojem i w tym samym stopniu.

  Dobre do      daty, nazwiska, kwoty, krótkie słowa
  Nie nadaje    przepisywania całych akapitów — sąsiednie wiersze
  się do        nie są łamane na nowo

Naciśnij „Włącz tryb edycji”: wszystkie obszary tekstu na stronie
zmienią kolor na niebieski, więc widzisz dokładnie, w co można kliknąć.
Kliknij jeden, zmień go w polu po prawej i naciśnij „Zastosuj zmianę”.
Ctrl+Z cofa wszystko.

Nowy tekst siada dokładnie na linii, na której stał stary. Żeby go
przesunąć, chwyć go myszą i przeciągnij: dwie linie pokazują, gdzie
wyląduje, a gdy zbliży się do linii sąsiedniego tekstu, przyczepia się
do niej. Strzałki na klawiaturze przesuwają go drobnymi krokami, gdy
nie chcesz się do niczego wyrównywać.


USUWANIE OBSZARU — KOD QR, LOGO, PIECZĄTKA
------------------------------------------
Kod QR nie jest ani tekstem, ani obrazem: rysują go tysiące drobnych
kresek. Dlatego nie usuwa go ani „Ukryj trwale”, ani skasowanie obrazu.

W zakładce Edycja, na samym dole, naciśnij „Wybierz obszar do usunięcia”
i przeciągnij nad nim prostokąt w podglądzie. Wszystko, co jest w środku —
tekst, obrazy i rysunki — znika z pliku; nie zostaje tylko zasłonięte.

To, co jedynie dotyka krawędzi prostokąta, pozostaje nienaruszone, więc
ramki strony i linie tabel się nie rwą. Weź obszar 2-3 mm szerszy niż
kod.


POWIĘKSZANIE I PRZESUWANIE
--------------------------
Pod stroną: przyciski  -  i  +  , bieżący procent, oraz „Dopasuj”,
które wraca do rozmiaru okna.

  Ctrl + kółko      powiększanie i pomniejszanie
  kółko             przewijanie w górę i w dół
  Shift + kółko     przewijanie w lewo i w prawo
  przeciąganie      przesuwa stronę, gdy jest powiększona


JĘZYK
-----
Lista w prawym górnym rogu. Interfejs zmienia się od razu, bez
zamykania dokumentu, a wybór jest zapamiętywany.


OCR — DO DOKUMENTÓW SKANOWANYCH
-------------------------------
Jeśli PDF to skan (zdjęcie papieru), tekstu nie da się zaznaczyć.
OCR odczytuje litery z obrazu.

Przyciski OCR pozostają szare, dopóki nie zainstalujesz Tesseract,
który jest darmowy:

  1. Pobierz instalator dla Windows ze strony
     https://github.com/UB-Mannheim/tesseract/wiki
  2. Uruchom go. W kroku z językami („Additional language data”)
     zaznacz potrzebne języki.
  3. Zostaw domyślny folder.
  4. Zamknij i otwórz PDF Tool ponownie. Przyciski włączą się same.

Cała reszta działa świetnie także bez Tesseract.


KLAWIATURA
----------
  Ctrl+O   otwórz          Ctrl+Z   cofnij
  Ctrl+S   zapisz          Ctrl+Y   ponów
  Ctrl+Shift+S  zapisz jako    Ctrl+A  zaznacz wszystkie strony
  Delete   usuń zaznaczone strony
  Page Up / Page Down      poprzednia / następna strona
  Escape   wyjdź z trybu edycji lub umieszczania obrazu

  Shift+kliknięcie miniatury zaznacza cały zakres.


BEZPIECZEŃSTWO
--------------
Gdy zapisujesz na oryginalnym pliku, obok zostaje kopia zapasowa z
.bak dodanym do nazwy. Jeśli coś pójdzie źle, usuń „.bak” z nazwy i
masz z powrotem pierwotny plik.

„Ukryj trwale” naprawdę usuwa tekst z pliku. Po zapisaniu nie ma już
odwrotu.
