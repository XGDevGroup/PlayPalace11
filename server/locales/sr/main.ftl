# Glavne poruke korisničkog interfejsa za PlayPalace

# Kategorije igara
category-card-games = Igre kartama
category-dice-games = Igre sa kockicama
category-board-games = Igre na tabli
category-rb-play-center = RB Play centar
category-poker = Poker
category-uncategorized = Nekategorisano

# Naslovi menija
main-menu-title = Glavni meni
play-menu-title = Igraj
categories-menu-title = Kategorije igara
tables-menu-title = Dostupni stolovi

# Stavke menija
play = Igraj
view-active-tables = Prikaži aktivne stolove
options = Podešavanja
logout = Odjavi se
back = Nazad
context-menu = Kontekstni meni.
no-actions-available = Nema dostupnih radnji.
create-table = Napravi novi sto
join-as-player = Pridruži se kao igrač
join-as-spectator = Pridruži se kao posmatrač
leave-table = Napusti sto
start-game = Pokreni igru
add-bot = Dodaj robota
remove-bot = Ukloni robota
actions-menu = Meni sa radnjama
save-table = Sačuvaj sto
whose-turn = Ko je na potezu
whos-at-table = Ko je za stolom
check-scores = Proveri rezultat
check-scores-detailed = Detaljni rezultati
check-game-options = Proveri opcije igre
no-game-options = Nema opcija igre.

# Poruke o redu igranja
game-player-skipped = { $player } se preskače.

# Poruke o stolu
table-created = { $host } pravi novi sto za igru { $game }.
table-joined = { $player } se pridružuje stolu.
table-left = { $player } napušta sto.
new-host = { $player } je sada vlasnik.
waiting-for-players = Čekanje na igrače. {$min} minimalno, { $max } maksimalno.
game-starting = Igra počinje!
table-listing = Sto igrača { $host } ({ $count } korisnika)
table-listing-one = Sto igrača { $host } ({ $count } korisnik)
table-listing-with = Sto igrača { $host }  ({ $count } korisnika) sa { $members }
table-listing-game = { $game }: Sto igrača { $host }  ({ $count } korisnika)
table-listing-game-one = { $game }: sto igrača { $host }  ({ $count } korisnik)
table-listing-game-with = { $game }: sto igrača { $host }  ({ $count } korisnika) sa { $members }
table-not-exists = Sto više ne postoji.
table-full = Sto je popunjen.
player-replaced-by-bot = { $player } napušta i zamenjen/a je robotom.
player-took-over = { $player } preuzima mesto robota.
spectator-joined = Pridružili ste se stolu igrača { $host } kao posmatrač.

# Režim posmatrača
spectate = Posmatraj
now-playing = { $player } sada igra.
now-spectating = { $player } sada posmatra.
spectator-left = { $player } više ne posmatra.

# Opšte
welcome = Dobrodošli u PlayPalace!
goodbye = Doviđenja!

# User presence announcements
user-online = { $player } je na mreži.
user-offline = { $player } je van mreže.
user-is-admin = { $player } je administrator za PlayPalace.
user-is-server-owner = { $player } je vlasnik servera za PlayPalace.
online-users-none = Nema nikoga na mreži.
online-users-one = 1 korisnik: { $users }
online-users-many = { $count } korisnika: { $users }
online-user-not-in-game = Nije u igri
online-user-waiting-approval = Čeka na odobravanje

# Opcije
language = Jezik
language-option = Jezik: { $language }
language-changed = Jezik je postavljen na { $language }.

# Stanja logičkih opcija
option-on = Uključeno
option-off = Isključeno

# Opcije zvuka
turn-sound-option = Zvuk za potez: { $status }

# Opcije kockica
clear-kept-option = Skloni sačuvane kockice pri bacanju: { $status }
dice-keeping-style-option = Stil čuvanja kockica: { $style }
dice-keeping-style-changed = Stil čuvanja kockica je postavljen na { $style }.
dice-keeping-style-indexes = Redni brojevi kockica
dice-keeping-style-values = Vrednosti kockica

# Imena botova
cancel = Otkaži
no-bot-names-available = Nema dostupnih imena za robote.
select-bot-name = Izaberi ime za robota
enter-bot-name = Unesi ime robota
no-options-available = Nema dostupnih opcija.
no-scores-available = Nema dostupnih rezultata.

# Procena trajanja
estimate-duration = Proceni trajanje
estimate-computing = Izračunavanje procenjenog trajanja igre...
estimate-result = Prosek bota: { $bot_time } (± { $std_dev }). { $outlier_info }Procenjeno vreme za ljude: { $human_time }.
estimate-error = Nije moguće proceniti trajanje.
estimate-already-running = Procena trajanja je već u toku.

