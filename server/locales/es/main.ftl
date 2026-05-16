# Main UI messages for PlayPalace

# Game categories
category-card-games = Juegos de Cartas
category-dice-games = Juegos de Dados
category-board-games = Juegos de Mesa
category-rb-play-center = Centro de Juegos RB
category-poker = Póker
category-uncategorized = Sin categoría

# Menu titles
main-menu-title = Menú Principal
play-menu-title = Jugar
categories-menu-title = Categorías de Juegos
tables-menu-title = Mesas Disponibles

# Menu items
play = Jugar
view-active-tables = Ver mesas activas
options = Opciones
logout = Cerrar sesión
back = Volver
context-menu = Menú contextual.
no-actions-available = No hay acciones disponibles.
create-table = Crear una mesa nueva
join-as-player = Unirse como jugador
join-as-spectator = Unirse como espectador
leave-table = Salir de la mesa
start-game = Iniciar juego
add-bot = Agregar bot
remove-bot = Eliminar bot
actions-menu = Menú de acciones
save-table = Guardar mesa
whose-turn = De quién es el turno
whos-at-table = Quién está en la mesa
check-scores = Ver puntuaciones
check-scores-detailed = Puntuaciones detalladas
check-game-options = Ver opciones del juego
no-game-options = No hay opciones de juego.

# Turn messages
game-player-skipped = { $player } es saltado.

# Table messages
table-created = { $host } creó una nueva mesa de { $game }.
table-joined = { $player } se unió a la mesa.
table-left = { $player } salió de la mesa.
new-host = { $player } ahora es el anfitrión.
waiting-for-players = Esperando jugadores. {$min} mín, { $max } máx.
game-starting = ¡El juego está comenzando!
table-listing = Mesa de { $host } ({ $count } usuarios)
table-listing-one = Mesa de { $host } ({ $count } usuario)
table-listing-with = Mesa de { $host } ({ $count } usuarios) con { $members }
table-listing-game = { $game }: Mesa de { $host } ({ $count } usuarios)
table-listing-game-one = { $game }: Mesa de { $host } ({ $count } usuario)
table-listing-game-with = { $game }: Mesa de { $host } ({ $count } usuarios) con { $members }
table-not-exists = La mesa ya no existe.
table-full = La mesa está llena.
player-replaced-by-bot = { $player } salió y fue reemplazado por un bot.
player-took-over = { $player } tomó el control del bot.
spectator-joined = Te uniste a la mesa de { $host } como espectador.

# Spectator mode
spectate = Espectador
now-playing = { $player } ahora está jugando.
now-spectating = { $player } ahora está como espectador.
spectator-left = { $player } dejó de ser espectador.

# General
welcome = ¡Bienvenido a PlayPalace!
goodbye = ¡Adiós!

# User presence announcements
user-online = { $player } se conectó.
user-offline = { $player } se desconectó.
user-is-admin = { $player } es un administrador de PlayPalace.
user-is-server-owner = { $player } es el propietario del servidor de PlayPalace.
online-users-none = No hay usuarios en línea.
online-users-one = 1 usuario: { $users }
online-users-many = { $count } usuarios: { $users }
online-user-not-in-game = No está en juego
online-user-waiting-approval = Esperando aprobación

# Options
language = Idioma
language-option = Idioma: { $language }
language-changed = Idioma establecido en { $language }.

# Boolean option states
option-on = Activado
option-off = Desactivado

# Sound options
turn-sound-option = Sonido de turno: { $status }

# Dice options
clear-kept-option = Limpiar dados mantenidos al tirar: { $status }
dice-keeping-style-option = Estilo de mantener dados: { $style }
dice-keeping-style-changed = Estilo de mantener dados establecido en { $style }.
dice-keeping-style-indexes = Índices de dados
dice-keeping-style-values = Valores de dados

# Bot names
cancel = Cancelar
no-bot-names-available = No hay nombres de bots disponibles.
select-bot-name = Selecciona un nombre para el bot
enter-bot-name = Ingresa el nombre del bot
no-options-available = No hay opciones disponibles.
no-scores-available = No hay puntuaciones disponibles.

# Duration estimation
estimate-duration = Estimar duración
estimate-computing = Calculando duración estimada del juego...
estimate-result = Promedio de bot: { $bot_time } (± { $std_dev }). { $outlier_info }Tiempo estimado para humano: { $human_time }.
estimate-error = No se pudo estimar la duración.
estimate-already-running = La estimación de duración ya está en progreso.

