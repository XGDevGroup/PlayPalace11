# Main UI messages for PlayPalace

# Game categories
category-card-games = Giochi di carte
category-dice-games = Giochi di dadi
category-rb-play-center = Centro RB Play
category-poker = Poker
category-uncategorized = Senza categoria

# Menu titles
main-menu-title = Menu principale
play-menu-title = Gioca
categories-menu-title = Categorie di gioco
tables-menu-title = Tavoli disponibili

# Menu items
play = Gioca
view-active-tables = Visualizza tavoli attivi
options = Opzioni
logout = Esci
back = Indietro
go-back = Torna indietro
context-menu = Menu contestuale.
no-actions-available = Nessuna azione disponibile.
create-table = Crea un nuovo tavolo
join-as-player = Unisciti come giocatore
join-as-spectator = Unisciti come spettatore
leave-table = Lascia tavolo
start-game = Inizia partita
add-bot = Aggiungi bot
remove-bot = Rimuovi bot
actions-menu = Menu azioni
save-table = Salva tavolo
whose-turn = Di chi è il turno
whos-at-table = Chi c'è al tavolo
check-scores = Controlla punteggi
check-scores-detailed = Punteggi dettagliati
check-game-options = Controlla opzioni di gioco
no-game-options = Nessuna opzione di gioco.

# Turn messages
game-player-skipped = { $player } viene saltato.

# Table messages
table-created = { $host } ha creato un nuovo tavolo { $game }.
table-joined = { $player } si è unito al tavolo.
table-left = { $player } ha lasciato il tavolo.
new-host = { $player } è ora il padrone di casa.
waiting-for-players = In attesa di giocatori. {$min} min, { $max } max.
game-starting = La partita sta iniziando!
table-listing = Tavolo di { $host } ({ $count } utenti)
table-listing-one = Tavolo di { $host } ({ $count } utente)
table-listing-with = Tavolo di { $host } ({ $count } utenti) con { $members }
table-listing-game = { $game }: tavolo di { $host } ({ $count } utenti)
table-listing-game-one = { $game }: tavolo di { $host } ({ $count } utente)
table-listing-game-with = { $game }: tavolo di { $host } ({ $count } utenti) con { $members }
table-not-exists = Il tavolo non esiste più.
table-full = Il tavolo è pieno.
player-replaced-by-bot = { $player } è uscito ed è stato sostituito da un bot.
player-took-over = { $player } ha preso il posto del bot.
spectator-joined = Ti sei unito al tavolo di { $host } come spettatore.

# Spectator mode
spectate = Guarda
now-playing = { $player } sta giocando ora.
now-spectating = { $player } sta guardando ora.
spectator-left = { $player } ha smesso di guardare.

# General
welcome = Benvenuto in PlayPalace!
goodbye = Arrivederci!

# User presence announcements
user-online = { $player } è entrato online.
user-offline = { $player } è andato offline.
user-is-admin = { $player } è un amministratore di PlayPalace.
user-is-server-owner = { $player } è il proprietario del server PlayPalace.
online-users-none = Nessun utente online.
online-users-one = 1 utente: { $users }
online-users-many = { $count } utenti: { $users }
online-user-not-in-game = Non in partita
online-user-waiting-approval = In attesa di approvazione

# Options
language = Lingua
language-option = Lingua: { $language }
language-changed = Lingua impostata su { $language }.

# Boolean option states
option-on = Attivo
option-off = Disattivo

# Sound options
turn-sound-option = Suono turno: { $status }

# Dice options
clear-kept-option = Cancella dadi mantenuti al lancio: { $status }
dice-keeping-style-option = Stile mantenimento dadi: { $style }
dice-keeping-style-changed = Stile mantenimento dadi impostato su { $style }.
dice-keeping-style-indexes = Indici dei dadi
dice-keeping-style-values = Valori dei dadi

# Bot names
cancel = Annulla
no-bot-names-available = Nessun nome bot disponibile.
select-bot-name = Seleziona un nome per il bot
enter-bot-name = Inserisci nome bot
no-options-available = Nessuna opzione disponibile.
no-scores-available = Nessun punteggio disponibile.

# Duration estimation
estimate-duration = Stima durata
estimate-computing = Calcolo della durata stimata della partita...
estimate-result = Media bot: { $bot_time } (± { $std_dev }). { $outlier_info }Tempo umano stimato: { $human_time }.
estimate-error = Impossibile stimare la durata.
estimate-already-running = La stima della durata è già in corso.

