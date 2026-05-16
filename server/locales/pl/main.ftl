# Main UI messages for PlayPalace

# Game categories
category-card-games = Gry karciane
category-dice-games = Gry kościane
category-board-games = Gry planszowe
category-rb-play-center = RB Play Center
category-poker = Poker
category-uncategorized = Niezkategoryzowane

# Menu titles
main-menu-title = Menu główne.
play-menu-title = Rozpocznij grę
categories-menu-title = Kategorie gier
tables-menu-title = Dostępne stoły
play = Play
view-active-tables = Pokaż aktywne stoły
options = Opcje
logout = Wyloguj się
back = Wróć
context-menu = Menu kontekstowe
no-actions-available = Brak dostępnych akcji.
create-table = Utwórz nowy stół
join-as-player = Dołącz jako gracz.
join-as-spectator = Dołącz jako obserwator
leave-table = Opuść stół
start-game = Rozpocznij grę
add-bot = Dodaj bota
remove-bot = Usuń bota
actions-menu = Menu akcji
save-table = Zapisz stół
whose-turn = Czyja tura?
whos-at-table = Kto jest przy stole?
check-scores = Sprawdź wyniki
check-scores-detailed = Szczegółowe wyniki
check-game-options = Sprawdź opcje gry
no-game-options = Brak opcji gry.

# Turn messages
game-player-skipped = { $player } został pominięty.

# Table messages
table-created = { $host } utworzył stół gry { $game }.
table-joined = { $player } dołączył do stołu
table-left = { $player } opuścił stół.
new-host = { $player } jest teraz hostem.
waiting-for-players = Stół czeka na graczy. Minimalnie { $min }, maksymalnie { $max } graczy.
game-starting = Gra się rozpoczyna!
table-listing = Stół { $host } ({ $count } użytkowników)
table-listing-one = Stół użytkownika {  $host } z ({ $count } użytkownikiem)
table-listing-with = { stół od $host }' ({ $count } użytkowników) z { $members }
table-listing-game = { $game }: Stół { $host } ({ $count } użytkowników)
table-listing-game-one = { $game }: Stół { $host } z ({ $count } użytkownikiem)
table-listing-game-with = { $game }: stół { $host } ({ $count } użytkowników) z { $members }
table-not-exists = Ten stół już nie istnieje
table-full = Stół jest pełny.
player-replaced-by-bot = { $player } opuścił grę, i został zastąpiony przez bota.
player-took-over = { $player } przejął kontrolę od bota
spectator-joined = Dołączyłeś do stołu { $host } jako obserwator.

# Spectator mode
spectate = Obserwuj
now-playing = { $player } dołącza do rozgrywki
now-spectating = { $player } teraz obserwuje rozgrywkę
spectator-left = { $player } przestał obserwować.

# General
welcome = Witaj w Play Palace!
goodbye = Do zobaczenia!

# User presence announcements
user-online = { $player } zalogował się.
user-offline = { $player } wylogował się.
online-users-none = Brak użytkowników online.
online-users-one = 1 użytkownik: { $users }
online-users-many = { $count } użytkowników: { $users }
online-user-not-in-game = Nie w grze
online-user-waiting-approval = Oczekuje na zatwierdzenie
user-is-admin = { $player } jest administratorem Play Palace.
user-is-server-owner = { $player } jest właścicielem serwera Play Palace.

# Options
language = Język
language-option = Język: { $language }
language-changed = Zmieniono język na { $language }.

# Boolean option states
option-on = Wł
option-off = Wył

# Sound options
turn-sound-option = Dźwięk tury { $status }

# Dice options
clear-kept-option = Odznacz kostki po rzucie: { $status }
dice-keeping-style-option = Styl zatrzymania kostek: { $style }
dice-keeping-style-changed = Styl zatrzymania kostek po rzucie został zmieniony na { $style }.
dice-keeping-style-indexes = Indeksy kości
dice-keeping-style-values = Wartości kości

# Bot names
cancel = Anuluj
no-bot-names-available = Brak nazw botów
select-bot-name = Wybierz nazwę dla bota
enter-bot-name = Wpisz nazwę bota
no-options-available = Brak opcji
no-scores-available = Brak wyników

# Duration estimation
estimate-duration = Oszacowany czas
estimate-computing = Szacowanie czasu trwania gry...
estimate-result = Oszacowany czas bota: { $bot_time } (± { $std_dev }). { $outlier_info }Szacowany czas gracza: { $human_time }.
estimate-error = Nie można oszacować czasu.
estimate-already-running = Szacowanie w toku

