# Hlavní UI zprávy pro PlayPalace

# Kategorie her
category-card-games = Karetní hry
category-dice-games = Hry s kostkami
category-rb-play-center = RB Play Center
category-poker = Poker
category-uncategorized = Nezařazené

# Názvy menu
main-menu-title = Hlavní menu
play-menu-title = Hrát
categories-menu-title = Kategorie her
tables-menu-title = Dostupné stoly

# Položky menu
play = Hrát
view-active-tables = Zobrazit aktivní stoly
options = Možnosti
logout = Odhlásit se
back = Zpět
go-back = Jít zpět
context-menu = Kontextové menu.
no-actions-available = Žádné akce k dispozici.
create-table = Vytvořit nový stůl
join-as-player = Připojit se jako hráč
join-as-spectator = Připojit se jako divák
leave-table = Opustit stůl
start-game = Začít hru
add-bot = Přidat bota
remove-bot = Odebrat bota
actions-menu = Menu akcí
save-table = Uložit stůl
whose-turn = Čí je tah
whos-at-table = Kdo je u stolu
check-scores = Zkontrolovat skóre
check-scores-detailed = Podrobné skóre
check-game-options = Zkontrolovat herní možnosti
no-game-options = Žádné herní možnosti.

# Zprávy o tahu
game-player-skipped = { $player } je přeskočen.

# Zprávy o stolu
table-created = { $host } vytvořil nový stůl pro { $game }.
table-joined = { $player } se připojil ke stolu.
table-left = { $player } opustil stůl.
new-host = { $player } je nyní hostitelem.
waiting-for-players = Čeká se na hráče. {$min} min, { $max } max.
game-starting = Hra začíná!
table-listing = Stůl hráče { $host } ({ $count } { $count ->
    [one] uživatel
    [few] uživatelé
    [many] uživatele
   *[other] uživatelů
})
table-listing-one = Stůl hráče { $host } ({ $count } uživatel)
table-listing-with = Stůl hráče { $host } ({ $count } { $count ->
    [one] uživatel
    [few] uživatelé
    [many] uživatele
   *[other] uživatelů
}) s { $members }
table-listing-game = { $game }: Stůl hráče { $host } ({ $count } { $count ->
    [one] uživatel
    [few] uživatelé
    [many] uživatele
   *[other] uživatelů
})
table-listing-game-one = { $game }: Stůl hráče { $host } ({ $count } uživatel)
table-listing-game-with = { $game }: Stůl hráče { $host } ({ $count } { $count ->
    [one] uživatel
    [few] uživatelé
    [many] uživatele
   *[other] uživatelů
}) s { $members }
table-not-exists = Stůl již neexistuje.
table-full = Stůl je plný.
player-replaced-by-bot = { $player } odešel a byl nahrazen botem.
player-took-over = { $player } převzal kontrolu od bota.
spectator-joined = Připojil jste se ke stolu hráče { $host } jako divák.

# Režim diváka
spectate = Sledovat
now-playing = { $player } nyní hraje.
now-spectating = { $player } nyní sleduje.
spectator-left = { $player } přestal sledovat.

# Obecné
welcome = Vítejte v PlayPalace!
goodbye = Na shledanou!

# Oznámení o přítomnosti uživatelů
user-online = { $player } se připojil.
user-offline = { $player } se odpojil.
user-is-admin = { $player } je administrátor PlayPalace.
user-is-server-owner = { $player } je vlastník serveru PlayPalace.
online-users-none = Žádní uživatelé online.
online-users-one = 1 uživatel: { $users }
online-users-many = { $count } { $count ->
    [one] uživatel
    [few] uživatelé
    [many] uživatele
   *[other] uživatelů
}: { $users }
online-user-not-in-game = Není ve hře
online-user-waiting-approval = Čeká na schválení

# Možnosti
language = Jazyk
language-option = Jazyk: { $language }
language-changed = Jazyk nastaven na { $language }.

