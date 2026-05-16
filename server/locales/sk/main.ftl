# Main UI messages for PlayPalace

# Game categories
category-card-games = Kartové hry
category-dice-games = Kockové hry
category-rb-play-center = RB Play centrum
category-poker = Poker
category-uncategorized = Bez kategórie

# Menu titles
main-menu-title = Hlavné menu
play-menu-title = Hraj
categories-menu-title = Kategórie hier
tables-menu-title = Dostupné stoly

# Menu items
play = Hraj
view-active-tables = Zobraziť aktívne stoly
options = Nastavenia
logout = Odhlásenie
back = Späť
go-back = Ísť späť
context-menu = Kontextové menu.
no-actions-available = Žiadne akcie k dispozícii.
create-table = Vytvoriť nový stôl
join-as-player = Pripojiť sa ako hráč
join-as-spectator = Pripojiť sa ako divák
leave-table = Opustiť stôl
start-game = Začať hru
add-bot = Pridať bota
remove-bot = Odstrániť bota
actions-menu = Menu akcií
save-table = Uložiť stôl
whose-turn = Čí je ťah
whos-at-table = Kto je pri stole
check-scores = Skontrolovať skóre
check-scores-detailed = Podrobné skóre
check-game-options = Skontrolovať nastavenia hry
no-game-options = Žiadne nastavenia hry.

# Turn messages
game-player-skipped = { $player } je preskočený.

# Table messages
table-created = { $host } vytvoril nový stôl { $game }.
table-joined = { $player } sa pripojil k stolu.
table-left = { $player } opustil stôl.
new-host = { $player } je teraz hostiteľ.
waiting-for-players = Čakanie na hráčov. {$min} min, { $max } max.
game-starting = Hra začína!
table-listing = Stôl od { $host } ({ $count } používateľov)
table-listing-one = Stôl od { $host } ({ $count } používateľ)
table-listing-with = Stôl od { $host } ({ $count } používateľov) s { $members }
table-listing-game = { $game }: stôl od { $host } ({ $count } používateľov)
table-listing-game-one = { $game }: stôl od { $host } ({ $count } používateľ)
table-listing-game-with = { $game }: stôl od { $host } ({ $count } používateľov) s { $members }
table-not-exists = Stôl už neexistuje.
table-full = Stôl je plný.
player-replaced-by-bot = { $player } odišiel a bol nahradený botom.
player-took-over = { $player } prevzal od bota.
spectator-joined = Pripojil si sa k stolu od { $host } ako divák.

# Spectator mode
spectate = Sleduj
now-playing = { $player } teraz hrá.
now-spectating = { $player } teraz sleduje.
spectator-left = { $player } prestal sledovať.

# General
welcome = Vitajte v PlayPalace!
goodbye = Dovidenia!

# User presence announcements
user-online = { $player } prišiel online.
user-offline = { $player } odišiel offline.
user-is-admin = { $player } je administrátor PlayPalace.
user-is-server-owner = { $player } je majiteľ servera PlayPalace.
online-users-none = Žiadni používatelia online.
online-users-one = 1 používateľ: { $users }
online-users-many = { $count } používateľov: { $users }
online-user-not-in-game = Nie je v hre
online-user-waiting-approval = Čaká na schválenie

# Options
language = Jazyk
language-option = Jazyk: { $language }
language-changed = Jazyk nastavený na { $language }.

# Boolean option states
option-on = Zapnuté
option-off = Vypnuté

# Sound options
turn-sound-option = Zvuk ťahu: { $status }

# Dice options
clear-kept-option = Vymazať ponechané kocky pri hode: { $status }
dice-keeping-style-option = Štýl ponechania kociek: { $style }
dice-keeping-style-changed = Štýl ponechania kociek nastavený na { $style }.
dice-keeping-style-indexes = Indexy kociek
dice-keeping-style-values = Hodnoty kociek

