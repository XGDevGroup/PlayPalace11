# Main UI messages for PlayPalace

# Game categories
category-card-games = Card Games
category-dice-games = Dice Games
category-board-games = Board Games
category-rb-play-center = RB Play Center
category-poker = Poker
category-uncategorized = Uncategorized
category-playaural = PlayAural

# Menu titles
main-menu-title = Main Menu
play-menu-title = Play
categories-menu-title = Game Categories
tables-menu-title = Available Tables

# Menu items
play = Play
view-active-tables = View active tables
options = Options
logout = Logout
back = Back
done = Done
context-menu = Context menu.
no-actions-available = No actions available.
placeholder-feature = This feature is under consideration, thus is unavailable at this time.
create-table = Create a new table
join-as-player = Join as player
join-as-spectator = Join as spectator
leave-table = Leave table
start-game = Start game
add-bot = Add bot
remove-bot = Remove bot
actions-menu = Actions menu
save-table = Save table
whose-turn = Whose turn
whos-at-table = Who's at the table
check-scores = Check scores
check-scores-detailed = Detailed scores
check-game-options = Check Game Options
no-game-options = No Game Options

# Turn messages
game-player-skipped = { $player } is skipped.

# Table messages
table-created = { $host } created a new { $game } table.
table-joined = { $player } joined the table.
table-left = { $player } left the table.
new-host = { $player } is now the host.
waiting-for-players = Waiting for players. {$min} min, { $max } max.
game-starting = Game starting!
table-listing = { $host }'s table ({ $count } users)
table-listing-one = { $host }'s table ({ $count } user)
table-listing-with = { $host }'s table ({ $count } users) with { $members }
table-listing-game = { $game }: { $host }'s table ({ $count } users)
table-listing-game-one = { $game }: { $host }'s table ({ $count } user)
table-listing-game-with = { $game }: { $host }'s table ({ $count } users) with { $members }
table-not-exists = Table no longer exists.
table-full = Table is full.
player-replaced-by-bot = { $player } left and was replaced by a bot.
player-took-over = { $player } took over from the bot.
spectator-joined = Joined { $host }'s table as a spectator.

# Spectator mode
spectate = Spectate
now-playing = { $player } is now playing.
now-spectating = { $player } is now spectating.
spectator-left = { $player } stopped spectating.

# General
welcome = Welcome to PlayPalace!
goodbye = Goodbye!

# Visibility control
visibility-public = public
visibility-private = private
visibility-available = available
visibility-unavailable = unavailable

# User presence announcements
user-online = { $player } came online.
user-offline = { $player } went offline.
user-is-admin = { $player } is an administrator of PlayPalace.
user-is-server-owner = { $player } is the server owner of PlayPalace.
online-users-none = No users online.
online-users-one = 1 user: { $users }
online-users-many = { $count } users: { $users }
online-user-not-in-game = Not in game
online-user-waiting-approval = Waiting for approval

# Action states
action-locked = This action is currently unavailable.

# Option states and helpers
option-on = On
option-off = Off
option-locked = This option is currently locked by another setting.

# Options
language = Language
language-option = Language: { $language }
language-changed = Language set to { $language }.

fluent-languages-option = Fluent languages ({ $count })

# Preference categories
pref-category-display = Display
pref-category-sounds = Sounds
pref-category-dice = Dice Behaviour
pref-category-gameplay = Gameplay

# Preference labels (shown in menus)
pref-set-play-turn-sound = Turn sound: { $status }
pref-desc-play-turn-sound = Play a sound when it becomes your turn
pref-changed-play-turn-sound = Turn sound { $status }.

pref-set-brief-announcements = Brief announcements: { $status }
pref-desc-brief-announcements = Use shorter announcements during gameplay instead of detailed commentary
pref-changed-brief-announcements = Brief announcements { $status }.

pref-set-clear-kept-on-roll = Clear kept dice when rolling: { $status }
pref-desc-clear-kept-on-roll = Automatically unkeep all dice after each roll
pref-changed-clear-kept-on-roll = Clear kept dice when rolling { $status }.

pref-set-dice-keeping-style = Dice keeping style: { $choice }
pref-desc-dice-keeping-style = How dice are selected for keeping
pref-select-dice-keeping-style = Select dice keeping style:
pref-changed-dice-keeping-style = Dice keeping style set to { $choice }.
pref-dice-keeping-style-playpalace = Dice indexes
pref-dice-keeping-style-quentin_c = Dice values

