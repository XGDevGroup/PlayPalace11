# Main UI messages for PlayPalace

# Game categories
category-card-games = Jocuri de cărți
category-dice-games = Jocuri cu zaruri
category-rb-play-center = Centrul RB Play
category-poker = Poker
category-uncategorized = Fără categorie

# Menu titles
main-menu-title = Meniu principal
play-menu-title = Joacă
categories-menu-title = Categorii de jocuri
tables-menu-title = Mese disponibile

# Menu items
play = Joacă
view-active-tables = Vezi mesele active
options = Opțiuni
logout = Deconectare
back = Înapoi
go-back = Înapoi
context-menu = Meniu contextual.
no-actions-available = Nicio acțiune disponibilă.
create-table = Creează o masă nouă
join-as-player = Alătură-te ca jucător
join-as-spectator = Alătură-te ca spectator
leave-table = Părăsește masa
start-game = Începe jocul
add-bot = Adaugă bot
remove-bot = Elimină bot
actions-menu = Meniu acțiuni
save-table = Salvează masa
whose-turn = Al cui e rândul
whos-at-table = Cine e la masă
check-scores = Verifică scorurile
check-scores-detailed = Scoruri detaliate
check-game-options = Verifică opțiunile jocului
no-game-options = Nicio opțiune de joc disponibilă.

# Turn messages
game-player-skipped = { $player } este sărit.

# Table messages
table-created = { $host } a creat o masă nouă de { $game }.
table-joined = { $player } s-a alăturat la masă.
table-left = { $player } a părăsit masa.
new-host = { $player } este acum gazda.
waiting-for-players = Se așteaptă jucători. {$min} min, { $max } max.
game-starting = Jocul începe!
table-listing = Masa lui { $host } ({ $count } utilizatori)
table-listing-one = Masa lui { $host } ({ $count } utilizator)
table-listing-with = Masa lui { $host } ({ $count } utilizatori) cu { $members }
table-listing-game = { $game }: masa lui { $host } ({ $count } utilizatori)
table-listing-game-one = { $game }: masa lui { $host } ({ $count } utilizator)
table-listing-game-with = { $game }: masa lui { $host } ({ $count } utilizatori) cu { $members }
table-not-exists = Masa nu mai există.
table-full = Masa este plină.
player-replaced-by-bot = { $player } a plecat și a fost înlocuit de un bot.
player-took-over = { $player } a preluat de la bot.
spectator-joined = Te-ai alăturat la masa lui { $host } ca spectator.

# Spectator mode
spectate = Spectează
now-playing = { $player } joacă acum.
now-spectating = { $player } spectează acum.
spectator-left = { $player } a oprit să specteze.

# General
welcome = Bun venit la PlayPalace!
goodbye = La revedere!

# User presence announcements
user-online = { $player } a intrat online.
user-offline = { $player } a ieșit offline.
user-is-admin = { $player } este administrator al PlayPalace.
user-is-server-owner = { $player } este proprietarul serverului PlayPalace.
online-users-none = Niciun utilizator online.
online-users-one = 1 utilizator: { $users }
online-users-many = { $count } utilizatori: { $users }
online-user-not-in-game = Nu e în joc
online-user-waiting-approval = Așteaptă aprobare

# Options
language = Limbă
language-option = Limbă: { $language }
language-changed = Limba setată la { $language }.

# Boolean option states
option-on = Activ
option-off = Inactiv

# Sound options
turn-sound-option = Sunet tură: { $status }

# Dice options
clear-kept-option = Șterge zarurile păstrate la aruncare: { $status }
dice-keeping-style-option = Stil păstrare zaruri: { $style }
dice-keeping-style-changed = Stil păstrare zaruri setat la { $style }.
dice-keeping-style-indexes = Indici zaruri
dice-keeping-style-values = Valori zaruri

# Bot names
cancel = Anulează
no-bot-names-available = Niciun nume de bot disponibil.
select-bot-name = Selectează un nume pentru bot
enter-bot-name = Introdu numele botului
no-options-available = Nicio opțiune disponibilă.
no-scores-available = Niciun scor disponibil.

# Duration estimation
estimate-duration = Estimează durata
estimate-computing = Se calculează durata estimată a jocului...
estimate-result = Media bot: { $bot_time } (± { $std_dev }). { $outlier_info }Timp uman estimat: { $human_time }.
estimate-error = Nu s-a putut estima durata.
estimate-already-running = Estimarea duratei este deja în curs.