# Bot names
cancel = Zrušiť
no-bot-names-available = Žiadne mená botov k dispozícii.
select-bot-name = Vyberte meno pre bota
enter-bot-name = Zadajte meno bota
no-options-available = Žiadne možnosti k dispozícii.
no-scores-available = Žiadne skóre k dispozícii.

# Duration estimation
estimate-duration = Odhadnúť trvanie
estimate-computing = Vypočítavam odhadované trvanie hry...
estimate-result = Priemer bota: { $bot_time } (± { $std_dev }). { $outlier_info }Odhadovaný ľudský čas: { $human_time }.
estimate-error = Nepodarilo sa odhadnúť trvanie.
estimate-already-running = Odhad trvania už prebieha.

# Save/Restore
saved-tables = Uložené stoly
no-saved-tables = Nemáte žiadne uložené stoly.
no-active-tables = Žiadne aktívne stoly.
restore-table = Obnoviť
delete-saved-table = Vymazať
saved-table-deleted = Uložený stôl vymazaný.
missing-players = Nemožno obnoviť: títo hráči nie sú k dispozícii: { $players }
table-restored = Stôl obnovený! Všetci hráči boli presunutí.
table-saved-destroying = Stôl uložený! Návrat do hlavného menu.
game-type-not-found = Typ hry už neexistuje.

# Action disabled reasons
action-not-your-turn = Nie je tvoj ťah.
action-not-playing = Hra ešte nezačala.
action-spectator = Diváci to nemôžu urobiť.
action-not-host = Len hostiteľ to môže urobiť.
action-game-in-progress = Nie je možné to urobiť, kým hra prebieha.
action-need-more-players = Na začatie je potrebných viac hráčov.
action-table-full = Stôl je plný.
action-no-bots = Žiadni botovia na odstránenie.
action-bots-cannot = Botovia to nemôžu urobiť.
action-no-scores = Zatiaľ nie sú k dispozícii žiadne skóre.

# Dice actions
dice-not-rolled = Ešte si nehodil.
dice-locked = Táto kocka je zamknutá.
dice-no-dice = Žiadne kocky k dispozícii.

# Game actions
game-turn-start = Ťah hráča { $player }.
game-no-turn = Momentálne nie je nikto na ťahu.
table-no-players = Žiadni hráči.
table-players-one = { $count } hráč: { $players }.
table-players-many = { $count } hráčov: { $players }.
table-spectators = Diváci: { $spectators }.
game-leave = Opustiť
game-over = Koniec hry
game-final-scores = Konečné skóre
game-points = { $count } { $count ->
    [one] bod
    [few] body
    [many] bodov
   *[other] bodov
}
play = Hraj

# Leaderboards
leaderboards = Rebríčky
leaderboards-menu-title = Rebríčky
leaderboards-select-game = Vyberte hru pre zobrazenie rebríčka
leaderboard-no-data = Zatiaľ žiadne údaje rebríčka pre túto hru.

# Leaderboard types
leaderboard-type-wins = Lídri podľa víťazstiev
leaderboard-type-rating = Hodnotenie zručnosti
leaderboard-type-total-score = Celkové skóre
leaderboard-type-high-score = Najvyššie skóre
leaderboard-type-games-played = Odohraté hry
leaderboard-type-avg-points-per-turn = Priemerné body na ťah
leaderboard-type-best-single-turn = Najlepší jednotlivý ťah
leaderboard-type-score-per-round = Skóre na kolo

# Leaderboard headers
leaderboard-wins-header = { $game } - Lídri podľa víťazstiev
leaderboard-total-score-header = { $game } - Celkové skóre
leaderboard-high-score-header = { $game } - Najvyššie skóre
leaderboard-games-played-header = { $game } - Odohraté hry
leaderboard-rating-header = { $game } - Hodnotenia zručnosti
leaderboard-avg-points-header = { $game } - Priemerné body na ťah
leaderboard-best-turn-header = { $game } - Najlepší jednotlivý ťah
leaderboard-score-per-round-header = { $game } - Skóre na kolo

