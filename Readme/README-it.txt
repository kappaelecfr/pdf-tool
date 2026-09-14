PDF Tool — guida rapida
==========================================================

Un editor PDF che gira sul tuo computer. Senza internet, senza
account. Nessun file lascia questa macchina.


APRIRE UN FILE — tre modi
-------------------------
  * il pulsante «Apri PDF», in alto a sinistra
  * trascina un PDF direttamente nella finestra
  * trascina un PDF sull'icona «PDF Tool.exe»


LE QUATTRO SCHEDE, A DESTRA
---------------------------
  Pagine    unire, dividere, ruotare, eliminare, riordinare. Scegli
            le pagine cliccando le miniature a sinistra, oppure
            scrivi un intervallo:  1-3, 7, 10-

  Aggiungi  filigrana, numerazione, e un'immagine, firma o timbro
            che posizioni con un clic

  Modifica  cambiare il testo del PDF, trova e sostituisci, e
            l'oscuramento definitivo

  Estrai    testo, tabelle in .csv, immagini, pagine in PNG, OCR e
            compressione


MODIFICARE IL TESTO — DA LEGGERE
--------------------------------
Un PDF non conserva testo modificabile come Word. Il testo è disegnato
in posizioni fisse sulla pagina.

Cosa fa l'applicazione: copre il testo vecchio con il colore dello
sfondo (che rileva da sola) e riscrive sopra il testo nuovo, con un
carattere simile e lo stesso corpo.

  Va bene per    date, nomi, importi, parole brevi
  Non serve a    riscrivere interi paragrafi — le righe intorno non
                 vengono rimpaginate

Premi «Attiva la modalità modifica» e tutte le aree di testo della
pagina diventano blu, così vedi esattamente cosa è cliccabile. Cliccane
una, cambiala nella casella a destra, premi «Applica la modifica».
Ctrl+Z annulla qualsiasi cosa.

Il testo nuovo si posa esattamente sulla riga dove stava il vecchio. Se un
carattere sostitutivo lo lascia comunque di un soffio fuori posto, puoi
allinearlo: le frecce sotto il riquadro lo spostano di un quarto di punto,
oppure lo afferri con il mouse e lo trascini dove serve.


CANCELLARE UN'AREA — CODICE QR, LOGO, TIMBRO
--------------------------------------------
Un codice QR non è né testo né immagine: è tracciato con migliaia di
piccoli segni. Per questo non lo tolgono né «Nascondi definitivamente» né
la cancellazione di un'immagine.

Nella scheda Modifica, in fondo, premi «Scegli un'area da cancellare» e
traccia un rettangolo sopra di esso nell'anteprima. Tutto ciò che sta
dentro — testo, immagini e disegni — esce dal file; non viene soltanto
coperto.

Ciò che sfiora soltanto il bordo del rettangolo resta intatto, così le
cornici della pagina e le righe delle tabelle non si spezzano. Prendi
l'area 2-3 mm più larga del codice.


ZOOM E SPOSTAMENTO
------------------
Sotto la pagina: i pulsanti  -  e  +  , la percentuale attuale e
«Adatta», che riporta la pagina alla dimensione della finestra.

  Ctrl + rotella     ingrandisci e riduci
  rotella            scorri su e giù
  Maiusc + rotella   scorri a sinistra e a destra
  trascina col mouse sposta la pagina quando è ingrandita


LINGUA
------
L'elenco in alto a destra. L'interfaccia cambia subito, senza chiudere
il documento, e la scelta viene ricordata.


OCR — PER DOCUMENTI SCANSIONATI
-------------------------------
Se il PDF è una scansione (una foto della carta), il testo non si può
selezionare. L'OCR legge le lettere dall'immagine.

I pulsanti OCR restano grigi finché non installi Tesseract, gratuito:

  1. Scarica l'installatore per Windows da
     https://github.com/UB-Mannheim/tesseract/wiki
  2. Avvialo. Al passaggio delle lingue («Additional language data»)
     spunta le lingue che ti servono.
  3. Lascia la cartella predefinita.
  4. Chiudi e riapri PDF Tool. I pulsanti si attivano da soli.

Tutto il resto funziona benissimo anche senza Tesseract.


TASTIERA
--------
  Ctrl+O   apri            Ctrl+Z   annulla
  Ctrl+S   salva           Ctrl+Y   ripeti
  Ctrl+Maiusc+S  salva con nome   Ctrl+A  seleziona tutte le pagine
  Canc     elimina le pagine selezionate
  Pag su / Pag giù         pagina precedente / successiva
  Esc      esci dalla modalità modifica o dal posizionamento

  Maiusc+clic su una miniatura seleziona tutto l'intervallo.


SICUREZZA
---------
Quando salvi sopra il file originale, accanto resta una copia di
sicurezza con .bak aggiunto al nome. Se qualcosa va storto, togli
«.bak» dal nome e hai indietro il file iniziale.

«Nascondi definitivamente» toglie davvero il testo dal file. Dopo il
salvataggio non si torna indietro.