# Save/Restore
saved-tables = Mesas Guardadas
no-saved-tables = No tienes mesas guardadas.
no-active-tables = No hay mesas activas.
restore-table = Restaurar
delete-saved-table = Eliminar
saved-table-deleted = Mesa guardada eliminada.
missing-players = No se puede restaurar: estos jugadores no están disponibles: { $players }
table-restored = ¡Mesa restaurada! Todos los jugadores han sido transferidos.
table-saved-destroying = ¡Mesa guardada! Regresando al menú principal.
game-type-not-found = El tipo de juego ya no existe.

# Action disabled reasons
action-not-your-turn = No es tu turno.
action-not-playing = El juego no ha comenzado.
action-spectator = Los espectadores no pueden hacer esto.
action-not-host = Solo el anfitrión puede hacer esto.
action-game-in-progress = No se puede hacer esto mientras el juego está en progreso.
action-need-more-players = Se necesitan al menos { $min_players } jugadores para comenzar.
action-table-full = La mesa está llena.
action-no-bots = No hay bots para eliminar.
action-bots-cannot = Los bots no pueden hacer esto.
action-no-scores = Aún no hay puntuaciones disponibles.

# Dice actions
dice-not-rolled = Aún no has tirado.
dice-locked = Este dado está bloqueado.
dice-no-dice = No hay dados disponibles.

# Game actions
game-turn-start = Turno de { $player }.
game-no-turn = No es el turno de nadie ahora mismo.
table-no-players = No hay jugadores.
table-players-one = { $count } jugador: { $players }.
table-players-many = { $count } jugadores: { $players }.
table-spectators = Espectadores: { $spectators }.
game-leave = Salir
game-over = Juego Terminado
game-final-scores = Puntuaciones Finales
game-points = { $count } { $count ->
    [one] punto
   *[other] puntos
}
play = Jugar

# Leaderboards
leaderboards = Tablas de Clasificación
leaderboards-menu-title = Tablas de Clasificación
leaderboards-select-game = Selecciona un juego para ver su tabla de clasificación
leaderboard-no-data = Aún no hay datos de tabla de clasificación para este juego.

# Leaderboard types
leaderboard-type-wins = Líderes en Victorias
leaderboard-type-rating = Clasificación de Habilidad
leaderboard-type-total-score = Puntuación Total
leaderboard-type-high-score = Puntuación Máxima
leaderboard-type-games-played = Juegos Jugados
leaderboard-type-avg-points-per-turn = Promedio de Puntos Por Turno
leaderboard-type-best-single-turn = Mejor Turno Individual
leaderboard-type-score-per-round = Puntuación Por Ronda

# Leaderboard headers
leaderboard-wins-header = { $game } - Líderes en Victorias
leaderboard-total-score-header = { $game } - Puntuación Total
leaderboard-high-score-header = { $game } - Puntuación Máxima
leaderboard-games-played-header = { $game } - Juegos Jugados
leaderboard-rating-header = { $game } - Clasificaciones de Habilidad
leaderboard-avg-points-header = { $game } - Promedio de Puntos Por Turno
leaderboard-best-turn-header = { $game } - Mejor Turno Individual
leaderboard-score-per-round-header = { $game } - Puntuación Por Ronda

# Leaderboard entries
leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] victoria
   *[other] victorias
} { $losses } { $losses ->
    [one] derrota
   *[other] derrotas
}, { $percentage }% tasa de victoria
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } promedio
leaderboard-games-entry = { $rank }. { $player }: { $value } juegos

# Player stats
leaderboard-player-stats = Tus estadísticas: { $wins } victorias, { $losses } derrotas ({ $percentage }% tasa de victoria)
leaderboard-no-player-stats = Aún no has jugado este juego.

# Skill rating leaderboard
leaderboard-no-ratings = Aún no hay datos de clasificación para este juego.
leaderboard-rating-entry = { $rank }. { $player }: { $rating } clasificación ({ $mu } ± { $sigma })
leaderboard-player-rating = Tu clasificación: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = Aún no tienes clasificación para este juego.

# My Stats menu
my-stats = Mis Estadísticas
my-stats-select-game = Selecciona un juego para ver tus estadísticas
my-stats-no-data = Aún no has jugado este juego.
my-stats-no-games = Aún no has jugado ningún juego.
my-stats-header = { $game } - Tus Estadísticas
my-stats-wins = Victorias: { $value }
my-stats-losses = Derrotas: { $value }
my-stats-winrate = Tasa de victoria: { $value }%
my-stats-games-played = Juegos jugados: { $value }
my-stats-total-score = Puntuación total: { $value }
my-stats-high-score = Puntuación máxima: { $value }
my-stats-rating = Clasificación de habilidad: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = Aún no hay clasificación de habilidad
my-stats-avg-per-turn = Promedio de puntos por turno: { $value }
my-stats-best-turn = Mejor turno individual: { $value }

