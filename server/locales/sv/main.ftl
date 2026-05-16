# Main UI messages for PlayPalace

# Game categories
category-card-games = Kortspel
category-dice-games = Tärningsspel
category-rb-play-center = RB Play-center
category-poker = Poker
category-uncategorized = Okategoriserad

# Menu titles
main-menu-title = Huvudmeny
play-menu-title = Spela
categories-menu-title = Spelkategorier
tables-menu-title = Tillgängliga bord

# Menu items
play = Spela
view-active-tables = Visa aktiva bord
options = Inställningar
logout = Logga ut
back = Tillbaka
go-back = Gå tillbaka
context-menu = Kontextmeny.
no-actions-available = Inga åtgärder tillgängliga.
create-table = Skapa nytt bord
join-as-player = Gå med som spelare
join-as-spectator = Gå med som åskådare
leave-table = Lämna bord
start-game = Starta spel
add-bot = Lägg till bot
remove-bot = Ta bort bot
actions-menu = Åtgärdsmeny
save-table = Spara bord
whose-turn = Vems tur
whos-at-table = Vem är vid bordet
check-scores = Kontrollera poäng
check-scores-detailed = Detaljerad poäng
check-game-options = Kontrollera spelalternativ
no-game-options = Inga spelalternativ tillgängliga.

# Turn messages
game-player-skipped = { $player } hoppas över.

# Table messages
table-created = { $host } skapade ett nytt { $game }-bord.
table-joined = { $player } gick med vid bordet.
table-left = { $player } lämnade bordet.
new-host = { $player } är nu värd.
waiting-for-players = Väntar på spelare. {$min} min, { $max } max.
game-starting = Spelet startar!
table-listing = { $host }s bord ({ $count } användare)
table-listing-one = { $host }s bord ({ $count } användare)
table-listing-with = { $host }s bord ({ $count } användare) med { $members }
table-listing-game = { $game }: { $host }s bord ({ $count } användare)
table-listing-game-one = { $game }: { $host }s bord ({ $count } användare)
table-listing-game-with = { $game }: { $host }s bord ({ $count } användare) med { $members }
table-not-exists = Bordet finns inte längre.
table-full = Bordet är fullt.
player-replaced-by-bot = { $player } lämnade och ersattes av en bot.
player-took-over = { $player } tog över från boten.
spectator-joined = Gick med vid { $host }s bord som åskådare.

# Spectator mode
spectate = Åskåda
now-playing = { $player } spelar nu.
now-spectating = { $player } åskådar nu.
spectator-left = { $player } slutade åskåda.

# General
welcome = Välkommen till PlayPalace!
goodbye = Hej då!

# User presence announcements
user-online = { $player } kom online.
user-offline = { $player } gick offline.
user-is-admin = { $player } är administratör för PlayPalace.
user-is-server-owner = { $player } är serverägare för PlayPalace.
online-users-none = Inga användare online.
online-users-one = 1 användare: { $users }
online-users-many = { $count } användare: { $users }
online-user-not-in-game = Inte i spel
online-user-waiting-approval = Väntar på godkännande

# Options
language = Språk
language-option = Språk: { $language }
language-changed = Språk inställt till { $language }.

# Boolean option states
option-on = På
option-off = Av

# Sound options
turn-sound-option = Dragljud: { $status }

# Dice options
clear-kept-option = Rensa sparade tärningar vid kast: { $status }
dice-keeping-style-option = Stil för att spara tärningar: { $style }
dice-keeping-style-changed = Stil för att spara tärningar inställd till { $style }.
dice-keeping-style-indexes = Tärningsindex
dice-keeping-style-values = Tärningsvärden

# Bot names
cancel = Avbryt
no-bot-names-available = Inga botnamn tillgängliga.
select-bot-name = Välj ett namn för boten
enter-bot-name = Ange botnamn
no-options-available = Inga alternativ tillgängliga.
no-scores-available = Inga poäng tillgängliga.

# Duration estimation
estimate-duration = Uppskatta varaktighet
estimate-computing = Beräknar uppskattad spelvaraktighet...
estimate-result = Bot-genomsnitt: { $bot_time } (± { $std_dev }). { $outlier_info }Uppskattad mänsklig tid: { $human_time }.
estimate-error = Kunde inte uppskatta varaktighet.
estimate-already-running = Varaktighetsuppskattning pågår redan.

