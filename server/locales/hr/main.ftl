# Main UI messages for PlayPalace

# Game categories
category-card-games = Kartaške igre
category-dice-games = Igre s kockicama
category-rb-play-center = RB Play centar
category-poker = Poker
category-uncategorized = Bez kategorije

# Menu titles
main-menu-title = Glavni izbornik
play-menu-title = Igraj
categories-menu-title = Kategorije igara
tables-menu-title = Dostupni stolovi

# Menu items
play = Igraj
view-active-tables = Pregledaj aktivne stolove
options = Postavke
logout = Odjava
back = Natrag
go-back = Idi natrag
context-menu = Kontekstualni izbornik.
no-actions-available = Nema dostupnih radnji.
create-table = Stvori novi stol
join-as-player = Pridruži se kao igrač
join-as-spectator = Pridruži se kao promatrač
leave-table = Napusti stol
start-game = Započni igru
add-bot = Dodaj bota
remove-bot = Ukloni bota
actions-menu = Izbornik radnji
save-table = Spremi stol
whose-turn = Čiji je red
whos-at-table = Tko je za stolom
check-scores = Provjeri rezultate
check-scores-detailed = Detaljni rezultati
check-game-options = Provjeri opcije igre
no-game-options = Nema opcija igre.

# Turn messages
game-player-skipped = { $player } je preskočen.

# Table messages
table-created = { $host } je stvorio novi { $game } stol.
table-joined = { $player } se pridružio stolu.
table-left = { $player } je napustio stol.
new-host = { $player } je sada domaćin.
waiting-for-players = Čekanje igrača. {$min} min, { $max } max.
game-starting = Igra počinje!
table-listing = Stol od { $host } ({ $count } korisnika)
table-listing-one = Stol od { $host } ({ $count } korisnik)
table-listing-with = Stol od { $host } ({ $count } korisnika) s { $members }
table-listing-game = { $game }: stol od { $host } ({ $count } korisnika)
table-listing-game-one = { $game }: stol od { $host } ({ $count } korisnik)
table-listing-game-with = { $game }: stol od { $host } ({ $count } korisnika) s { $members }
table-not-exists = Stol više ne postoji.
table-full = Stol je pun.
player-replaced-by-bot = { $player } je napustio i zamijenjen je botom.
player-took-over = { $player } je preuzeo od bota.
spectator-joined = Pridružio se stolu od { $host } kao promatrač.

# Spectator mode
spectate = Promatraj
now-playing = { $player } sada igra.
now-spectating = { $player } sada promatra.
spectator-left = { $player } je prestao promatrati.

# General
welcome = Dobrodošli u PlayPalace!
goodbye = Doviđenja!

# User presence announcements
user-online = { $player } je došao online.
user-offline = { $player } je otišao offline.
user-is-admin = { $player } je administrator PlayPalace-a.
user-is-server-owner = { $player } je vlasnik servera PlayPalace-a.
online-users-none = Nema korisnika online.
online-users-one = 1 korisnik: { $users }
online-users-many = { $count } korisnika: { $users }
online-user-not-in-game = Nije u igri
online-user-waiting-approval = Čeka odobrenje

# Options
language = Jezik
language-option = Jezik: { $language }
language-changed = Jezik postavljen na { $language }.

# Boolean option states
option-on = Uključeno
option-off = Isključeno

# Sound options
turn-sound-option = Zvuk poteza: { $status }

# Dice options
clear-kept-option = Obriši zadržane kockice pri bacanju: { $status }
dice-keeping-style-option = Stil zadržavanja kockica: { $style }
dice-keeping-style-changed = Stil zadržavanja kockica postavljen na { $style }.
dice-keeping-style-indexes = Indeksi kockica
dice-keeping-style-values = Vrijednosti kockica

# Bot names
cancel = Odustani
no-bot-names-available = Nema dostupnih imena botova.
select-bot-name = Odaberi ime za bota
enter-bot-name = Unesi ime bota
no-options-available = Nema dostupnih opcija.
no-scores-available = Nema dostupnih rezultata.

# Duration estimation
estimate-duration = Procijeni trajanje
estimate-computing = Izračunavanje procijenjenog trajanja igre...
estimate-result = Prosjek bota: { $bot_time } (± { $std_dev }). { $outlier_info }Procijenjeno ljudsko vrijeme: { $human_time }.
estimate-error = Nije moguće procijeniti trajanje.
estimate-already-running = Procjena trajanja je već u tijeku.