# Prediction system
predict-outcomes = Predecir resultados
predict-header = Resultados Predichos (por clasificación de habilidad)
predict-entry = { $rank }. { $player } (clasificación: { $rating })
predict-entry-2p = { $rank }. { $player } (clasificación: { $rating }, { $probability }% probabilidad de ganar)
predict-unavailable = Las predicciones de clasificación no están disponibles.
predict-need-players = Se necesitan al menos 2 jugadores humanos para predicciones.
action-need-more-humans = Se necesitan más jugadores humanos.
confirm-leave-game = ¿Estás seguro de que quieres salir de la mesa?
confirm-yes = Sí
confirm-no = No

# Administration
administration = Administración
admin-menu-title = Administración

# Account approval
account-approval = Aprobación de Cuenta
account-approval-menu-title = Aprobación de Cuenta
no-pending-accounts = No hay cuentas pendientes.
approve-account = Aprobar
decline-account = Rechazar
account-approved = La cuenta de { $player } ha sido aprobada.
account-declined = La cuenta de { $player } ha sido rechazada y eliminada.

# Waiting for approval (shown to unapproved users)
waiting-for-approval = Tu cuenta está esperando aprobación por un administrador.
account-approved-welcome = ¡Tu cuenta ha sido aprobada! ¡Bienvenido a PlayPalace!
account-declined-goodbye = Tu solicitud de cuenta ha sido rechazada.
    Razón:
account-banned = Tu cuenta está baneada y no se puede acceder.

# Login errors
incorrect-username = El nombre de usuario que ingresaste no existe.
incorrect-password = La contraseña que ingresaste es incorrecta.
already-logged-in = Esta cuenta ya está conectada.

# Validación de credenciales
credential-username-length = El nombre de usuario debe tener entre { $min } y { $max } caracteres.
credential-password-length = La contraseña debe tener entre { $min } y { $max } caracteres.

# Límite de intentos
rate-limit-login-ip = Demasiados intentos de inicio de sesión desde esta dirección. Espera un momento e inténtalo de nuevo.
rate-limit-login-user = Demasiados intentos fallidos de inicio de sesión para este nombre de usuario. Espera un momento e inténtalo de nuevo.
rate-limit-registration = Demasiados intentos de registro desde esta dirección. Espera un momento e inténtalo de nuevo.
rate-limit-refresh = Demasiados intentos de actualización desde esta dirección. Espera un momento e inténtalo de nuevo.

# Errores de sesión y autenticación
account-not-found = Cuenta no encontrada.
session-expired = La sesión ha expirado. Por favor, inicia sesión de nuevo.
session-token-mismatch = El token de sesión no coincide con el nombre de usuario.
refresh-token-expired = El token de actualización ha expirado. Por favor, inicia sesión de nuevo.
refresh-token-mismatch = El token de actualización no coincide con el nombre de usuario.

# Registro
registration-success = ¡Registro exitoso! Tu cuenta está esperando aprobación.
registration-username-taken = El nombre de usuario ya está en uso. Por favor, elige un nombre de usuario diferente.

# Valor predeterminado de preferencias
pref-invalid-value = Selección no válida, se usará el valor predeterminado.

# Decline reason
decline-reason-prompt = Ingresa una razón para rechazar (o presiona Escape para cancelar):
account-action-empty-reason = No se dio razón.

# Admin notifications for account requests
account-request = solicitud de cuenta
account-action = acción de cuenta tomada

# Admin promotion/demotion
promote-admin = Promover Administrador
demote-admin = Degradar Administrador
promote-admin-menu-title = Promover Administrador
demote-admin-menu-title = Degradar Administrador
no-users-to-promote = No hay usuarios disponibles para promover.
no-admins-to-demote = No hay administradores disponibles para degradar.
confirm-promote = ¿Estás seguro de que quieres promover a { $player } a administrador?
confirm-demote = ¿Estás seguro de que quieres degradar a { $player } de administrador?
broadcast-to-all = Anunciar a todos los usuarios
broadcast-to-admins = Anunciar solo a administradores
broadcast-to-nobody = Silencioso (sin anuncio)
promote-announcement = ¡{ $player } ha sido promovido a administrador!
promote-announcement-you = ¡Has sido promovido a administrador!
demote-announcement = { $player } ha sido degradado de administrador.
demote-announcement-you = Has sido degradado de administrador.
not-admin-anymore = Ya no eres administrador y no puedes realizar esta acción.
not-server-owner = Solo el propietario del servidor puede realizar esta acción.