# Save/Restore
saved-tables = Sparade bord
no-saved-tables = Du har inga sparade bord.
no-active-tables = Inga aktiva bord.
restore-table = Återställ
delete-saved-table = Ta bort
saved-table-deleted = Sparat bord borttaget.
missing-players = Kan inte återställa: dessa spelare är inte tillgängliga: { $players }
table-restored = Bord återställt! Alla spelare har överförts.
table-saved-destroying = Bord sparat! Återgår till huvudmenyn.
game-type-not-found = Speltypen finns inte längre.

# Action disabled reasons
action-not-your-turn = Det är inte din tur.
action-not-playing = Spelet har inte startat.
action-spectator = Åskådare kan inte göra detta.
action-not-host = Endast värden kan göra detta.
action-game-in-progress = Kan inte göra detta medan spelet pågår.
action-need-more-players = Behöver fler spelare för att starta.
action-table-full = Bordet är fullt.
action-no-bots = Det finns inga botar att ta bort.
action-bots-cannot = Botar kan inte göra detta.
action-no-scores = Inga poäng tillgängliga ännu.

# Dice actions
dice-not-rolled = Du har inte kastat ännu.
dice-locked = Denna tärning är låst.
dice-no-dice = Inga tärningar tillgängliga.

# Game actions
game-turn-start = { $player }s tur.
game-no-turn = Ingen har turen just nu.
table-no-players = Inga spelare.
table-players-one = { $count } spelare: { $players }.
table-players-many = { $count } spelare: { $players }.
table-spectators = Åskådare: { $spectators }.
game-leave = Lämna
game-over = Spelet slut
game-final-scores = Slutpoäng
game-points = { $count } { $count ->
    [one] poäng
   *[other] poäng
}
play = Spela

# Leaderboards
leaderboards = Topplistan
leaderboards-menu-title = Topplistan
leaderboards-select-game = Välj ett spel för att visa dess topplista
leaderboard-no-data = Ingen topplistedata ännu för detta spel.

# Leaderboard types
leaderboard-type-wins = Vinstledare
leaderboard-type-rating = Färdighetsbetyg
leaderboard-type-total-score = Totalpoäng
leaderboard-type-high-score = Högsta poäng
leaderboard-type-games-played = Spelade spel
leaderboard-type-avg-points-per-turn = Genomsnittliga poäng per drag
leaderboard-type-best-single-turn = Bästa enskilda drag
leaderboard-type-score-per-round = Poäng per omgång

# Leaderboard headers
leaderboard-wins-header = { $game } - Vinstledare
leaderboard-total-score-header = { $game } - Totalpoäng
leaderboard-high-score-header = { $game } - Högsta poäng
leaderboard-games-played-header = { $game } - Spelade spel
leaderboard-rating-header = { $game } - Färdighetsbetyg
leaderboard-avg-points-header = { $game } - Genomsnittliga poäng per drag
leaderboard-best-turn-header = { $game } - Bästa enskilda drag
leaderboard-score-per-round-header = { $game } - Poäng per omgång

# Leaderboard entries
leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] vinst
   *[other] vinster
} { $losses } { $losses ->
    [one] förlust
   *[other] förluster
}, { $percentage }% vinstprocent
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } snitt
leaderboard-games-entry = { $rank }. { $player }: { $value } spel

# Player stats
leaderboard-player-stats = Din statistik: { $wins } vinster, { $losses } förluster ({ $percentage }% vinstprocent)
leaderboard-no-player-stats = Du har inte spelat detta spel än.

# Skill rating leaderboard
leaderboard-no-ratings = Ingen betygsinformation ännu för detta spel.
leaderboard-rating-entry = { $rank }. { $player }: { $rating } betyg ({ $mu } ± { $sigma })
leaderboard-player-rating = Ditt betyg: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = Du har inget betyg för detta spel än.

# My Stats menu
my-stats = Min statistik
my-stats-select-game = Välj ett spel för att visa din statistik
my-stats-no-data = Du har inte spelat detta spel än.
my-stats-no-games = Du har inte spelat några spel än.
my-stats-header = { $game } - Din statistik
my-stats-wins = Vinster: { $value }
my-stats-losses = Förluster: { $value }
my-stats-winrate = Vinstprocent: { $value }%
my-stats-games-played = Spelade spel: { $value }
my-stats-total-score = Totalpoäng: { $value }
my-stats-high-score = Högsta poäng: { $value }
my-stats-rating = Färdighetsbetyg: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = Inget färdighetsbetyg ännu
my-stats-avg-per-turn = Genomsnittliga poäng per drag: { $value }
my-stats-best-turn = Bästa enskilda drag: { $value }