# Leaderboard entries
leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] víťazstvo
    [few] víťazstvá
    [many] víťazstiev
   *[other] víťazstiev
} { $losses } { $losses ->
    [one] prehra
    [few] prehry
    [many] prehier
   *[other] prehier
}, { $percentage }% úspešnosť
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } priemer
leaderboard-games-entry = { $rank }. { $player }: { $value } hier

# Player stats
leaderboard-player-stats = Tvoje štatistiky: { $wins } víťazstiev, { $losses } prehier ({ $percentage }% úspešnosť)
leaderboard-no-player-stats = Ešte si nehrali túto hru.

# Skill rating leaderboard
leaderboard-no-ratings = Zatiaľ žiadne údaje hodnotenia pre túto hru.
leaderboard-rating-entry = { $rank }. { $player }: { $rating } hodnotenie ({ $mu } ± { $sigma })
leaderboard-player-rating = Tvoje hodnotenie: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = Ešte nemáte hodnotenie pre túto hru.

# My Stats menu
my-stats = Moje štatistiky
my-stats-select-game = Vyberte hru pre zobrazenie svojich štatistík
my-stats-no-data = Ešte si nehrali túto hru.
my-stats-no-games = Ešte si nehrali žiadnu hru.
my-stats-header = { $game } - Tvoje štatistiky
my-stats-wins = Víťazstvá: { $value }
my-stats-losses = Prehry: { $value }
my-stats-winrate = Úspešnosť: { $value }%
my-stats-games-played = Odohraté hry: { $value }
my-stats-total-score = Celkové skóre: { $value }
my-stats-high-score = Najvyššie skóre: { $value }
my-stats-rating = Hodnotenie zručnosti: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = Zatiaľ žiadne hodnotenie zručnosti
my-stats-avg-per-turn = Priemerné body na ťah: { $value }
my-stats-best-turn = Najlepší jednotlivý ťah: { $value }

# Prediction system
predict-outcomes = Predpovedať výsledky
predict-header = Predpovedané výsledky (podľa hodnotenia zručnosti)
predict-entry = { $rank }. { $player } (hodnotenie: { $rating })
predict-entry-2p = { $rank }. { $player } (hodnotenie: { $rating }, { $probability }% šanca na víťazstvo)
predict-unavailable = Predpovede hodnotení nie sú k dispozícii.
predict-need-players = Na predpovede sú potrební aspoň 2 ľudskí hráči.
action-need-more-humans = Potrebných je viac ľudských hráčov.
confirm-leave-game = Ste si istí, že chcete opustiť stôl?
confirm-yes = Áno
confirm-no = Nie

# Administration
administration = Administrácia
admin-menu-title = Administrácia

# Account approval
account-approval = Schválenie účtu
account-approval-menu-title = Schválenie účtu
no-pending-accounts = Žiadne čakajúce účty.
approve-account = Schváliť
decline-account = Odmietnuť
account-approved = Účet hráča { $player } bol schválený.
account-declined = Účet hráča { $player } bol odmietnutý a vymazaný.

# Waiting for approval (shown to unapproved users)
waiting-for-approval = Váš účet čaká na schválenie administrátorom.
account-approved-welcome = Váš účet bol schválený! Vitajte v PlayPalace!
account-declined-goodbye = Vaša žiadosť o účet bola odmietnutá.
    Dôvod:
account-banned = Váš účet je zakázaný a nie je možné k nemu pristupovať.

# Login errors
incorrect-username = Zadané používateľské meno neexistuje.
incorrect-password = Zadané heslo je nesprávne.
already-logged-in = Tento účet je už prihlásený.

# Overenie prihlasovacích údajov
credential-username-length = Používateľské meno musí mať od { $min } do { $max } znakov.
credential-password-length = Heslo musí mať od { $min } do { $max } znakov.

