# Messages de l'interface principale pour PlayPalace

# Catégories de jeux
category-card-games = Jeux de cartes
category-dice-games = Jeux de dés
category-board-games = Jeux de société
category-rb-play-center = Centre RB Play
category-poker = Poker
category-uncategorized = Non catégorisé

# Titres des menus
main-menu-title = Menu principal
play-menu-title = Jouer
categories-menu-title = Catégories de jeux
tables-menu-title = Tables disponibles

# Éléments de menu
play = Jouer
view-active-tables = Voir les tables actives
options = Options
logout = Déconnexion
back = Retour
context-menu = Menu contextuel.
no-actions-available = Aucune action disponible.
create-table = Créer une nouvelle table
join-as-player = Rejoindre en tant que joueur
join-as-spectator = Rejoindre en tant que spectateur
leave-table = Quitter la table
start-game = Démarrer le jeu
add-bot = Ajouter un bot
remove-bot = Retirer un bot
actions-menu = Menu des actions
save-table = Sauvegarder la table
whose-turn = Tour de qui
whos-at-table = Qui est à la table
check-scores = Vérifier les scores
check-scores-detailed = Scores détaillés
check-game-options = Vérifier les options de jeu
no-game-options = Aucune option de jeu.

# Messages de tour
game-player-skipped = { $player } est passé.

# Messages de table
table-created = { $host } a créé une nouvelle table { $game }.
table-joined = { $player } a rejoint la table.
table-left = { $player } a quitté la table.
new-host = { $player } est maintenant l'hôte.
waiting-for-players = En attente de joueurs. {$min} min, { $max } max.
game-starting = Le jeu commence !
table-listing = Table de { $host } ({ $count } utilisateurs)
table-listing-one = Table de { $host } ({ $count } utilisateur)
table-listing-with = Table de { $host } ({ $count } utilisateurs) avec { $members }
table-listing-game = { $game } : Table de { $host } ({ $count } utilisateurs)
table-listing-game-one = { $game } : Table de { $host } ({ $count } utilisateur)
table-listing-game-with = { $game } : Table de { $host } ({ $count } utilisateurs) avec { $members }
table-not-exists = La table n'existe plus.
table-full = La table est pleine.
player-replaced-by-bot = { $player } est parti et a été remplacé par un bot.
player-took-over = { $player } a pris le relais du bot.
spectator-joined = A rejoint la table de { $host } en tant que spectateur.

# Mode spectateur
spectate = Observer
now-playing = { $player } joue maintenant.
now-spectating = { $player } observe maintenant.
spectator-left = { $player } a cessé d'observer.

# Général
welcome = Bienvenue à PlayPalace !
goodbye = Au revoir !

# Annonces de présence des utilisateurs
user-online = { $player } est en ligne.
user-offline = { $player } est hors ligne.
user-is-admin = { $player } est administrateur de PlayPalace.
user-is-server-owner = { $player } est propriétaire du serveur PlayPalace.
online-users-none = Aucun utilisateur en ligne.
online-users-one = 1 utilisateur : { $users }
online-users-many = { $count } utilisateurs : { $users }
online-user-not-in-game = Pas en jeu
online-user-waiting-approval = En attente d'approbation

# Options
language = Langue
language-option = Langue : { $language }
language-changed = Langue définie sur { $language }.

# États des options booléennes
option-on = Activé
option-off = Désactivé

# Options sonores
turn-sound-option = Son de tour : { $status }

# Options de dés
clear-kept-option = Effacer les dés gardés lors du lancer : { $status }
dice-keeping-style-option = Style de conservation des dés : { $style }
dice-keeping-style-changed = Style de conservation des dés défini sur { $style }.
dice-keeping-style-indexes = Index des dés
dice-keeping-style-values = Valeurs des dés

# Noms de bots
cancel = Annuler
no-bot-names-available = Aucun nom de bot disponible.
select-bot-name = Sélectionnez un nom pour le bot
enter-bot-name = Entrez le nom du bot
no-options-available = Aucune option disponible.
no-scores-available = Aucun score disponible.

# Estimation de durée
estimate-duration = Estimer la durée
estimate-computing = Calcul de la durée estimée du jeu...
estimate-result = Moyenne des bots : { $bot_time } (± { $std_dev }). { $outlier_info }Temps humain estimé : { $human_time }.
estimate-error = Impossible d'estimer la durée.
estimate-already-running = L'estimation de durée est déjà en cours.

# Sauvegarder/Restaurer
saved-tables = Tables sauvegardées
no-saved-tables = Vous n'avez aucune table sauvegardée.
no-active-tables = Aucune table active.
restore-table = Restaurer
delete-saved-table = Supprimer
saved-table-deleted = Table sauvegardée supprimée.
missing-players = Impossible de restaurer : ces joueurs ne sont pas disponibles : { $players }
table-restored = Table restaurée ! Tous les joueurs ont été transférés.
table-saved-destroying = Table sauvegardée ! Retour au menu principal.
game-type-not-found = Le type de jeu n'existe plus.

