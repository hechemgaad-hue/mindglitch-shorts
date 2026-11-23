# Qualité vidéo MindGlitch : critères, backlog et journal

Objectif du propriétaire : s'améliorer en continu, vidéo après vidéo, pour atteindre la meilleure qualité possible.
Contraintes techniques : pas d'accès aux banques d'images ou de vidéos (réseau limité), pas de GPU ; tout est généré par make_short.py (PIL, numpy, ffmpeg, voix Kokoro locale, musique et sons synthétisés).

## Grille de contrôle (note chaque critère de 1 à 5 sur chaque vidéo regardée image par image)
1. Lisibilité : sous-titres entiers, centrés, contrastés, aucun mot coupé ni astérisque
2. Illustration : chaque phrase a une scène précise et pertinente, variée d'une phrase à l'autre
3. Rythme : un changement visuel ou sonore au moins toutes les 2 à 3 s, accroche dans la 1re seconde
4. Son : voix claire, musique discrète, effets cohérents, volume global homogène
5. Cohérence avec le fond : l'image illustre vraiment le fait, pas un emoji décoratif
6. Différence avec les vidéos précédentes (format, palette, voix, visuels)
7. Exactitude des faits et des chiffres affichés

## Procédure d'amélioration (un seul changement par jour)
1. Relire les 3 dernières vidéos (extraire des images avec ffmpeg et les regarder), noter la grille, croiser avec notes/performance.json.
2. Choisir l'élément le plus faible OU l'idée du backlog avec le meilleur rapport impact/effort.
3. Développer dans make_short_next.py (copie de make_short.py), jamais directement dans make_short.py.
4. Tester : rendre une vidéo de test non publiée (scripts existants), contrôler ffprobe (1080x1920, audio, 15-59 s) et regarder au moins 6 images réparties.
5. Promouvoir seulement si la vidéo est meilleure ET sans régression : copier make_short.py vers make_short_stable.py (sauvegarde), puis make_short_next.py vers make_short.py. Sinon, noter l'échec dans le journal et ne rien promouvoir.
6. Commit, push, noter dans le journal ci-dessous.
Ne jamais modifier ni supprimer une publication Metricool existante.