# Save/Restore
saved-tables = Tavoli salvati
no-saved-tables = Non hai tavoli salvati.
no-active-tables = Nessun tavolo attivo.
restore-table = Ripristina
delete-saved-table = Elimina
saved-table-deleted = Tavolo salvato eliminato.
missing-players = Impossibile ripristinare: questi giocatori non sono disponibili: { $players }
table-restored = Tavolo ripristinato! Tutti i giocatori sono stati trasferiti.
table-saved-destroying = Tavolo salvato! Ritorno al menu principale.
game-type-not-found = Il tipo di gioco non esiste più.

# Action disabled reasons
action-not-your-turn = Non è il tuo turno.
action-not-playing = La partita non è ancora iniziata.
action-spectator = Gli spettatori non possono farlo.
action-not-host = Solo il padrone di casa può farlo.
action-game-in-progress = Non puoi farlo mentre la partita è in corso.
action-need-more-players = Servono più giocatori per iniziare.
action-table-full = Il tavolo è pieno.
action-no-bots = Non ci sono bot da rimuovere.
action-bots-cannot = I bot non possono farlo.
action-no-scores = Nessun punteggio ancora disponibile.

# Dice actions
dice-not-rolled = Non hai ancora lanciato.
dice-locked = Questo dado è bloccato.
dice-no-dice = Nessun dado disponibile.

# Game actions
game-turn-start = Turno di { $player }.
game-no-turn = Nessuno ha il turno ora.
table-no-players = Nessun giocatore.
table-players-one = { $count } giocatore: { $players }.
table-players-many = { $count } giocatori: { $players }.
table-spectators = Spettatori: { $spectators }.
game-leave = Esci
game-over = Partita terminata
game-final-scores = Punteggi finali
game-points = { $count } { $count ->
    [one] punto
   *[other] punti
}
play = Gioca

# Leaderboards
leaderboards = Classifiche
leaderboards-menu-title = Classifiche
leaderboards-select-game = Seleziona un gioco per visualizzare la classifica
leaderboard-no-data = Nessun dato di classifica per questo gioco.

# Leaderboard types
leaderboard-type-wins = Leader per vittorie
leaderboard-type-rating = Valutazione abilità
leaderboard-type-total-score = Punteggio totale
leaderboard-type-high-score = Punteggio più alto
leaderboard-type-games-played = Partite giocate
leaderboard-type-avg-points-per-turn = Punti medi per turno
leaderboard-type-best-single-turn = Miglior turno singolo
leaderboard-type-score-per-round = Punteggio per round

# Leaderboard headers
leaderboard-wins-header = { $game } - Leader per vittorie
leaderboard-total-score-header = { $game } - Punteggio totale
leaderboard-high-score-header = { $game } - Punteggio più alto
leaderboard-games-played-header = { $game } - Partite giocate
leaderboard-rating-header = { $game } - Valutazioni abilità
leaderboard-avg-points-header = { $game } - Punti medi per turno
leaderboard-best-turn-header = { $game } - Miglior turno singolo
leaderboard-score-per-round-header = { $game } - Punteggio per round

# Leaderboard entries
leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] vittoria
   *[other] vittorie
} { $losses } { $losses ->
    [one] sconfitta
   *[other] sconfitte
}, { $percentage }% di vittorie
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } medio
leaderboard-games-entry = { $rank }. { $player }: { $value } partite

# Player stats
leaderboard-player-stats = Le tue statistiche: { $wins } vittorie, { $losses } sconfitte ({ $percentage }% di vittorie)
leaderboard-no-player-stats = Non hai ancora giocato a questo gioco.

# Skill rating leaderboard
leaderboard-no-ratings = Nessun dato di valutazione per questo gioco.
leaderboard-rating-entry = { $rank }. { $player }: { $rating } valutazione ({ $mu } ± { $sigma })
leaderboard-player-rating = La tua valutazione: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = Non hai ancora una valutazione per questo gioco.

# My Stats menu
my-stats = Le mie statistiche
my-stats-select-game = Seleziona un gioco per visualizzare le tue statistiche
my-stats-no-data = Non hai ancora giocato a questo gioco.
my-stats-no-games = Non hai ancora giocato a nessun gioco.
my-stats-header = { $game } - Le tue statistiche
my-stats-wins = Vittorie: { $value }
my-stats-losses = Sconfitte: { $value }
my-stats-winrate = Tasso di vittoria: { $value }%
my-stats-games-played = Partite giocate: { $value }
my-stats-total-score = Punteggio totale: { $value }
my-stats-high-score = Punteggio più alto: { $value }
my-stats-rating = Valutazione abilità: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = Nessuna valutazione abilità ancora
my-stats-avg-per-turn = Punti medi per turno: { $value }
my-stats-best-turn = Miglior turno singolo: { $value }