# Server ownership transfer
transfer-ownership = Transferir Propiedad
transfer-ownership-menu-title = Transferir Propiedad
no-admins-for-transfer = No hay administradores disponibles para transferir la propiedad.
confirm-transfer-ownership = ¿Estás seguro de que quieres transferir la propiedad del servidor a { $player }? Serás degradado a administrador.
transfer-ownership-announcement = ¡{ $player } ahora es el propietario del servidor de Play Palace!
transfer-ownership-announcement-you = ¡Ahora eres el propietario del servidor de Play palace!

# User banning
ban-user = Banear Usuario
unban-user = Desbanear Usuario
no-users-to-ban = No hay usuarios disponibles para banear.
no-users-to-unban = No hay usuarios baneados para desbanear.
confirm-ban = ¿Estás seguro de que quieres banear a { $player }?
confirm-unban = ¿Estás seguro de que quieres desbanear a { $player }?
ban-reason-prompt = Ingresa una razón para el baneo (opcional):
unban-reason-prompt = Ingresa una razón para el desbaneo (opcional):
user-banned = { $player } ha sido baneado.
user-unbanned = { $player } ha sido desbaneado.
you-have-been-banned = Has sido baneado de este servidor.
    Razón:
you-have-been-unbanned = Has sido desbaneado de este servidor.
    Razón:
ban-no-reason = No se dio razón.

# Virtual bots (server owner only)
virtual-bots = Bots Virtuales
virtual-bots-fill = Llenar Servidor
virtual-bots-clear = Eliminar Todos los Bots
virtual-bots-status = Estado
virtual-bots-clear-confirm = ¿Estás seguro de que quieres eliminar todos los bots virtuales? Esto también destruirá cualquier mesa en la que estén.
virtual-bots-not-available = Los bots virtuales no están disponibles.
virtual-bots-filled = Agregados { $added } bots virtuales. { $online } están ahora en línea.
virtual-bots-already-filled = Todos los bots virtuales de la configuración ya están activos.
virtual-bots-cleared = Eliminados { $bots } bots virtuales y destruidas { $tables } { $tables ->
    [one] mesa
   *[other] mesas
}.
virtual-bot-table-closed = Mesa cerrada por el administrador.
virtual-bots-none-to-clear = No hay bots virtuales para eliminar.
virtual-bots-status-report = Bots Virtuales: { $total } total, { $online } en línea, { $offline } fuera de línea, { $in_game } en juego.
virtual-bots-guided-overview = Mesas Guiadas
virtual-bots-groups-overview = Grupos de Bots
virtual-bots-profiles-overview = Perfiles
virtual-bots-guided-header = Mesas guiadas: { $count } regla(s). Asignación: { $allocation }, respaldo: { $fallback }, perfil predeterminado: { $default_profile }.
virtual-bots-guided-empty = No hay reglas de mesa guiada configuradas.
virtual-bots-guided-status-active = activo
virtual-bots-guided-status-inactive = inactivo
virtual-bots-guided-table-linked = vinculado a mesa { $table_id } (anfitrión { $host }, jugadores { $players }, humanos { $humans })
virtual-bots-guided-table-stale = mesa { $table_id } falta en el servidor
virtual-bots-guided-table-unassigned = no hay mesa rastreada actualmente
virtual-bots-guided-next-change = próximo cambio en { $ticks } ticks
virtual-bots-guided-no-schedule = sin ventana de programación
virtual-bots-guided-warning = ⚠ insuficiente
virtual-bots-guided-line = { $table }: juego { $game }, prioridad { $priority }, bots { $assigned } (mín { $min_bots }, máx { $max_bots }), esperando { $waiting }, no disponibles { $unavailable }, estado { $status }, perfil { $profile }, grupos { $groups }. { $table_state }. { $next_change } { $warning_text }
virtual-bots-groups-header = Grupos de bots: { $count } etiqueta(s), { $bots } bots configurados.
virtual-bots-groups-empty = No hay grupos de bots definidos.
virtual-bots-groups-line = { $group }: perfil { $profile }, bots { $total } (en línea { $online }, esperando { $waiting }, en juego { $in_game }, fuera de línea { $offline }), reglas { $rules }.
virtual-bots-groups-no-rules = ninguno
virtual-bots-no-profile = predeterminado
virtual-bots-profile-inherit-default = hereda perfil predeterminado
virtual-bots-profiles-header = Perfiles: { $count } definidos (predeterminado: { $default_profile }).
virtual-bots-profiles-empty = No hay perfiles definidos.
virtual-bots-profiles-line = { $profile } ({ $bot_count } bots) anulaciones: { $overrides }.
virtual-bots-profiles-no-overrides = hereda configuración base

localization-in-progress-try-again = La localización está en progreso. Vuelve a intentarlo en un minuto.
