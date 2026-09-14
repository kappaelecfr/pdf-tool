PDF Tool — guide rapide
==========================================================

Un éditeur PDF qui tourne sur votre propre ordinateur. Sans internet,
sans compte. Aucun fichier ne quitte cette machine.


OUVRIR UN FICHIER — trois façons
--------------------------------
  * le bouton « Ouvrir un PDF », en haut à gauche
  * faites glisser un PDF directement dans la fenêtre
  * faites glisser un PDF sur l'icône « PDF Tool.exe »


LES QUATRE ONGLETS, À DROITE
----------------------------
  Pages     fusionner, découper, tourner, supprimer, réordonner.
            Choisissez les pages en cliquant sur les miniatures à
            gauche, ou saisissez une plage :  1-3, 7, 10-

  Ajouter   filigrane, numérotation, et une image, signature ou
            tampon que vous posez d'un clic

  Éditer    modifier le texte du PDF, rechercher et remplacer, et
            le caviardage définitif

  Extraire  texte, tableaux en .csv, images, pages en PNG, OCR et
            compression


MODIFIER LE TEXTE — À LIRE
--------------------------
Un PDF ne conserve pas de texte modifiable comme Word. Le texte est
dessiné à des positions fixes sur la page.

Ce que fait l'application : elle recouvre l'ancien texte avec la
couleur du fond (qu'elle détecte seule) et réécrit le nouveau texte
par-dessus, dans une police proche et à la même taille.

  Convient pour     dates, noms, montants, mots courts
  Pas pour          réécrire des paragraphes entiers — les lignes
                    autour ne sont pas réagencées

Cliquez sur « Activer le mode édition » : toutes les zones de texte de
la page deviennent bleues, vous voyez donc exactement ce qui est
cliquable. Cliquez sur l'une, modifiez-la dans la case à droite, puis
« Appliquer la modification ». Ctrl+Z annule tout.

Le texte nouveau se pose exactement sur la ligne qu'occupait l'ancien.
Pour le déplacer, saisissez-le à la souris et faites-le glisser : deux
lignes montrent où il va tomber, et dès qu'il approche de la ligne d'un
texte voisin il s'y accroche. Les flèches du clavier le déplacent par
petits pas, quand vous ne voulez vous aligner sur rien.


EFFACER UNE ZONE — CODE QR, LOGO, TAMPON
----------------------------------------
Un code QR n'est ni du texte ni une image : il est tracé à partir de
milliers de petits traits. C'est pourquoi ni «Masquer définitivement» ni
la suppression d'une image ne l'enlèvent.

Dans l'onglet Édition, tout en bas, appuyez sur «Choisir une zone à
effacer» et tracez un rectangle par-dessus dans l'aperçu. Tout ce qui se
trouve dedans — texte, images et dessins — quitte le fichier ; ce n'est
pas simplement recouvert.

Ce qui ne fait qu'effleurer le bord du rectangle reste intact : les cadres
de la page et les filets des tableaux ne se cassent pas. Prenez la zone
2 à 3 mm plus large que le code.
COPIER UNE ZONE D'UN PDF VERS UN AUTRE
--------------------------------------
Vous avez un en-tête d'entreprise, une signature ou un tableau dans un
PDF et vous le voulez dans un autre. Ne le photographiez pas : copiez-le.

Dans l'onglet Ajouter, en bas, appuyez sur «Copier une zone» et tracez un
rectangle sur ce qui vous intéresse. Ouvrez ensuite le PDF où le mettre,
appuyez sur «Coller en cliquant sur la page» et cliquez à l'endroit voulu.

La zone part avec son texte : il reste du texte, cherchable et
sélectionnable après le collage. Le fichier grossit de quelques
kilo-octets, pas de centaines.

Si vous voulez tout de même une image — pour que personne ne puisse en
recopier le texte, par exemple — cochez «Coller comme image». La taille
vient alors du réglage de qualité de l'onglet Extraire.

Seul ce qui est dans le rectangle est copié. Le reste de la page
d'origine ne part pas.




ZOOM ET DÉPLACEMENT
-------------------
Sous la page : les boutons  -  et  +  , le pourcentage actuel, et
« Ajuster » qui ramène la page à la taille de la fenêtre.

  Ctrl + molette      zoom avant et arrière
  molette             défilement vertical
  Maj + molette       défilement horizontal
  glisser à la souris déplace la page quand elle est agrandie


LANGUE
------
La liste en haut à droite. L'interface change aussitôt, sans fermer
votre document, et votre choix est retenu.


OCR — POUR LES DOCUMENTS NUMÉRISÉS
----------------------------------
Si le PDF est un scan (une photo de papier), le texte ne peut pas être
sélectionné. L'OCR lit les lettres dans l'image.

Les boutons OCR restent gris tant que Tesseract n'est pas installé.
Il est gratuit :

  1. Téléchargez l'installeur Windows sur
     https://github.com/UB-Mannheim/tesseract/wiki
  2. Lancez-le. À l'étape des langues (« Additional language data »),
     cochez les langues dont vous avez besoin.
  3. Gardez le dossier par défaut.
  4. Fermez et rouvrez PDF Tool. Les boutons s'activent tout seuls.

Tout le reste fonctionne très bien sans Tesseract.


CLAVIER
-------
  Ctrl+O   ouvrir          Ctrl+Z   annuler
  Ctrl+S   enregistrer     Ctrl+Y   rétablir
  Ctrl+Maj+S  enregistrer sous   Ctrl+A  sélectionner toutes les pages
  Suppr    supprimer les pages sélectionnées
  Page préc. / Page suiv.  page précédente / suivante
  Échap    quitter le mode édition ou le placement d'image

  Maj+clic sur une miniature sélectionne toute la plage.


SÉCURITÉ
--------
Quand vous enregistrez par-dessus le fichier d'origine, une copie de
sauvegarde est gardée à côté, avec .bak ajouté au nom. Si quelque
chose tourne mal, retirez « .bak » du nom et vous récupérez l'original.

« Masquer définitivement » retire réellement le texte du fichier.
Après l'enregistrement, il n'y a pas de retour en arrière.