pref-set-confirm-destructive-actions = Confirm destructive actions: { $status }
pref-desc-confirm-destructive-actions = Request confirmation when performing destructive actions like passing your turn
pref-changed-confirm-destructive-actions = Confirm destructive actions { $status }.

# Preference system
pref-back = Back
pref-reset-all = Reset all preferences to defaults
pref-reset-category = Reset { $category } to defaults
pref-reset-done = Preferences reset to defaults.
pref-per-game-for = { $game }: { $value }
pref-default = Default

# Legacy keys (kept for compatibility)
turn-sound-option = Turn sound: { $status }
clear-kept-option = Clear kept dice when rolling: { $status }
dice-keeping-style-option = Dice keeping style: { $style }
dice-keeping-style-changed = Dice keeping style set to { $style }.
dice-keeping-style-indexes = Dice indexes
dice-keeping-style-values = Dice values

# Bot names
cancel = Cancel
no-bot-names-available = No bot names available.
select-bot-name = Select a name for the bot
enter-bot-name = Enter bot name
no-options-available = No options available.
no-scores-available = No scores available.

# Duration estimation
estimate-duration = Estimate duration
estimate-computing = Computing estimated game duration...
estimate-result = Bot average: { $bot_time } (± { $std_dev }). { $outlier_info }Estimated human time: { $human_time }.
estimate-error = Could not estimate duration.
estimate-already-running = Duration estimation already in progress.

# Save/Restore
saved-tables = Saved Tables
no-saved-tables = You have no saved tables.
no-active-tables = No active tables.
restore-table = Restore
delete-saved-table = Delete
saved-table-deleted = Saved table deleted.
missing-players = Cannot restore: these players are not available: { $players }
table-restored = Table restored! All players have been transferred.
table-saved-destroying = Table saved! Returning to main menu.
game-type-not-found = Game type no longer exists.

# Action disabled reasons
action-not-your-turn = It's not your turn.
action-not-playing = The game hasn't started.
action-spectator = Spectators cannot do this.
action-not-host = Only the host can do this.
action-game-in-progress = Cannot do this while the game is in progress.
action-need-more-players = Need at least { $min_players } players to start.
action-table-full = The table is full.
action-no-bots = There are no bots to remove.
action-bots-cannot = Bots cannot do this.
action-no-scores = No scores available yet.

# Dice actions
dice-not-rolled = You haven't rolled yet.
dice-locked = This die is locked.
dice-no-dice = No dice available.

# Game actions
game-turn-start = { $player }'s turn.
game-no-turn = No one's turn right now.
table-no-players = No players.
table-players-one = { $count } player: { $players }.
table-players-many = { $count } players: { $players }.
table-spectators = Spectators: { $spectators }.
game-leave = Leave
game-over = Game Over
game-over-leave = Congratulations you did great!
game-final-scores = Final Scores
game-points = { $count } { $count ->
    [one] point
   *[other] points
}
play = Play

# Leaderboards
leaderboards = Leaderboards
leaderboards-menu-title = Leaderboards
leaderboards-select-game = Select a game to view its leaderboard
leaderboard-no-data = No leaderboard data yet for this game.

# Leaderboard types
leaderboard-type-wins = Win Leaders
leaderboard-type-rating = Skill Rating
leaderboard-type-total-score = Total Score
leaderboard-type-high-score = High Score
leaderboard-type-games-played = Games Played
leaderboard-type-avg-points-per-turn = Avg Points Per Turn
leaderboard-type-best-single-turn = Best Single Turn
leaderboard-type-score-per-round = Score Per Round

# Leaderboard headers
leaderboard-wins-header = { $game } - Win Leaders
leaderboard-total-score-header = { $game } - Total Score
leaderboard-high-score-header = { $game } - High Score
leaderboard-games-played-header = { $game } - Games Played
leaderboard-rating-header = { $game } - Skill Ratings
leaderboard-avg-points-header = { $game } - Avg Points Per Turn
leaderboard-best-turn-header = { $game } - Best Single Turn
leaderboard-score-per-round-header = { $game } - Score Per Round

# Leaderboard entries
leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] win
   *[other] wins
} { $losses } { $losses ->
    [one] loss
   *[other] losses
}, { $percentage }% winrate
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } avg
leaderboard-games-entry = { $rank }. { $player }: { $value } games

# Player stats
leaderboard-player-stats = Your stats: { $wins } wins, { $losses } losses ({ $percentage }% win rate)
leaderboard-no-player-stats = You haven't played this game yet.