# Save/Restore
saved-tables = Spremljeni stolovi
no-saved-tables = Nemate spremljenih stolova.
no-active-tables = Nema aktivnih stolova.
restore-table = Vrati
delete-saved-table = Obriši
saved-table-deleted = Spremljeni stol obrisan.
missing-players = Nije moguće vratiti: ovi igrači nisu dostupni: { $players }
table-restored = Stol vraćen! Svi igrači su prebačeni.
table-saved-destroying = Stol spremljen! Vraćanje na glavni izbornik.
game-type-not-found = Vrsta igre više ne postoji.

# Action disabled reasons
action-not-your-turn = Nije tvoj red.
action-not-playing = Igra nije započela.
action-spectator = Promatrači ne mogu to učiniti.
action-not-host = Samo domaćin može to učiniti.
action-game-in-progress = Ne može se učiniti dok je igra u tijeku.
action-need-more-players = Potrebno je više igrača za početak.
action-table-full = Stol je pun.
action-no-bots = Nema botova za ukloniti.
action-bots-cannot = Botovi ne mogu to učiniti.
action-no-scores = Još nema dostupnih rezultata.

# Dice actions
dice-not-rolled = Još nisi bacio kockice.
dice-locked = Ova kockica je zaključana.
dice-no-dice = Nema dostupnih kockica.

# Game actions
game-turn-start = Red igrača { $player }.
game-no-turn = Trenutno nitko nije na redu.
table-no-players = Nema igrača.
table-players-one = { $count } igrač: { $players }.
table-players-many = { $count } igrača: { $players }.
table-spectators = Promatrači: { $spectators }.
game-leave = Napusti
game-over = Kraj igre
game-final-scores = Konačni rezultati
game-points = { $count } { $count ->
    [one] bod
   *[other] bodova
}
play = Igraj

# Leaderboards
leaderboards = Ljestvice
leaderboards-menu-title = Ljestvice
leaderboards-select-game = Odaberi igru za pregled ljestvice
leaderboard-no-data = Još nema podataka na ljestvici za ovu igru.

# Leaderboard types
leaderboard-type-wins = Vodeći po pobjedama
leaderboard-type-rating = Ocjena vještine
leaderboard-type-total-score = Ukupni rezultat
leaderboard-type-high-score = Najbolji rezultat
leaderboard-type-games-played = Odigrane igre
leaderboard-type-avg-points-per-turn = Prosječni bodovi po potezu
leaderboard-type-best-single-turn = Najbolji pojedinačni potez
leaderboard-type-score-per-round = Rezultat po rundi

# Leaderboard headers
leaderboard-wins-header = { $game } - Vodeći po pobjedama
leaderboard-total-score-header = { $game } - Ukupni rezultat
leaderboard-high-score-header = { $game } - Najbolji rezultat
leaderboard-games-played-header = { $game } - Odigrane igre
leaderboard-rating-header = { $game } - Ocjene vještine
leaderboard-avg-points-header = { $game } - Prosječni bodovi po potezu
leaderboard-best-turn-header = { $game } - Najbolji pojedinačni potez
leaderboard-score-per-round-header = { $game } - Rezultat po rundi

# Leaderboard entries
leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] pobjeda
   *[other] pobjeda
} { $losses } { $losses ->
    [one] poraz
   *[other] poraza
}, { $percentage }% pobjeda
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } prosječno
leaderboard-games-entry = { $rank }. { $player }: { $value } igara

# Player stats
leaderboard-player-stats = Tvoje statistike: { $wins } pobjeda, { $losses } poraza ({ $percentage }% pobjeda)
leaderboard-no-player-stats = Još nisi igrao ovu igru.

# Skill rating leaderboard
leaderboard-no-ratings = Još nema podataka o ocjenama za ovu igru.
leaderboard-rating-entry = { $rank }. { $player }: { $rating } ocjena ({ $mu } ± { $sigma })
leaderboard-player-rating = Tvoja ocjena: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = Još nemaš ocjenu za ovu igru.

# My Stats menu
my-stats = Moje statistike
my-stats-select-game = Odaberi igru za pregled svojih statistika
my-stats-no-data = Još nisi igrao ovu igru.
my-stats-no-games = Još nisi igrao nijednu igru.
my-stats-header = { $game } - Tvoje statistike
my-stats-wins = Pobjede: { $value }
my-stats-losses = Porazi: { $value }
my-stats-winrate = Postotak pobjeda: { $value }%
my-stats-games-played = Odigrane igre: { $value }
my-stats-total-score = Ukupni rezultat: { $value }
my-stats-high-score = Najbolji rezultat: { $value }
my-stats-rating = Ocjena vještine: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = Još nema ocjene vještine
my-stats-avg-per-turn = Prosječni bodovi po potezu: { $value }
my-stats-best-turn = Najbolji pojedinačni potez: { $value }

