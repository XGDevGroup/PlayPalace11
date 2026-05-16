# Main UI messages for PlayPalace

# Game categories
category-card-games = Kártyajátékok
category-dice-games = Kockajátékok
category-rb-play-center = RB Play központ
category-poker = Póker
category-uncategorized = Kategorizálatlan

# Menu titles
main-menu-title = Főmenü
play-menu-title = Játék
categories-menu-title = Játékkategóriák
tables-menu-title = Elérhető asztalok

# Menu items
play = Játék
view-active-tables = Aktív asztalok megtekintése
options = Beállítások
logout = Kijelentkezés
back = Vissza
go-back = Vissza
context-menu = Helyi menü.
no-actions-available = Nincsenek elérhető műveletek.
create-table = Új asztal létrehozása
join-as-player = Csatlakozás játékosként
join-as-spectator = Csatlakozás nézőként
leave-table = Asztal elhagyása
start-game = Játék indítása
add-bot = Bot hozzáadása
remove-bot = Bot eltávolítása
actions-menu = Műveletek menü
save-table = Asztal mentése
whose-turn = Kié a lépés
whos-at-table = Ki van az asztalnál
check-scores = Eredmények ellenőrzése
check-scores-detailed = Részletes eredmények
check-game-options = Játékbeállítások ellenőrzése
no-game-options = Nincsenek játékbeállítások.

# Turn messages
game-player-skipped = { $player } ki van hagyva.

# Table messages
table-created = { $host } új { $game } asztalt hozott létre.
table-joined = { $player } csatlakozott az asztalhoz.
table-left = { $player } elhagyta az asztalt.
new-host = { $player } most a házigazda.
waiting-for-players = Játékosokra várunk. {$min} min, { $max } max.
game-starting = Játék indul!
table-listing = { $host } asztala ({ $count } felhasználó)
table-listing-one = { $host } asztala ({ $count } felhasználó)
table-listing-with = { $host } asztala ({ $count } felhasználó) { $members } társaságával
table-listing-game = { $game }: { $host } asztala ({ $count } felhasználó)
table-listing-game-one = { $game }: { $host } asztala ({ $count } felhasználó)
table-listing-game-with = { $game }: { $host } asztala ({ $count } felhasználó) { $members } társaságával
table-not-exists = Az asztal már nem létezik.
table-full = Az asztal megtelt.
player-replaced-by-bot = { $player } kilépett és egy bot váltotta fel.
player-took-over = { $player } átvette a bot helyét.
spectator-joined = Csatlakoztál { $host } asztalához nézőként.

# Spectator mode
spectate = Nézés
now-playing = { $player } most játszik.
now-spectating = { $player } most nézi a játékot.
spectator-left = { $player } abbahagyta a nézést.

# General
welcome = Üdvözlünk a PlayPalace-ban!
goodbye = Viszlát!

# User presence announcements
user-online = { $player } online lett.
user-offline = { $player } offline lett.
user-is-admin = { $player } a PlayPalace adminisztrátora.
user-is-server-owner = { $player } a PlayPalace szerver tulajdonosa.
online-users-none = Nincsenek online felhasználók.
online-users-one = 1 felhasználó: { $users }
online-users-many = { $count } felhasználó: { $users }
online-user-not-in-game = Nincs játékban
online-user-waiting-approval = Jóváhagyásra vár

# Options
language = Nyelv
language-option = Nyelv: { $language }
language-changed = Nyelv beállítva: { $language }.

# Boolean option states
option-on = Be
option-off = Ki

# Sound options
turn-sound-option = Lépés hang: { $status }

# Dice options
clear-kept-option = Megtartott kockák törlése dobáskor: { $status }
dice-keeping-style-option = Kockamegtartási stílus: { $style }
dice-keeping-style-changed = Kockamegtartási stílus beállítva: { $style }.
dice-keeping-style-indexes = Kockaindexek
dice-keeping-style-values = Kockaértékek

