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
- [ ] Normalisation du volume (cible environ -14 LUFS) et léger ducking de la musique sous la voix
- [ ] Transitions variées entre scènes (glissement, zoom traversant, glitch) au lieu d'un seul flash
- [ ] Nouveaux types de visuels : comparaison "vs" à deux colonnes, liste qui se coche, carte-citation, chronologie, jauge
- [ ] Particules d'emojis (pluie, explosion) au moment de la révélation
- [ ] Rythme de voix plus naturel : pauses plus longues avant la révélation, vitesse légèrement variable
- [ ] Musique différente selon la palette (tonalité, tempo, instrumentation)
- [ ] Mise en avant visuelle de la révélation (zoom plus fort, mot en grand plein écran)
- [ ] Styles de sous-titres différents selon le format (quiz, top 3, mythe)
- [ ] Image de couverture (miniature) soignée si la chaîne l'autorise (videoThumbnailUrl dans Metricool, nécessite une chaîne vérifiée)
- [ ] Synchronisation mot à mot plus précise (alignement réel de la voix si un outil local est disponible)

## Journal des améliorations
(rien pour l'instant)