# Prediction system
predict-outcomes = Predvidi ishode
predict-header = Predviđeni ishodi (prema ocjeni vještine)
predict-entry = { $rank }. { $player } (ocjena: { $rating })
predict-entry-2p = { $rank }. { $player } (ocjena: { $rating }, { $probability }% šansa za pobjedu)
predict-unavailable = Predviđanja ocjena nisu dostupna.
predict-need-players = Potrebna su najmanje 2 ljudska igrača za predviđanja.
action-need-more-humans = Potrebno je više ljudskih igrača.
confirm-leave-game = Jesi li siguran da želiš napustiti stol?
confirm-yes = Da
confirm-no = Ne

# Administration
administration = Administracija
admin-menu-title = Administracija

# Account approval
account-approval = Odobrenje računa
account-approval-menu-title = Odobrenje računa
no-pending-accounts = Nema računa na čekanju.
approve-account = Odobri
decline-account = Odbij
account-approved = Račun korisnika { $player } je odobren.
account-declined = Račun korisnika { $player } je odbijen i obrisan.

# Waiting for approval (shown to unapproved users)
waiting-for-approval = Tvoj račun čeka odobrenje administratora.
account-approved-welcome = Tvoj račun je odobren! Dobrodošao u PlayPalace!
account-declined-goodbye = Tvoj zahtjev za račun je odbijen.
    Razlog:
account-banned = Tvoj račun je blokiran i ne može se pristupiti.

# Login errors
incorrect-username = Korisničko ime koje si unio ne postoji.
incorrect-password = Lozinka koju si unio je netočna.
already-logged-in = Ovaj račun je već prijavljen.

# Provjera valjanosti vjerodajnica
credential-username-length = Korisničko ime mora imati između { $min } i { $max } znakova.
credential-password-length = Lozinka mora imati između { $min } i { $max } znakova.

# Ograničenje brzine
rate-limit-login-ip = Previše pokušaja prijave s ove adrese. Pričekaj i pokušaj ponovo.
rate-limit-login-user = Previše neuspjelih pokušaja prijave za ovo korisničko ime. Pričekaj i pokušaj ponovo.
rate-limit-registration = Previše pokušaja registracije s ove adrese. Pričekaj i pokušaj ponovo.
rate-limit-refresh = Previše pokušaja osvježavanja s ove adrese. Pričekaj i pokušaj ponovo.

# Greške sesije i autentikacije
account-not-found = Račun nije pronađen.
session-expired = Sesija je istekla. Prijavi se ponovo.
session-token-mismatch = Token sesije ne odgovara korisničkom imenu.
refresh-token-expired = Token za osvježavanje je istekao. Prijavi se ponovo.
refresh-token-mismatch = Token za osvježavanje ne odgovara korisničkom imenu.

# Registracija
registration-success = Registracija uspješna! Tvoj račun čeka odobrenje.
registration-username-taken = Korisničko ime je već zauzeto. Odaberi drugo korisničko ime.

# Zadana vrijednost preferencije
pref-invalid-value = Nevažeći odabir, koristi se zadana vrijednost.

# Decline reason
decline-reason-prompt = Unesi razlog za odbijanje (ili pritisni Escape za odustajanje):
account-action-empty-reason = Razlog nije naveden.

# Admin notifications for account requests
account-request = zahtjev za račun
account-action = poduzeta radnja za račun

# Admin promotion/demotion
promote-admin = Promakni administratora
demote-admin = Razriješi administratora
promote-admin-menu-title = Promakni administratora
demote-admin-menu-title = Razriješi administratora
no-users-to-promote = Nema korisnika dostupnih za promicanje.
no-admins-to-demote = Nema administratora dostupnih za razrješenje.
confirm-promote = Jesi li siguran da želiš promaknuti { $player } u administratora?
confirm-demote = Jesi li siguran da želiš razriješiti { $player } s pozicije administratora?
broadcast-to-all = Objavi svim korisnicima
broadcast-to-admins = Objavi samo administratorima
broadcast-to-nobody = Tiho (bez objave)
promote-announcement = { $player } je promaknut u administratora!
promote-announcement-you = Promaknut si u administratora!
demote-announcement = { $player } je razriješen s pozicije administratora.
demote-announcement-you = Razriješen si s pozicije administratora.
not-admin-anymore = Više nisi administrator i ne možeš izvršiti ovu radnju.
not-server-owner = Samo vlasnik servera može izvršiti ovu radnju.

