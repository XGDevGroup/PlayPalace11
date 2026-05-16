# Haupt-UI-Nachrichten für PlayPalace

# Spielkategorien
category-card-games = Kartenspiele
category-dice-games = Würfelspiele
category-board-games = Brettspiele
category-rb-play-center = RB Play Center
category-poker = Poker
category-uncategorized = Unkategorisiert

# Menütitel
main-menu-title = Hauptmenü
play-menu-title = Spielen
categories-menu-title = Spielkategorien
tables-menu-title = Verfügbare Tische

# Menüeinträge
play = Spielen
view-active-tables = Aktive Tische anzeigen
options = Optionen
logout = Abmelden
back = Zurück
context-menu = Kontextmenü.
no-actions-available = Keine Aktionen verfügbar.
create-table = Neuen Tisch erstellen
join-as-player = Als Spieler beitreten
join-as-spectator = Als Zuschauer beitreten
leave-table = Tisch verlassen
start-game = Spiel starten
add-bot = Bot hinzufügen
remove-bot = Bot entfernen
actions-menu = Aktionsmenü
save-table = Tisch speichern
whose-turn = Wer ist am Zug
whos-at-table = Wer ist am Tisch
check-scores = Punktzahlen prüfen
check-scores-detailed = Detaillierte Punktzahlen
check-game-options = Spieloptionen prüfen
no-game-options = Keine Spieloptionen verfügbar.

# Zugnachrichten
game-player-skipped = { $player } wird übersprungen.

# Tischnachrichten
table-created = { $host } hat einen neuen { $game }-Tisch erstellt.
table-joined = { $player } ist dem Tisch beigetreten.
table-left = { $player } hat den Tisch verlassen.
new-host = { $player } ist jetzt der Gastgeber.
waiting-for-players = Warte auf Spieler. {$min} min, { $max } max.
game-starting = Spiel startet!
table-listing = Tisch von { $host } ({ $count } Benutzer)
table-listing-one = Tisch von { $host } ({ $count } Benutzer)
table-listing-with = Tisch von { $host } ({ $count } Benutzer) mit { $members }
table-listing-game = { $game }: Tisch von { $host } ({ $count } Benutzer)
table-listing-game-one = { $game }: Tisch von { $host } ({ $count } Benutzer)
table-listing-game-with = { $game }: Tisch von { $host } ({ $count } Benutzer) mit { $members }
table-not-exists = Tisch existiert nicht mehr.
table-full = Tisch ist voll.
player-replaced-by-bot = { $player } hat den Tisch verlassen und wurde durch einen Bot ersetzt.
player-took-over = { $player } hat vom Bot übernommen.
spectator-joined = Tisch von { $host } als Zuschauer beigetreten.

# Zuschauermodus
spectate = Zuschauen
now-playing = { $player } spielt jetzt.
now-spectating = { $player } schaut jetzt zu.
spectator-left = { $player } schaut nicht mehr zu.

# Allgemein
welcome = Willkommen bei PlayPalace!
goodbye = Auf Wiedersehen!

# Benutzer-Präsenzankündigungen
user-online = { $player } ist online gekommen.
user-offline = { $player } ist offline gegangen.
user-is-admin = { $player } ist ein Administrator von PlayPalace.
user-is-server-owner = { $player } ist der Serverbesitzer von PlayPalace.
online-users-none = Keine Benutzer online.
online-users-one = 1 Benutzer: { $users }
online-users-many = { $count } Benutzer: { $users }
online-user-not-in-game = Nicht im Spiel
online-user-waiting-approval = Wartet auf Genehmigung

# Optionen
language = Sprache
language-option = Sprache: { $language }
language-changed = Sprache auf { $language } gesetzt.

# Boolesche Optionszustände
option-on = An
option-off = Aus

# Sound-Optionen
turn-sound-option = Zug-Sound: { $status }

# Würfel-Optionen
clear-kept-option = Behaltene Würfel beim Würfeln löschen: { $status }
dice-keeping-style-option = Würfel-Behalten-Stil: { $style }
dice-keeping-style-changed = Würfel-Behalten-Stil auf { $style } gesetzt.
dice-keeping-style-indexes = Würfelindizes
dice-keeping-style-values = Würfelwerte