# Bot names
cancel = Mégse
no-bot-names-available = Nincsenek elérhető botnevek.
select-bot-name = Válassz nevet a botnak
enter-bot-name = Add meg a bot nevét
no-options-available = Nincsenek elérhető beállítások.
no-scores-available = Nincsenek elérhető eredmények.

# Duration estimation
estimate-duration = Időtartam becslése
estimate-computing = Játék időtartamának kiszámítása...
estimate-result = Bot átlag: { $bot_time } (± { $std_dev }). { $outlier_info }Becsült emberi idő: { $human_time }.
estimate-error = Nem sikerült az időtartam becslése.
estimate-already-running = Az időtartam becslése már folyamatban van.

# Save/Restore
saved-tables = Mentett asztalok
no-saved-tables = Nincsenek mentett asztalaid.
no-active-tables = Nincsenek aktív asztalok.
restore-table = Visszaállítás
delete-saved-table = Törlés
saved-table-deleted = Mentett asztal törölve.
missing-players = Nem lehet visszaállítani: ezek a játékosok nem elérhetők: { $players }
table-restored = Asztal visszaállítva! Minden játékos áthelyezve.
table-saved-destroying = Asztal mentve! Vissza a főmenübe.
game-type-not-found = A játéktípus már nem létezik.

# Action disabled reasons
action-not-your-turn = Nem te vagy soron.
action-not-playing = A játék még nem kezdődött el.
action-spectator = A nézők nem tehetik ezt meg.
action-not-host = Csak a házigazda teheti ezt meg.
action-game-in-progress = Nem lehet megtenni játék közben.
action-need-more-players = Több játékos szükséges az indításhoz.
action-table-full = Az asztal megtelt.
action-no-bots = Nincsenek eltávolítható botok.
action-bots-cannot = A botok nem tehetik ezt meg.
action-no-scores = Még nincsenek elérhető eredmények.

# Dice actions
dice-not-rolled = Még nem dobtál.
dice-locked = Ez a kocka zárolva van.
dice-no-dice = Nincsenek elérhető kockák.

# Game actions
game-turn-start = { $player } lép.
game-no-turn = Most senki sem lép.
table-no-players = Nincsenek játékosok.
table-players-one = { $count } játékos: { $players }.
table-players-many = { $count } játékos: { $players }.
table-spectators = Nézők: { $spectators }.
game-leave = Kilépés
game-over = Játék vége
game-final-scores = Végeredmények
game-points = { $count } { $count ->
    [one] pont
   *[other] pont
}
play = Játék

# Leaderboards
leaderboards = Ranglisták
leaderboards-menu-title = Ranglisták
leaderboards-select-game = Válassz egy játékot a ranglista megtekintéséhez
leaderboard-no-data = Még nincsenek ranglista adatok ehhez a játékhoz.

# Leaderboard types
leaderboard-type-wins = Győzelmek ranglistája
leaderboard-type-rating = Képességértékelés
leaderboard-type-total-score = Összpontszám
leaderboard-type-high-score = Legmagasabb pontszám
leaderboard-type-games-played = Játszott játékok
leaderboard-type-avg-points-per-turn = Átlagos pont lépésenként
leaderboard-type-best-single-turn = Legjobb egyetlen lépés
leaderboard-type-score-per-round = Pontszám körönként

# Leaderboard headers
leaderboard-wins-header = { $game } - Győzelmek ranglistája
leaderboard-total-score-header = { $game } - Összpontszám
leaderboard-high-score-header = { $game } - Legmagasabb pontszám
leaderboard-games-played-header = { $game } - Játszott játékok
leaderboard-rating-header = { $game } - Képességértékelések
leaderboard-avg-points-header = { $game } - Átlagos pont lépésenként
leaderboard-best-turn-header = { $game } - Legjobb egyetlen lépés
leaderboard-score-per-round-header = { $game } - Pontszám körönként