## Backlog d'idées (par priorité)
- [x] Normalisation du volume (cible environ -14 LUFS) et léger ducking de la musique sous la voix (fait 2026-11-18)
- [x] Emojis qui apparaissent minuscules au début d'une scène : pop démarrant à 60 % de taille (fait 2026-11-21)
- [ ] Fond animé qui occupe le bas (vagues/particules plus denses) pour renforcer le rythme visuel
- [ ] Transitions variées entre scènes (glissement, zoom traversant, glitch) au lieu d'un seul flash
- [ ] Nouveaux types de visuels : comparaison "vs" à deux colonnes, liste qui se coche, carte-citation, chronologie, jauge
- [x] Occuper le tiers inférieur vide : recentrer verticalement emoji + sous-titres (fait 2026-11-20 ; reste ~20 % vide en bas, volontaire pour la zone d'interface Shorts)
- [ ] Scènes composées (plusieurs emojis dessinant une situation) au lieu de paires génériques
- [ ] Particules d'emojis (pluie, explosion) au moment de la révélation
- [x] Sous-titres : éviter les coupes de phrase en fragments orphelins en regroupant par unités de sens (fait 2026-11-22)
- [ ] Scènes à pair d'emojis générique (ex. 🔁❓ pour "switch", 🏫🌍 pour "schools") : dictionnaire de scènes plus précises
- [ ] Rythme de voix plus naturel : pauses plus longues avant la révélation, vitesse légèrement variable
- [ ] Musique différente selon la palette (tonalité, tempo, instrumentation)
- [ ] Mise en avant visuelle de la révélation (zoom plus fort, mot en grand plein écran)
- [ ] Scènes à un seul emoji (ex. "2006.") : ajouter une carte date/année plein écran ou un second visuel pertinent
- [ ] Styles de sous-titres différents selon le format (quiz, top 3, mythe)
- [ ] Bas d'écran (~30 % vide) : visuel secondaire animé (barre de progression de fait, mot-clé géant) sans empiéter sur la zone d'interface Shorts
- [x] Scènes à emojis statiques : micro-mouvement continu (respiration, dérive, rotation) pendant toute la phrase (fait 2026-11-23)
- [ ] Image de couverture (miniature) soignée si la chaîne l'autorise (videoThumbnailUrl dans Metricool, nécessite une chaîne vérifiée)
- [ ] Synchronisation mot à mot plus précise (alignement réel de la voix si un outil local est disponible)

- [ ] Playbook/scripts : liste de paires d'emojis précises par concept (winners, save, Africa...) à intégrer dans la consigne d'écriture des scripts

## Journal des améliorations
### 2026-11-18 - Normalisation du volume + ducking de la musique
- Constaté (8 vidéos du 17 et 18/11, 6 images chacune, volumedetect) : 1080x1920 + audio OK, 19 à 25 s. Volume moyen de -18,5 à -21 dB (écart 2,5 dB entre vidéos), trop bas pour des Shorts. Aucune statistique dans performance.json (0 vue renseignée), croisement impossible.
- Notes moyennes (estimées) : lisibilité 4,5 ; illustration 3 (paires d'emojis génériques, jauges/grilles bien) ; rythme 4 ; son 3 (bas et inégal) ; cohérence fond 3 ; différence 3,5 (mise en page identique, tiers inférieur de l'écran vide) ; faits non revérifiés ici.
- Changé : make_short.py -> ducking de la musique (-65 % sous la voix, enveloppe lissée) + loudnorm 2 passes (cible -14 LUFS, crête -1,5 dBTP) avant encodage. Repli sans normalisation si ffmpeg échoue.
- Test (scripts/2026-11-18_2 et _3, rendus dans /tmp) : 1080x1920, audio, 24,8 s / 22 s. Intégré -21,3 LUFS -> -15,0 LUFS (_2) et -14,3 LUFS (_3), crête -1,3 dBFS. Images identiques côté visuel/sous-titres, aucune régression. Promu (make_short_stable.py = ancienne version).
- Note son avant/après : 3 -> 4.

### 2026-11-19 - Grand nombre auto-ajusté (plus de coupure)
- Constaté (10 vidéos du 18 et 19/11, 6 images chacune, volumedetect) : tout en 1080x1920 + audio, 17 à 25 s. Volume moyen du 19/11 : -13,7 à -14,5 dB (homogène, normalisation OK) contre -18,5 à -21 dB le 18/11. performance.json : toujours aucune statistique, croisement impossible.
- Défaut grave : dans 2026-11-19_4 (type "number"), "15 min" à 330 px dépasse la largeur et s'affiche "L5 mir" (coupé des deux côtés). Autres défauts : tiers inférieur vide, paires d'emojis génériques (microscope + diagramme répétés), scène "2006." avec un seul emoji.
- Notes moyennes (estimées) : lisibilité 4 (3 sur la vidéo au nombre coupé) ; illustration 3 ; rythme 4 ; son 4 ; cohérence fond 3 ; différence 3,5.
- Changé : make_short.py -> taille de police du visuel "number" calculée pour que la valeur finale tienne dans la largeur (marge 90 px, plancher 120 px).
- Test (scripts/2026-11-19_4 rendu dans /tmp, ancien vs nouveau) : 1080x1920, audio, 21,8 s, volume identique (-14,5 dB) ; 8 images comparées : "15 min" entièrement visible, sous-titres et rythme inchangés. Promu (make_short_stable.py = version précédente).
- Note lisibilité avant/après sur ce cas : 3 -> 5.


### 2026-11-20 - Recentrage vertical (scène + sous-titres)
- Constaté (10 vidéos des 19 et 20/11, 6 images pour 6 d'entre elles, volumedetect) : toutes 1080x1920 + audio, 16,9 à 24,2 s, volume moyen -13,5 à -15,2 dB (homogène). performance.json : toujours aucune statistique, croisement impossible.
- Défauts : ~40 % de l'écran vide en bas (scène à y=640, sous-titres à 66 %), emojis de taille modeste, paires d'emojis génériques (école + globe, microscope + document), emojis minuscules au début du pop. Sous-titres entiers, "15 min" OK.
- Notes moyennes (estimées) : lisibilité 4,5 ; illustration 3 ; rythme 4 ; son 4 ; cohérence fond 3 ; différence 3,5.
- Changé : make_short.py -> centre de scène 640 -> 780, emojis +15 %, barres liées au centre, grille décalée, sous-titres 66 % -> 72,5 % de la hauteur.
- Test (scripts 2026-11-20_3, 2026-11-20_1, 2026-11-19_4, rendus /tmp, ancien vs nouveau) : 1080x1920, audio, durées identiques, volume identique (-13,5/-15,2/-14,5 dB). 6 images par vidéo : sous-titres entiers, barres, nombre "15 min" et emojis bien placés, rythme inchangé. Promu (make_short_stable.py = version précédente).
- Note mise en page avant/après : 3 -> 4.

### 2026-11-21 - Pop des emojis démarrant à 60 %
- Constaté (10 vidéos des 20 et 21/11, 6 images chacune, volumedetect) : toutes 1080x1920 + audio, 18,2 à 24,2 s, volume moyen -13,5 à -15,2 dB, crête -1,1 à -1,5 dB (homogène). performance.json : toujours aucune statistique, croisement impossible.
- Défauts : emojis minuscules ou réduits à un point au début de chaque scène (ex. 2026-11-20_2, microscope + document), paires d'emojis génériques (🔁❓, 🏫🌍), sous-titres découpés en fragments orphelins ("A", "I?\"", "IN A"), scènes à un seul emoji, bas d'écran encore vide (volontaire).
- Notes moyennes (estimées) : lisibilité 4 ; illustration 3 ; rythme 4 ; son 4 ; cohérence fond 3 ; différence 3,5 ; faits non revérifiés.
- Changé : make_short.py -> taille du pop = 60 % + 40 % de la courbe d'ease, décalage entre emojis 0,10 -> 0,05, durée 0,38 -> 0,25 de scène.
- Test (scripts/2026-11-20_1 rendu dans /tmp, ancien vs nouveau) : 1080x1920, audio, 21,2 s, volume identique (-15,2 dB). Images de début de scène : plus d'emoji minuscule, les 3 emojis visibles dès 0,4 s ; sous-titres et rythme inchangés. Promu (make_short_stable.py = version précédente).
- Note rythme/illustration au début de scène avant/après : 3 -> 4.

### 2026-11-22 - Sous-titres regroupés par unités de sens
- Constaté (vidéos des 21 et 22/11, 6 images chacune pour 5 d'entre elles, volumedetect) : toutes 1080x1920 + audio, 20,6 à 23,3 s, volume moyen -13,5 à -14,1 dB, crête -1,4/-1,5 dB (homogène). performance.json : toujours aucune statistique, croisement impossible.
- Défauts : sous-titres finissant sur un mot-outil ("DOMINANT LEFT OR", "THEY FOUND NO", "THE BRAINS OF"), paires d'emojis génériques (🧠🔁 répété en 22_4, 🥶🤷), emojis statiques pendant la phrase, bas d'écran vide (~30 %). Nombres, jauges, barres OK.
- Notes moyennes (estimées) : lisibilité 4 ; illustration 3 ; rythme 3,5 ; son 4 ; cohérence fond 3 ; différence 3,5 ; faits non revérifiés.
- Changé : make_short.py -> pages() : coupe après ponctuation puis découpage optimal (programmation dynamique) en pages de 1 à 3 mots, pénalisant les fins sur mot-outil, les pages d'un mot et les tailles déséquilibrées.
- Test (scripts/2026-11-22_1, ancien vs nouveau, 8 images) : 1080x1920, audio aac, 20,65 s, -13,5 dB identiques ; fins sur mot-outil 4/8 -> 0/8, sous-titres entiers, rythme inchangé. Un 2e rendu (2026-11-22_2) a dépassé le délai de la session et n'a pas été comparé. Promu (make_short_stable.py = version précédente).
- Limite : quelques pages commencent par un mot-outil ("OF 1,011 PEOPLE", "FOR A") ; acceptable. Note lisibilité avant/après : 4 -> 4,5.

### 2026-11-23 - Micro-mouvement continu des emojis
- Constaté (vidéos des 22 et 23/11, 6 images pour 5 d'entre elles, volumedetect) : toutes 1080x1920 + audio, 19,5 à 31,9 s, volume moyen -13,5 à -15,4 dB, crête -1,3 à -1,5 dB (homogène). performance.json : toujours aucune statistique, croisement impossible.
- Défauts : emojis quasi immobiles après le pop (bob de 18 px, 6°), paires génériques choisies dans les scripts (✈️🔍 pour "the winners", 🖼️🧮 pour "save 200", 🌍🏛️ pour "African countries", 🆕✨ pour "the fresh"), bas d'écran vide (~25 %). Sous-titres entiers, barres OK.
- Notes moyennes (estimées) : lisibilité 4,5 ; illustration 3 ; rythme 3,5 ; son 4 ; cohérence fond 3 ; différence 3,5 ; faits non revérifiés.
- Changé : make_short.py -> emojis : bob 34 px, dérive horizontale, respiration +-5 % avec zoom progressif +6 %, rotation +-10 deg.
- Test (scripts/2026-11-23_3, ancien vs nouveau, 6 images) : 1080x1920, audio, 21,1 s, -13,6 dB identiques ; emojis plus grands/inclinés, sous-titres et barres entiers, aucune coupure. Mesure de mouvement automatique non aboutie : jugement visuel uniquement. Promu (make_short_stable.py = version précédente).
- Note rythme visuel avant/après : 3,5 -> 4 (estimé).
- Nouvelles idées : guide de choix d'emojis précis pour les rédacteurs de scripts (éviter les paires génériques) ; visuel secondaire dans le bas d'écran.