# Skill rating leaderboard
leaderboard-no-ratings = No rating data yet for this game.
leaderboard-rating-entry = { $rank }. { $player }: { $rating } rating ({ $mu } ± { $sigma })
leaderboard-player-rating = Your rating: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = You don't have a rating for this game yet.

# My Stats menu
my-stats = My Stats
my-stats-select-game = Select a game to view your stats
my-stats-no-data = You haven't played this game yet.
my-stats-no-games = You haven't played any games yet.
my-stats-header = { $game } - Your Stats
my-stats-wins = Wins: { $value }
my-stats-losses = Losses: { $value }
my-stats-winrate = Win rate: { $value }%
my-stats-games-played = Games played: { $value }
my-stats-total-score = Total score: { $value }
my-stats-high-score = High score: { $value }
my-stats-rating = Skill rating: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = No skill rating yet
my-stats-avg-per-turn = Avg points per turn: { $value }
my-stats-best-turn = Best single turn: { $value }

# Prediction system
predict-outcomes = Predict outcomes
predict-header = Predicted Outcomes (by skill rating)
predict-entry = { $rank }. { $player } (rating: { $rating })
predict-entry-2p = { $rank }. { $player } (rating: { $rating }, { $probability }% win chance)
predict-unavailable = Rating predictions are not available.
predict-need-players = Need at least 2 human players for predictions.
action-need-more-humans = Need more human players.
confirm-leave-game = Are you sure you want to leave the table?
confirm-logout = Are you sure you want to log out?
confirm-yes = Yes
confirm-no = No

# Administration
administration = Administration
admin-menu-title = Administration

# Account approval
account-approval = Account Approval
account-approval-menu-title = Account Approval
no-pending-accounts = No pending accounts.
approve-account = Approve
decline-account = Decline
account-approved = { $player }'s account has been approved.
account-declined = { $player }'s account has been declined and deleted.

# Waiting for approval (shown to unapproved users)
waiting-for-approval = Your account is waiting for approval by an administrator.
account-approved-welcome = Your account has been approved! Welcome to PlayPalace!
account-declined-goodbye = Your account request has been declined.
    Reason:
account-banned = Your account is banned and cannot be accessed.

# Login errors
incorrect-username = The username you entered does not exist.
incorrect-password = The password you entered is incorrect.
already-logged-in = This account is already logged in.
accounts-blocked = Sorry, registration is currently disabled. Only administrators or the server owner can create accounts at this time. Check back later!

# Credential validation
credential-username-length = Username must be between { $min } and { $max } characters.
credential-password-length = Password must be between { $min } and { $max } characters.

# Rate limiting
rate-limit-login-ip = Too many login attempts from this address. Please wait and try again.
rate-limit-login-user = Too many failed login attempts for this username. Please wait and try again.
rate-limit-registration = Too many registration attempts from this address. Please wait and try again.
rate-limit-refresh = Too many refresh attempts from this address. Please wait and try again.

# Session/auth errors
account-not-found = Account not found.
session-expired = Session expired. Please log in again.
session-token-mismatch = Session token does not match username.
refresh-token-expired = Refresh token expired. Please log in again.
refresh-token-mismatch = Refresh token does not match username.

# Registration
registration-success = Registration successful! Your account is waiting for approval.
registration-username-taken = Username already taken. Please choose a different username.

# Preference fallback
pref-invalid-value = Invalid selection, using default.

# Decline reason
decline-reason-prompt = Enter a reason for declining (or press Escape to cancel):
account-action-empty-reason = No reason given.

# Admin notifications for account requests
account-request = account request
account-action = account action taken

# Admin promotion/demotion
promote-admin = Promote Admin
demote-admin = Demote Admin
promote-admin-menu-title = Promote Admin
demote-admin-menu-title = Demote Admin
no-users-to-promote = No users available to promote.
no-admins-to-demote = No admins available to demote.
confirm-promote = Are you sure you want to promote { $player } to admin?
confirm-demote = Are you sure you want to demote { $player } from admin?
broadcast-to-all = Announce to all users
broadcast-to-admins = Announce to admins only
broadcast-to-nobody = Silent (no announcement)
promote-announcement = { $player } has been promoted to admin!
promote-announcement-you = You have been promoted to admin!
demote-announcement = { $player } has been demoted from admin.
demote-announcement-you = You have been demoted from admin.
not-admin-anymore = You are no longer an admin and cannot perform this action.
not-server-owner = Only the server owner can perform this action.