# Bot-Namen
cancel = Abbrechen
no-bot-names-available = Keine Bot-Namen verfügbar.
select-bot-name = Wählen Sie einen Namen für den Bot
enter-bot-name = Bot-Namen eingeben
no-options-available = Keine Optionen verfügbar.
no-scores-available = Keine Punktzahlen verfügbar.

# Dauerschätzung
estimate-duration = Dauer schätzen
estimate-computing = Berechne geschätzte Spieldauer...
estimate-result = Bot-Durchschnitt: { $bot_time } (± { $std_dev }). { $outlier_info }Geschätzte menschliche Zeit: { $human_time }.
estimate-error = Konnte Dauer nicht schätzen.
estimate-already-running = Dauerschätzung läuft bereits.

# Speichern/Wiederherstellen
saved-tables = Gespeicherte Tische
no-saved-tables = Sie haben keine gespeicherten Tische.
no-active-tables = Keine aktiven Tische.
restore-table = Wiederherstellen
delete-saved-table = Löschen
saved-table-deleted = Gespeicherter Tisch gelöscht.
missing-players = Kann nicht wiederherstellen: diese Spieler sind nicht verfügbar: { $players }
table-restored = Tisch wiederhergestellt! Alle Spieler wurden übertragen.
table-saved-destroying = Tisch gespeichert! Kehre zum Hauptmenü zurück.
game-type-not-found = Spieltyp existiert nicht mehr.

# Gründe für deaktivierte Aktionen
action-not-your-turn = Sie sind nicht am Zug.
action-not-playing = Das Spiel hat noch nicht begonnen.
action-spectator = Zuschauer können dies nicht tun.
action-not-host = Nur der Gastgeber kann dies tun.
action-game-in-progress = Kann dies nicht tun, während das Spiel läuft.
action-need-more-players = Es werden mindestens { $min_players } Spieler zum Starten benötigt.
action-table-full = Der Tisch ist voll.
action-no-bots = Es gibt keine Bots zum Entfernen.
action-bots-cannot = Bots können dies nicht tun.
action-no-scores = Noch keine Punktzahlen verfügbar.

# Würfelaktionen
dice-not-rolled = Sie haben noch nicht gewürfelt.
dice-locked = Dieser Würfel ist gesperrt.
dice-no-dice = Keine Würfel verfügbar.

# Spielaktionen
game-turn-start = { $player } ist am Zug.
game-no-turn = Momentan ist niemand am Zug.
table-no-players = Keine Spieler.
table-players-one = { $count } Spieler: { $players }.
table-players-many = { $count } Spieler: { $players }.
table-spectators = Zuschauer: { $spectators }.
game-leave = Verlassen
game-over = Spiel vorbei
game-final-scores = Endpunktzahlen
game-points = { $count } { $count ->
    [one] Punkt
   *[other] Punkte
}
play = Spielen

# Bestenlisten
leaderboards = Bestenlisten
leaderboards-menu-title = Bestenlisten
leaderboards-select-game = Wählen Sie ein Spiel aus, um seine Bestenliste anzuzeigen
leaderboard-no-data = Noch keine Bestenlistendaten für dieses Spiel.

# Bestenlistentypen
leaderboard-type-wins = Sieg-Anführer
leaderboard-type-rating = Fähigkeitsbewertung
leaderboard-type-total-score = Gesamtpunktzahl
leaderboard-type-high-score = Höchstpunktzahl
leaderboard-type-games-played = Gespielte Spiele
leaderboard-type-avg-points-per-turn = Durchschn. Punkte pro Zug
leaderboard-type-best-single-turn = Bester einzelner Zug
leaderboard-type-score-per-round = Punktzahl pro Runde

# Bestenlistenüberschriften
leaderboard-wins-header = { $game } - Sieg-Anführer
leaderboard-total-score-header = { $game } - Gesamtpunktzahl
leaderboard-high-score-header = { $game } - Höchstpunktzahl
leaderboard-games-played-header = { $game } - Gespielte Spiele
leaderboard-rating-header = { $game } - Fähigkeitsbewertungen
leaderboard-avg-points-header = { $game } - Durchschn. Punkte pro Zug
leaderboard-best-turn-header = { $game } - Bester einzelner Zug
leaderboard-score-per-round-header = { $game } - Punktzahl pro Runde