# Čuvanje/Vraćanje
saved-tables = Sačuvani stolovi
no-saved-tables = Nemate sačuvanih stolova.
no-active-tables = Nema aktivnih stolova.
restore-table = Vrati
delete-saved-table = Obriši
saved-table-deleted = Sačuvan sto je obrisan.
missing-players = Nije moguće vratiti sto: ovi igrači nisu dostupni: { $players }
table-restored = Sto je vraćen! Svi igrači su prebačeni.
table-saved-destroying = Sto je sačuvan! Povratak u glavni meni.
game-type-not-found = Vrsta igre više ne postoji.

# Razlozi onemogućenih radnji
action-not-your-turn = Niste na potezu.
action-not-playing = Igra još nije počela.
action-spectator = Posmatrači ne mogu ovo da rade.
action-not-host = Samo vlasnik može ovo da uradi.
action-game-in-progress = Ovo ne možete uraditi dok je igra u toku.
action-need-more-players = Potrebno vam je bar { $min_players } igrača za početak.
action-table-full = Sto je popunjen.
action-no-bots = Nema robota za uklanjanje.
action-bots-cannot = Roboti ne mogu ovo da rade.
action-no-scores = Još uvek nema dostupnih rezultata.

# Radnje sa kockicama
dice-not-rolled = Još uvek niste bacili kockice.
dice-locked = Ova kockica je zaključana.
dice-no-dice = Nema dostupnih kockica.

# Radnje u igri
game-turn-start = { $player } je na potezu.
game-no-turn = Trenutno niko nije na potezu.
table-no-players = Nema igrača.
table-players-one = { $count } igrač: { $players }.
table-players-many = { $count } igrača: { $players }.
table-spectators = Posmatrači: { $spectators }.
game-leave = Napusti
game-over = Igra je gotova
game-final-scores = Konačni rezultat
game-points = { $count } { $count ->
    [one] poen
    *[other] poena
}
play = Igraj

# Rang liste
leaderboards = Rang liste
leaderboards-menu-title = Rang liste
leaderboards-select-game = Izaberi igru za prikaz rang liste
leaderboard-no-data = Još uvek nema podataka za rang listu ove igre.

# Tipovi rang listi
leaderboard-type-wins = Najviše pobeda
leaderboard-type-rating = Rang veštine
leaderboard-type-total-score = Ukupan rezultat
leaderboard-type-high-score = Najbolji rezultat
leaderboard-type-games-played = Odigranih igara
leaderboard-type-avg-points-per-turn = Prosečno poena po potezu
leaderboard-type-best-single-turn = Najbolji pojedinačni potez
leaderboard-type-score-per-round = Rezultat po rundi

# Zaglavlja rang listi
leaderboard-wins-header = { $game } - Najviše pobeda
leaderboard-total-score-header = { $game } - Ukupan rezultat
leaderboard-high-score-header = { $game } - Najbolji rezultat
leaderboard-games-played-header = { $game } - Odigranih igara
leaderboard-rating-header = { $game } - Rangovi veštine
leaderboard-avg-points-header = { $game } - Prosečno poena po potezu
leaderboard-best-turn-header = { $game } - Najbolji pojedinačni potez
leaderboard-score-per-round-header = { $game } - Rezultat po rundi

# Unosi na rang listi
leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] pobeda
    [few] pobede
    *[other] pobeda
} { $losses } { $losses ->
    [one] poraz
    [few] poraza
    *[other] poraza
}, { $percentage }% pobeda
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } prosečno
leaderboard-games-entry = { $rank }. { $player }: { $value } igara

# Statistika igrača
leaderboard-player-stats = Vaša statistika: { $wins } pobeda, { $losses } poraza ({ $percentage }% uspešnost)
leaderboard-no-player-stats = Još uvek niste igrali ovu igru.

# Rang lista veština
leaderboard-no-ratings = Još uvek nema podataka o rangu za ovu igru.
leaderboard-rating-entry = { $rank }. { $player }: { $rating } rang ({ $mu } ± { $sigma })
leaderboard-player-rating = Vaš rang: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = Još uvek nemate rang za ovu igru.

# Meni "Moja statistika"
my-stats = Moja statistika
my-stats-select-game = Izaberi igru za prikaz svoje statistike
my-stats-no-data = Još uvek niste igrali ovu igru.
my-stats-no-games = Još uvek niste odigrali nijednu igru.
my-stats-header = { $game } - Vaša statistika
my-stats-wins = Pobede: { $value }
my-stats-losses = Porazi: { $value }
my-stats-winrate = Procenat pobeda: { $value }%
my-stats-games-played = Odigranih igara: { $value }
my-stats-total-score = Ukupan rezultat: { $value }
my-stats-high-score = Najbolji rezultat: { $value }
my-stats-rating = Rang veštine: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = Još uvek nema ranga veštine
my-stats-avg-per-turn = Prosečno poena po potezu: { $value }
my-stats-best-turn = Najbolji pojedinačni potez: { $value }