# Stavy booleovských možností
option-on = Zapnuto
option-off = Vypnuto

# Zvukové možnosti
turn-sound-option = Zvuk tahu: { $status }

# Možnosti kostek
clear-kept-option = Vymazat držené kostky při hodu: { $status }
dice-keeping-style-option = Styl držení kostek: { $style }
dice-keeping-style-changed = Styl držení kostek nastaven na { $style }.
dice-keeping-style-indexes = Indexy kostek
dice-keeping-style-values = Hodnoty kostek

# Jména botů
cancel = Zrušit
no-bot-names-available = Žádná jména botů k dispozici.
select-bot-name = Vyberte jméno pro bota
enter-bot-name = Zadejte jméno bota
no-options-available = Žádné možnosti k dispozici.
no-scores-available = Žádné skóre k dispozici.

# Odhad trvání
estimate-duration = Odhadnout trvání
estimate-computing = Výpočet odhadovaného trvání hry...
estimate-result = Průměr bota: { $bot_time } (± { $std_dev }). { $outlier_info }Odhadovaný čas pro lidi: { $human_time }.
estimate-error = Nelze odhadnout trvání.
estimate-already-running = Odhad trvání již běží.

# Uložení/Obnovení
saved-tables = Uložené stoly
no-saved-tables = Nemáte žádné uložené stoly.
no-active-tables = Žádné aktivní stoly.
restore-table = Obnovit
delete-saved-table = Smazat
saved-table-deleted = Uložený stůl smazán.
missing-players = Nelze obnovit: tito hráči nejsou dostupní: { $players }
table-restored = Stůl obnoven! Všichni hráči byli přeneseni.
table-saved-destroying = Stůl uložen! Návrat do hlavního menu.
game-type-not-found = Typ hry již neexistuje.

# Důvody zakázaných akcí
action-not-your-turn = Není váš tah.
action-not-playing = Hra nezačala.
action-spectator = Diváci to nemohou dělat.
action-not-host = Pouze hostitel to může udělat.
action-game-in-progress = Nelze udělat, když hra probíhá.
action-need-more-players = Je potřeba více hráčů ke startu.
action-table-full = Stůl je plný.
action-no-bots = Nejsou žádní boti k odebrání.
action-bots-cannot = Boti to nemohou dělat.
action-no-scores = Žádné skóre ještě není k dispozici.

# Akce kostek
dice-not-rolled = Ještě jste nehráli.
dice-locked = Tato kostka je uzamčena.
dice-no-dice = Žádné kostky k dispozici.

# Herní akce
game-turn-start = Tah hráče { $player }.
game-no-turn = Momentálně není tah nikoho.
table-no-players = Žádní hráči.
table-players-one = { $count } hráč: { $players }.
table-players-many = { $count } { $count ->
    [one] hráč
    [few] hráči
    [many] hráče
   *[other] hráčů
}: { $players }.
table-spectators = Diváci: { $spectators }.
game-leave = Odejít
game-over = Konec hry
game-final-scores = Konečné skóre
game-points = { $count } { $count ->
    [one] bod
    [few] body
    [many] bodu
   *[other] bodů
}
play = Hrát

# Žebříčky
leaderboards = Žebříčky
leaderboards-menu-title = Žebříčky
leaderboards-select-game = Vyberte hru pro zobrazení jejího žebříčku
leaderboard-no-data = Pro tuto hru zatím nejsou žádná data žebříčku.

# Typy žebříčků
leaderboard-type-wins = Vedoucí ve výhrách
leaderboard-type-rating = Hodnocení dovedností
leaderboard-type-total-score = Celkové skóre
leaderboard-type-high-score = Nejvyšší skóre
leaderboard-type-games-played = Odehrané hry
leaderboard-type-avg-points-per-turn = Průměrné body za tah
leaderboard-type-best-single-turn = Nejlepší jeden tah
leaderboard-type-score-per-round = Skóre za kolo

