# Main UI messages for PlayPalace

# Game categories
category-card-games = Kaartspellen
category-dice-games = Dobbelsteenspellen
category-rb-play-center = RB Play Center
category-poker = Poker
category-uncategorized = Niet gecategoriseerd

# Menu titles
main-menu-title = Hoofdmenu
play-menu-title = Speel
categories-menu-title = Spel Categorieën
tables-menu-title = Beschikbare Tafels

# Menu items
play = Speel
view-active-tables = Bekijk actieve tafels
options = Opties
logout = Uitloggen
back = Terug
go-back = Ga terug
context-menu = Contextmenu.
no-actions-available = Geen acties beschikbaar.
create-table = Maak een nieuwe tafel
join-as-player = Sluit aan als speler
join-as-spectator = Sluit aan als toeschouwer
leave-table = Verlaat tafel
start-game = Start spel
add-bot = Bot toevoegen
remove-bot = Bot verwijderen
actions-menu = Acties menu
save-table = Tafel opslaan
whose-turn = Wie is aan de beurt
whos-at-table = Wie is er aan tafel
check-scores = Bekijk scores
check-scores-detailed = Gedetailleerde scores
check-game-options = Spelopties bekijken
no-game-options = Geen spelopties beschikbaar.

# Turn messages
game-player-skipped = { $player } wordt overgeslagen.

# Table messages
table-created = { $host } maakte een nieuwe { $game } tafel.
table-joined = { $player } sloot zich aan bij de tafel.
table-left = { $player } verliet de tafel.
new-host = { $player } is nu de host.
waiting-for-players = Wachten op spelers. {$min} min, { $max } max.
game-starting = Spel start!
table-listing = { $host }'s tafel ({ $count } gebruikers)
table-listing-one = { $host }'s tafel ({ $count } gebruiker)
table-listing-with = { $host }'s tafel ({ $count } gebruikers) met { $members }
table-listing-game = { $game }: { $host }'s tafel ({ $count } gebruikers)
table-listing-game-one = { $game }: { $host }'s tafel ({ $count } gebruiker)
table-listing-game-with = { $game }: { $host }'s tafel ({ $count } gebruikers) met { $members }
table-not-exists = Tafel bestaat niet meer.
table-full = Tafel is vol.
player-replaced-by-bot = { $player } vertrok en werd vervangen door een bot.
player-took-over = { $player } nam het over van de bot.
spectator-joined = Aangesloten bij { $host }'s tafel als toeschouwer.

# Spectator mode
spectate = Toeschouw
now-playing = { $player } speelt nu.
now-spectating = { $player } kijkt nu toe.
spectator-left = { $player } stopte met toekijken.

# General
welcome = Welkom bij PlayPalace!
goodbye = Tot ziens!

# User presence announcements
user-online = { $player } kwam online.
user-offline = { $player } ging offline.
user-is-admin = { $player } is een beheerder van PlayPalace.
user-is-server-owner = { $player } is de servereigenaar van PlayPalace.
online-users-none = Geen gebruikers online.
online-users-one = 1 gebruiker: { $users }
online-users-many = { $count } gebruikers: { $users }
online-user-not-in-game = Niet in spel
online-user-waiting-approval = Wacht op goedkeuring

# Options
language = Taal
language-option = Taal: { $language }
language-changed = Taal ingesteld op { $language }.

# Boolean option states
option-on = Aan
option-off = Uit

# Sound options
turn-sound-option = Beurtgeluid: { $status }

# Dice options
clear-kept-option = Wis bewaarde dobbelstenen bij gooien: { $status }
dice-keeping-style-option = Dobbelstenen bewaardstijl: { $style }
dice-keeping-style-changed = Dobbelstenen bewaardstijl ingesteld op { $style }.
dice-keeping-style-indexes = Dobbelstenen indices
dice-keeping-style-values = Dobbelstenen waarden

# Bot names
cancel = Annuleer
no-bot-names-available = Geen botnamen beschikbaar.
select-bot-name = Selecteer een naam voor de bot
enter-bot-name = Voer botnaam in
no-options-available = Geen opties beschikbaar.
no-scores-available = Geen scores beschikbaar.

# Duration estimation
estimate-duration = Schat duur
estimate-computing = Geschatte spelduur berekenen...
estimate-result = Bot gemiddelde: { $bot_time } (± { $std_dev }). { $outlier_info }Geschatte menselijke tijd: { $human_time }.
estimate-error = Kon duur niet schatten.
estimate-already-running = Duurschatting al bezig.