# Sistem predviđanja
predict-outcomes = Predvidi ishode
predict-header = Predviđeni ishodi (prema rangu veštine)
predict-entry = { $rank }. { $player } (rang: { $rating })
predict-entry-2p = { $rank }. { $player } (rang: { $rating }, { $probability }% šanse za pobedu)
predict-unavailable = Predviđanja ranga nisu dostupna.
predict-need-players = Potrebna su najmanje 2 ljudska igrača za predviđanje.
action-need-more-humans = Potrebno je više ljudskih igrača.
confirm-leave-game = Da li ste sigurni da želite da napustite sto?
confirm-logout = Da li ste sigurni da želite da se odjavite?
confirm-yes = Da
confirm-no = Ne

# Administration
administration = Administracija
admin-menu-title = Administracija

# Account approval
account-approval = Odobravanje naloga
account-approval-menu-title = Odobravanje naloga
no-pending-accounts = Nema naloga koji čekaju na odobravanje.
approve-account = Odobri
decline-account = Odbij
account-approved = Nalog igrača { $player } je odobren.
account-declined = Nalog igrača { $player } je odbijen i obrisan.

# Waiting for approval (shown to unapproved users)
waiting-for-approval = Vaš nalog čeka na odobravanje od administratora. Molimo sačekajte...
account-approved-welcome = Vaš nalog je odobren! Dobro došli u PlayPalace!
account-declined-goodbye = Vaš zahtev za nalog je odbijen.
Razlog:
account-banned = Vašem nalogu je zabranjen pristup.

# Login errors
incorrect-username = Korisničko ime koje ste upisali ne postoji.
incorrect-password = Lozinka koju ste upisali je netačna.
already-logged-in = Ovaj nalog je već prijavljen.

# Credential validation
credential-username-length = Korisničko ime mora imati između { $min } i { $max } znakova.
credential-password-length = Lozinka mora imati između { $min } i { $max } znakova.

# Rate limiting
rate-limit-login-ip = Previše pokušaja prijave sa ove adrese. Sačekajte i pokušajte ponovo.
rate-limit-login-user = Previše neuspešnih pokušaja prijave za ovo korisničko ime. Sačekajte i pokušajte ponovo.
rate-limit-registration = Previše pokušaja registracije sa ove adrese. Sačekajte i pokušajte ponovo.
rate-limit-refresh = Previše pokušaja osvežavanja sa ove adrese. Sačekajte i pokušajte ponovo.

# Session/auth errors
account-not-found = Nalog nije pronađen.
session-expired = Sesija je istekla. Molimo prijavite se ponovo.
session-token-mismatch = Token sesije se ne poklapa sa korisničkim imenom.
refresh-token-expired = Token za osvežavanje je istekao. Molimo prijavite se ponovo.
refresh-token-mismatch = Token za osvežavanje se ne poklapa sa korisničkim imenom.

# Registration
registration-success = Registracija je uspešna! Vaš nalog čeka na odobravanje.
registration-username-taken = Korisničko ime je već zauzeto. Molimo izaberite drugo ime.

# Preference fallback
pref-invalid-value = Nevažeći izbor, koristim podrazumevanu vrednost.

# Decline reason
decline-reason-prompt = Upišite razlog odbijanja (ili pritisnite Escape da otkažete):
account-action-empty-reason = Nijedan razlog nije upisan.

# Admin notifications for account requests
account-request = Zahtev naloga
account-action = Radnja za nalog izvršena

# Admin promotion/demotion
promote-admin = Promoviši u administratora
demote-admin = Ukloni administratora
promote-admin-menu-title = Promoviši u administratora
demote-admin-menu-title = Ukloni administratora
no-users-to-promote = Nema dostupnih korisnika za promovisanje.
no-admins-to-demote = Nema dostupnih administratora za uklanjanje.
confirm-promote = Da li ste sigurni da želite da promovišete { $player } u administratora?
confirm-demote = Da li ste sigurni da želite da uklonite { $player } kao administratora?
broadcast-to-all = Obavesti sve korisnike
broadcast-to-admins = Obavesti samo administratore
broadcast-to-nobody = Tiho (bez obaveštenja)
promote-announcement = { $player } je promovisan u administratora!
promote-announcement-you = Promovisani ste u administratora!
demote-announcement = { $player } više nije administrator.
demote-announcement-you = Više niste administrator.
not-admin-anymore = Više niste administrator i ne možete izvršiti ovu radnju.
not-server-owner = Samo vlasnik servera može da izvrši ovu radnju.

