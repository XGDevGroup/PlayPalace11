# Main UI messages for PlayPalace

# Game categories
category-card-games = Kartne igre
category-dice-games = Igre s kockami
category-rb-play-center = RB Play center
category-poker = Poker
category-uncategorized = Brez kategorije

# Menu titles
main-menu-title = Glavni meni
play-menu-title = Igraj
categories-menu-title = Kategorije iger
tables-menu-title = Razpoložljive mize

# Menu items
play = Igraj
view-active-tables = Prikaži aktivne mize
options = Nastavitve
logout = Odjava
back = Nazaj
go-back = Pojdi nazaj
context-menu = Kontekstni meni.
no-actions-available = Ni razpoložljivih dejanj.
create-table = Ustvari novo mizo
join-as-player = Pridruži se kot igralec
join-as-spectator = Pridruži se kot gledalec
leave-table = Zapusti mizo
start-game = Začni igro
add-bot = Dodaj bota
remove-bot = Odstrani bota
actions-menu = Meni dejanj
save-table = Shrani mizo
whose-turn = Čigava poteza
whos-at-table = Kdo je pri mizi
check-scores = Preveri rezultate
check-scores-detailed = Podrobni rezultati
check-game-options = Preveri možnosti igre
no-game-options = Ni možnosti igre.

# Turn messages
game-player-skipped = { $player } je preskočen.

# Table messages
table-created = { $host } je ustvaril novo mizo { $game }.
table-joined = { $player } se je pridružil mizi.
table-left = { $player } je zapustil mizo.
new-host = { $player } je zdaj gostitelj.
waiting-for-players = Čakanje na igralce. {$min} min, { $max } max.
game-starting = Igra se začenja!
table-listing = Miza od { $host } ({ $count } uporabnikov)
table-listing-one = Miza od { $host } ({ $count } uporabnik)
table-listing-with = Miza od { $host } ({ $count } uporabnikov) z { $members }
table-listing-game = { $game }: miza od { $host } ({ $count } uporabnikov)
table-listing-game-one = { $game }: miza od { $host } ({ $count } uporabnik)
table-listing-game-with = { $game }: miza od { $host } ({ $count } uporabnikov) z { $members }
table-not-exists = Miza ne obstaja več.
table-full = Miza je polna.
player-replaced-by-bot = { $player } je odšel in ga je zamenjal bot.
player-took-over = { $player } je prevzel od bota.
spectator-joined = Pridružil si se mizi od { $host } kot gledalec.

# Spectator mode
spectate = Opazuj
now-playing = { $player } zdaj igra.
now-spectating = { $player } zdaj opazuje.
spectator-left = { $player } je prenehal opazovati.

# General
welcome = Dobrodošli v PlayPalace!
goodbye = Nasvidenje!

# User presence announcements
user-online = { $player } je prišel na splet.
user-offline = { $player } je odšel brez povezave.
user-is-admin = { $player } je administrator PlayPalace.
user-is-server-owner = { $player } je lastnik strežnika PlayPalace.
online-users-none = Ni uporabnikov na spletu.
online-users-one = 1 uporabnik: { $users }
online-users-many = { $count } uporabnikov: { $users }
online-user-not-in-game = Ni v igri
online-user-waiting-approval = Čaka na odobritev

# Options
language = Jezik
language-option = Jezik: { $language }
language-changed = Jezik nastavljen na { $language }.

# Boolean option states
option-on = Vklopljeno
option-off = Izklopljeno

# Sound options
turn-sound-option = Zvok poteze: { $status }

# Dice options
clear-kept-option = Počisti obdržane kocke pri metu: { $status }
dice-keeping-style-option = Stil obdrževanja kock: { $style }
dice-keeping-style-changed = Stil obdrževanja kock nastavljen na { $style }.
dice-keeping-style-indexes = Indeksi kock
dice-keeping-style-values = Vrednosti kock

# Bot names
cancel = Prekliči
no-bot-names-available = Ni razpoložljivih imen botov.
select-bot-name = Izberi ime za bota
enter-bot-name = Vnesi ime bota
no-options-available = Ni razpoložljivih možnosti.
no-scores-available = Ni razpoložljivih rezultatov.

# Duration estimation
estimate-duration = Oceni trajanje
estimate-computing = Izračunavanje ocenjenega trajanja igre...
estimate-result = Povprečje bota: { $bot_time } (± { $std_dev }). { $outlier_info }Ocenjen človeški čas: { $human_time }.
estimate-error = Trajanja ni bilo mogoče oceniti.
estimate-already-running = Ocena trajanja že poteka.

