PDF Tool — Kurzanleitung
==========================================================

Ein PDF-Editor, der auf Ihrem eigenen Rechner läuft. Ohne Internet,
ohne Konto. Keine Datei verlässt diesen Rechner.


EINE DATEI ÖFFNEN — drei Wege
-----------------------------
  * die Schaltfläche „PDF öffnen“ oben links
  * eine PDF direkt ins Fenster ziehen
  * eine PDF auf das Symbol „PDF Tool.exe“ ziehen


DIE VIER REGISTER, RECHTS
-------------------------
  Seiten       zusammenführen, aufteilen, drehen, löschen, umordnen.
               Seiten wählen Sie per Klick auf die Miniaturen links,
               oder Sie tippen einen Bereich:  1-3, 7, 10-

  Hinzufügen   Wasserzeichen, Seitenzahlen, sowie ein Bild, eine
               Unterschrift oder einen Stempel, den Sie per Klick
               setzen

  Bearbeiten   den Text in der PDF ändern, suchen und ersetzen,
               sowie dauerhaftes Schwärzen

  Auslesen     Text, Tabellen als .csv, Bilder, Seiten als PNG, OCR
               und Verkleinern


TEXT BEARBEITEN — BITTE LESEN
-----------------------------
Eine PDF speichert keinen bearbeitbaren Text wie Word. Der Text ist an
festen Stellen auf die Seite gemalt.

Was das Programm tut: Es überdeckt den alten Text mit der Hintergrund-
farbe (die es selbst erkennt) und schreibt den neuen Text darüber, in
einer ähnlichen Schrift und derselben Größe.

  Gut geeignet für   Datum, Namen, Beträge, kurze Wörter
  Nicht gedacht für  ganze Absätze neu schreiben — die umgebenden
                     Zeilen werden nicht neu umbrochen

Klicken Sie auf „Bearbeitungsmodus starten“: Alle Textbereiche der
Seite werden blau, so sehen Sie genau, was anklickbar ist. Klicken Sie
einen an, ändern Sie ihn im Feld rechts und drücken Sie „Änderung
übernehmen“. Ctrl+Z macht alles rückgängig.

Der neue Text sitzt genau auf der Linie, auf der der alte stand. Zum
Verschieben fassen Sie ihn mit der Maus und ziehen: zwei Linien zeigen,
wo er landen wird, und sobald er der Linie eines Nachbartextes nahe
kommt, rastet er darauf ein. Die Pfeiltasten verschieben ihn in kleinen
Schritten, wenn Sie sich an nichts ausrichten wollen.


EINEN BEREICH LÖSCHEN — QR-CODE, LOGO, STEMPEL
----------------------------------------------
Ein QR-Code ist weder Text noch Bild: er ist aus Tausenden kleiner
Striche gezeichnet. Darum entfernt ihn weder „Endgültig verbergen“ noch
das Löschen eines Bildes.

Im Register Bearbeiten, ganz unten, drücken Sie „Bereich zum Löschen
wählen“ und ziehen im Vorschaufenster ein Rechteck darüber. Alles darin —
Text, Bilder und Zeichnungen — verlässt die Datei; es wird nicht nur
überdeckt.

Was den Rand des Rechtecks nur berührt, bleibt unversehrt, damit
Seitenrahmen und Tabellenlinien nicht zerbrechen. Nehmen Sie den Bereich
2-3 mm breiter als den Code.


ZOOM UND BEWEGEN
----------------
Unter der Seite: die Schaltflächen  -  und  +  , der aktuelle
Prozentwert und „Einpassen“, das die Seite auf Fenstergröße bringt.

  Strg + Mausrad     vergrößern und verkleinern
  Mausrad            nach oben und unten blättern
  Umschalt + Mausrad nach links und rechts
  mit der Maus ziehen verschiebt die vergrößerte Seite


SPRACHE
-------
Die Liste oben rechts. Die Oberfläche wechselt sofort, ohne Ihr
Dokument zu schließen, und Ihre Wahl wird gemerkt.


OCR — FÜR GESCANNTE DOKUMENTE
-----------------------------
Wenn die PDF ein Scan ist (ein Foto von Papier), lässt sich der Text
nicht markieren. OCR liest die Buchstaben aus dem Bild.

Die OCR-Schaltflächen bleiben grau, bis Sie Tesseract installieren,
es ist kostenlos:

  1. Laden Sie das Windows-Installationsprogramm herunter von
     https://github.com/UB-Mannheim/tesseract/wiki
  2. Starten Sie es. Beim Schritt mit den Sprachen („Additional
     language data“) kreuzen Sie die benötigten Sprachen an.
  3. Behalten Sie den Standardordner.
  4. PDF Tool schließen und neu öffnen. Die Schaltflächen werden von
     selbst aktiv.

Alles andere funktioniert auch ohne Tesseract einwandfrei.


TASTATUR
--------
  Strg+O   öffnen          Strg+Z   rückgängig
  Strg+S   speichern       Strg+Y   wiederholen
  Strg+Umschalt+S  speichern unter   Strg+A  alle Seiten wählen
  Entf     gewählte Seiten löschen
  Bild auf / Bild ab       vorige / nächste Seite
  Esc      Bearbeitungsmodus oder Bildplatzierung verlassen

  Umschalt+Klick auf eine Miniatur wählt den ganzen Bereich.


SICHERHEIT
----------
Wenn Sie über die Originaldatei speichern, bleibt daneben eine
Sicherungskopie mit .bak im Namen. Geht etwas schief, entfernen Sie
„.bak“ aus dem Namen und haben die Ursprungsdatei zurück.

„Dauerhaft verbergen“ entfernt den Text wirklich aus der Datei. Nach
dem Speichern gibt es kein Zurück.