# Server ownership transfer
transfer-ownership = Prebaci vlasništvo
transfer-ownership-menu-title = Prebaci vlasništvo
no-admins-for-transfer = Nema dostupnih administratora kojima se može prebaciti vlasništvo.
confirm-transfer-ownership = Da li ste sigurni da želite da prebacite vlasništvo servera igraču { $player }? Ostaćete administrator.
transfer-ownership-announcement = { $player } je sada vlasnik Play Palace servera!
transfer-ownership-announcement-you = Sada ste vlasnik Play palace servera!

# User banning
ban-user = Zabrani pristup korisniku
unban-user = Vrati pristup korisniku
no-users-to-ban = Nema dostupnih korisnika za zabranu pristupa.
no-users-to-unban = Nema korisnika kojima je zabranjen pristup.
confirm-ban = Da li ste sigurni da želite da zabranite pristup igraču { $player }?
confirm-unban = Da li ste sigurni da želite da vratite pristup igraču { $player }?
ban-reason-prompt = Upišite razlog zabrane (opciono):
unban-reason-prompt = Upišite razlog vraćanja pristupa (opciono):
user-banned = { $player } više nema pristup.
user-unbanned = { $player } ponovo ima pristup.
you-have-been-banned = Zabranjen vam je pristup ovom serveru.
    Razlog:
you-have-been-unbanned = Ponovo imate pristup ovom serveru.
    Razlog:
ban-no-reason = Bez razloga.

# Virtual bots (server owner only)
virtual-bots = Virtuelni roboti
virtual-bots-fill = Popuni server
virtual-bots-clear = Očisti sve robote
virtual-bots-status = Status
virtual-bots-clear-confirm = Da li ste sigurni da želite da obrišete sve virtuelne robote? Ovo će takođe uništiti sve stolove u kojima se oni nalaze.
virtual-bots-not-available = Virtuelni roboti nisu dostupni.
virtual-bots-filled = Dodato { $added } virtuelnih robota. { $online } su sada na mreži.
virtual-bots-already-filled = Svi virtuelni roboti iz konfiguracije su sada aktivni.
virtual-bots-cleared = Obrisano { $bots } virtuelnih robota i { $tables } { $tables ->
    [one] sto uništen
    [few] stola uništena
   *[other] stolova uništeno
}.
virtual-bot-table-closed = Administrator je zatvorio sto.
virtual-bots-none-to-clear = Nema virtuelnih robota za brisanje.
virtual-bots-status-report = Virtuelni roboti: { $total } ukupno, { $online } na mreži, { $offline } van mreže, { $in_game } u igri.
virtual-bots-guided-overview = Navođeni stolovi
virtual-bots-groups-overview = Grupe robota
virtual-bots-profiles-overview = Profili
virtual-bots-guided-header = Navođeni stolovi: { $count } pravila. Dodeljeno: { $allocation }, alternativa: { $fallback }, podrazumevani profil: { $default_profile }.
virtual-bots-guided-empty = Nijedno pravilo za navođene stolove nije podešeno.
virtual-bots-guided-status-active = Aktivno
virtual-bots-guided-status-inactive = Neaktivno
virtual-bots-guided-table-linked = Povezan sa stolom { $table_id } (vlasnik { $host }, igrači { $players }, ljudi { $humans })
virtual-bots-guided-table-stale = Sto { $table_id } nedostaje na serveru
virtual-bots-guided-table-unassigned = Nijedan sto se trenutno ne prati
virtual-bots-guided-next-change = sledeća promena za { $ticks } tikova
virtual-bots-guided-no-schedule = Nema zakazane promene
virtual-bots-guided-warning = ⚠ nije dovoljno popunjeno
virtual-bots-guided-line = { $table }: igra { $game }, prioritet { $priority }, roboti { $assigned } (minimalno { $min_bots }, maksimalno { $max_bots }), čeka { $waiting }, nedostupno { $unavailable }, status { $status }, profil { $profile }, grupe { $groups }. { $table_state }. { $next_change } { $warning_text }
virtual-bots-groups-header = Grupe robota: { $count } oznake, { $bots } podešenih robota.
virtual-bots-groups-empty = Nema definisanih grupa robota.
virtual-bots-groups-line = { $group }: profil { $profile }, roboti { $total } (na mreži { $online }, čeka { $waiting }, u igri { $in_game }, van mreže { $offline }), pravila { $rules }.
virtual-bots-groups-no-rules = Nema
virtual-bots-no-profile = Podrazumevani
virtual-bots-profile-inherit-default = Preuzima podrazumevani profil
virtual-bots-profiles-header = Profili: { $count } definisano (podrazumevani: { $default_profile }).
virtual-bots-profiles-empty = Nema definisanih profila.
virtual-bots-profiles-line = { $profile } ({ $bot_count } robota) zamene: { $overrides }.
virtual-bots-profiles-no-overrides = Preuzima osnovnu konfiguraciju

localization-in-progress-try-again = Učitavanje prevoda u toku. Molimo pokušajte ponovo za minut.