# Prediction system
predict-outcomes = Förutse resultat
predict-header = Förutsedda resultat (efter färdighetsbetyg)
predict-entry = { $rank }. { $player } (betyg: { $rating })
predict-entry-2p = { $rank }. { $player } (betyg: { $rating }, { $probability }% vinst chans)
predict-unavailable = Betygsprognoser är inte tillgängliga.
predict-need-players = Behöver minst 2 mänskliga spelare för prognoser.
action-need-more-humans = Behöver fler mänskliga spelare.
confirm-leave-game = Är du säker på att du vill lämna bordet?
confirm-yes = Ja
confirm-no = Nej

# Administration
administration = Administration
admin-menu-title = Administration

# Account approval
account-approval = Kontogodkännande
account-approval-menu-title = Kontogodkännande
no-pending-accounts = Inga väntande konton.
approve-account = Godkänn
decline-account = Avslå
account-approved = { $player }s konto har godkänts.
account-declined = { $player }s konto har avslagits och raderats.

# Waiting for approval (shown to unapproved users)
waiting-for-approval = Ditt konto väntar på godkännande av en administratör.
account-approved-welcome = Ditt konto har godkänts! Välkommen till PlayPalace!
account-declined-goodbye = Din kontoansökan har avslagits.
    Anledning:
account-banned = Ditt konto är avstängt och kan inte nås.

# Login errors
incorrect-username = Användarnamnet du angav finns inte.
incorrect-password = Lösenordet du angav är felaktigt.
already-logged-in = Detta konto är redan inloggat.

# Credential validation
credential-username-length = Användarnamnet måste vara mellan { $min } och { $max } tecken.
credential-password-length = Lösenordet måste vara mellan { $min } och { $max } tecken.

# Rate limiting
rate-limit-login-ip = För många inloggningsförsök från den här adressen. Vänta och försök igen.
rate-limit-login-user = För många misslyckade inloggningsförsök för det här användarnamnet. Vänta och försök igen.
rate-limit-registration = För många registreringsförsök från den här adressen. Vänta och försök igen.
rate-limit-refresh = För många uppdateringsförsök från den här adressen. Vänta och försök igen.

# Session/auth errors
account-not-found = Kontot hittades inte.
session-expired = Sessionen har gått ut. Logga in igen.
session-token-mismatch = Sessionstoken matchar inte användarnamnet.
refresh-token-expired = Uppdateringstoken har gått ut. Logga in igen.
refresh-token-mismatch = Uppdateringstoken matchar inte användarnamnet.

# Registration
registration-success = Registreringen lyckades! Ditt konto väntar på godkännande.
registration-username-taken = Användarnamnet är redan taget. Välj ett annat användarnamn.

# Preference fallback
pref-invalid-value = Ogiltigt val, använder standard.

# Decline reason
decline-reason-prompt = Ange en anledning för avslag (eller tryck Escape för att avbryta):
account-action-empty-reason = Ingen anledning angiven.

# Admin notifications for account requests
account-request = kontoansökan
account-action = kontoåtgärd vidtagen

# Admin promotion/demotion
promote-admin = Befordra administratör
demote-admin = Degradera administratör
promote-admin-menu-title = Befordra administratör
demote-admin-menu-title = Degradera administratör
no-users-to-promote = Inga användare tillgängliga att befordra.
no-admins-to-demote = Inga administratörer tillgängliga att degradera.
confirm-promote = Är du säker på att du vill befordra { $player } till administratör?
confirm-demote = Är du säker på att du vill degradera { $player } från administratör?
broadcast-to-all = Meddela alla användare
broadcast-to-admins = Meddela endast administratörer
broadcast-to-nobody = Tyst (inget meddelande)
promote-announcement = { $player } har befordrats till administratör!
promote-announcement-you = Du har befordrats till administratör!
demote-announcement = { $player } har degraderats från administratör.
demote-announcement-you = Du har degraderats från administratör.
not-admin-anymore = Du är inte längre administratör och kan inte utföra denna åtgärd.
not-server-owner = Endast serverägaren kan utföra denna åtgärd.

