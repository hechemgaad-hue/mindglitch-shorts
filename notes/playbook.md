# Playbook MindGlitch (lu par la tâche quotidienne avant d'écrire les scripts)

Mis à jour par la tâche "MindGlitch - contrôle performance". Ne changer qu'UNE variable principale par jour pour savoir ce qui marche.

## Règles de performance imposées par le propriétaire
- Moins de 100 vues 4 h après publication : remise en question obligatoire, changer au moins un élément concret.
- Moins de 1000 vues 48 h après publication : remise en question plus profonde (sujet, format, accroche, horaires).

## Configuration active (baseline, 2026-11-17)
- Thème : faits de psychologie, en anglais
- Accroche : promesse ou affirmation surprenante (≤10 mots)
- Rythme : phrases <14 mots, 18 à 30 s, voix am_michael, boucle outro/accroche
- Visuels : emojis animés + compteurs/barres, palettes 0 à 4
- Volume : 5 Shorts par jour (décision du propriétaire, 2026-11-17 ; avant : 3). Scripts scripts/AAAA-MM-JJ_1 à _5.
- Créneaux : 09:00, 12:00, 15:00, 18:00, 20:30 (Paris), un Short par créneau ; ne pas pousser plus de 5 par jour
- Titres : question ou affirmation choc + " #Shorts"

## Variété et valeur ajoutée (règle permanente, ajoutée le 2026-11-17)
But : que chaque vidéo soit clairement différente des autres et utile au spectateur (sans rien cacher : on garde la mention "contenu généré par IA").
- Formats à alterner, jamais le même format deux fois dans la même journée, ni plus de 2 jours de suite :
  1. Mythe contre réalité ("Everyone believes X. It's false.")
  2. Top 3 (3 exemples concrets numérotés)
  3. Mini-quiz (question, 2 options à l'écran, réponse révélée vers la fin ; visuals de type emoji/grid)
  4. Histoire d'une expérience célèbre (contexte, protocole en une phrase, résultat)
  5. "Que se passe-t-il si..." (conséquence psychologique concrète d'une situation du quotidien)
  6. Astuce applicable aujourd'hui (une action simple en 1 étape, issue d'un effet documenté)
- Chaque vidéo doit contenir un angle, un exemple ou un chiffre précis qui la rend différente d'une autre vidéo du même effet : pas de généralités.
- Varier la voix d'une vidéo à l'autre parmi celles disponibles dans Kokoro (vérifier avec Kokoro(...).get_voices() les voix anglaises, ex. am_michael, af_heart, bm_george, af_bella) et la palette (0 à 4). Varier aussi la longueur (18 à 30 s) et le type d'accroche.
- Chaque fait doit venir d'une source identifiable (étude, chercheur, année) que tu peux citer ; pour les expériences célèbres, vérifier sur le web avant écriture. En cas de doute, ne pas publier ce fait.
- Premier commentaire : dans createScheduledPost, renseigne info.firstCommentText avec une question courte qui invite à répondre (ex. "Which of these have you noticed in yourself? 👇"), adaptée au sujet de la vidéo. (Metricool publie ce commentaire ; l'épinglage éventuel reste manuel.)
- Mention "contenu généré par IA" : toujours isAiGeneratedContent true.

## Filet de sécurité du générateur
- La production utilise make_short.py. Si cette version échoue ou produit un défaut, utiliser make_short_stable.py (dernière version validée) et le signaler dans le compte rendu.
- Les améliorations techniques sont gérées par la tâche "amelioration qualite" (voir notes/quality.md). Ne pas modifier le générateur pour autre chose qu'un correctif de bug.

## Journal des changements
### 2026-11-17 - Passage de 3 à 5 Shorts par jour (décision du propriétaire)
- Changement : volume 3 -> 5, créneaux 09:00/12:00/15:00/18:00/20:30. Pas lié à un verdict de performance (aucune vidéo évaluée à ce jour).
- Contrainte : 5 formats différents par jour parmi les 6 de la règle de variété (jamais deux fois le même format le même jour) ; varier voix, palette et longueur.
- Mesure : comparer vues à 4 h par créneau (les 2 nouveaux, 09:00 et 15:00, sont à surveiller) et vérifier que la baisse de vues par vidéo n'est pas liée à la saturation.
- Note : les créneaux 09:00 et 15:00 sont une hypothèse à valider ; la tâche de création doit lire cette config (son prompt peut encore mentionner 3 vidéos).