# Server ownership transfer
transfer-ownership = Prenesi vlasništvo
transfer-ownership-menu-title = Prenesi vlasništvo
no-admins-for-transfer = Nema administratora dostupnih za prijenos vlasništva.
confirm-transfer-ownership = Jesi li siguran da želiš prenijeti vlasništvo servera na { $player }? Bit ćeš razriješen na administratora.
transfer-ownership-announcement = { $player } je sada vlasnik servera Play Palace!
transfer-ownership-announcement-you = Sada si vlasnik servera Play Palace!

# User banning
ban-user = Blokiraj korisnika
unban-user = Odblokiraj korisnika
no-users-to-ban = Nema korisnika dostupnih za blokiranje.
no-users-to-unban = Nema blokiranih korisnika za odblokiranje.
confirm-ban = Jesi li siguran da želiš blokirati { $player }?
confirm-unban = Jesi li siguran da želiš odblokirati { $player }?
ban-reason-prompt = Unesi razlog za blokiranje (neobavezno):
unban-reason-prompt = Unesi razlog za odblokiranje (neobavezno):
user-banned = { $player } je blokiran.
user-unbanned = { $player } je odblokiran.
you-have-been-banned = Blokiran si s ovog servera.
    Razlog:
you-have-been-unbanned = Odblokiran si s ovog servera.
    Razlog:
ban-no-reason = Razlog nije naveden.

# Virtual bots (server owner only)
virtual-bots = Virtualni botovi
virtual-bots-fill = Popuni server
virtual-bots-clear = Obriši sve botove
virtual-bots-status = Status
virtual-bots-clear-confirm = Jesi li siguran da želiš obrisati sve virtualne botove? Ovo će također uništiti sve stolove na kojima se nalaze.
virtual-bots-not-available = Virtualni botovi nisu dostupni.
virtual-bots-filled = Dodano { $added } virtualnih botova. { $online } je sada online.
virtual-bots-already-filled = Svi virtualni botovi iz konfiguracije su već aktivni.
virtual-bots-cleared = Obrisano { $bots } virtualnih botova i uništeno { $tables } { $tables ->
    [one] stol
   *[other] stolova
}.
virtual-bot-table-closed = Stol zatvoren od strane administratora.
virtual-bots-none-to-clear = Nema virtualnih botova za brisanje.
virtual-bots-status-report = Virtualni botovi: { $total } ukupno, { $online } online, { $offline } offline, { $in_game } u igri.
virtual-bots-guided-overview = Vođeni stolovi
virtual-bots-groups-overview = Grupe botova
virtual-bots-profiles-overview = Profili
virtual-bots-guided-header = Vođeni stolovi: { $count } pravilo(a). Alokacija: { $allocation }, povratno: { $fallback }, zadani profil: { $default_profile }.
virtual-bots-guided-empty = Nisu konfigurirani vođeni stolovi.
virtual-bots-guided-status-active = aktivan
virtual-bots-guided-status-inactive = neaktivan
virtual-bots-guided-table-linked = povezan sa stolom { $table_id } (domaćin { $host }, igrači { $players }, ljudi { $humans })
virtual-bots-guided-table-stale = stol { $table_id } nedostaje na serveru
virtual-bots-guided-table-unassigned = trenutno nije praćen nijedan stol
virtual-bots-guided-next-change = sljedeća promjena za { $ticks } tikova
virtual-bots-guided-no-schedule = nema rasporeda
virtual-bots-guided-warning = ⚠ nedovoljno popunjeno
virtual-bots-guided-line = { $table }: igra { $game }, prioritet { $priority }, botovi { $assigned } (min { $min_bots }, max { $max_bots }), čeka { $waiting }, nedostupno { $unavailable }, status { $status }, profil { $profile }, grupe { $groups }. { $table_state }. { $next_change } { $warning_text }
virtual-bots-groups-header = Grupe botova: { $count } oznaka(a), { $bots } konfiguriranih botova.
virtual-bots-groups-empty = Nisu definirane grupe botova.
virtual-bots-groups-line = { $group }: profil { $profile }, botovi { $total } (online { $online }, čeka { $waiting }, u igri { $in_game }, offline { $offline }), pravila { $rules }.
virtual-bots-groups-no-rules = nema
virtual-bots-no-profile = zadano
virtual-bots-profile-inherit-default = nasljeđuje zadani profil
virtual-bots-profiles-header = Profili: { $count } definirano (zadano: { $default_profile }).
virtual-bots-profiles-empty = Nisu definirani profili.
virtual-bots-profiles-line = { $profile } ({ $bot_count } botova) nadjačava: { $overrides }.
virtual-bots-profiles-no-overrides = nasljeđuje osnovnu konfiguraciju

localization-in-progress-try-again = Lokalizacija je u tijeku. Pokušajte ponovno za minutu.