# Obmedzenie počtu pokusov
rate-limit-login-ip = Príliš veľa pokusov o prihlásenie z tejto adresy. Počkajte prosím a skúste znova.
rate-limit-login-user = Príliš veľa neúspešných pokusov o prihlásenie pre toto používateľské meno. Počkajte prosím a skúste znova.
rate-limit-registration = Príliš veľa pokusov o registráciu z tejto adresy. Počkajte prosím a skúste znova.
rate-limit-refresh = Príliš veľa pokusov o obnovenie z tejto adresy. Počkajte prosím a skúste znova.

# Chyby relácie a autentifikácie
account-not-found = Účet nebol nájdený.
session-expired = Relácia vypršala. Prihláste sa prosím znova.
session-token-mismatch = Token relácie nezodpovedá používateľskému menu.
refresh-token-expired = Token obnovy vypršal. Prihláste sa prosím znova.
refresh-token-mismatch = Token obnovy nezodpovedá používateľskému menu.

# Registrácia
registration-success = Registrácia bola úspešná! Váš účet čaká na schválenie.
registration-username-taken = Toto používateľské meno je už obsadené. Zvoľte si prosím iné používateľské meno.

# Predvolené nastavenie
pref-invalid-value = Neplatný výber, používa sa predvolená hodnota.

# Decline reason
decline-reason-prompt = Zadajte dôvod odmietnutia (alebo stlačte Escape pre zrušenie):
account-action-empty-reason = Nebol zadaný žiadny dôvod.

# Admin notifications for account requests
account-request = žiadosť o účet
account-action = vykonaná akcia účtu

# Admin promotion/demotion
promote-admin = Povýšiť administrátora
demote-admin = Degradovať administrátora
promote-admin-menu-title = Povýšiť administrátora
demote-admin-menu-title = Degradovať administrátora
no-users-to-promote = Žiadni používatelia k dispozícii na povýšenie.
no-admins-to-demote = Žiadni administrátori k dispozícii na degradovanie.
confirm-promote = Ste si istí, že chcete povýšiť { $player } na administrátora?
confirm-demote = Ste si istí, že chcete degradovať { $player } z administrátora?
broadcast-to-all = Oznámiť všetkým používateľom
broadcast-to-admins = Oznámiť len administrátorom
broadcast-to-nobody = Ticho (bez oznámenia)
promote-announcement = { $player } bol povýšený na administrátora!
promote-announcement-you = Boli ste povýšený na administrátora!
demote-announcement = { $player } bol degradovaný z administrátora.
demote-announcement-you = Boli ste degradovaný z administrátora.
not-admin-anymore = Už nie ste administrátor a nemôžete vykonať túto akciu.
not-server-owner = Túto akciu môže vykonať len majiteľ servera.

# Server ownership transfer
transfer-ownership = Previesť vlastníctvo
transfer-ownership-menu-title = Previesť vlastníctvo
no-admins-for-transfer = Žiadni administrátori k dispozícii na prevedenie vlastníctva.
confirm-transfer-ownership = Ste si istí, že chcete previesť vlastníctvo servera na { $player }? Budete degradovaný na administrátora.
transfer-ownership-announcement = { $player } je teraz majiteľ servera Play Palace!
transfer-ownership-announcement-you = Teraz ste majiteľ servera Play Palace!

# User banning
ban-user = Zakázať používateľa
unban-user = Odblokovať používateľa
no-users-to-ban = Žiadni používatelia k dispozícii na zakázanie.
no-users-to-unban = Žiadni zakázaní používatelia na odblokovanie.
confirm-ban = Ste si istí, že chcete zakázať { $player }?
confirm-unban = Ste si istí, že chcete odblokovať { $player }?
ban-reason-prompt = Zadajte dôvod zákazu (voliteľné):
unban-reason-prompt = Zadajte dôvod odblokovania (voliteľné):
user-banned = { $player } bol zakázaný.
user-unbanned = { $player } bol odblokovaný.
you-have-been-banned = Boli ste zakázaný na tomto serveri.
    Dôvod:
