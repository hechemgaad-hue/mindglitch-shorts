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

### 2026-11-18 - Controle performance : donnees indisponibles, aucun verdict
- Metricool (connecteurs "videos published in range" et "all videos", 14->18/11) ne renvoie aucune ligne pour les Shorts MindGlitch, y compris ceux publies le 17/11 (>18 h). Seules 2 vieilles videos non liees apparaissent. Pas de chiffres, donc pas de verdict ni de changement de strategie (on ne fabrique rien).
- A faire : si toujours vide au prochain controle, verifier la connexion YouTube dans Metricool / consulter YouTube Studio ; l'analyse reprendra des que des chiffres existent.

### 2026-11-18 (soir) - Controle performance : toujours aucune donnee, aucun verdict
- Metricool (videos published in range 14->18/11 + evolution YTEV02/YTEV13) : aucune ligne / vues null ou 0, y compris pour les Shorts du 17/11 (>27 h). Donnees non exploitables, donc ni verdict 4 h/48 h ni changement de strategie (rien n'est fabrique).
- Hypothese : liaison YouTube/Metricool a verifier (ou stats non remontees). Action proprietaire : verifier dans YouTube Studio les vues reelles des Shorts du 17 et 18/11 ; si 17/11 < 1000 vues a 48 h (19/11 soir), l'evaluation echec_48h devra etre faite manuellement ou apres retablissement des donnees.

### 2026-11-19 (nuit) - Controle performance : toujours aucune donnee, aucun verdict
- Metricool (videos published in range 10->19/11) renvoie 0 ligne, y compris pour les Shorts du 17/11 (>30 h) et du 18/11 matin (>16 h). Aucun chiffre, donc ni verdict ni changement de strategie.
- Action proprietaire : verifier la liaison YouTube dans Metricool et les vues dans YouTube Studio. Les echeances 48 h du 17/11 (19/11 soir) ne pourront etre jugees qu'avec des donnees.

### 2026-11-19 (apres-midi) - Controle performance : toujours aucune donnee, aucun verdict
- Metricool (videos published in range 15->19/11, metrics YTVP02/04/17/06/07/08/09/11/12) renvoie 0 ligne, y compris pour les Shorts du 17/11 (>46 h, echeance 48 h a 18:00-21:30 ce soir) et du 18/11. Rien n'est fabrique : ni verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (4e controle consecutif vide) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; sans donnees, les regles 4 h/48 h ne peuvent pas etre appliquees.

### 2026-11-19 (soir) - Controle performance : 5e controle vide, echeance 48 h depassee sans donnees
- Metricool (videos published in range 15->19/11, memes metriques) renvoie 0 ligne : Shorts du 17/11 (>51 h, echeance 48 h passee) et du 18/11 non evaluables. Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire : relever les vues dans YouTube Studio et/ou reconnecter YouTube dans Metricool ; evaluation echec_48h/ok_48h a faire manuellement a partir de ces chiffres.

### 2026-11-20 (nuit) - Controle performance : 6e controle vide, aucun verdict
- Metricool (videos published in range 01->20/11, memes metriques) renvoie 0 ligne : Shorts du 17/11 (>54 h) et du 18/11 non evaluables ; ceux du 19/11 (ids non remontes) non plus. Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; sans donnees, les regles 4 h/48 h ne peuvent pas etre appliquees.

### 2026-11-20 (apres-midi) - Controle performance : 7e controle vide, aucun verdict
- Metricool (videos published in range 16->20/11, memes metriques) renvoie 0 ligne : Shorts du 17, 18 et 19/11 non evaluables (echeance 48 h du 17/11 et du 18/11 matin depassee). Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation a faire manuellement sinon.

### 2026-11-20 (soir) - Controle performance : 8e controle vide, aucun verdict
- Metricool (videos published in range 16->20/11, memes metriques) renvoie 0 ligne : Shorts du 17, 18, 19 et du 20/11 (matin/midi) non evaluables. Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, 8 controles consecutifs vides) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-21 (nuit) - Controle performance : 9e controle vide, aucun verdict
- Metricool (videos published in range 17->21/11, memes metriques) renvoie 0 ligne : Shorts du 17 au 20/11 non evaluables (echeances 4 h et 48 h depassees pour tous sauf ceux du 20/11 soir). Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, 9 controles consecutifs vides) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-21 (apres-midi) - Controle performance : 10e controle vide, aucun verdict
- Metricool (videos published in range, 01/10->21/11, metriques YTVP02/04/06/08/09/17) ne renvoie aucun Short MindGlitch (seulement 4 vieilles videos non liees, vues null). Shorts du 17 au 21/11 (matin/midi) non evaluables. Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, 10 controles consecutifs vides) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-21 (soir) - Controle performance : 11e controle vide, aucun verdict
- Metricool (videos published in range 17->21/11, metriques YTVP02/04/17/06/07/08/09/11/12) renvoie 0 ligne : Shorts du 17 au 21/11 non evaluables. Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, 11 controles consecutifs vides, >4 jours) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-22 (nuit) - Controle performance : 12e controle vide, aucun verdict
- Metricool (videos published in range 18->22/11, metriques YTVP02/04/17/06/07/08/09/11/12) renvoie 0 ligne : Shorts du 17 au 21/11 non evaluables (>5 jours pour les premiers). Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, 12 controles consecutifs vides) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-22 (apres-midi) - Controle performance : 13e controle vide, aucun verdict
- Metricool (videos published in range 18->22/11, metriques YTVP02/04/17/06/07/08/09/11/12) renvoie 0 ligne : Shorts du 17 au 22/11 non evaluables. Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, 13 controles consecutifs vides, >5 jours) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-22 (soir) - Controle performance : 14e controle vide, aucun verdict
- Metricool (videos published in range 18->22/11, metriques YTVP02/04/17/06/07/08/09/11/12) renvoie 0 ligne : Shorts du 17 au 22/11 non evaluables. Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, 14 controles consecutifs vides, >5 jours) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-23 (nuit) - Controle performance : 15e controle vide, aucun verdict
- Metricool (videos published in range 19->23/11, metriques YTVP02/04/17/06/07/08/09/11/12) renvoie 0 ligne : Shorts du 17 au 22/11 non evaluables (>5 jours). Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, 15 controles consecutifs vides) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-23 (apres-midi) - Controle performance : 16e controle vide, aucun verdict
- Metricool (videos published in range 19->23/11 et 01/10->23/11, metriques YTVP02/04/17/06/07/08/09/11/12) ne renvoie aucun Short MindGlitch (seulement 4 vieilles videos non liees, vues null). Shorts du 17 au 23/11 (matin/midi) non evaluables. Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, 16 controles consecutifs vides, >6 jours) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-23 (soir) - Controle performance : 17e controle vide, aucun verdict
- Metricool (videos published in range 19->23/11, metriques YTVP02/04/17/06/07/08/09/11/12) renvoie 0 ligne : Shorts du 17 au 23/11 non evaluables. Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, 17 controles consecutifs vides, >6 jours) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-24 (nuit) - Controle performance : 18e controle vide, aucun verdict
- Metricool (videos published in range 20->24/11 et 01->24/11, metriques YTVP02/04/17/06/07/08/09/11/12) renvoie 0 ligne : Shorts du 17 au 23/11 non evaluables (>7 jours pour les premiers). Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, 18 controles consecutifs vides) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-24 (apres-midi) - Controle performance : 19e controle vide, aucun verdict
- Metricool (videos published in range 20->24/11, metriques YTVP02/04/17/06/07/08/09/11/12) renvoie 0 ligne : Shorts du 17 au 24/11 (matin/midi) non evaluables. Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, 19 controles consecutifs vides, >7 jours) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-24 (soir) - Controle performance : 20e controle vide, aucun verdict
- Metricool (videos published in range 20->24/11 et 01/10->24/11, metriques YTVP02/04/17/06/08/09) renvoie 0 ligne MindGlitch (seulement 4 vieilles videos non liees, vues null). Shorts du 17 au 24/11 non evaluables. Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, 20 controles consecutifs vides, >7 jours) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-25 (nuit) - Controle performance : 21e controle vide, aucun verdict
- Metricool (videos published in range 21->25/11, metriques YTVP02/04/17/06/07/08/09/11/12) renvoie 0 ligne : Shorts du 17 au 24/11 non evaluables (>8 jours pour les premiers). Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, 21 controles consecutifs vides) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-25 (apres-midi) - Controle performance : 22e controle vide, aucun verdict
- Metricool (videos published in range 21->25/11, metriques YTVP02/04/17/06/07/08/09/11/12) renvoie 0 ligne : Shorts du 17 au 25/11 (matin) non evaluables. Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, 22 controles consecutifs vides, >8 jours) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-25 (soir) - Controle performance : 23e controle vide, aucun verdict
- Metricool (videos published in range 21->25/11, metriques YTVP02/04/17/06/07/08/09/11/12) renvoie 0 ligne : Shorts du 17 au 25/11 non evaluables. Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, 23 controles consecutifs vides, >8 jours) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-26 (nuit) - Controle performance : 24e controle vide, aucun verdict
- Metricool (videos published in range 22/11->26/11 et 01/10->26/11, metriques YTVP02/04/17/06/07/08/09/11/12) ne renvoie aucun Short MindGlitch (seulement 4 vieilles videos non liees, vues null). Shorts du 17 au 25/11 non evaluables. Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, 24 controles consecutifs vides, >8 jours) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-26 (apres-midi) - Controle performance : 25e controle vide, aucun verdict
- Metricool (videos published in range 22->26/11, metriques YTVP02/04/17/06/07/08/09/11/12) renvoie 0 ligne : Shorts du 17 au 26/11 (matin/midi) non evaluables. Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, 25 controles consecutifs vides, >9 jours) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-26 (soir) - Controle performance : 26e controle vide, aucun verdict
- Metricool (videos published in range 22->26/11 et 01/11->26/11, metriques YTVP02/04/17/06/07/08/09/11/12) renvoie 0 ligne : Shorts du 17 au 26/11 non evaluables. Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, 26 controles consecutifs vides, >9 jours) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-27 (nuit) - Controle performance : 27e controle vide, aucun verdict
- Metricool (videos published in range 23->27/11 et 01->27/11, metriques YTVP02/04/17/06/07/08/09/11/12) renvoie 0 ligne : Shorts du 17 au 26/11 non evaluables (>10 jours pour les premiers). Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, 27 controles consecutifs vides) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-27 (apres-midi) - Controle performance : toujours aucune donnee, aucun verdict
- Metricool (videos published in range 23->27/11, metriques YTVP02/04/17/06/07/08/09/11/12) renvoie 0 ligne : Shorts du 17 au 27/11 non evaluables. Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, plus de 10 jours sans donnees) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-27 (soir) - Controle performance : 28e controle vide, aucun verdict
- Metricool (videos published in range 23->27/11, memes metriques) renvoie 0 ligne : Shorts du 17 au 27/11 non evaluables. Aucun chiffre, donc aucun verdict ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, 28 controles consecutifs vides) : reconnecter YouTube dans Metricool et/ou relever les vues dans YouTube Studio ; evaluation manuelle sinon.