# Bestenlisteneinträge
leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] Sieg
   *[other] Siege
} { $losses } { $losses ->
    [one] Niederlage
   *[other] Niederlagen
}, { $percentage }% Siegrate
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } Durchschnitt
leaderboard-games-entry = { $rank }. { $player }: { $value } Spiele

# Spielerstatistiken
leaderboard-player-stats = Ihre Statistiken: { $wins } Siege, { $losses } Niederlagen ({ $percentage }% Siegrate)
leaderboard-no-player-stats = Sie haben dieses Spiel noch nicht gespielt.

# Fähigkeitsbewertungs-Bestenliste
leaderboard-no-ratings = Noch keine Bewertungsdaten für dieses Spiel.
leaderboard-rating-entry = { $rank }. { $player }: { $rating } Bewertung ({ $mu } ± { $sigma })
leaderboard-player-rating = Ihre Bewertung: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = Sie haben noch keine Bewertung für dieses Spiel.

# Meine Statistiken-Menü
my-stats = Meine Statistiken
my-stats-select-game = Wählen Sie ein Spiel aus, um Ihre Statistiken anzuzeigen
my-stats-no-data = Sie haben dieses Spiel noch nicht gespielt.
my-stats-no-games = Sie haben noch keine Spiele gespielt.
my-stats-header = { $game } - Ihre Statistiken
my-stats-wins = Siege: { $value }
my-stats-losses = Niederlagen: { $value }
my-stats-winrate = Siegrate: { $value }%
my-stats-games-played = Gespielte Spiele: { $value }
my-stats-total-score = Gesamtpunktzahl: { $value }
my-stats-high-score = Höchstpunktzahl: { $value }
my-stats-rating = Fähigkeitsbewertung: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = Noch keine Fähigkeitsbewertung
my-stats-avg-per-turn = Durchschn. Punkte pro Zug: { $value }
my-stats-best-turn = Bester einzelner Zug: { $value }

# Vorhersagesystem
predict-outcomes = Ergebnisse vorhersagen
predict-header = Vorhergesagte Ergebnisse (nach Fähigkeitsbewertung)
predict-entry = { $rank }. { $player } (Bewertung: { $rating })
predict-entry-2p = { $rank }. { $player } (Bewertung: { $rating }, { $probability }% Gewinnchance)
predict-unavailable = Bewertungsvorhersagen sind nicht verfügbar.
predict-need-players = Brauche mindestens 2 menschliche Spieler für Vorhersagen.
action-need-more-humans = Brauche mehr menschliche Spieler.
confirm-leave-game = Sind Sie sicher, dass Sie den Tisch verlassen möchten?
confirm-yes = Ja
confirm-no = Nein

# Administration
administration = Administration
admin-menu-title = Administration

# Kontogenehmigung
account-approval = Kontogenehmigung
account-approval-menu-title = Kontogenehmigung
no-pending-accounts = Keine ausstehenden Konten.
approve-account = Genehmigen
decline-account = Ablehnen
account-approved = Das Konto von { $player } wurde genehmigt.
account-declined = Das Konto von { $player } wurde abgelehnt und gelöscht.

# Warten auf Genehmigung (für nicht genehmigte Benutzer)
waiting-for-approval = Ihr Konto wartet auf Genehmigung durch einen Administrator.
account-approved-welcome = Ihr Konto wurde genehmigt! Willkommen bei PlayPalace!
account-declined-goodbye = Ihre Kontoanfrage wurde abgelehnt.
    Grund:
account-banned = Ihr Konto ist gesperrt und kann nicht verwendet werden.

# Anmeldefehler
incorrect-username = Der von Ihnen eingegebene Benutzername existiert nicht.
incorrect-password = Das von Ihnen eingegebene Passwort ist falsch.
already-logged-in = Dieses Konto ist bereits angemeldet.