# Prediction system
predict-outcomes = Prevedi risultati
predict-header = Risultati previsti (in base alla valutazione abilità)
predict-entry = { $rank }. { $player } (valutazione: { $rating })
predict-entry-2p = { $rank }. { $player } (valutazione: { $rating }, { $probability }% di probabilità di vittoria)
predict-unavailable = Le previsioni di valutazione non sono disponibili.
predict-need-players = Servono almeno 2 giocatori umani per le previsioni.
action-need-more-humans = Servono più giocatori umani.
confirm-leave-game = Sei sicuro di voler lasciare il tavolo?
confirm-yes = Sì
confirm-no = No

# Administration
administration = Amministrazione
admin-menu-title = Amministrazione

# Account approval
account-approval = Approvazione account
account-approval-menu-title = Approvazione account
no-pending-accounts = Nessun account in attesa.
approve-account = Approva
decline-account = Rifiuta
account-approved = L'account di { $player } è stato approvato.
account-declined = L'account di { $player } è stato rifiutato ed eliminato.

# Waiting for approval (shown to unapproved users)
waiting-for-approval = Il tuo account è in attesa di approvazione da parte di un amministratore.
account-approved-welcome = Il tuo account è stato approvato! Benvenuto in PlayPalace!
account-declined-goodbye = La tua richiesta di account è stata rifiutata.
    Motivo:
account-banned = Il tuo account è stato bannato e non è accessibile.

# Login errors
incorrect-username = Il nome utente inserito non esiste.
incorrect-password = La password inserita non è corretta.
already-logged-in = Questo account è già connesso.

# Validazione credenziali
credential-username-length = Il nome utente deve essere compreso tra { $min } e { $max } caratteri.
credential-password-length = La password deve essere compresa tra { $min } e { $max } caratteri.

# Limitazione tentativi
rate-limit-login-ip = Troppi tentativi di accesso da questo indirizzo. Attendi e riprova.
rate-limit-login-user = Troppi tentativi di accesso falliti per questo nome utente. Attendi e riprova.
rate-limit-registration = Troppi tentativi di registrazione da questo indirizzo. Attendi e riprova.
rate-limit-refresh = Troppi tentativi di aggiornamento da questo indirizzo. Attendi e riprova.

# Errori di sessione/autenticazione
account-not-found = Account non trovato.
session-expired = Sessione scaduta. Accedi di nuovo.
session-token-mismatch = Il token di sessione non corrisponde al nome utente.
refresh-token-expired = Token di aggiornamento scaduto. Accedi di nuovo.
refresh-token-mismatch = Il token di aggiornamento non corrisponde al nome utente.

# Registrazione
registration-success = Registrazione effettuata! Il tuo account è in attesa di approvazione.
registration-username-taken = Nome utente già in uso. Scegli un nome utente diverso.

# Preferenza predefinita
pref-invalid-value = Selezione non valida, verrà utilizzato il valore predefinito.

# Decline reason
decline-reason-prompt = Inserisci il motivo del rifiuto (o premi Escape per annullare):
account-action-empty-reason = Nessun motivo fornito.

# Admin notifications for account requests
account-request = richiesta di account
account-action = azione sull'account effettuata

# Admin promotion/demotion
promote-admin = Promuovi amministratore
demote-admin = Retrocedi amministratore
promote-admin-menu-title = Promuovi amministratore
demote-admin-menu-title = Retrocedi amministratore
no-users-to-promote = Nessun utente disponibile da promuovere.
no-admins-to-demote = Nessun amministratore disponibile da retrocedere.
confirm-promote = Sei sicuro di voler promuovere { $player } ad amministratore?
confirm-demote = Sei sicuro di voler retrocedere { $player } da amministratore?
broadcast-to-all = Annuncia a tutti gli utenti
broadcast-to-admins = Annuncia solo agli amministratori
broadcast-to-nobody = Silenzioso (nessun annuncio)
promote-announcement = { $player } è stato promosso ad amministratore!
promote-announcement-you = Sei stato promosso ad amministratore!
demote-announcement = { $player } è stato retrocesso da amministratore.
demote-announcement-you = Sei stato retrocesso da amministratore.
not-admin-anymore = Non sei più un amministratore e non puoi eseguire questa azione.
not-server-owner = Solo il proprietario del server può eseguire questa azione.