# Save/Restore
saved-tables = Opgeslagen Tafels
no-saved-tables = Je hebt geen opgeslagen tafels.
no-active-tables = Geen actieve tafels.
restore-table = Herstel
delete-saved-table = Verwijder
saved-table-deleted = Opgeslagen tafel verwijderd.
missing-players = Kan niet herstellen: deze spelers zijn niet beschikbaar: { $players }
table-restored = Tafel hersteld! Alle spelers zijn overgedragen.
table-saved-destroying = Tafel opgeslagen! Terugkeren naar hoofdmenu.
game-type-not-found = Speltype bestaat niet meer.

# Action disabled reasons
action-not-your-turn = Het is niet jouw beurt.
action-not-playing = Het spel is nog niet gestart.
action-spectator = Toeschouwers kunnen dit niet doen.
action-not-host = Alleen de host kan dit doen.
action-game-in-progress = Kan dit niet doen terwijl het spel bezig is.
action-need-more-players = Meer spelers nodig om te starten.
action-table-full = De tafel is vol.
action-no-bots = Er zijn geen bots om te verwijderen.
action-bots-cannot = Bots kunnen dit niet doen.
action-no-scores = Nog geen scores beschikbaar.

# Dice actions
dice-not-rolled = Je hebt nog niet gegooid.
dice-locked = Deze dobbelsteen is vergrendeld.
dice-no-dice = Geen dobbelstenen beschikbaar.

# Game actions
game-turn-start = { $player } is aan de beurt.
game-no-turn = Niemand is nu aan de beurt.
table-no-players = Geen spelers.
table-players-one = { $count } speler: { $players }.
table-players-many = { $count } spelers: { $players }.
table-spectators = Toeschouwers: { $spectators }.
game-leave = Verlaat
game-over = Spel Voorbij
game-final-scores = Eindscores
game-points = { $count } { $count ->
    [one] punt
   *[other] punten
}
play = Speel

# Leaderboards
leaderboards = Klassementen
leaderboards-menu-title = Klassementen
leaderboards-select-game = Selecteer een spel om het klassement te bekijken
leaderboard-no-data = Nog geen klassementsgegevens voor dit spel.

# Leaderboard types
leaderboard-type-wins = Winleiders
leaderboard-type-rating = Vaardigheidsbeoordeling
leaderboard-type-total-score = Totale Score
leaderboard-type-high-score = Hoge Score
leaderboard-type-games-played = Spellen Gespeeld
leaderboard-type-avg-points-per-turn = Gem Punten Per Beurt
leaderboard-type-best-single-turn = Beste Enkele Beurt
leaderboard-type-score-per-round = Score Per Ronde

# Leaderboard headers
leaderboard-wins-header = { $game } - Winleiders
leaderboard-total-score-header = { $game } - Totale Score
leaderboard-high-score-header = { $game } - Hoge Score
leaderboard-games-played-header = { $game } - Spellen Gespeeld
leaderboard-rating-header = { $game } - Vaardigheidsbeoordelingen
leaderboard-avg-points-header = { $game } - Gem Punten Per Beurt
leaderboard-best-turn-header = { $game } - Beste Enkele Beurt
leaderboard-score-per-round-header = { $game } - Score Per Ronde

# Leaderboard entries
leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] overwinning
   *[other] overwinningen
} { $losses } { $losses ->
    [one] verlies
   *[other] verliezen
}, { $percentage }% winpercentage
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } gem
leaderboard-games-entry = { $rank }. { $player }: { $value } spellen

# Player stats
leaderboard-player-stats = Jouw statistieken: { $wins } overwinningen, { $losses } verliezen ({ $percentage }% winpercentage)
leaderboard-no-player-stats = Je hebt dit spel nog niet gespeeld.

# Skill rating leaderboard
leaderboard-no-ratings = Nog geen beoordelingsgegevens voor dit spel.
leaderboard-rating-entry = { $rank }. { $player }: { $rating } beoordeling ({ $mu } ± { $sigma })
leaderboard-player-rating = Jouw beoordeling: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = Je hebt nog geen beoordeling voor dit spel.

# My Stats menu
my-stats = Mijn Statistieken
my-stats-select-game = Selecteer een spel om je statistieken te bekijken
my-stats-no-data = Je hebt dit spel nog niet gespeeld.
my-stats-no-games = Je hebt nog geen spellen gespeeld.
my-stats-header = { $game } - Jouw Statistieken
my-stats-wins = Overwinningen: { $value }
my-stats-losses = Verliezen: { $value }
my-stats-winrate = Winpercentage: { $value }%
my-stats-games-played = Spellen gespeeld: { $value }
my-stats-total-score = Totale score: { $value }
my-stats-high-score = Hoge score: { $value }
my-stats-rating = Vaardigheidsbeoordeling: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = Nog geen vaardigheidsbeoordeling
my-stats-avg-per-turn = Gem punten per beurt: { $value }
my-stats-best-turn = Beste enkele beurt: { $value }