# Raisons d'action désactivée
action-not-your-turn = Ce n'est pas votre tour.
action-not-playing = Le jeu n'a pas encore commencé.
action-spectator = Les spectateurs ne peuvent pas faire cela.
action-not-host = Seul l'hôte peut faire cela.
action-game-in-progress = Impossible de faire cela pendant que le jeu est en cours.
action-need-more-players = Besoin d’au moins { $min_players } joueurs pour commencer.
action-table-full = La table est pleine.
action-no-bots = Il n'y a aucun bot à retirer.
action-bots-cannot = Les bots ne peuvent pas faire cela.
action-no-scores = Aucun score disponible pour le moment.

# Actions de dés
dice-not-rolled = Vous n'avez pas encore lancé les dés.
dice-locked = Ce dé est verrouillé.
dice-no-dice = Aucun dé disponible.

# Actions de jeu
game-turn-start = Tour de { $player }.
game-no-turn = Aucun tour en ce moment.
table-no-players = Aucun joueur.
table-players-one = { $count } joueur : { $players }.
table-players-many = { $count } joueurs : { $players }.
table-spectators = Spectateurs : { $spectators }.
game-leave = Quitter
game-over = Fin du jeu
game-final-scores = Scores finaux
game-points = { $count } { $count ->
    [0] point
    [1] point
   *[other] points
}
play = Jouer

# Classements
leaderboards = Classements
leaderboards-menu-title = Classements
leaderboards-select-game = Sélectionnez un jeu pour voir son classement
leaderboard-no-data = Aucune donnée de classement pour ce jeu.

# Types de classement
leaderboard-type-wins = Leaders de victoires
leaderboard-type-rating = Classement de compétence
leaderboard-type-total-score = Score total
leaderboard-type-high-score = Meilleur score
leaderboard-type-games-played = Parties jouées
leaderboard-type-avg-points-per-turn = Moy. points par tour
leaderboard-type-best-single-turn = Meilleur tour unique
leaderboard-type-score-per-round = Score par manche

# En-têtes de classement
leaderboard-wins-header = { $game } - Leaders de victoires
leaderboard-total-score-header = { $game } - Score total
leaderboard-high-score-header = { $game } - Meilleur score
leaderboard-games-played-header = { $game } - Parties jouées
leaderboard-rating-header = { $game } - Classements de compétence
leaderboard-avg-points-header = { $game } - Moy. points par tour
leaderboard-best-turn-header = { $game } - Meilleur tour unique
leaderboard-score-per-round-header = { $game } - Score par manche

# Entrées de classement
leaderboard-wins-entry = { $rank } : { $player }, { $wins } { $wins ->
    [0] victoire
    [1] victoire
   *[other] victoires
} { $losses } { $losses ->
    [0] défaite
    [1] défaite
   *[other] défaites
}, { $percentage }% de victoires
leaderboard-score-entry = { $rank }. { $player } : { $value }
leaderboard-avg-entry = { $rank }. { $player } : { $value } moy
leaderboard-games-entry = { $rank }. { $player } : { $value } parties

# Statistiques du joueur
leaderboard-player-stats = Vos stats : { $wins } victoires, { $losses } défaites ({ $percentage }% de victoires)
leaderboard-no-player-stats = Vous n'avez pas encore joué à ce jeu.

