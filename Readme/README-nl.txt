PDF Tool — korte handleiding
==========================================================

Een PDF-bewerker die op je eigen computer draait. Geen internet, geen
account. Geen enkel bestand verlaat deze machine.


EEN BESTAND OPENEN — drie manieren
----------------------------------
  * de knop „PDF openen”, linksboven
  * sleep een PDF rechtstreeks in het venster
  * sleep een PDF op het pictogram „PDF Tool.exe”


DE VIER TABBLADEN, RECHTS
-------------------------
  Pagina's    samenvoegen, splitsen, draaien, verwijderen, ordenen.
              Kies pagina's door links op de miniaturen te klikken,
              of typ een bereik:  1-3, 7, 10-

  Toevoegen   watermerk, paginanummers, en een afbeelding,
              handtekening of stempel die je met een klik plaatst

  Bewerken    de tekst in de PDF wijzigen, zoeken en vervangen, en
              definitief redigeren

  Uitpakken   tekst, tabellen als .csv, afbeeldingen, pagina's als
              PNG, OCR en verkleinen


TEKST BEWERKEN — LEES DIT
-------------------------
Een PDF bewaart geen bewerkbare tekst zoals Word. De tekst is op vaste
plekken op de pagina getekend.

Wat de app doet: hij dekt de oude tekst af met de achtergrondkleur (die
hij zelf herkent) en schrijft de nieuwe tekst eroverheen, in een
gelijkend lettertype en dezelfde grootte.

  Werkt goed voor   datums, namen, bedragen, korte woorden
  Niet bedoeld om   hele alinea's te herschrijven — de omliggende
                    regels worden niet opnieuw ingedeeld

Klik op „Bewerkmodus starten”: alle tekstzones op de pagina worden
blauw, zodat je precies ziet waarop je kunt klikken. Klik er een aan,
wijzig hem in het vak rechts en druk op „Wijziging toepassen”.
Ctrl+Z maakt alles ongedaan.

De nieuwe tekst komt precies op de regel waar de oude stond. Om hem te
verplaatsen pakt u hem met de muis en sleept: twee lijnen tonen waar
hij terechtkomt, en zodra hij bij de regel van een naburige tekst komt,
klikt hij eraan vast. De pijltjestoetsen verplaatsen hem met kleine
stapjes, voor als u zich nergens op wilt uitlijnen.


EEN ZONE WISSEN — QR-CODE, LOGO, STEMPEL
----------------------------------------
Een QR-code is tekst noch afbeelding: hij is uit duizenden kleine streken
getekend. Daarom halen noch „Definitief verbergen” noch het wissen van een
afbeelding hem weg.

In het tabblad Bewerken, helemaal onderaan, drukt u op „Kies een zone om
te wissen” en sleept u er in het voorbeeld een rechthoek overheen. Alles
wat erbinnen zit — tekst, afbeeldingen en tekeningen — verlaat het
bestand; het wordt niet alleen afgedekt.

Wat de rand van de rechthoek alleen raakt, blijft heel, zodat paginakaders
en tabellijnen niet breken. Neem de zone 2-3 mm ruimer dan de code.
EEN ZONE VAN DE ENE PDF NAAR DE ANDERE KOPIËREN
-----------------------------------------------
U hebt een bedrijfshoofd, een handtekening of een tabel in een pdf en u
wilt ze in een andere. Fotografeer ze niet: kopieer ze.

In het tabblad Toevoegen, onderaan, drukt u op „Een zone kopiëren” en
sleept u een rechthoek over wat u wilt. Open dan de pdf waarin ze moet
komen, druk op „Plakken door op de pagina te klikken” en klik op de
juiste plek.

De zone gaat mee met haar tekst: het blijft tekst, doorzoekbaar en
selecteerbaar na het plakken. Het bestand groeit met enkele kilobytes,
niet met honderden.

Wilt u toch een afbeelding — zodat niemand de tekst eruit kan kopiëren,
bijvoorbeeld — vink dan „Als afbeelding plakken” aan. De grootte komt dan
uit de kwaliteitsinstelling van het tabblad Uitnemen.

Alleen wat binnen de rechthoek ligt, wordt gekopieerd. De rest van de
bronpagina blijft achter.




ZOOMEN EN VERSCHUIVEN
---------------------
Onder de pagina: de knoppen  -  en  +  , het huidige percentage, en
„Passend”, dat de pagina terugbrengt naar venstergrootte.

  Ctrl + wiel      in- en uitzoomen
  wiel             omhoog en omlaag scrollen
  Shift + wiel     naar links en rechts scrollen
  slepen met muis  verschuift de pagina als die is ingezoomd


TAAL
----
De lijst rechtsboven. De interface wisselt meteen, zonder je document
te sluiten, en je keuze wordt onthouden.


OCR — VOOR GESCANDE DOCUMENTEN
------------------------------
Als de PDF een scan is (een foto van papier), kan de tekst niet worden
geselecteerd. OCR leest de letters uit het beeld.

De OCR-knoppen blijven grijs tot je Tesseract installeert, dat gratis
is:

  1. Download het Windows-installatieprogramma van
     https://github.com/UB-Mannheim/tesseract/wiki
  2. Start het. Vink bij de stap met de talen („Additional language
     data”) de talen aan die je nodig hebt.
  3. Laat de standaardmap staan.
  4. Sluit PDF Tool en open het opnieuw. De knoppen worden vanzelf
     actief.

Al het andere werkt prima zonder Tesseract.


TOETSENBORD
-----------
  Ctrl+O   openen          Ctrl+Z   ongedaan maken
  Ctrl+S   opslaan         Ctrl+Y   opnieuw
  Ctrl+Shift+S  opslaan als    Ctrl+A  alle pagina's selecteren
  Delete   de geselecteerde pagina's verwijderen
  Page Up / Page Down      vorige / volgende pagina
  Escape   bewerkmodus of afbeelding plaatsen verlaten

  Shift+klik op een miniatuur selecteert het hele bereik.


VEILIGHEID
----------
Als je over het oorspronkelijke bestand opslaat, blijft er ernaast een
reservekopie staan met .bak in de naam. Gaat er iets mis, haal „.bak”
weg uit de naam en je hebt het oorspronkelijke bestand terug.

„Definitief verbergen” haalt de tekst echt uit het bestand. Na het
opslaan is er geen weg terug.