# Prediction system
predict-outcomes = Voorspel uitkomsten
predict-header = Voorspelde Uitkomsten (op vaardigheidsbeoordeling)
predict-entry = { $rank }. { $player } (beoordeling: { $rating })
predict-entry-2p = { $rank }. { $player } (beoordeling: { $rating }, { $probability }% winkans)
predict-unavailable = Beoordelingsvoorspellingen zijn niet beschikbaar.
predict-need-players = Minstens 2 menselijke spelers nodig voor voorspellingen.
action-need-more-humans = Meer menselijke spelers nodig.
confirm-leave-game = Weet je zeker dat je de tafel wilt verlaten?
confirm-yes = Ja
confirm-no = Nee

# Administration
administration = Beheer
admin-menu-title = Beheer

# Account approval
account-approval = Accountgoedkeuring
account-approval-menu-title = Accountgoedkeuring
no-pending-accounts = Geen accounts in afwachting.
approve-account = Goedkeuren
decline-account = Afwijzen
account-approved = { $player }'s account is goedgekeurd.
account-declined = { $player }'s account is afgewezen en verwijderd.

# Waiting for approval (shown to unapproved users)
waiting-for-approval = Je account wacht op goedkeuring door een beheerder.
account-approved-welcome = Je account is goedgekeurd! Welkom bij PlayPalace!
account-declined-goodbye = Je accountaanvraag is afgewezen.
    Reden:
account-banned = Je account is verbannen en kan niet worden geopend.

# Login errors
incorrect-username = De gebruikersnaam die je invoerde bestaat niet.
incorrect-password = Het wachtwoord dat je invoerde is onjuist.
already-logged-in = Dit account is al ingelogd.

# Validatie van inloggegevens
credential-username-length = Gebruikersnaam moet tussen { $min } en { $max } tekens zijn.
credential-password-length = Wachtwoord moet tussen { $min } en { $max } tekens zijn.

# Snelheidsbeperking
rate-limit-login-ip = Te veel inlogpogingen van dit adres. Wacht even en probeer het opnieuw.
rate-limit-login-user = Te veel mislukte inlogpogingen voor deze gebruikersnaam. Wacht even en probeer het opnieuw.
rate-limit-registration = Te veel registratiepogingen van dit adres. Wacht even en probeer het opnieuw.
rate-limit-refresh = Te veel vernieuwingspogingen van dit adres. Wacht even en probeer het opnieuw.

# Sessie- en authenticatiefouten
account-not-found = Account niet gevonden.
session-expired = Sessie verlopen. Log opnieuw in.
session-token-mismatch = Sessietoken komt niet overeen met de gebruikersnaam.
refresh-token-expired = Vernieuwingstoken verlopen. Log opnieuw in.
refresh-token-mismatch = Vernieuwingstoken komt niet overeen met de gebruikersnaam.

# Registratie
registration-success = Registratie geslaagd! Je account wacht op goedkeuring.
registration-username-taken = Gebruikersnaam al in gebruik. Kies een andere gebruikersnaam.

# Voorkeur standaardwaarde
pref-invalid-value = Ongeldige selectie, standaardwaarde wordt gebruikt.

# Decline reason
decline-reason-prompt = Voer een reden in om af te wijzen (of druk op Escape om te annuleren):
account-action-empty-reason = Geen reden gegeven.

# Admin notifications for account requests
account-request = accountaanvraag
account-action = accountactie ondernomen

# Admin promotion/demotion
promote-admin = Promoveer Beheerder
demote-admin = Degradeer Beheerder
promote-admin-menu-title = Promoveer Beheerder
demote-admin-menu-title = Degradeer Beheerder
no-users-to-promote = Geen gebruikers beschikbaar om te promoveren.
no-admins-to-demote = Geen beheerders beschikbaar om te degraderen.
confirm-promote = Weet je zeker dat je { $player } wilt promoveren tot beheerder?
confirm-demote = Weet je zeker dat je { $player } wilt degraderen van beheerder?
broadcast-to-all = Kondig aan aan alle gebruikers
broadcast-to-admins = Kondig alleen aan aan beheerders
broadcast-to-nobody = Stil (geen aankondiging)
promote-announcement = { $player } is gepromoveerd tot beheerder!
promote-announcement-you = Je bent gepromoveerd tot beheerder!
demote-announcement = { $player } is gedegradeerd van beheerder.
demote-announcement-you = Je bent gedegradeerd van beheerder.
not-admin-anymore = Je bent geen beheerder meer en kunt deze actie niet uitvoeren.
not-server-owner = Alleen de servereigenaar kan deze actie uitvoeren.