# Validierung der Anmeldedaten
credential-username-length = Der Benutzername muss zwischen { $min } und { $max } Zeichen lang sein.
credential-password-length = Das Passwort muss zwischen { $min } und { $max } Zeichen lang sein.

# Anfragebegrenzung
rate-limit-login-ip = Zu viele Anmeldeversuche von dieser Adresse. Bitte warten Sie und versuchen Sie es erneut.
rate-limit-login-user = Zu viele fehlgeschlagene Anmeldeversuche für diesen Benutzernamen. Bitte warten Sie und versuchen Sie es erneut.
rate-limit-registration = Zu viele Registrierungsversuche von dieser Adresse. Bitte warten Sie und versuchen Sie es erneut.
rate-limit-refresh = Zu viele Aktualisierungsversuche von dieser Adresse. Bitte warten Sie und versuchen Sie es erneut.

# Sitzungs- und Authentifizierungsfehler
account-not-found = Konto nicht gefunden.
session-expired = Sitzung abgelaufen. Bitte melden Sie sich erneut an.
session-token-mismatch = Sitzungstoken stimmt nicht mit dem Benutzernamen überein.
refresh-token-expired = Aktualisierungstoken abgelaufen. Bitte melden Sie sich erneut an.
refresh-token-mismatch = Aktualisierungstoken stimmt nicht mit dem Benutzernamen überein.

# Registrierung
registration-success = Registrierung erfolgreich! Ihr Konto wartet auf Genehmigung.
registration-username-taken = Benutzername bereits vergeben. Bitte wählen Sie einen anderen Benutzernamen.

# Einstellungs-Fallback
pref-invalid-value = Ungültige Auswahl, Standardwert wird verwendet.

# Ablehnungsgrund
decline-reason-prompt = Geben Sie einen Grund für die Ablehnung ein (oder drücken Sie Escape zum Abbrechen):
account-action-empty-reason = Kein Grund angegeben.

# Admin-Benachrichtigungen für Kontoanfragen
account-request = Kontoanfrage
account-action = Kontoaktion durchgeführt

# Admin-Beförderung/Herabstufung
promote-admin = Admin befördern
demote-admin = Admin herabstufen
promote-admin-menu-title = Admin befördern
demote-admin-menu-title = Admin herabstufen
no-users-to-promote = Keine Benutzer verfügbar zum Befördern.
no-admins-to-demote = Keine Admins verfügbar zum Herabstufen.
confirm-promote = Sind Sie sicher, dass Sie { $player } zum Admin befördern möchten?
confirm-demote = Sind Sie sicher, dass Sie { $player } vom Admin herabstufen möchten?
broadcast-to-all = An alle Benutzer ankündigen
broadcast-to-admins = Nur an Admins ankündigen
broadcast-to-nobody = Still (keine Ankündigung)
promote-announcement = { $player } wurde zum Admin befördert!
promote-announcement-you = Sie wurden zum Admin befördert!
demote-announcement = { $player } wurde vom Admin herabgestuft.
demote-announcement-you = Sie wurden vom Admin herabgestuft.
not-admin-anymore = Sie sind kein Admin mehr und können diese Aktion nicht durchführen.
not-server-owner = Nur der Serverbesitzer kann diese Aktion durchführen.

# Serverbesitzübertragung
transfer-ownership = Besitz übertragen
transfer-ownership-menu-title = Besitz übertragen
no-admins-for-transfer = Keine Admins verfügbar zur Besitzübertragung.
confirm-transfer-ownership = Sind Sie sicher, dass Sie den Serverbesitz an { $player } übertragen möchten? Sie werden zum Admin herabgestuft.
transfer-ownership-announcement = { $player } ist jetzt der Play Palace-Serverbesitzer!
transfer-ownership-announcement-you = Sie sind jetzt der Play Palace-Serverbesitzer!

# Benutzersperrung
ban-user = Benutzer sperren
unban-user = Benutzer entsperren
no-users-to-ban = Keine Benutzer verfügbar zum Sperren.
no-users-to-unban = Keine gesperrten Benutzer zum Entsperren.
confirm-ban = Sind Sie sicher, dass Sie { $player } sperren möchten?
confirm-unban = Sind Sie sicher, dass Sie { $player } entsperren möchten?
ban-reason-prompt = Geben Sie einen Grund für die Sperrung ein (optional):
unban-reason-prompt = Geben Sie einen Grund für die Entsperrung ein (optional):
user-banned = { $player } wurde gesperrt.
user-unbanned = { $player } wurde entsperrt.
you-have-been-banned = Sie wurden von diesem Server gesperrt.
    Grund:
you-have-been-unbanned = Sie wurden von diesem Server entsperrt.
    Grund:
ban-no-reason = Kein Grund angegeben.

# Virtuelle Bots (nur Serverbesitzer)
virtual-bots = Virtuelle Bots
virtual-bots-fill = Server füllen
virtual-bots-clear = Alle Bots löschen
virtual-bots-status = Status
virtual-bots-clear-confirm = Sind Sie sicher, dass Sie alle virtuellen Bots löschen möchten? Dies wird auch alle Tische zerstören, an denen sie sind.
virtual-bots-not-available = Virtuelle Bots sind nicht verfügbar.
virtual-bots-filled = { $added } virtuelle Bots hinzugefügt. { $online } sind jetzt online.
virtual-bots-already-filled = Alle virtuellen Bots aus der Konfiguration sind bereits aktiv.
virtual-bots-cleared = { $bots } virtuelle Bots gelöscht und { $tables } { $tables ->
    [one] Tisch
   *[other] Tische
} zerstört.
virtual-bot-table-closed = Tisch vom Administrator geschlossen.
virtual-bots-none-to-clear = Keine virtuellen Bots zum Löschen.
virtual-bots-status-report = Virtuelle Bots: { $total } insgesamt, { $online } online, { $offline } offline, { $in_game } im Spiel.
virtual-bots-guided-overview = Geführte Tische
virtual-bots-groups-overview = Bot-Gruppen
virtual-bots-profiles-overview = Profile
virtual-bots-guided-header = Geführte Tische: { $count } Regel(n). Zuteilung: { $allocation }, Rückfall: { $fallback }, Standardprofil: { $default_profile }.
virtual-bots-guided-empty = Keine geführten Tischregeln konfiguriert.
virtual-bots-guided-status-active = aktiv
virtual-bots-guided-status-inactive = inaktiv
virtual-bots-guided-table-linked = mit Tisch { $table_id } verknüpft (Gastgeber { $host }, Spieler { $players }, Menschen { $humans })
virtual-bots-guided-table-stale = Tisch { $table_id } fehlt auf Server
virtual-bots-guided-table-unassigned = momentan wird kein Tisch verfolgt
virtual-bots-guided-next-change = nächste Änderung in { $ticks } Ticks
virtual-bots-guided-no-schedule = kein Zeitplanfenster
virtual-bots-guided-warning = ⚠ unterbesetzt
virtual-bots-guided-line = { $table }: Spiel { $game }, Priorität { $priority }, Bots { $assigned } (min { $min_bots }, max { $max_bots }), wartend { $waiting }, nicht verfügbar { $unavailable }, Status { $status }, Profil { $profile }, Gruppen { $groups }. { $table_state }. { $next_change } { $warning_text }
virtual-bots-groups-header = Bot-Gruppen: { $count } Tag(s), { $bots } konfigurierte Bots.
virtual-bots-groups-empty = Keine Bot-Gruppen definiert.
virtual-bots-groups-line = { $group }: Profil { $profile }, Bots { $total } (online { $online }, wartend { $waiting }, im Spiel { $in_game }, offline { $offline }), Regeln { $rules }.
virtual-bots-groups-no-rules = keine
virtual-bots-no-profile = Standard
virtual-bots-profile-inherit-default = erbt Standardprofil
virtual-bots-profiles-header = Profile: { $count } definiert (Standard: { $default_profile }).
virtual-bots-profiles-empty = Keine Profile definiert.
virtual-bots-profiles-line = { $profile } ({ $bot_count } Bots) Überschreibungen: { $overrides }.
virtual-bots-profiles-no-overrides = erbt Basiskonfiguration

localization-in-progress-try-again = Die Lokalisierung wird noch geladen. Bitte versuchen Sie es in einer Minute erneut.