# Leaderboard entries
leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] győzelem
   *[other] győzelem
} { $losses } { $losses ->
    [one] vereség
   *[other] vereség
}, { $percentage }% győzelmi arány
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } átlag
leaderboard-games-entry = { $rank }. { $player }: { $value } játék

# Player stats
leaderboard-player-stats = Statisztikáid: { $wins } győzelem, { $losses } vereség ({ $percentage }% győzelmi arány)
leaderboard-no-player-stats = Még nem játszottad ezt a játékot.

# Skill rating leaderboard
leaderboard-no-ratings = Még nincsenek értékelési adatok ehhez a játékhoz.
leaderboard-rating-entry = { $rank }. { $player }: { $rating } értékelés ({ $mu } ± { $sigma })
leaderboard-player-rating = Értékelésed: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = Még nincs értékelésed ehhez a játékhoz.

# My Stats menu
my-stats = Statisztikáim
my-stats-select-game = Válassz egy játékot a statisztikák megtekintéséhez
my-stats-no-data = Még nem játszottad ezt a játékot.
my-stats-no-games = Még nem játszottál egyetlen játékot sem.
my-stats-header = { $game } - Statisztikáid
my-stats-wins = Győzelmek: { $value }
my-stats-losses = Vereségek: { $value }
my-stats-winrate = Győzelmi arány: { $value }%
my-stats-games-played = Játszott játékok: { $value }
my-stats-total-score = Összpontszám: { $value }
my-stats-high-score = Legmagasabb pontszám: { $value }
my-stats-rating = Képességértékelés: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = Még nincs képességértékelés
my-stats-avg-per-turn = Átlagos pont lépésenként: { $value }
my-stats-best-turn = Legjobb egyetlen lépés: { $value }

# Prediction system
predict-outcomes = Eredmények előrejelzése
predict-header = Előrejelzett eredmények (képességértékelés alapján)
predict-entry = { $rank }. { $player } (értékelés: { $rating })
predict-entry-2p = { $rank }. { $player } (értékelés: { $rating }, { $probability }% győzelmi esély)
predict-unavailable = Az értékelés alapú előrejelzések nem elérhetők.
predict-need-players = Legalább 2 emberi játékos szükséges az előrejelzésekhez.
action-need-more-humans = Több emberi játékos szükséges.
confirm-leave-game = Biztosan el akarod hagyni az asztalt?
confirm-yes = Igen
confirm-no = Nem

# Administration
administration = Adminisztráció
admin-menu-title = Adminisztráció

# Account approval
account-approval = Fiók jóváhagyása
account-approval-menu-title = Fiók jóváhagyása
no-pending-accounts = Nincsenek függőben lévő fiókok.
approve-account = Jóváhagyás
decline-account = Elutasítás
account-approved = { $player } fiókja jóváhagyva.
account-declined = { $player } fiókja elutasítva és törölve.

# Waiting for approval (shown to unapproved users)
waiting-for-approval = A fiókod adminisztrátori jóváhagyásra vár.
account-approved-welcome = A fiókod jóváhagyva! Üdvözlünk a PlayPalace-ban!
account-declined-goodbye = A fiókregisztrációd elutasítva.
    Indok:
account-banned = A fiókod tiltva van és nem érhető el.

# Login errors
incorrect-username = A megadott felhasználónév nem létezik.
incorrect-password = A megadott jelszó helytelen.
already-logged-in = Ez a fiók már be van jelentkezve.

# Hitelesítő adatok ellenőrzése
credential-username-length = A felhasználónévnek { $min } és { $max } karakter között kell lennie.
credential-password-length = A jelszónak { $min } és { $max } karakter között kell lennie.