# Save/Restore
saved-tables = Zapisane stoły
no-saved-tables = Nie masz zapisanych stołów
no-active-tables = Brak aktywnych stołów.
restore-table = Przywróć
delete-saved-table = Usuń
saved-table-deleted = Usunięto zapisany stół
missing-players = Nie można przywrócić stołu z uwagi na brak następujących graczy: { $players }
table-restored = Przywrócono stół! Wszyscy gracze zostali przeniesieni
table-saved-destroying = Zapisano stół, wracasz do głównego menu.
game-type-not-found = Ten typ gry już nie istnieje.

# Action disabled reasons
action-not-your-turn = To nie jest Twoja tura
action-not-playing = Gra jeszcze się nie rozpoczęła
action-spectator = Obserwatorzy nie mogą tego robić!
action-not-host = Tylko host może to zrobić!
action-game-in-progress = Podczas trwania gry, nie można tego zrobić.
action-need-more-players = Potrzeba co najmniej { $min_players } graczy, aby rozpocząć.
action-table-full = Stół jest pełny
action-no-bots = Nie ma żadnych botów do usunięcia.
action-bots-cannot = Boty nie mogą tego wykonać.
action-no-scores = Jeszcze nie ma wyników.

# Dice actions
dice-not-rolled = Jeszcze nie rzuciłeś kostką.
dice-locked = Ta kość jest zablokowana
dice-no-dice = brak kości

# Game actions
game-turn-start = Kolej gracza { $player }.
game-no-turn = Nikt teraz nie ma tury.
table-no-players = Brak graczy.
table-players-one = { $count } gracz: { $players }.
table-players-many = { $count } Gracze: { $players }.
table-spectators = Obserwatorzy: { $spectators }.
game-leave = Opuść
game-over = Koniec gry
game-final-scores = Wyniki końcowe:
game-points = { $count } { $count ->
    [one] punkt
   *[other] punktów
}
play = Graj

# Leaderboards
leaderboards = Rankingi
leaderboards-menu-title = Rankingi
leaderboards-select-game = Wybierz grę, aby przeglądać wyniki.
leaderboard-no-data = Brak wyników dla tej gry.

# Leaderboard types
leaderboard-type-wins = Ranking wygranych liderów
leaderboard-type-rating = Ranking umiejętności
leaderboard-type-total-score = Ranking całkowitych wyników
leaderboard-type-high-score = Ranking najwyższych wyników
leaderboard-type-games-played = Największej liczby rozegranych gier
leaderboard-type-avg-points-per-turn = Średnia punktów na turę
leaderboard-type-best-single-turn = Najlepsza pojedyńcza tura
leaderboard-type-score-per-round = Wynik na rundę

# Leaderboard headers
leaderboard-wins-header = { $game } - liderzy wygranych gier
leaderboard-total-score-header = { $game } - całkowite wyniki
leaderboard-high-score-header = { $game } - najwyższe wyniki
leaderboard-games-played-header = { $game } - rozegrane gry
leaderboard-rating-header = { $game } - oceny umiejętności
leaderboard-avg-points-header = { $game } - średnia liczba punktów  na turę
leaderboard-best-turn-header = { $game } - najlepsza pojedyncza tura
leaderboard-score-per-round-header = { $game } - wynik na rundę

# Leaderboard entries
leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] wygrana
   *[other] wygranych
} { $losses } { $losses ->
    [one] przegrana
   *[other] przegranych
}, { $percentage }% winrate
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } avg
leaderboard-games-entry = { $rank }. { $player }: { $value } gier

# Player stats
leaderboard-player-stats = Twoje statystyki: { $wins } wygranych, { $losses } przegranych, { $percentage } procent wygranych
leaderboard-no-player-stats = Jeszcze nie grałeś w tą grę

# Skill rating leaderboard
leaderboard-no-ratings = Brak  danych dla tej gry.
leaderboard-rating-entry = { $rank }. { $player }: { $rating } rating ({ $mu } ± { $sigma })
leaderboard-player-rating = Twój ranking: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = Nie masz jeszcze żadnych wyników w tej grze.