# Server ownership transfer
transfer-ownership = Trasferisci proprietà
transfer-ownership-menu-title = Trasferisci proprietà
no-admins-for-transfer = Nessun amministratore disponibile per il trasferimento di proprietà.
confirm-transfer-ownership = Sei sicuro di voler trasferire la proprietà del server a { $player }? Sarai retrocesso ad amministratore.
transfer-ownership-announcement = { $player } è ora il proprietario del server Play Palace!
transfer-ownership-announcement-you = Ora sei il proprietario del server Play Palace!

# User banning
ban-user = Banna utente
unban-user = Rimuovi ban utente
no-users-to-ban = Nessun utente disponibile da bannare.
no-users-to-unban = Nessun utente bannato da sbannare.
confirm-ban = Sei sicuro di voler bannare { $player }?
confirm-unban = Sei sicuro di voler rimuovere il ban a { $player }?
ban-reason-prompt = Inserisci il motivo del ban (opzionale):
unban-reason-prompt = Inserisci il motivo della rimozione del ban (opzionale):
user-banned = { $player } è stato bannato.
user-unbanned = Il ban di { $player } è stato rimosso.
you-have-been-banned = Sei stato bannato da questo server.
    Motivo:
you-have-been-unbanned = Il tuo ban è stato rimosso da questo server.
    Motivo:
ban-no-reason = Nessun motivo fornito.

# Virtual bots (server owner only)
virtual-bots = Bot virtuali
virtual-bots-fill = Riempi server
virtual-bots-clear = Elimina tutti i bot
virtual-bots-status = Stato
virtual-bots-clear-confirm = Sei sicuro di voler eliminare tutti i bot virtuali? Questo distruggerà anche tutti i tavoli in cui si trovano.
virtual-bots-not-available = I bot virtuali non sono disponibili.
virtual-bots-filled = Aggiunti { $added } bot virtuali. { $online } sono ora online.
virtual-bots-already-filled = Tutti i bot virtuali dalla configurazione sono già attivi.
virtual-bots-cleared = Eliminati { $bots } bot virtuali e distrutti { $tables } { $tables ->
    [one] tavolo
   *[other] tavoli
}.
virtual-bot-table-closed = Tavolo chiuso dall'amministratore.
virtual-bots-none-to-clear = Nessun bot virtuale da eliminare.
virtual-bots-status-report = Bot virtuali: { $total } totali, { $online } online, { $offline } offline, { $in_game } in partita.
virtual-bots-guided-overview = Tavoli guidati
virtual-bots-groups-overview = Gruppi di bot
virtual-bots-profiles-overview = Profili
virtual-bots-guided-header = Tavoli guidati: { $count } regola(e). Allocazione: { $allocation }, fallback: { $fallback }, profilo predefinito: { $default_profile }.
virtual-bots-guided-empty = Nessuna regola di tavolo guidato configurata.
virtual-bots-guided-status-active = attivo
virtual-bots-guided-status-inactive = inattivo
virtual-bots-guided-table-linked = collegato al tavolo { $table_id } (host { $host }, giocatori { $players }, umani { $humans })
virtual-bots-guided-table-stale = tavolo { $table_id } mancante sul server
virtual-bots-guided-table-unassigned = nessun tavolo attualmente tracciato
virtual-bots-guided-next-change = prossimo cambio tra { $ticks } tick
virtual-bots-guided-no-schedule = nessuna finestra di pianificazione
virtual-bots-guided-warning = ⚠ non completamente riempito
virtual-bots-guided-line = { $table }: gioco { $game }, priorità { $priority }, bot { $assigned } (min { $min_bots }, max { $max_bots }), in attesa { $waiting }, non disponibile { $unavailable }, stato { $status }, profilo { $profile }, gruppi { $groups }. { $table_state }. { $next_change } { $warning_text }
virtual-bots-groups-header = Gruppi di bot: { $count } tag, { $bots } bot configurati.
virtual-bots-groups-empty = Nessun gruppo di bot definito.
virtual-bots-groups-line = { $group }: profilo { $profile }, bot { $total } (online { $online }, in attesa { $waiting }, in partita { $in_game }, offline { $offline }), regole { $rules }.
virtual-bots-groups-no-rules = nessuna
virtual-bots-no-profile = predefinito
virtual-bots-profile-inherit-default = eredita profilo predefinito
virtual-bots-profiles-header = Profili: { $count } definiti (predefinito: { $default_profile }).
virtual-bots-profiles-empty = Nessun profilo definito.
virtual-bots-profiles-line = { $profile } ({ $bot_count } bot) sostituzioni: { $overrides }.
virtual-bots-profiles-no-overrides = eredita configurazione base

localization-in-progress-try-again = La localizzazione è in corso. Riprova tra un minuto.
