# Messages du jeu Mile by Mile

# Nom du jeu
game-name-milebymile = Mile by Mile

# Options de jeu
milebymile-set-distance = Distance de course : { $miles } miles
milebymile-enter-distance = Entrez la distance de course (300-3000)
milebymile-set-winning-score = Score gagnant : { $score } points
milebymile-enter-winning-score = Entrez le score gagnant (1000-10000)
milebymile-toggle-perfect-crossing = Requérir arrivée exacte : { $enabled }
milebymile-toggle-stacking = Autoriser empilement d'attaques : { $enabled }
milebymile-toggle-reshuffle = Remélanger la défausse : { $enabled }
milebymile-toggle-karma = Règle du karma : { $enabled }
milebymile-set-rig = Truquage du paquet : { $rig }
milebymile-select-rig = Sélectionnez l'option de truquage du paquet

# Annonces de changement d'options
milebymile-option-changed-distance = Distance de course définie sur { $miles } miles.
milebymile-option-changed-winning = Score gagnant défini sur { $score } points.
milebymile-option-changed-crossing = Requérir arrivée exacte { $enabled }.
milebymile-option-changed-stacking = Autoriser empilement d'attaques { $enabled }.
milebymile-option-changed-reshuffle = Remélanger la défausse { $enabled }.
milebymile-option-changed-karma = Règle du karma { $enabled }.
milebymile-option-changed-rig = Truquage du paquet défini sur { $rig }.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Statut
milebymile-status = { $name } : { $points } points, { $miles } miles, Problèmes : { $problems }, Sécurités : { $safeties }

# Actions de cartes
milebymile-no-matching-safety = Vous n'avez pas la carte de sécurité correspondante !
milebymile-cant-play = Vous ne pouvez pas jouer { $card } car { $reason }.
milebymile-no-card-selected = Aucune carte sélectionnée à défausser.
milebymile-no-valid-targets = Aucune cible valide pour ce danger !
milebymile-you-drew = Vous avez pioché : { $card }
milebymile-discards = { $player } défausse une carte.
milebymile-select-target = Sélectionnez une cible

# Jouer des distances
milebymile-plays-distance-individual = { $player } joue { $distance } miles, et est maintenant à { $total } miles.
milebymile-plays-distance-team = { $player } joue { $distance } miles ; leur équipe est maintenant à { $total } miles.

# Voyage terminé
milebymile-journey-complete-perfect-individual = { $player } a terminé le voyage avec un franchissement parfait !
milebymile-journey-complete-perfect-team = L'équipe { $team } a terminé le voyage avec un franchissement parfait !
milebymile-journey-complete-individual = { $player } a terminé le voyage !
milebymile-journey-complete-team = L'équipe { $team } a terminé le voyage !

# Jouer des dangers
milebymile-plays-hazard-individual = { $player } joue { $card } sur { $target }.
milebymile-plays-hazard-team = { $player } joue { $card } sur l'équipe { $team }.

# Jouer des remèdes/sécurités
milebymile-plays-card = { $player } joue { $card }.
milebymile-plays-dirty-trick = { $player } joue { $card } comme un Sale Tour !

# Paquet
milebymile-deck-reshuffled = Défausse remélangée dans le paquet.

# Course
milebymile-new-race = Nouvelle course commence !
milebymile-race-complete = Course terminée ! Calcul des scores...
milebymile-earned-points = { $name } a gagné { $score } points cette course : { $breakdown }.
milebymile-total-scores = Scores totaux :
milebymile-team-score = { $name } : { $score } points

# Répartition des scores
milebymile-from-distance = { $miles } de distance parcourue
milebymile-from-trip = { $points } pour avoir terminé le voyage
milebymile-from-perfect = { $points } pour un franchissement parfait
milebymile-from-safe = { $points } pour un voyage sûr
milebymile-from-shutout = { $points } pour un blanchissage
milebymile-from-safeties = { $points } pour { $count } { $safeties ->
    [0] sécurité
    [1] sécurité
   *[other] sécurités
}
milebymile-from-all-safeties = { $points } pour les 4 sécurités
milebymile-from-dirty-tricks = { $points } pour { $count } { $tricks ->
    [0] sale tour
    [1] sale tour
   *[other] sales tours
}

# Fin de jeu
milebymile-wins-individual = { $player } gagne le jeu !
milebymile-wins-team = L'équipe { $team } gagne le jeu ! ({ $members })
milebymile-final-score = Score final : { $score } points