you-have-been-unbanned = Boli ste odblokovaný na tomto serveri.
    Dôvod:
ban-no-reason = Nebol zadaný žiadny dôvod.

# Virtual bots (server owner only)
virtual-bots = Virtuálni botovia
virtual-bots-fill = Naplniť server
virtual-bots-clear = Vymazať všetkých botov
virtual-bots-status = Stav
virtual-bots-clear-confirm = Ste si istí, že chcete vymazať všetkých virtuálnych botov? Toto zničí aj všetky stoly, na ktorých sa nachádzajú.
virtual-bots-not-available = Virtuálni botovia nie sú k dispozícii.
virtual-bots-filled = Pridaných { $added } virtuálnych botov. { $online } je teraz online.
virtual-bots-already-filled = Všetci virtuálni botovia z konfigurácie sú už aktívni.
virtual-bots-cleared = Vymazaných { $bots } virtuálnych botov a zničených { $tables } { $tables ->
    [one] stôl
    [few] stoly
    [many] stolov
   *[other] stolov
}.
virtual-bot-table-closed = Stôl zatvorený administrátorom.
virtual-bots-none-to-clear = Žiadni virtuálni botovia na vymazanie.
virtual-bots-status-report = Virtuálni botovia: { $total } celkom, { $online } online, { $offline } offline, { $in_game } v hre.
virtual-bots-guided-overview = Vedené stoly
virtual-bots-groups-overview = Skupiny botov
virtual-bots-profiles-overview = Profily
virtual-bots-guided-header = Vedené stoly: { $count } pravidlo/pravidiel. Alokácia: { $allocation }, záložné: { $fallback }, predvolený profil: { $default_profile }.
virtual-bots-guided-empty = Žiadne pravidlá vedených stolov nie sú nakonfigurované.
virtual-bots-guided-status-active = aktívny
virtual-bots-guided-status-inactive = neaktívny
virtual-bots-guided-table-linked = prepojený so stolom { $table_id } (hostiteľ { $host }, hráči { $players }, ľudia { $humans })
virtual-bots-guided-table-stale = stôl { $table_id } chýba na serveri
virtual-bots-guided-table-unassigned = momentálne nie je sledovaný žiadny stôl
virtual-bots-guided-next-change = ďalšia zmena za { $ticks } tiknutí
virtual-bots-guided-no-schedule = žiadne plánovacie okno
virtual-bots-guided-warning = ⚠ nedostatočne naplnený
virtual-bots-guided-line = { $table }: hra { $game }, priorita { $priority }, botovia { $assigned } (min { $min_bots }, max { $max_bots }), čakajúci { $waiting }, nedostupní { $unavailable }, stav { $status }, profil { $profile }, skupiny { $groups }. { $table_state }. { $next_change } { $warning_text }
virtual-bots-groups-header = Skupiny botov: { $count } značka/značiek, { $bots } nakonfigurovaných botov.
virtual-bots-groups-empty = Žiadne skupiny botov nie sú definované.
virtual-bots-groups-line = { $group }: profil { $profile }, botovia { $total } (online { $online }, čakajúci { $waiting }, v hre { $in_game }, offline { $offline }), pravidlá { $rules }.
virtual-bots-groups-no-rules = žiadne
virtual-bots-no-profile = predvolený
virtual-bots-profile-inherit-default = dedí predvolený profil
virtual-bots-profiles-header = Profily: { $count } definovaných (predvolený: { $default_profile }).
virtual-bots-profiles-empty = Žiadne profily nie sú definované.
virtual-bots-profiles-line = { $profile } ({ $bot_count } botov) prepíše: { $overrides }.
virtual-bots-profiles-no-overrides = dedí základnú konfiguráciu

localization-in-progress-try-again = Lokalizácia sa stále načítava. Skúste to prosím znova o minútu.