# Save/Restore
saved-tables = Mese salvate
no-saved-tables = Nu ai mese salvate.
no-active-tables = Nicio masă activă.
restore-table = Restaurează
delete-saved-table = Șterge
saved-table-deleted = Masă salvată ștearsă.
missing-players = Nu se poate restaura: acești jucători nu sunt disponibili: { $players }
table-restored = Masă restaurată! Toți jucătorii au fost transferați.
table-saved-destroying = Masă salvată! Revenire la meniul principal.
game-type-not-found = Tipul de joc nu mai există.

# Action disabled reasons
action-not-your-turn = Nu e rândul tău.
action-not-playing = Jocul nu a început.
action-spectator = Spectatorii nu pot face asta.
action-not-host = Doar gazda poate face asta.
action-game-in-progress = Nu se poate face în timp ce jocul e în desfășurare.
action-need-more-players = Sunt necesari mai mulți jucători pentru a începe.
action-table-full = Masa este plină.
action-no-bots = Nu sunt boți de eliminat.
action-bots-cannot = Boții nu pot face asta.
action-no-scores = Încă nu sunt scoruri disponibile.

# Dice actions
dice-not-rolled = Nu ai aruncat încă.
dice-locked = Acest zar este blocat.
dice-no-dice = Niciun zar disponibil.

# Game actions
game-turn-start = Rândul lui { $player }.
game-no-turn = Nimeni nu e la rând acum.
table-no-players = Niciun jucător.
table-players-one = { $count } jucător: { $players }.
table-players-many = { $count } jucători: { $players }.
table-spectators = Spectatori: { $spectators }.
game-leave = Pleacă
game-over = Joc terminat
game-final-scores = Scoruri finale
game-points = { $count } { $count ->
    [one] punct
    [few] puncte
   *[other] de puncte
}
play = Joacă

# Leaderboards
leaderboards = Clasamente
leaderboards-menu-title = Clasamente
leaderboards-select-game = Selectează un joc pentru a vedea clasamentul
leaderboard-no-data = Încă nu există date de clasament pentru acest joc.

# Leaderboard types
leaderboard-type-wins = Lideri după victorii
leaderboard-type-rating = Evaluare abilitate
leaderboard-type-total-score = Scor total
leaderboard-type-high-score = Scor maxim
leaderboard-type-games-played = Jocuri jucate
leaderboard-type-avg-points-per-turn = Puncte medii pe tură
leaderboard-type-best-single-turn = Cea mai bună tură
leaderboard-type-score-per-round = Scor pe rundă

# Leaderboard headers
leaderboard-wins-header = { $game } - Lideri după victorii
leaderboard-total-score-header = { $game } - Scor total
leaderboard-high-score-header = { $game } - Scor maxim
leaderboard-games-played-header = { $game } - Jocuri jucate
leaderboard-rating-header = { $game } - Evaluări abilitate
leaderboard-avg-points-header = { $game } - Puncte medii pe tură
leaderboard-best-turn-header = { $game } - Cea mai bună tură
leaderboard-score-per-round-header = { $game } - Scor pe rundă

# Leaderboard entries
leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] victorie
    [few] victorii
   *[other] de victorii
} { $losses } { $losses ->
    [one] înfrângere
    [few] înfrângeri
   *[other] de înfrângeri
}, { $percentage }% rată de victorie
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } medie
leaderboard-games-entry = { $rank }. { $player }: { $value } jocuri

# Player stats
leaderboard-player-stats = Statisticile tale: { $wins } victorii, { $losses } înfrângeri ({ $percentage }% rată de victorie)
leaderboard-no-player-stats = Nu ai jucat încă acest joc.

# Skill rating leaderboard
leaderboard-no-ratings = Încă nu există date de evaluare pentru acest joc.
leaderboard-rating-entry = { $rank }. { $player }: { $rating } evaluare ({ $mu } ± { $sigma })
leaderboard-player-rating = Evaluarea ta: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = Nu ai încă o evaluare pentru acest joc.

# My Stats menu
my-stats = Statisticile mele
my-stats-select-game = Selectează un joc pentru a vedea statisticile tale
my-stats-no-data = Nu ai jucat încă acest joc.
my-stats-no-games = Nu ai jucat încă niciun joc.
my-stats-header = { $game } - Statisticile tale
my-stats-wins = Victorii: { $value }
my-stats-losses = Înfrângeri: { $value }
my-stats-winrate = Rată de victorie: { $value }%
my-stats-games-played = Jocuri jucate: { $value }
my-stats-total-score = Scor total: { $value }
my-stats-high-score = Scor maxim: { $value }
my-stats-rating = Evaluare abilitate: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = Încă nu ai evaluare de abilitate
my-stats-avg-per-turn = Puncte medii pe tură: { $value }
my-stats-best-turn = Cea mai bună tură: { $value }