# Server ownership transfer
transfer-ownership = Transfer Ownership
transfer-ownership-menu-title = Transfer Ownership
no-admins-for-transfer = No admins available to transfer ownership to.
confirm-transfer-ownership = Are you sure you want to transfer server ownership to { $player }? You will be demoted to admin.
transfer-ownership-announcement = { $player } is now the Play Palace server owner!
transfer-ownership-announcement-you = You are now the Play palace server owner!

# User banning
ban-user = Ban User
unban-user = Unban User
no-users-to-ban = No users available to ban.
no-users-to-unban = No banned users to unban.
confirm-ban = Are you sure you want to ban { $player }?
confirm-unban = Are you sure you want to unban { $player }?
ban-reason-prompt = Enter a reason for the ban (optional):
unban-reason-prompt = Enter a reason for the unban (optional):
user-banned = { $player } has been banned.
user-unbanned = { $player } has been unbanned.
you-have-been-banned = You have been banned from this server.
    Reason:
you-have-been-unbanned = You have been unbanned from this server.
    Reason:
ban-no-reason = No reason given.

# Virtual bots (server owner only)
virtual-bots = Virtual Bots
virtual-bots-fill = Fill Server
virtual-bots-clear = Clear All Bots
virtual-bots-status = Status
virtual-bots-clear-confirm = Are you sure you want to clear all virtual bots? This will also destroy any tables they are in.
virtual-bots-not-available = Virtual bots are not available.
virtual-bots-filled = Added { $added } virtual bots. { $online } are now online.
virtual-bots-already-filled = All virtual bots from the configuration are already active.
virtual-bots-cleared = Cleared { $bots } virtual bots and destroyed { $tables } { $tables ->
    [one] table
   *[other] tables
}.
virtual-bot-table-closed = Table closed by administrator.
virtual-bots-none-to-clear = No virtual bots to clear.
virtual-bots-status-report = Virtual Bots: { $total } total, { $online } online, { $offline } offline, { $in_game } in game.
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

# Documents
documents = Documents
documents-menu-title = Documents System
documents-all = All documents
documents-uncategorized = Uncategorized documents
documents-no-documents = No documents found.
documents-no-content = No content available for this document.

# Document actions
documents-view = View document content
documents-update-contents = Edit document content
documents-settings = Document settings
documents-update-title = Change title
documents-manage-visibility = Manage visibility
documents-modify-categories = Modify category list
documents-add-translation = Add translation
documents-remove-translation = Remove translation
documents-delete-document = Delete document
documents-title-prompt = Enter the document title for the { $language } translation:
documents-title-changed = Title updated for { $language }.
documents-visibility-changed = Visibility updated for { $language }.
documents-visibility-no-permission = You do not have permission to change visibility for { $language }.
documents-categories-updated = Categories updated.
documents-content-prompt = Enter the content for the { $language } translation:
documents-translation-added = Translation added for { $language }.
documents-no-languages-available = No languages available for translation.
documents-remove-translation-confirm = Remove the { $language } translation? This cannot be undone.
documents-remove-translation-source = The source translation cannot be removed.
documents-remove-title-confirm = Also remove the { $language } title? Choose no to keep it for a future translation.
documents-translation-removed = { $language } translation removed.
documents-delete-confirm = Delete this document? It has { $count } translations. This cannot be undone.
documents-deleted = Document deleted.
documents-no-permission = You do not have any relevant assigned languages for this document.
documents-visibility-count = Manage visibility ({ $public }/{ $total } languages public)
documents-locked = This document is currently being edited by { $username }. You cannot edit it right now.
documents-remove-translation-locked = The { $language } translation is currently being edited by { $username } and cannot be removed.
documents-delete-locked = This document cannot be deleted because the { $language } translation is currently being edited by { $username }.
documents-content-saved = Document content saved for { $language }.
documents-content-unchanged = No changes to save.
documents-editor-prompt = Edit: { $title } ({ $language })
documents-source-label = { $language } (source)
documents-content-label = { $language } Contents

# Document & category creation
documents-new-document = New document
documents-new-category = New category
documents-scope-prompt = Choose the scope for this document.
documents-scope-shared = Shared (all servers)
documents-scope-independent = Independent (this server only)
documents-select-categories = Select categories for the new document.
documents-new-document-slug-prompt = Enter the sluggified title in English. This is the internal identifier for the document, for example my_game_rules:
documents-document-created = Document created.
documents-slug-exists = A document with this identifier already exists.
documents-slug-invalid = Invalid slug. Use only lowercase letters, numbers, and underscores.
documents-new-category-slug-prompt = Enter the sluggified name in English. This is the internal identifier for the category, for example game_rules:
documents-category-created = Category created.
documents-slug-exists-category = A category with this slug already exists.