# Save/Restore
saved-tables = Shranjene mize
no-saved-tables = Nimate shranjenih miz.
no-active-tables = Ni aktivnih miz.
restore-table = Obnovi
delete-saved-table = Izbriši
saved-table-deleted = Shranjena miza izbrisana.
missing-players = Ni mogoče obnoviti: ti igralci niso na voljo: { $players }
table-restored = Miza obnovljena! Vsi igralci so bili preneseni.
table-saved-destroying = Miza shranjena! Vrnitev v glavni meni.
game-type-not-found = Vrsta igre ne obstaja več.

# Action disabled reasons
action-not-your-turn = Ni tvoja poteza.
action-not-playing = Igra še ni začela.
action-spectator = Gledalci tega ne morejo storiti.
action-not-host = To lahko stori samo gostitelj.
action-game-in-progress = Tega ni mogoče storiti med igro.
action-need-more-players = Za začetek je potrebnih več igralcev.
action-table-full = Miza je polna.
action-no-bots = Ni botov za odstranitev.
action-bots-cannot = Boti tega ne morejo storiti.
action-no-scores = Še ni razpoložljivih rezultatov.

# Dice actions
dice-not-rolled = Še nisi vrgel.
dice-locked = Ta kocka je zaklenjena.
dice-no-dice = Ni razpoložljivih kock.

# Game actions
game-turn-start = Poteza igralca { $player }.
game-no-turn = Trenutno nihče ni na potezi.
table-no-players = Ni igralcev.
table-players-one = { $count } igralec: { $players }.
table-players-many = { $count } igralcev: { $players }.
table-spectators = Gledalci: { $spectators }.
game-leave = Zapusti
game-over = Konec igre
game-final-scores = Končni rezultati
game-points = { $count } { $count ->
    [one] točka
   *[other] točk
}
play = Igraj

# Leaderboards
leaderboards = Lestvice
leaderboards-menu-title = Lestvice
leaderboards-select-game = Izberi igro za ogled lestvice
leaderboard-no-data = Za to igro še ni podatkov na lestvici.

# Leaderboard types
leaderboard-type-wins = Vodilni po zmagah
leaderboard-type-rating = Ocena spretnosti
leaderboard-type-total-score = Skupni rezultat
leaderboard-type-high-score = Najvišji rezultat
leaderboard-type-games-played = Odigrane igre
leaderboard-type-avg-points-per-turn = Povprečne točke na potezo
leaderboard-type-best-single-turn = Najboljša posamezna poteza
leaderboard-type-score-per-round = Rezultat na krog

# Leaderboard headers
leaderboard-wins-header = { $game } - Vodilni po zmagah
leaderboard-total-score-header = { $game } - Skupni rezultat
leaderboard-high-score-header = { $game } - Najvišji rezultat
leaderboard-games-played-header = { $game } - Odigrane igre
leaderboard-rating-header = { $game } - Ocene spretnosti
leaderboard-avg-points-header = { $game } - Povprečne točke na potezo
leaderboard-best-turn-header = { $game } - Najboljša posamezna poteza
leaderboard-score-per-round-header = { $game } - Rezultat na krog

# Leaderboard entries
leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] zmaga
   *[other] zmag
} { $losses } { $losses ->
    [one] poraz
   *[other] porazov
}, { $percentage }% uspešnost
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } povprečno
leaderboard-games-entry = { $rank }. { $player }: { $value } iger

# Player stats
leaderboard-player-stats = Tvoje statistike: { $wins } zmag, { $losses } porazov ({ $percentage }% uspešnost)
leaderboard-no-player-stats = Te igre še nisi igral.

# Skill rating leaderboard
leaderboard-no-ratings = Za to igro še ni podatkov o ocenah.
leaderboard-rating-entry = { $rank }. { $player }: { $rating } ocena ({ $mu } ± { $sigma })
leaderboard-player-rating = Tvoja ocena: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = Za to igro še nimaš ocene.

# My Stats menu
my-stats = Moje statistike
my-stats-select-game = Izberi igro za ogled svojih statistik
my-stats-no-data = Te igre še nisi igral.
my-stats-no-games = Še nisi igral nobene igre.
my-stats-header = { $game } - Tvoje statistike
my-stats-wins = Zmage: { $value }
my-stats-losses = Porazi: { $value }
my-stats-winrate = Odstotek zmag: { $value }%
my-stats-games-played = Odigrane igre: { $value }
my-stats-total-score = Skupni rezultat: { $value }
my-stats-high-score = Najvišji rezultat: { $value }
my-stats-rating = Ocena spretnosti: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = Še ni ocene spretnosti
my-stats-avg-per-turn = Povprečne točke na potezo: { $value }
my-stats-best-turn = Najboljša posamezna poteza: { $value }