# Classement de compétence
leaderboard-no-ratings = Aucune donnée de classement pour ce jeu.
leaderboard-rating-entry = { $rank }. { $player } : { $rating } classement ({ $mu } ± { $sigma })
leaderboard-player-rating = Votre classement : { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = Vous n'avez pas encore de classement pour ce jeu.

# Menu Mes statistiques
my-stats = Mes statistiques
my-stats-select-game = Sélectionnez un jeu pour voir vos statistiques
my-stats-no-data = Vous n'avez pas encore joué à ce jeu.
my-stats-no-games = Vous n'avez joué à aucun jeu.
my-stats-header = { $game } - Vos statistiques
my-stats-wins = Victoires : { $value }
my-stats-losses = Défaites : { $value }
my-stats-winrate = Taux de victoires : { $value }%
my-stats-games-played = Parties jouées : { $value }
my-stats-total-score = Score total : { $value }
my-stats-high-score = Meilleur score : { $value }
my-stats-rating = Classement de compétence : { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = Pas encore de classement de compétence
my-stats-avg-per-turn = Moy. points par tour : { $value }
my-stats-best-turn = Meilleur tour unique : { $value }

# Système de prédiction
predict-outcomes = Prédire les résultats
predict-header = Résultats prédits (par classement de compétence)
predict-entry = { $rank }. { $player } (classement : { $rating })
predict-entry-2p = { $rank }. { $player } (classement : { $rating }, { $probability }% de chance de victoire)
predict-unavailable = Les prédictions de classement ne sont pas disponibles.
predict-need-players = Besoin d'au moins 2 joueurs humains pour les prédictions.
action-need-more-humans = Besoin de plus de joueurs humains.
confirm-leave-game = Êtes-vous sûr de vouloir quitter la table ?
confirm-yes = Oui
confirm-no = Non

# Administration
administration = Administration
admin-menu-title = Administration

# Approbation de compte
account-approval = Approbation de compte
account-approval-menu-title = Approbation de compte
no-pending-accounts = Aucun compte en attente.
approve-account = Approuver
decline-account = Refuser
account-approved = Le compte de { $player } a été approuvé.
account-declined = Le compte de { $player } a été refusé et supprimé.

# En attente d'approbation (affiché aux utilisateurs non approuvés)
waiting-for-approval = Votre compte est en attente d'approbation par un administrateur.
account-approved-welcome = Votre compte a été approuvé ! Bienvenue à PlayPalace !
account-declined-goodbye = Votre demande de compte a été refusée.
    Raison :
account-banned = Votre compte est banni et ne peut pas être accédé.

# Erreurs de connexion
incorrect-username = Le nom d'utilisateur que vous avez entré n'existe pas.
incorrect-password = Le mot de passe que vous avez entré est incorrect.
already-logged-in = Ce compte est déjà connecté.

# Validation des identifiants
credential-username-length = Le nom d'utilisateur doit comporter entre { $min } et { $max } caractères.
credential-password-length = Le mot de passe doit comporter entre { $min } et { $max } caractères.

# Limitation de débit
rate-limit-login-ip = Trop de tentatives de connexion depuis cette adresse. Veuillez patienter et réessayer.
rate-limit-login-user = Trop de tentatives de connexion échouées pour ce nom d'utilisateur. Veuillez patienter et réessayer.
rate-limit-registration = Trop de tentatives d'inscription depuis cette adresse. Veuillez patienter et réessayer.
rate-limit-refresh = Trop de tentatives de rafraîchissement depuis cette adresse. Veuillez patienter et réessayer.

# Erreurs de session et d'authentification
account-not-found = Compte introuvable.
session-expired = Session expirée. Veuillez vous reconnecter.
session-token-mismatch = Le jeton de session ne correspond pas au nom d'utilisateur.
refresh-token-expired = Jeton de rafraîchissement expiré. Veuillez vous reconnecter.
refresh-token-mismatch = Le jeton de rafraîchissement ne correspond pas au nom d'utilisateur.

# Inscription
registration-success = Inscription réussie ! Votre compte est en attente d'approbation.
registration-username-taken = Ce nom d'utilisateur est déjà pris. Veuillez en choisir un autre.

# Préférence par défaut
pref-invalid-value = Sélection invalide, utilisation de la valeur par défaut.

# Raison du refus
decline-reason-prompt = Entrez une raison pour le refus (ou appuyez sur Échap pour annuler) :
account-action-empty-reason = Aucune raison donnée.

# Notifications d'administration pour les demandes de compte
account-request = demande de compte
account-action = action de compte prise

# Promotion/rétrogradation d'administrateur
promote-admin = Promouvoir administrateur
demote-admin = Rétrograder administrateur
promote-admin-menu-title = Promouvoir administrateur
demote-admin-menu-title = Rétrograder administrateur
no-users-to-promote = Aucun utilisateur disponible à promouvoir.
no-admins-to-demote = Aucun administrateur disponible à rétrograder.
confirm-promote = Êtes-vous sûr de vouloir promouvoir { $player } en tant qu'administrateur ?
confirm-demote = Êtes-vous sûr de vouloir rétrograder { $player } d'administrateur ?
broadcast-to-all = Annoncer à tous les utilisateurs
broadcast-to-admins = Annoncer aux administrateurs uniquement
broadcast-to-nobody = Silencieux (aucune annonce)
promote-announcement = { $player } a été promu administrateur !
promote-announcement-you = Vous avez été promu administrateur !
demote-announcement = { $player } a été rétrogradé d'administrateur.
demote-announcement-you = Vous avez été rétrogradé d'administrateur.
not-admin-anymore = Vous n'êtes plus administrateur et ne pouvez pas effectuer cette action.
not-server-owner = Seul le propriétaire du serveur peut effectuer cette action.

# Transfert de propriété du serveur
transfer-ownership = Transférer la propriété
transfer-ownership-menu-title = Transférer la propriété
no-admins-for-transfer = Aucun administrateur disponible pour transférer la propriété.
confirm-transfer-ownership = Êtes-vous sûr de vouloir transférer la propriété du serveur à { $player } ? Vous serez rétrogradé en administrateur.
transfer-ownership-announcement = { $player } est maintenant le propriétaire du serveur Play Palace !
transfer-ownership-announcement-you = Vous êtes maintenant le propriétaire du serveur Play Palace !

# Bannissement d'utilisateurs
ban-user = Bannir l'utilisateur
unban-user = Débannir l'utilisateur
no-users-to-ban = Aucun utilisateur disponible à bannir.
no-users-to-unban = Aucun utilisateur banni à débannir.
confirm-ban = Êtes-vous sûr de vouloir bannir { $player } ?
confirm-unban = Êtes-vous sûr de vouloir débannir { $player } ?
ban-reason-prompt = Entrez une raison pour le bannissement (facultatif) :
unban-reason-prompt = Entrez une raison pour le débannissement (facultatif) :
user-banned = { $player } a été banni.
user-unbanned = { $player } a été débanni.
you-have-been-banned = Vous avez été banni de ce serveur.
    Raison :
you-have-been-unbanned = Vous avez été débanni de ce serveur.
    Raison :
ban-no-reason = Aucune raison donnée.

# Bots virtuels (propriétaire du serveur uniquement)
virtual-bots = Bots virtuels
virtual-bots-fill = Remplir le serveur
virtual-bots-clear = Effacer tous les bots
virtual-bots-status = Statut
virtual-bots-clear-confirm = Êtes-vous sûr de vouloir effacer tous les bots virtuels ? Cela détruira également toutes les tables dans lesquelles ils se trouvent.
virtual-bots-not-available = Les bots virtuels ne sont pas disponibles.
virtual-bots-filled = Ajouté { $added } bots virtuels. { $online } sont maintenant en ligne.
virtual-bots-already-filled = Tous les bots virtuels de la configuration sont déjà actifs.
virtual-bots-cleared = Effacé { $bots } bots virtuels et détruit { $tables } { $tables ->
    [0] table
    [1] table
   *[other] tables
}.
virtual-bot-table-closed = Table fermée par l'administrateur.
virtual-bots-none-to-clear = Aucun bot virtuel à effacer.
virtual-bots-status-report = Bots virtuels : { $total } au total, { $online } en ligne, { $offline } hors ligne, { $in_game } en jeu.
virtual-bots-guided-overview = Tables guidées
virtual-bots-groups-overview = Groupes de bots
virtual-bots-profiles-overview = Profils
virtual-bots-guided-header = Tables guidées : { $count } règle(s). Allocation : { $allocation }, repli : { $fallback }, profil par défaut : { $default_profile }.
virtual-bots-guided-empty = Aucune règle de table guidée n'est configurée.
virtual-bots-guided-status-active = actif
virtual-bots-guided-status-inactive = inactif
virtual-bots-guided-table-linked = lié à la table { $table_id } (hôte { $host }, joueurs { $players }, humains { $humans })
virtual-bots-guided-table-stale = table { $table_id } manquante sur le serveur
virtual-bots-guided-table-unassigned = aucune table n'est actuellement suivie
virtual-bots-guided-next-change = prochain changement dans { $ticks } ticks
virtual-bots-guided-no-schedule = aucune fenêtre de planification
virtual-bots-guided-warning = ⚠ sous-rempli
virtual-bots-guided-line = { $table } : jeu { $game }, priorité { $priority }, bots { $assigned } (min { $min_bots }, max { $max_bots }), en attente { $waiting }, indisponible { $unavailable }, statut { $status }, profil { $profile }, groupes { $groups }. { $table_state }. { $next_change } { $warning_text }
virtual-bots-groups-header = Groupes de bots : { $count } étiquette(s), { $bots } bots configurés.
virtual-bots-groups-empty = Aucun groupe de bots n'est défini.
virtual-bots-groups-line = { $group } : profil { $profile }, bots { $total } (en ligne { $online }, en attente { $waiting }, en jeu { $in_game }, hors ligne { $offline }), règles { $rules }.
virtual-bots-groups-no-rules = aucune
virtual-bots-no-profile = par défaut
virtual-bots-profile-inherit-default = hérite du profil par défaut
virtual-bots-profiles-header = Profils : { $count } définis (par défaut : { $default_profile }).
virtual-bots-profiles-empty = Aucun profil n'est défini.
virtual-bots-profiles-line = { $profile } ({ $bot_count } bots) remplacements : { $overrides }.
virtual-bots-profiles-no-overrides = hérite de la configuration de base

localization-in-progress-try-again = La localisation est en cours. Veuillez réessayer dans une minute.