# Hlavičky žebříčků
leaderboard-wins-header = { $game } - Vedoucí ve výhrách
leaderboard-total-score-header = { $game } - Celkové skóre
leaderboard-high-score-header = { $game } - Nejvyšší skóre
leaderboard-games-played-header = { $game } - Odehrané hry
leaderboard-rating-header = { $game } - Hodnocení dovedností
leaderboard-avg-points-header = { $game } - Průměrné body za tah
leaderboard-best-turn-header = { $game } - Nejlepší jeden tah
leaderboard-score-per-round-header = { $game } - Skóre za kolo

# Položky žebříčku
leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] výhra
    [few] výhry
    [many] výhry
   *[other] výher
} { $losses } { $losses ->
    [one] prohra
    [few] prohry
    [many] prohry
   *[other] proher
}, { $percentage }% úspěšnost
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } průměr
leaderboard-games-entry = { $rank }. { $player }: { $value } her

# Statistiky hráče
leaderboard-player-stats = Vaše statistiky: { $wins } výher, { $losses } proher ({ $percentage }% úspěšnost)
leaderboard-no-player-stats = Tuto hru jste ještě nehrál.

# Žebříček hodnocení dovedností
leaderboard-no-ratings = Pro tuto hru zatím nejsou žádná data hodnocení.
leaderboard-rating-entry = { $rank }. { $player }: { $rating } hodnocení ({ $mu } ± { $sigma })
leaderboard-player-rating = Vaše hodnocení: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = Pro tuto hru zatím nemáte hodnocení.

# Menu Moje statistiky
my-stats = Moje statistiky
my-stats-select-game = Vyberte hru pro zobrazení vašich statistik
my-stats-no-data = Tuto hru jste ještě nehrál.
my-stats-no-games = Zatím jste nehráli žádné hry.
my-stats-header = { $game } - Vaše statistiky
my-stats-wins = Výhry: { $value }
my-stats-losses = Prohry: { $value }
my-stats-winrate = Úspěšnost: { $value }%
my-stats-games-played = Odehrané hry: { $value }
my-stats-total-score = Celkové skóre: { $value }
my-stats-high-score = Nejvyšší skóre: { $value }
my-stats-rating = Hodnocení dovedností: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = Zatím žádné hodnocení dovedností
my-stats-avg-per-turn = Průměrné body za tah: { $value }
my-stats-best-turn = Nejlepší jeden tah: { $value }

# Systém předpovědí
predict-outcomes = Předpovědět výsledky
predict-header = Předpovězené výsledky (podle hodnocení dovedností)
predict-entry = { $rank }. { $player } (hodnocení: { $rating })
predict-entry-2p = { $rank }. { $player } (hodnocení: { $rating }, { $probability }% šance na výhru)
predict-unavailable = Předpovědi podle hodnocení nejsou k dispozici.
predict-need-players = Pro předpovědi jsou potřeba alespoň 2 lidští hráči.
action-need-more-humans = Je potřeba více lidských hráčů.
confirm-leave-game = Opravdu chcete opustit stůl?
confirm-yes = Ano
confirm-no = Ne

# Administrativa
administration = Administrativa
admin-menu-title = Administrativa

# Schvalování účtů
account-approval = Schvalování účtů
account-approval-menu-title = Schvalování účtů
no-pending-accounts = Žádné čekající účty.
approve-account = Schválit
decline-account = Odmítnout
account-approved = Účet hráče { $player } byl schválen.
account-declined = Účet hráče { $player } byl odmítnut a smazán.

# Čekání na schválení (zobrazeno neschváleným uživatelům)
waiting-for-approval = Váš účet čeká na schválení administrátorem.
account-approved-welcome = Váš účet byl schválen! Vítejte v PlayPalace!
account-declined-goodbye = Vaše žádost o účet byla odmítnuta.
    Důvod:
account-banned = Váš účet je zablokován a nelze k němu přistupovat.

# Chyby při přihlášení
incorrect-username = Zadané uživatelské jméno neexistuje.
incorrect-password = Zadané heslo je nesprávné.
already-logged-in = Tento účet je již přihlášen.