# Prediction system
predict-outcomes = Napoveduj izide
predict-header = Napovedani izidi (po oceni spretnosti)
predict-entry = { $rank }. { $player } (ocena: { $rating })
predict-entry-2p = { $rank }. { $player } (ocena: { $rating }, { $probability }% možnost zmage)
predict-unavailable = Napovedi ocen niso na voljo.
predict-need-players = Za napovedi sta potrebna vsaj 2 človeška igralca.
action-need-more-humans = Potrebnih je več človeških igralcev.
confirm-leave-game = Si prepričan, da želiš zapustiti mizo?
confirm-yes = Da
confirm-no = Ne

# Administration
administration = Administracija
admin-menu-title = Administracija

# Account approval
account-approval = Odobritev računa
account-approval-menu-title = Odobritev računa
no-pending-accounts = Ni računov v čakanju.
approve-account = Odobri
decline-account = Zavrni
account-approved = Račun igralca { $player } je bil odobren.
account-declined = Račun igralca { $player } je bil zavrnjen in izbrisan.

# Waiting for approval (shown to unapproved users)
waiting-for-approval = Tvoj račun čaka na odobritev administratorja.
account-approved-welcome = Tvoj račun je bil odobren! Dobrodošel v PlayPalace!
account-declined-goodbye = Tvoja zahteva za račun je bila zavrnjena.
    Razlog:
account-banned = Tvoj račun je blokiran in ni dostopen.

# Login errors
incorrect-username = Vneseno uporabniško ime ne obstaja.
incorrect-password = Vneseno geslo je napačno.
already-logged-in = Ta račun je že prijavljen.

# Credential validation
credential-username-length = Uporabniško ime mora biti med { $min } in { $max } znaki.
credential-password-length = Geslo mora biti med { $min } in { $max } znaki.

# Rate limiting
rate-limit-login-ip = Preveč poskusov prijave s tega naslova. Počakaj in poskusi znova.
rate-limit-login-user = Preveč neuspešnih poskusov prijave za to uporabniško ime. Počakaj in poskusi znova.
rate-limit-registration = Preveč poskusov registracije s tega naslova. Počakaj in poskusi znova.
rate-limit-refresh = Preveč poskusov osvežitve s tega naslova. Počakaj in poskusi znova.

# Session/auth errors
account-not-found = Račun ni bil najden.
session-expired = Seja je potekla. Prosimo, prijavi se znova.
session-token-mismatch = Žeton seje se ne ujema z uporabniškim imenom.
refresh-token-expired = Žeton za osvežitev je potekel. Prosimo, prijavi se znova.
refresh-token-mismatch = Žeton za osvežitev se ne ujema z uporabniškim imenom.

# Registration
registration-success = Registracija je uspela! Tvoj račun čaka na odobritev.
registration-username-taken = To uporabniško ime je že zasedeno. Prosimo, izberi drugačno.

# Preference fallback
pref-invalid-value = Neveljavna izbira, uporabljam privzeto vrednost.

# Decline reason
decline-reason-prompt = Vnesi razlog za zavrnitev (ali pritisni Escape za preklic):
account-action-empty-reason = Razlog ni naveden.

# Admin notifications for account requests
account-request = zahteva za račun
account-action = izvedeno dejanje za račun

# Admin promotion/demotion
promote-admin = Povišaj administratorja
demote-admin = Poniži administratorja
promote-admin-menu-title = Povišaj administratorja
demote-admin-menu-title = Poniži administratorja
no-users-to-promote = Ni uporabnikov za povišanje.
no-admins-to-demote = Ni administratorjev za ponižanje.
confirm-promote = Si prepričan, da želiš povišati { $player } v administratorja?
confirm-demote = Si prepričan, da želiš ponižati { $player } iz administratorja?
broadcast-to-all = Objavi vsem uporabnikom
broadcast-to-admins = Objavi samo administratorjem
broadcast-to-nobody = Tiho (brez objave)
promote-announcement = { $player } je bil povišan v administratorja!
promote-announcement-you = Povišan si bil v administratorja!
demote-announcement = { $player } je bil ponižan iz administratorja.
demote-announcement-you = Ponižan si bil iz administratorja.
not-admin-anymore = Nisi več administrator in ne moreš izvesti tega dejanja.
not-server-owner = To dejanje lahko izvede samo lastnik strežnika.