# My Stats menu
my-stats = Moje  Statystyki
my-stats-select-game = Wybierz grę, aby zobaczyć swoje statystyki
my-stats-no-data = Jeszcze nie grałeś w tą grę.
my-stats-no-games = Jeszcze nie grałeś w żadną grę.
my-stats-header = { $game } - Twoje statystyki
my-stats-wins = Wygranych: { $value }
my-stats-losses = Przegranych: { $value }
my-stats-winrate = Procent wygranych: { $value }%
my-stats-games-played = Rozegrane gry: { $value }
my-stats-total-score = Całkowite wyniki: { $value }
my-stats-high-score = Najwyższy wynik: { $value }
my-stats-rating = Ocena umiejętności: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = Brak oceny umiejętności
my-stats-avg-per-turn = Średnia liczba punktów na turę: { $value }
my-stats-best-turn = Najlepsza pojedyncza tura: { $value }
# Prediction system
predict-outcomes = Przewiduj wyniki
predict-header = Przewidywane wyniki na podstawie poziomu umiejętności
predict-entry = { $rank }. { $player } (rating: { $rating })
predict-entry-2p = { $rank }. { $player } (rating: { $rating }, { $probability }% win chance)
predict-unavailable = Prognoza ocen nie jest dostępna.
predict-need-players = Potrzebne jest conajmniej dwóch realnych graczy do przewidywania.
action-need-more-humans = Potrzeba więcej ludzi.
confirm-leave-game = Czy na pewno chcesz opuścić stół?
confirm-yes = Tak
confirm-no = Nie

# Administration
administration = Administracja
admin-menu-title = Administracja

# Account approval
account-approval = Zatwierdzanie kont
account-approval-menu-title = Zatwierdzanie kont
no-pending-accounts = Brak kont oczekujących na zatwierdzenie.
approve-account = Zatwierdź
decline-account = Odrzuć
account-approved = Konto gracza { $player } zostało zatwierdzone.
account-declined = Konto gracza { $player } zostało odrzucone i usunięte.

# Waiting for approval (shown to unapproved users)
waiting-for-approval = Twoje konto oczekuje na zatwierdzenie przez administratora.
account-approved-welcome = Twoje konto zostało zatwierdzone! Witamy w PlayPalace!
account-declined-goodbye = Twoja prośba o zatwierdzenie konta została odrzucona.
    Powód:
account-banned = Twoje konto zostało zbanowane i nie można uzyskać do niego dostępu.

# Błędy logowania
incorrect-username = Wprowadzona nazwa użytkownika nie istnieje.
incorrect-password = Wprowadzone hasło jest nieprawidłowe.
already-logged-in = To konto jest już zalogowane.

# Walidacja danych logowania
credential-username-length = Nazwa użytkownika musi mieć od { $min } do { $max } znaków.
credential-password-length = Hasło musi mieć od { $min } do { $max } znaków.

# Ograniczenie liczby prób
rate-limit-login-ip = Zbyt wiele prób logowania z tego adresu. Poczekaj chwilę i spróbuj ponownie.
rate-limit-login-user = Zbyt wiele nieudanych prób logowania dla tej nazwy użytkownika. Poczekaj chwilę i spróbuj ponownie.
rate-limit-registration = Zbyt wiele prób rejestracji z tego adresu. Poczekaj chwilę i spróbuj ponownie.
rate-limit-refresh = Zbyt wiele prób odświeżenia z tego adresu. Poczekaj chwilę i spróbuj ponownie.

# Błędy sesji i autoryzacji
account-not-found = Nie znaleziono konta.
session-expired = Sesja wygasła. Zaloguj się ponownie.
session-token-mismatch = Token sesji nie pasuje do nazwy użytkownika.
refresh-token-expired = Token odświeżania wygasł. Zaloguj się ponownie.
refresh-token-mismatch = Token odświeżania nie pasuje do nazwy użytkownika.

# Rejestracja
registration-success = Rejestracja zakończona pomyślnie! Twoje konto oczekuje na zatwierdzenie.
registration-username-taken = Ta nazwa użytkownika jest już zajęta. Wybierz inną nazwę użytkownika.

# Domyślne preferencje
pref-invalid-value = Nieprawidłowy wybór, używam wartości domyślnej.

# Powód odrzucenia
decline-reason-prompt = Podaj powód odrzucenia (lub naciśnij Escape, aby anulować):
account-action-empty-reason = Nie podano powodu.

# Admin notifications for account requests
account-request = Prośba o konto
account-action = Podjęto działanie dotyczące konta