# Category management
documents-rename-category = Rename category
documents-category-settings = Category settings
documents-delete-category = Delete category
documents-category-name-prompt = Enter the display name for this category for the { $language } translation:
documents-category-renamed = Category renamed.
documents-sort-method = Sort method
documents-sort-alphabetical = Alphabetical
documents-sort-date-created = Date created
documents-sort-date-modified = Date modified
documents-sort-changed = Sort method updated.
documents-delete-category-confirm = Delete this category? Documents will not be deleted, but will lose this category association.
documents-category-deleted = Category deleted.

# Document infrastructure (sync, export, promote, contribution)
documents-sync = Sync shared documents
documents-sync-success = Shared documents synced successfully.
documents-sync-failed = Sync failed: { $reason }
documents-sync-pending-warning = Warning: { $count } uncommitted changes to shared documents exist. Export them before syncing to avoid losing local edits.
documents-sync-local-changes = { $count } documents have local changes. Select which to discard before syncing.
documents-sync-discard-label = { $title } (discard); ({ $description })
documents-sync-keep-label = { $title } (keep); ({ $description })
documents-sync-confirm = Sync now
documents-sync-discard-all = Discard all
documents-sync-keep-all = Keep all
documents-sync-tag-absent = item is absent from local: keep = don't add from upstream, discard = add from upstream
documents-sync-tag-present = item is only present on local: keep = don't delete from local, discard = delete from local
documents-sync-tag-content = content changes
documents-sync-tag-metadata = metadata changes
documents-sync-tag-content-and-metadata = content and metadata changes
documents-commit-message-prompt = Describe your changes (optional):
documents-commit-success = Changes committed.
documents-commit-failed = Commit failed: { $reason }
documents-export-pending = Export pending changes ({ $count })
documents-export-success = Exported { $count } changes to { $path }.
documents-export-no-changes = No pending changes to export.
documents-pending-commits-button = Pending commits ({ $count })
documents-pending-commits-info = { $count } commits ahead of upstream. The server owner can push these changes to the repository.
documents-pr-button = Create pull request ({ $count } commits)
documents-pr-success = Pull request created: { $url }
documents-pr-failed = Pull request failed: { $reason }
documents-pr-no-commits = No commits to include in a pull request.
documents-promote-to-shared = Promote to shared
documents-promote-confirm = Are you sure you want to promote this document to shared scope? This makes it visible to all servers syncing from this repository.
documents-promoted-to-shared = Document promoted to shared scope.
documents-promote-failed = Failed to promote document. It may already be shared or a conflict exists.
documents-based-on-stale = Upstream source changed: { $source }

# Transcriber management
transcribers-by-language = View transcribers by language
transcribers-by-user = View transcribers by user
transcribers-language-users = { $language } ({ $count } users)
transcribers-language-users-one = { $language } ({ $count } user)
transcribers-user-languages = { $user } ({ $count } languages)
transcribers-user-languages-one = { $user } ({ $count } language)
transcribers-no-users = No transcribers assigned to this language.
transcribers-no-languages = No languages assigned to this user.
transcribers-no-transcribers = No transcribers have been assigned yet.
transcribers-add-user = Add user
transcribers-add-users = Add users
transcribers-add-languages = Add languages
transcribers-remove-confirm = Remove { $user } as a transcriber for { $language }?
transcribers-remove-lang-confirm = Remove { $language } from { $user }'s transcriber assignments?
transcribers-removed = { $user } has been removed as a transcriber for { $language }.
transcribers-added = { $user } has been added as a transcriber for { $language }.
transcribers-users-added = Added { $users } as transcribers for { $language }.
transcribers-languages-added = Added { $user } as a transcriber for { $languages }.
transcribers-not-fluent = { $user } does not have { $language } in their fluent languages and cannot be assigned as a transcriber for it.
transcribers-no-eligible-users = No eligible users found. Users must have this language in their fluent languages.
transcribers-no-users-to-add = No users available to add. All users with fluent languages are already transcribers.
transcribers-no-eligible-languages = No eligible languages found. This user has no unassigned fluent languages.
transcribers-remove-transcriber = Remove transcriber
transcribers-remove-all-confirm = Remove all transcriber assignments from { $user }?
transcribers-removed-all = Removed all transcriber assignments from { $user }.

localization-in-progress-try-again = Localization in progress. Please try again in a minute.

# Errors
internal-error = Something went wrong. Please try again.