# Server ownership transfer
transfer-ownership = Prenesi lastništvo
transfer-ownership-menu-title = Prenesi lastništvo
no-admins-for-transfer = Ni administratorjev za prenos lastništva.
confirm-transfer-ownership = Si prepričan, da želiš prenesti lastništvo strežnika na { $player }? Ponižan boš v administratorja.
transfer-ownership-announcement = { $player } je zdaj lastnik strežnika Play Palace!
transfer-ownership-announcement-you = Zdaj si lastnik strežnika Play Palace!

# User banning
ban-user = Blokiraj uporabnika
unban-user = Odblokiraj uporabnika
no-users-to-ban = Ni uporabnikov za blokiranje.
no-users-to-unban = Ni blokiranih uporabnikov za odblokiranje.
confirm-ban = Si prepričan, da želiš blokirati { $player }?
confirm-unban = Si prepričan, da želiš odblokirati { $player }?
ban-reason-prompt = Vnesi razlog za blokiranje (neobvezno):
unban-reason-prompt = Vnesi razlog za odblokiranje (neobvezno):
user-banned = { $player } je bil blokiran.
user-unbanned = { $player } je bil odblokiran.
you-have-been-banned = Blokiran si bil na tem strežniku.
    Razlog:
you-have-been-unbanned = Odblokiran si bil na tem strežniku.
    Razlog:
ban-no-reason = Razlog ni naveden.

# Virtual bots (server owner only)
virtual-bots = Virtualni boti
virtual-bots-fill = Napolni strežnik
virtual-bots-clear = Izbriši vse bote
virtual-bots-status = Stanje
virtual-bots-clear-confirm = Si prepričan, da želiš izbrisati vse virtualne bote? To bo tudi uničilo vse mize, na katerih so.
virtual-bots-not-available = Virtualni boti niso na voljo.
virtual-bots-filled = Dodanih { $added } virtualnih botov. { $online } je zdaj na spletu.
virtual-bots-already-filled = Vsi virtualni boti iz konfiguracije so že aktivni.
virtual-bots-cleared = Izbrisanih { $bots } virtualnih botov in uničenih { $tables } { $tables ->
    [one] miza
   *[other] miz
}.
virtual-bot-table-closed = Mizo je zaprl administrator.
virtual-bots-none-to-clear = Ni virtualnih botov za brisanje.
virtual-bots-status-report = Virtualni boti: { $total } skupaj, { $online } na spletu, { $offline } brez povezave, { $in_game } v igri.
virtual-bots-guided-overview = Vodene mize
virtual-bots-groups-overview = Skupine botov
virtual-bots-profiles-overview = Profili
virtual-bots-guided-header = Vodene mize: { $count } pravilo/pravil. Dodelitev: { $allocation }, nadomestno: { $fallback }, privzeti profil: { $default_profile }.
virtual-bots-guided-empty = Ni konfiguriranih pravil vodenih miz.
virtual-bots-guided-status-active = aktiven
virtual-bots-guided-status-inactive = neaktiven
virtual-bots-guided-table-linked = povezano z mizo { $table_id } (gostitelj { $host }, igralci { $players }, ljudje { $humans })
virtual-bots-guided-table-stale = miza { $table_id } manjka na strežniku
virtual-bots-guided-table-unassigned = trenutno ni sledena nobena miza
virtual-bots-guided-next-change = naslednja sprememba čez { $ticks } korakov
virtual-bots-guided-no-schedule = ni načrtovalnega okna
virtual-bots-guided-warning = ⚠ premalo napolnjeno
virtual-bots-guided-line = { $table }: igra { $game }, prioriteta { $priority }, boti { $assigned } (min { $min_bots }, max { $max_bots }), čakanje { $waiting }, nedostopno { $unavailable }, stanje { $status }, profil { $profile }, skupine { $groups }. { $table_state }. { $next_change } { $warning_text }
virtual-bots-groups-header = Skupine botov: { $count } oznaka/oznak, { $bots } konfiguriranih botov.
virtual-bots-groups-empty = Ni definiranih skupin botov.
virtual-bots-groups-line = { $group }: profil { $profile }, boti { $total } (na spletu { $online }, čakanje { $waiting }, v igri { $in_game }, brez povezave { $offline }), pravila { $rules }.
virtual-bots-groups-no-rules = ni
virtual-bots-no-profile = privzeto
virtual-bots-profile-inherit-default = podeduje privzeti profil
virtual-bots-profiles-header = Profili: { $count } definiranih (privzeto: { $default_profile }).
virtual-bots-profiles-empty = Ni definiranih profilov.
virtual-bots-profiles-line = { $profile } ({ $bot_count } botov) prepiše: { $overrides }.
virtual-bots-profiles-no-overrides = podeduje osnovno konfiguracijo

localization-in-progress-try-again = Lokalizacija je v teku. Poskusite znova čez minuto.