# Messages de karma - clash (les deux perdent le karma)
milebymile-karma-clash-you-target = Vous et votre cible êtes tous deux répudiés ! L'attaque est neutralisée.
milebymile-karma-clash-you-attacker = Vous et { $attacker } êtes tous deux répudiés ! L'attaque est neutralisée.
milebymile-karma-clash-others = { $attacker } et { $target } sont tous deux répudiés ! L'attaque est neutralisée.
milebymile-karma-clash-your-team = Votre équipe et votre cible sont toutes deux répudiées ! L'attaque est neutralisée.
milebymile-karma-clash-target-team = Vous et l'équipe { $team } êtes tous deux répudiés ! L'attaque est neutralisée.
milebymile-karma-clash-other-teams = L'équipe { $attacker } et l'équipe { $target } sont toutes deux répudiées ! L'attaque est neutralisée.

# Messages de karma - attaquant répudié
milebymile-karma-shunned-you = Vous avez été répudié pour votre agression ! Votre karma est perdu.
milebymile-karma-shunned-other = { $player } a été répudié pour son agression !
milebymile-karma-shunned-your-team = Votre équipe a été répudiée pour son agression ! Le karma de votre équipe est perdu.
milebymile-karma-shunned-other-team = L'équipe { $team } a été répudiée pour son agression !

# Fausse Vertu
milebymile-false-virtue-you = Vous jouez Fausse Vertu et regagnez votre karma !
milebymile-false-virtue-other = { $player } joue Fausse Vertu et regagne son karma !
milebymile-false-virtue-your-team = Votre équipe joue Fausse Vertu et regagne son karma !
milebymile-false-virtue-other-team = L'équipe { $team } joue Fausse Vertu et regagne son karma !

# Problèmes/Sécurités (pour affichage de statut)
milebymile-none = aucun

# Raisons de carte non jouable
milebymile-reason-not-on-team = vous n'êtes pas dans une équipe
milebymile-reason-stopped = vous êtes arrêté
milebymile-reason-has-problem = vous avez un problème qui empêche de conduire
milebymile-reason-speed-limit = la limitation de vitesse est active
milebymile-reason-exceeds-distance = cela dépasserait { $miles } miles
milebymile-reason-no-targets = il n'y a pas de cibles valides
milebymile-reason-no-speed-limit = vous n'êtes pas sous une limitation de vitesse
milebymile-reason-has-right-of-way = Priorité vous permet d'avancer sans feux verts
milebymile-reason-already-moving = vous êtes déjà en mouvement
milebymile-reason-must-fix-first = vous devez d'abord réparer le { $problem }
milebymile-reason-has-gas = votre voiture a de l'essence
milebymile-reason-tires-fine = vos pneus vont bien
milebymile-reason-no-accident = votre voiture n'a pas eu d'accident
milebymile-reason-has-safety = vous avez déjà cette sécurité
milebymile-reason-has-karma = vous avez toujours votre karma
milebymile-reason-generic = elle ne peut pas être jouée maintenant

# Noms de cartes
milebymile-card-out-of-gas = Panne d'essence
milebymile-card-flat-tire = Pneu crevé
milebymile-card-accident = Accident
milebymile-card-speed-limit = Limitation de vitesse
milebymile-card-stop = Stop
milebymile-card-gasoline = Essence
milebymile-card-spare-tire = Pneu de secours
milebymile-card-repairs = Réparations
milebymile-card-end-of-limit = Fin de limitation
milebymile-card-green-light = Feu vert
milebymile-card-extra-tank = Réservoir supplémentaire
milebymile-card-puncture-proof = Anti-crevaison
milebymile-card-driving-ace = As du volant
milebymile-card-right-of-way = Priorité
milebymile-card-false-virtue = Fausse Vertu
milebymile-card-miles = { $miles } miles

# Raisons d'action désactivée
milebymile-no-dirty-trick-window = Aucune fenêtre de sale tour n'est active.
milebymile-not-your-dirty-trick = Ce n'est pas la fenêtre de sale tour de votre équipe.
milebymile-between-races = Attendez le début de la prochaine course.

# Erreurs de validation
milebymile-error-karma-needs-three-teams = La règle du karma nécessite au moins 3 voitures/équipes distinctes.

milebymile-you-play-safety-with-effect = Vous jouez { $card }. { $effect }
milebymile-player-plays-safety-with-effect = { $player } joue { $card }. { $effect }
milebymile-you-play-dirty-trick-with-effect = Vous jouez { $card } comme un Coup Bas. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } joue { $card } comme un Coup Bas. { $effect }
milebymile-safety-effect-extra-tank = Maintenant protégé contre Panne d'essence.
milebymile-safety-effect-puncture-proof = Maintenant protégé contre Crevaison.
milebymile-safety-effect-driving-ace = Maintenant protégé contre Accident.
milebymile-safety-effect-right-of-way = Maintenant protégé contre Stop et Limitation de vitesse.