# Server ownership transfer
transfer-ownership = Överför ägarskap
transfer-ownership-menu-title = Överför ägarskap
no-admins-for-transfer = Inga administratörer tillgängliga att överföra ägarskap till.
confirm-transfer-ownership = Är du säker på att du vill överföra serverägarskapet till { $player }? Du kommer att degraderas till administratör.
transfer-ownership-announcement = { $player } är nu Play Palace-serverägare!
transfer-ownership-announcement-you = Du är nu Play Palace-serverägare!

# User banning
ban-user = Stäng av användare
unban-user = Häv avstängning
no-users-to-ban = Inga användare tillgängliga att stänga av.
no-users-to-unban = Inga avstängda användare att häva avstängning för.
confirm-ban = Är du säker på att du vill stänga av { $player }?
confirm-unban = Är du säker på att du vill häva avstängningen av { $player }?
ban-reason-prompt = Ange en anledning för avstängning (valfritt):
unban-reason-prompt = Ange en anledning för att häva avstängning (valfritt):
user-banned = { $player } har stängts av.
user-unbanned = { $player }s avstängning har hävts.
you-have-been-banned = Du har stängts av från denna server.
    Anledning:
you-have-been-unbanned = Din avstängning från denna server har hävts.
    Anledning:
ban-no-reason = Ingen anledning angiven.

# Virtual bots (server owner only)
virtual-bots = Virtuella botar
virtual-bots-fill = Fyll server
virtual-bots-clear = Rensa alla botar
virtual-bots-status = Status
virtual-bots-clear-confirm = Är du säker på att du vill rensa alla virtuella botar? Detta kommer också att förstöra alla bord de är vid.
virtual-bots-not-available = Virtuella botar är inte tillgängliga.
virtual-bots-filled = Lade till { $added } virtuella botar. { $online } är nu online.
virtual-bots-already-filled = Alla virtuella botar från konfigurationen är redan aktiva.
virtual-bots-cleared = Rensade { $bots } virtuella botar och förstörde { $tables } { $tables ->
    [one] bord
   *[other] bord
}.
virtual-bot-table-closed = Bordet stängt av administratör.
virtual-bots-none-to-clear = Inga virtuella botar att rensa.
virtual-bots-status-report = Virtuella botar: { $total } totalt, { $online } online, { $offline } offline, { $in_game } i spel.
virtual-bots-guided-overview = Styrda bord
virtual-bots-groups-overview = Botgrupper
virtual-bots-profiles-overview = Profiler
virtual-bots-guided-header = Styrda bord: { $count } regel/regler. Allokering: { $allocation }, reserv: { $fallback }, standardprofil: { $default_profile }.
virtual-bots-guided-empty = Inga styrda bordregler är konfigurerade.
virtual-bots-guided-status-active = aktiv
virtual-bots-guided-status-inactive = inaktiv
virtual-bots-guided-table-linked = länkat till bord { $table_id } (värd { $host }, spelare { $players }, människor { $humans })
virtual-bots-guided-table-stale = bord { $table_id } saknas på servern
virtual-bots-guided-table-unassigned = inget bord spåras för närvarande
virtual-bots-guided-next-change = nästa ändring om { $ticks } ticks
virtual-bots-guided-no-schedule = inget schemaläggningsfönster
virtual-bots-guided-warning = ⚠ underifyllt
virtual-bots-guided-line = { $table }: spel { $game }, prioritet { $priority }, botar { $assigned } (min { $min_bots }, max { $max_bots }), väntar { $waiting }, otillgänglig { $unavailable }, status { $status }, profil { $profile }, grupper { $groups }. { $table_state }. { $next_change } { $warning_text }
virtual-bots-groups-header = Botgrupper: { $count } tagg/taggar, { $bots } konfigurerade botar.
virtual-bots-groups-empty = Inga botgrupper är definierade.
virtual-bots-groups-line = { $group }: profil { $profile }, botar { $total } (online { $online }, väntar { $waiting }, i spel { $in_game }, offline { $offline }), regler { $rules }.
virtual-bots-groups-no-rules = inga
virtual-bots-no-profile = standard
virtual-bots-profile-inherit-default = ärver standardprofil
virtual-bots-profiles-header = Profiler: { $count } definierade (standard: { $default_profile }).
virtual-bots-profiles-empty = Inga profiler är definierade.
virtual-bots-profiles-line = { $profile } ({ $bot_count } botar) åsidosätter: { $overrides }.
virtual-bots-profiles-no-overrides = ärver baskonfiguration

localization-in-progress-try-again = Lokalisering pågår. Försök igen om en minut.