# Prediction system
predict-outcomes = Prezice rezultatele
predict-header = Rezultate prezise (după evaluarea abilității)
predict-entry = { $rank }. { $player } (evaluare: { $rating })
predict-entry-2p = { $rank }. { $player } (evaluare: { $rating }, { $probability }% șansă de victorie)
predict-unavailable = Predicțiile după evaluare nu sunt disponibile.
predict-need-players = Sunt necesari cel puțin 2 jucători umani pentru predicții.
action-need-more-humans = Sunt necesari mai mulți jucători umani.
confirm-leave-game = Ești sigur că vrei să părăsești masa?
confirm-yes = Da
confirm-no = Nu

# Administration
administration = Administrare
admin-menu-title = Administrare

# Account approval
account-approval = Aprobare cont
account-approval-menu-title = Aprobare cont
no-pending-accounts = Niciun cont în așteptare.
approve-account = Aprobă
decline-account = Refuză
account-approved = Contul lui { $player } a fost aprobat.
account-declined = Contul lui { $player } a fost refuzat și șters.

# Waiting for approval (shown to unapproved users)
waiting-for-approval = Contul tău așteaptă aprobarea unui administrator.
account-approved-welcome = Contul tău a fost aprobat! Bun venit la PlayPalace!
account-declined-goodbye = Cererea ta de cont a fost refuzată.
    Motiv:
account-banned = Contul tău este banat și nu poate fi accesat.

# Login errors
incorrect-username = Numele de utilizator introdus nu există.
incorrect-password = Parola introdusă este incorectă.
already-logged-in = Acest cont este deja conectat.

# Validarea credențialelor
credential-username-length = Numele de utilizator trebuie să aibă între { $min } și { $max } caractere.
credential-password-length = Parola trebuie să aibă între { $min } și { $max } caractere.

# Limitare tentative
rate-limit-login-ip = Prea multe încercări de conectare de la această adresă. Te rugăm să aștepți și să încerci din nou.
rate-limit-login-user = Prea multe încercări eșuate de conectare pentru acest nume de utilizator. Te rugăm să aștepți și să încerci din nou.
rate-limit-registration = Prea multe încercări de înregistrare de la această adresă. Te rugăm să aștepți și să încerci din nou.
rate-limit-refresh = Prea multe încercări de reîmprospătare de la această adresă. Te rugăm să aștepți și să încerci din nou.

# Erori de sesiune și autentificare
account-not-found = Contul nu a fost găsit.
session-expired = Sesiunea a expirat. Te rugăm să te conectezi din nou.
session-token-mismatch = Tokenul de sesiune nu corespunde numelui de utilizator.
refresh-token-expired = Tokenul de reîmprospătare a expirat. Te rugăm să te conectezi din nou.
refresh-token-mismatch = Tokenul de reîmprospătare nu corespunde numelui de utilizator.

# Înregistrare
registration-success = Înregistrare reușită! Contul tău așteaptă aprobarea.
registration-username-taken = Numele de utilizator este deja folosit. Te rugăm să alegi un alt nume de utilizator.

# Preferință implicită
pref-invalid-value = Selecție invalidă, se folosește valoarea implicită.

# Decline reason
decline-reason-prompt = Introdu un motiv pentru refuz (sau apasă Escape pentru anulare):
account-action-empty-reason = Niciun motiv dat.

# Admin notifications for account requests
account-request = cerere de cont
account-action = acțiune cont efectuată

# Admin promotion/demotion
promote-admin = Promovează administrator
demote-admin = Retrogradează administrator
promote-admin-menu-title = Promovează administrator
demote-admin-menu-title = Retrogradează administrator
no-users-to-promote = Niciun utilizator disponibil pentru promovare.
no-admins-to-demote = Niciun administrator disponibil pentru retrogradare.
confirm-promote = Ești sigur că vrei să-l promovezi pe { $player } la administrator?
confirm-demote = Ești sigur că vrei să-l retrogradezi pe { $player } de la administrator?
broadcast-to-all = Anunță la toți utilizatorii
broadcast-to-admins = Anunță doar la administratori
broadcast-to-nobody = Tăcut (fără anunț)
promote-announcement = { $player } a fost promovat la administrator!
promote-announcement-you = Ai fost promovat la administrator!
demote-announcement = { $player } a fost retrogradat de la administrator.
demote-announcement-you = Ai fost retrogradat de la administrator.
not-admin-anymore = Nu mai ești administrator și nu poți efectua această acțiune.
not-server-owner = Doar proprietarul serverului poate efectua această acțiune.