# Server ownership transfer
transfer-ownership = Draag Eigendom Over
transfer-ownership-menu-title = Draag Eigendom Over
no-admins-for-transfer = Geen beheerders beschikbaar om eigendom aan over te dragen.
confirm-transfer-ownership = Weet je zeker dat je servereigendom wilt overdragen aan { $player }? Je wordt gedegradeerd tot beheerder.
transfer-ownership-announcement = { $player } is nu de Play Palace servereigenaar!
transfer-ownership-announcement-you = Je bent nu de Play Palace servereigenaar!

# User banning
ban-user = Verban Gebruiker
unban-user = Ontban Gebruiker
no-users-to-ban = Geen gebruikers beschikbaar om te verbannen.
no-users-to-unban = Geen verbannen gebruikers om te ontbannen.
confirm-ban = Weet je zeker dat je { $player } wilt verbannen?
confirm-unban = Weet je zeker dat je { $player } wilt ontbannen?
ban-reason-prompt = Voer een reden in voor de ban (optioneel):
unban-reason-prompt = Voer een reden in voor de ontbanning (optioneel):
user-banned = { $player } is verbannen.
user-unbanned = { $player } is ontbannen.
you-have-been-banned = Je bent verbannen van deze server.
    Reden:
you-have-been-unbanned = Je bent ontbannen van deze server.
    Reden:
ban-no-reason = Geen reden gegeven.

# Virtual bots (server owner only)
virtual-bots = Virtuele Bots
virtual-bots-fill = Vul Server
virtual-bots-clear = Wis Alle Bots
virtual-bots-status = Status
virtual-bots-clear-confirm = Weet je zeker dat je alle virtuele bots wilt wissen? Dit zal ook alle tafels vernietigen waar ze aan zitten.
virtual-bots-not-available = Virtuele bots zijn niet beschikbaar.
virtual-bots-filled = { $added } virtuele bots toegevoegd. { $online } zijn nu online.
virtual-bots-already-filled = Alle virtuele bots uit de configuratie zijn al actief.
virtual-bots-cleared = { $bots } virtuele bots gewist en { $tables } { $tables ->
    [one] tafel
   *[other] tafels
} vernietigd.
virtual-bot-table-closed = Tafel gesloten door beheerder.
virtual-bots-none-to-clear = Geen virtuele bots om te wissen.
virtual-bots-status-report = Virtuele Bots: { $total } totaal, { $online } online, { $offline } offline, { $in_game } in spel.
virtual-bots-guided-overview = Begeleide Tafels
virtual-bots-groups-overview = Bot Groepen
virtual-bots-profiles-overview = Profielen
virtual-bots-guided-header = Begeleide tafels: { $count } regel(s). Allocatie: { $allocation }, fallback: { $fallback }, standaard profiel: { $default_profile }.
virtual-bots-guided-empty = Geen begeleide tafelregels zijn geconfigureerd.
virtual-bots-guided-status-active = actief
virtual-bots-guided-status-inactive = inactief
virtual-bots-guided-table-linked = gekoppeld aan tafel { $table_id } (host { $host }, spelers { $players }, mensen { $humans })
virtual-bots-guided-table-stale = tafel { $table_id } ontbreekt op server
virtual-bots-guided-table-unassigned = geen tafel wordt momenteel bijgehouden
virtual-bots-guided-next-change = volgende wijziging over { $ticks } ticks
virtual-bots-guided-no-schedule = geen planningsvenster
virtual-bots-guided-warning = ⚠ ondergevuld
virtual-bots-guided-line = { $table }: spel { $game }, prioriteit { $priority }, bots { $assigned } (min { $min_bots }, max { $max_bots }), wachtend { $waiting }, niet beschikbaar { $unavailable }, status { $status }, profiel { $profile }, groepen { $groups }. { $table_state }. { $next_change } { $warning_text }
virtual-bots-groups-header = Bot groepen: { $count } tag(s), { $bots } geconfigureerde bots.
virtual-bots-groups-empty = Geen bot groepen zijn gedefinieerd.
virtual-bots-groups-line = { $group }: profiel { $profile }, bots { $total } (online { $online }, wachtend { $waiting }, in-spel { $in_game }, offline { $offline }), regels { $rules }.
virtual-bots-groups-no-rules = geen
virtual-bots-no-profile = standaard
virtual-bots-profile-inherit-default = erft standaard profiel
virtual-bots-profiles-header = Profielen: { $count } gedefinieerd (standaard: { $default_profile }).
virtual-bots-profiles-empty = Geen profielen zijn gedefinieerd.
virtual-bots-profiles-line = { $profile } ({ $bot_count } bots) overschrijvingen: { $overrides }.
virtual-bots-profiles-no-overrides = erft basisconfiguratie

localization-in-progress-try-again = Lokalisatie is bezig. Probeer het over een minuut opnieuw.