# Ověření přihlašovacích údajů
credential-username-length = Uživatelské jméno musí mít mezi { $min } a { $max } znaky.
credential-password-length = Heslo musí mít mezi { $min } a { $max } znaky.

# Omezení počtu požadavků
rate-limit-login-ip = Příliš mnoho pokusů o přihlášení z této adresy. Počkejte prosím a zkuste to znovu.
rate-limit-login-user = Příliš mnoho neúspěšných pokusů o přihlášení pro toto uživatelské jméno. Počkejte prosím a zkuste to znovu.
rate-limit-registration = Příliš mnoho pokusů o registraci z této adresy. Počkejte prosím a zkuste to znovu.
rate-limit-refresh = Příliš mnoho pokusů o obnovení z této adresy. Počkejte prosím a zkuste to znovu.

# Chyby relace a ověření
account-not-found = Účet nebyl nalezen.
session-expired = Relace vypršela. Přihlaste se prosím znovu.
session-token-mismatch = Token relace neodpovídá uživatelskému jménu.
refresh-token-expired = Token obnovy vypršel. Přihlaste se prosím znovu.
refresh-token-mismatch = Token obnovy neodpovídá uživatelskému jménu.

# Registrace
registration-success = Registrace proběhla úspěšně! Váš účet čeká na schválení.
registration-username-taken = Uživatelské jméno je již obsazeno. Zvolte prosím jiné uživatelské jméno.

# Záložní hodnota předvolby
pref-invalid-value = Neplatný výběr, používá se výchozí hodnota.

# Důvod odmítnutí
decline-reason-prompt = Zadejte důvod odmítnutí (nebo stiskněte Escape pro zrušení):
account-action-empty-reason = Nebyl uveden žádný důvod.

# Oznámení pro adminy o žádostech o účty
account-request = žádost o účet
account-action = akce s účtem provedena

# Povýšení/degradace admina
promote-admin = Povýšit na admina
demote-admin = Odebrat admina
promote-admin-menu-title = Povýšit na admina
demote-admin-menu-title = Odebrat admina
no-users-to-promote = Žádní uživatelé k dispozici pro povýšení.
no-admins-to-demote = Žádní admini k dispozici pro odebrání.
confirm-promote = Opravdu chcete povýšit { $player } na admina?
confirm-demote = Opravdu chcete odebrat { $player } z adminů?
broadcast-to-all = Oznámit všem uživatelům
broadcast-to-admins = Oznámit pouze adminům
broadcast-to-nobody = Tiše (žádné oznámení)
promote-announcement = { $player } byl povýšen na admina!
promote-announcement-you = Byli jste povýšeni na admina!
demote-announcement = { $player } byl odebrán z adminů.
demote-announcement-you = Byli jste odebráni z adminů.
not-admin-anymore = Již nejste admin a nemůžete provést tuto akci.
not-server-owner = Pouze vlastník serveru může provést tuto akci.

# Převod vlastnictví serveru
transfer-ownership = Převést vlastnictví
transfer-ownership-menu-title = Převést vlastnictví
no-admins-for-transfer = Žádní admini k dispozici pro převod vlastnictví.
confirm-transfer-ownership = Opravdu chcete převést vlastnictví serveru na { $player }? Budete degradováni na admina.
transfer-ownership-announcement = { $player } je nyní vlastník serveru Play Palace!
transfer-ownership-announcement-you = Nyní jste vlastník serveru Play Palace!

# Blokování uživatelů
ban-user = Zablokovat uživatele
unban-user = Odblokovat uživatele
no-users-to-ban = Žádní uživatelé k dispozici pro zablokování.
no-users-to-unban = Žádní zablokovaní uživatelé k odblokování.
confirm-ban = Opravdu chcete zablokovat { $player }?
confirm-unban = Opravdu chcete odblokovat { $player }?
ban-reason-prompt = Zadejte důvod zablokování (volitelné):
unban-reason-prompt = Zadejte důvod odblokování (volitelné):
user-banned = { $player } byl zablokován.
user-unbanned = { $player } byl odblokován.
you-have-been-banned = Byli jste zablokováni na tomto serveru.
    Důvod:
you-have-been-unbanned = Byli jste odblokováni na tomto serveru.
    Důvod:
ban-no-reason = Nebyl uveden žádný důvod.

# Virtuální boti (pouze vlastník serveru)
virtual-bots = Virtuální boti
virtual-bots-fill = Naplnit server
virtual-bots-clear = Vymazat všechny boty
virtual-bots-status = Stav
virtual-bots-clear-confirm = Opravdu chcete vymazat všechny virtuální boty? Tím se také zničí všechny stoly, ve kterých jsou.
virtual-bots-not-available = Virtuální boti nejsou k dispozici.
virtual-bots-filled = Přidáno { $added } virtuálních botů. { $online } je nyní online.
virtual-bots-already-filled = Všichni virtuální boti z konfigurace jsou již aktivní.
virtual-bots-cleared = Vymazáno { $bots } virtuálních botů a zničeno { $tables } { $tables ->
    [one] stůl
    [few] stoly
    [many] stolu
   *[other] stolů
}.
virtual-bot-table-closed = Stůl uzavřen administrátorem.
virtual-bots-none-to-clear = Žádní virtuální boti k vymazání.
virtual-bots-status-report = Virtuální boti: { $total } celkem, { $online } online, { $offline } offline, { $in_game } ve hře.
virtual-bots-guided-overview = Vedené stoly
virtual-bots-groups-overview = Skupiny botů
virtual-bots-profiles-overview = Profily
virtual-bots-guided-header = Vedené stoly: { $count } pravidel. Alokace: { $allocation }, záložní: { $fallback }, výchozí profil: { $default_profile }.
virtual-bots-guided-empty = Nejsou nakonfigurována žádná pravidla pro vedené stoly.
virtual-bots-guided-status-active = aktivní
virtual-bots-guided-status-inactive = neaktivní
virtual-bots-guided-table-linked = propojeno se stolem { $table_id } (hostitel { $host }, hráči { $players }, lidé { $humans })
virtual-bots-guided-table-stale = stůl { $table_id } chybí na serveru
virtual-bots-guided-table-unassigned = momentálně není sledován žádný stůl
virtual-bots-guided-next-change = další změna za { $ticks } tiků
virtual-bots-guided-no-schedule = žádné plánovací okno
virtual-bots-guided-warning = ⚠ nedostatečně naplněno
virtual-bots-guided-line = { $table }: hra { $game }, priorita { $priority }, boti { $assigned } (min { $min_bots }, max { $max_bots }), čekající { $waiting }, nedostupní { $unavailable }, stav { $status }, profil { $profile }, skupiny { $groups }. { $table_state }. { $next_change } { $warning_text }
virtual-bots-groups-header = Skupiny botů: { $count } značek, { $bots } nakonfigurovaných botů.
virtual-bots-groups-empty = Nejsou definovány žádné skupiny botů.
virtual-bots-groups-line = { $group }: profil { $profile }, boti { $total } (online { $online }, čekající { $waiting }, ve hře { $in_game }, offline { $offline }), pravidla { $rules }.
virtual-bots-groups-no-rules = žádná
virtual-bots-no-profile = výchozí
virtual-bots-profile-inherit-default = dědí výchozí profil
virtual-bots-profiles-header = Profily: { $count } definováno (výchozí: { $default_profile }).
virtual-bots-profiles-empty = Nejsou definovány žádné profily.
virtual-bots-profiles-line = { $profile } ({ $bot_count } botů) přepsání: { $overrides }.
virtual-bots-profiles-no-overrides = dědí základní konfiguraci

localization-in-progress-try-again = Lokalizace se stále načítá. Zkuste to prosím za minutu znovu.