# Server ownership transfer
transfer-ownership = Transferă proprietatea
transfer-ownership-menu-title = Transferă proprietatea
no-admins-for-transfer = Niciun administrator disponibil pentru transferul proprietății.
confirm-transfer-ownership = Ești sigur că vrei să transferi proprietatea serverului către { $player }? Vei fi retrogradat la administrator.
transfer-ownership-announcement = { $player } este acum proprietarul serverului Play Palace!
transfer-ownership-announcement-you = Acum ești proprietarul serverului Play Palace!

# User banning
ban-user = Banează utilizator
unban-user = Debanează utilizator
no-users-to-ban = Niciun utilizator disponibil pentru banare.
no-users-to-unban = Niciun utilizator banat de debanat.
confirm-ban = Ești sigur că vrei să-l banezi pe { $player }?
confirm-unban = Ești sigur că vrei să-l debanezi pe { $player }?
ban-reason-prompt = Introdu un motiv pentru banare (opțional):
unban-reason-prompt = Introdu un motiv pentru debanare (opțional):
user-banned = { $player } a fost banat.
user-unbanned = { $player } a fost debanat.
you-have-been-banned = Ai fost banat de pe acest server.
    Motiv:
you-have-been-unbanned = Ai fost debanat de pe acest server.
    Motiv:
ban-no-reason = Niciun motiv dat.

# Virtual bots (server owner only)
virtual-bots = Boți virtuali
virtual-bots-fill = Umple serverul
virtual-bots-clear = Șterge toți boții
virtual-bots-status = Stare
virtual-bots-clear-confirm = Ești sigur că vrei să ștergi toți boții virtuali? Asta va distruge și toate mesele în care se află.
virtual-bots-not-available = Boții virtuali nu sunt disponibili.
virtual-bots-filled = Adăugați { $added } boți virtuali. { $online } sunt acum online.
virtual-bots-already-filled = Toți boții virtuali din configurație sunt deja activi.
virtual-bots-cleared = Șterși { $bots } boți virtuali și distruse { $tables } { $tables ->
    [one] masă
    [few] mese
   *[other] de mese
}.
virtual-bot-table-closed = Masă închisă de administrator.
virtual-bots-none-to-clear = Niciun bot virtual de șters.
virtual-bots-status-report = Boți virtuali: { $total } total, { $online } online, { $offline } offline, { $in_game } în joc.
virtual-bots-guided-overview = Mese ghidate
virtual-bots-groups-overview = Grupuri de boți
virtual-bots-profiles-overview = Profiluri
virtual-bots-guided-header = Mese ghidate: { $count } regulă/reguli. Alocare: { $allocation }, rezervă: { $fallback }, profil implicit: { $default_profile }.
virtual-bots-guided-empty = Nicio regulă de masă ghidată configurată.
virtual-bots-guided-status-active = activ
virtual-bots-guided-status-inactive = inactiv
virtual-bots-guided-table-linked = legată de masa { $table_id } (gazdă { $host }, jucători { $players }, umani { $humans })
virtual-bots-guided-table-stale = masa { $table_id } lipsește pe server
virtual-bots-guided-table-unassigned = nicio masă urmărită în prezent
virtual-bots-guided-next-change = următoarea schimbare în { $ticks } cicluri
virtual-bots-guided-no-schedule = nicio fereastră de programare
virtual-bots-guided-warning = ⚠ incomplet umplută
virtual-bots-guided-line = { $table }: joc { $game }, prioritate { $priority }, boți { $assigned } (min { $min_bots }, max { $max_bots }), în așteptare { $waiting }, indisponibil { $unavailable }, stare { $status }, profil { $profile }, grupuri { $groups }. { $table_state }. { $next_change } { $warning_text }
virtual-bots-groups-header = Grupuri de boți: { $count } etichetă/etichete, { $bots } boți configurați.
virtual-bots-groups-empty = Niciun grup de boți definit.
virtual-bots-groups-line = { $group }: profil { $profile }, boți { $total } (online { $online }, în așteptare { $waiting }, în joc { $in_game }, offline { $offline }), reguli { $rules }.
virtual-bots-groups-no-rules = niciuna
virtual-bots-no-profile = implicit
virtual-bots-profile-inherit-default = moștenește profilul implicit
virtual-bots-profiles-header = Profiluri: { $count } definite (implicit: { $default_profile }).
virtual-bots-profiles-empty = Niciun profil definit.
virtual-bots-profiles-line = { $profile } ({ $bot_count } boți) suprascrie: { $overrides }.
virtual-bots-profiles-no-overrides = moștenește configurația de bază

localization-in-progress-try-again = Localizarea este în curs. Vă rugăm să încercați din nou peste un minut.