### 2026-11-28 (nuit) - Controle performance : 29e controle sans stat par video, MAIS 1res donnees niveau chaine (alerte)
- Metricool "videos published in range" (24->28/11 et 01->28/11) renvoie toujours 0 ligne : aucun verdict 4 h/48 h possible, aucun chiffre fabrique. Configuration active inchangee.
- Nouveau : l'endpoint evolution donne enfin des vues CHAINE/jour (YTEV02) : 17/11 1539, 18/11 2374, 19/11 2388, 20/11 1428, 21/11 2271, puis 22/11 13, 23/11 2, 24/11 4 (25-27/11 null = retard probable). Abonnes 8 -> 14 (17->22/11), 0 gagne depuis le 22/11. Non attribuable a une video precise (5 Shorts/jour publies).
- Lecture prudente : ~1400-2400 vues/jour du 17 au 21/11 (soit ~300-480 vues/Short) puis effondrement brutal le 22/11. Cause inconnue : retard de remontee des donnees recentes OU probleme reel de diffusion (restriction/contenu repetitif/Shorts non listes ou prives ?). Aucun changement de strategie decide : un seul signal niveau chaine ne permet pas d'isoler une variable.
- Action proprietaire (urgent) : ouvrir YouTube Studio > Analytique (vues par video, 17->28/11) et verifier avertissements / statut de monetisation / visibilite des Shorts publies depuis le 22/11 ; communiquer les chiffres par video pour evaluation manuelle 4 h/48 h.

### 2026-11-28 (apres-midi) - Controle performance : 30e controle sans stat par video, aucun verdict
- Metricool (videos published in range 24->28/11) renvoie 0 ligne ; evolution chaine (YTEV02) inchangee depuis la nuit : 22/11 13 vues, 23/11 2, 24/11 4, 25-27/11 null, abonnes 14 stables. Aucun chiffre par video, donc aucun verdict 4 h/48 h ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent, >11 jours sans donnees par video, chute chaine depuis le 22/11) : verifier YouTube Studio (avertissements, visibilite des Shorts, liaison Metricool) et fournir les vues par video.

### 2026-11-28 (soir) - Controle performance : 31e controle sans stat par video, aucun verdict
- Metricool (videos published in range 24->28/11 ; all videos 01->28/11) renvoie 0 ligne. Evolution chaine inchangee : 22/11 13 vues, 23/11 2, 24/11 4, 25-27/11 null, abonnes 14 stables. Aucun chiffre par video : ni verdict 4 h/48 h ni changement de strategie. Configuration active inchangee.
- Action proprietaire (urgent) : verifier YouTube Studio (avertissements, visibilite des Shorts depuis le 22/11, liaison Metricool) et fournir les vues par video.