# Sebességkorlátozás
rate-limit-login-ip = Túl sok bejelentkezési kísérlet érkezett erről a címről. Várj és próbáld újra.
rate-limit-login-user = Túl sok sikertelen bejelentkezési kísérlet történt ehhez a felhasználónévhez. Várj és próbáld újra.
rate-limit-registration = Túl sok regisztrációs kísérlet érkezett erről a címről. Várj és próbáld újra.
rate-limit-refresh = Túl sok frissítési kísérlet érkezett erről a címről. Várj és próbáld újra.

# Munkamenet- és hitelesítési hibák
account-not-found = A fiók nem található.
session-expired = A munkamenet lejárt. Jelentkezz be újra.
session-token-mismatch = A munkamenet-token nem egyezik a felhasználónévvel.
refresh-token-expired = A frissítési token lejárt. Jelentkezz be újra.
refresh-token-mismatch = A frissítési token nem egyezik a felhasználónévvel.

# Regisztráció
registration-success = Sikeres regisztráció! A fiókod jóváhagyásra vár.
registration-username-taken = Ez a felhasználónév már foglalt. Válassz másikat.

# Beállítás alapértelmezett értéke
pref-invalid-value = Érvénytelen választás, az alapértelmezett értéket használja.

# Decline reason
decline-reason-prompt = Add meg az elutasítás indokát (vagy nyomd meg az Escape-et a visszavonáshoz):
account-action-empty-reason = Nincs megadva indok.

# Admin notifications for account requests
account-request = fiók regisztrációs kérelem
account-action = fiókművelet végrehajtva

# Admin promotion/demotion
promote-admin = Adminisztrátor kinevezése
demote-admin = Adminisztrátor lefokozása
promote-admin-menu-title = Adminisztrátor kinevezése
demote-admin-menu-title = Adminisztrátor lefokozása
no-users-to-promote = Nincsenek kinevezésre alkalmas felhasználók.
no-admins-to-demote = Nincsenek lefokozásra alkalmas adminisztrátorok.
confirm-promote = Biztosan ki akarod nevezni { $player }-t adminisztrátornak?
confirm-demote = Biztosan le akarod fokozni { $player }-t az adminisztrátori pozícióból?
broadcast-to-all = Bejelentés minden felhasználónak
broadcast-to-admins = Bejelentés csak adminisztrátoroknak
broadcast-to-nobody = Csendes (nincs bejelentés)
promote-announcement = { $player } adminisztrátorrá lett kinevezve!
promote-announcement-you = Adminisztrátorrá lettél kinevezve!
demote-announcement = { $player } le lett fokozva az adminisztrátori pozícióból.
demote-announcement-you = Le lettél fokozva az adminisztrátori pozícióból.
not-admin-anymore = Már nem vagy adminisztrátor és nem hajthatod végre ezt a műveletet.
not-server-owner = Csak a szerver tulajdonosa hajthatja végre ezt a műveletet.

# Server ownership transfer
transfer-ownership = Tulajdonjog átruházása
transfer-ownership-menu-title = Tulajdonjog átruházása
no-admins-for-transfer = Nincsenek adminisztrátorok a tulajdonjog átruházásához.
confirm-transfer-ownership = Biztosan át akarod ruházni a szerver tulajdonjogát { $player }-re? Adminisztrátorrá leszel lefokozva.
transfer-ownership-announcement = { $player } most a Play Palace szerver tulajdonosa!
transfer-ownership-announcement-you = Most te vagy a Play Palace szerver tulajdonosa!

# User banning
ban-user = Felhasználó tiltása
unban-user = Felhasználó tiltásának feloldása
no-users-to-ban = Nincsenek tiltásra alkalmas felhasználók.
no-users-to-unban = Nincsenek tiltás feloldására alkalmas felhasználók.
confirm-ban = Biztosan tiltani akarod { $player }-t?
confirm-unban = Biztosan fel akarod oldani { $player } tiltását?
ban-reason-prompt = Add meg a tiltás indokát (opcionális):
unban-reason-prompt = Add meg a tiltás feloldásának indokát (opcionális):
user-banned = { $player } tiltva.
user-unbanned = { $player } tiltása feloldva.
you-have-been-banned = Tiltva lettél erről a szerverről.
    Indok:
you-have-been-unbanned = Tiltásod feloldva erről a szerverről.
    Indok:
ban-no-reason = Nincs megadva indok.

# Virtual bots (server owner only)
virtual-bots = Virtuális botok
virtual-bots-fill = Szerver feltöltése
virtual-bots-clear = Összes bot törlése
virtual-bots-status = Állapot
virtual-bots-clear-confirm = Biztosan törölni akarod az összes virtuális botot? Ez az általuk létrehozott asztalokat is megsemmisíti.
virtual-bots-not-available = A virtuális botok nem elérhetők.
virtual-bots-filled = { $added } virtuális bot hozzáadva. { $online } van online.
virtual-bots-already-filled = A konfigurációból minden virtuális bot már aktív.
virtual-bots-cleared = { $bots } virtuális bot törölve és { $tables } { $tables ->
    [one] asztal
   *[other] asztal
} megsemmisítve.
virtual-bot-table-closed = Asztal adminisztrátor által bezárva.
virtual-bots-none-to-clear = Nincsenek törlendő virtuális botok.
virtual-bots-status-report = Virtuális botok: { $total } összesen, { $online } online, { $offline } offline, { $in_game } játékban.
virtual-bots-guided-overview = Irányított asztalok
virtual-bots-groups-overview = Bot csoportok
virtual-bots-profiles-overview = Profilok
virtual-bots-guided-header = Irányított asztalok: { $count } szabály. Allokáció: { $allocation }, tartalék: { $fallback }, alapértelmezett profil: { $default_profile }.
virtual-bots-guided-empty = Nincsenek konfigurálva irányított asztal szabályok.
virtual-bots-guided-status-active = aktív
virtual-bots-guided-status-inactive = inaktív
virtual-bots-guided-table-linked = csatolva a(z) { $table_id } asztalhoz (házigazda { $host }, játékosok { $players }, emberek { $humans })
virtual-bots-guided-table-stale = { $table_id } asztal hiányzik a szerverről
virtual-bots-guided-table-unassigned = jelenleg nincs követett asztal
virtual-bots-guided-next-change = következő változás { $ticks } ciklus múlva
virtual-bots-guided-no-schedule = nincs ütemezési időszak
virtual-bots-guided-warning = ⚠ nem elég játékos
virtual-bots-guided-line = { $table }: játék { $game }, prioritás { $priority }, botok { $assigned } (min { $min_bots }, max { $max_bots }), várakozó { $waiting }, nem elérhető { $unavailable }, állapot { $status }, profil { $profile }, csoportok { $groups }. { $table_state }. { $next_change } { $warning_text }
virtual-bots-groups-header = Bot csoportok: { $count } címke, { $bots } konfigurált bot.
virtual-bots-groups-empty = Nincsenek definiált bot csoportok.
virtual-bots-groups-line = { $group }: profil { $profile }, botok { $total } (online { $online }, várakozó { $waiting }, játékban { $in_game }, offline { $offline }), szabályok { $rules }.
virtual-bots-groups-no-rules = nincs
virtual-bots-no-profile = alapértelmezett
virtual-bots-profile-inherit-default = örökli az alapértelmezett profilt
virtual-bots-profiles-header = Profilok: { $count } definiálva (alapértelmezett: { $default_profile }).
virtual-bots-profiles-empty = Nincsenek definiált profilok.
virtual-bots-profiles-line = { $profile } ({ $bot_count } bot) felülírások: { $overrides }.
virtual-bots-profiles-no-overrides = örökli az alap konfigurációt

localization-in-progress-try-again = A lokalizáció folyamatban van. Kérjük, próbálja újra egy perc múlva.