# Admin promotion/demotion
promote-admin = Awansuj na administratora
demote-admin = Zdegraduj administratora
promote-admin-menu-title = Awansuj na administratora
demote-admin-menu-title = Degraduj administratora
no-users-to-promote = Brak użytkowników, których mógłbyś awansować.
no-admins-to-demote = Brak administratorów, których mógłbyś zdegradować.
confirm-promote = Czy na pewno chcesz awansować { $player } na administratora?
confirm-demote = Czy na pewno chcesz zdegradować { $player } z funkcji administratora?
broadcast-to-all = Wyślij ogłoszenie do wszystkich użytkowników
broadcast-to-admins = Wyślij ogłoszenie tylko dla administratorów
broadcast-to-nobody = Cisza, (brak ogłoszenia)
promote-announcement = { $player } został awansowany na administratora!
promote-announcement-you = Zostałeś awansowany na administratora!
demote-announcement = { $player } został zdegradowany z funkcji administratora.
demote-announcement-you = Zostałeś zdegradowany z funkcji administratora.
not-admin-anymore = Nie jesteś już administratorem, i nie możesz wykonać tej akcji.
not-server-owner = Tylko właściciel serwera może wykonać tę akcję.

# Server ownership transfer
transfer-ownership = Przekaż własność
transfer-ownership-menu-title = Przekaż własność
no-admins-for-transfer = Brak administratorów, którym można przekazać własność.
confirm-transfer-ownership = Czy na pewno chcesz przekazać własność serwera graczowi { $player }? Zostaniesz zdegradowany do funkcji administratora.
transfer-ownership-announcement = { $player } jest teraz właścicielem serwera Play Palace!
transfer-ownership-announcement-you = Jesteś teraz właścicielem serwera Play Palace!

# Banowanie użytkowników
ban-user = Zbanuj użytkownika
unban-user = Odbanuj użytkownika
no-users-to-ban = Brak użytkowników do zbanowania.
no-users-to-unban = Brak zbanowanych użytkowników do odbanowania.
confirm-ban = Czy na pewno chcesz zbanować { $player }?
confirm-unban = Czy na pewno chcesz odbanować { $player }?
ban-reason-prompt = Podaj powód bana (opcjonalnie):
unban-reason-prompt = Podaj powód odbanowania (opcjonalnie):
user-banned = { $player } został zbanowany.
user-unbanned = { $player } został odbanowany.
you-have-been-banned = Zostałeś zbanowany na tym serwerze.
    Powód:
you-have-been-unbanned = Zostałeś odbanowany na tym serwerze.
    Powód:
virtual-bots-guided-overview = Guided Tables
virtual-bots-groups-overview = Bot Groups
virtual-bots-profiles-overview = Profiles
virtual-bots-guided-header = Guided tables: { $count } rule(s). Allocation: { $allocation }, fallback: { $fallback }, default profile: { $default_profile }.
virtual-bots-guided-empty = No guided table rules are configured.
virtual-bots-guided-status-active = active
virtual-bots-guided-status-inactive = inactive
virtual-bots-guided-table-linked = linked to table { $table_id } (host { $host }, players { $players }, humans { $humans })
virtual-bots-guided-table-stale = table { $table_id } missing on server
virtual-bots-guided-table-unassigned = no table is currently tracked
virtual-bots-guided-next-change = next change in { $ticks } ticks
virtual-bots-guided-no-schedule = no scheduling window
virtual-bots-guided-warning = ⚠ underfilled
virtual-bots-guided-line = { $table }: game { $game }, priority { $priority }, bots { $assigned } (min { $min_bots }, max { $max_bots }), waiting { $waiting }, unavailable { $unavailable }, status { $status }, profile { $profile }, groups { $groups }. { $table_state }. { $next_change } { $warning_text }
virtual-bots-groups-header = Bot groups: { $count } tag(s), { $bots } configured bots.
virtual-bots-groups-empty = No bot groups are defined.
virtual-bots-groups-line = { $group }: profile { $profile }, bots { $total } (online { $online }, waiting { $waiting }, in-game { $in_game }, offline { $offline }), rules { $rules }.
virtual-bots-groups-no-rules = none
virtual-bots-no-profile = default
virtual-bots-profile-inherit-default = inherits default profile
virtual-bots-profiles-header = Profiles: { $count } defined (default: { $default_profile }).
virtual-bots-profiles-empty = No profiles are defined.
virtual-bots-profiles-line = { $profile } ({ $bot_count } bots) overrides: { $overrides }.
virtual-bots-profiles-no-overrides = inherits base configuration

localization-in-progress-try-again = Lokalizacja jest w toku. Spróbuj ponownie za minutę.
