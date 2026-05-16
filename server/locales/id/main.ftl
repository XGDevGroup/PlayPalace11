# Main UI messages for PlayPalace

# Game categories
category-card-games = Permainan Kartu
category-dice-games = Permainan Dadu
category-rb-play-center = RB Play Center
category-poker = Poker
category-uncategorized = Tidak Dikategorikan

# Menu titles
main-menu-title = Menu Utama
play-menu-title = Main
categories-menu-title = Kategori Permainan
tables-menu-title = Meja Tersedia

# Menu items
play = Main
view-active-tables = Lihat meja aktif
options = Pilihan
logout = Keluar
back = Kembali
go-back = Kembali
context-menu = Menu konteks.
no-actions-available = Tidak ada aksi tersedia.
create-table = Buat meja baru
join-as-player = Gabung sebagai pemain
join-as-spectator = Gabung sebagai penonton
leave-table = Tinggalkan meja
start-game = Mulai permainan
add-bot = Tambah bot
remove-bot = Hapus bot
actions-menu = Menu aksi
save-table = Simpan meja
whose-turn = Giliran siapa
whos-at-table = Siapa yang di meja
check-scores = Periksa skor
check-scores-detailed = Skor detail
check-game-options = Periksa opsi permainan
no-game-options = Tidak ada opsi permainan.

# Turn messages
game-player-skipped = { $player } dilewati.

# Table messages
table-created = { $host } membuat meja { $game } baru.
table-joined = { $player } bergabung ke meja.
table-left = { $player } meninggalkan meja.
new-host = { $player } sekarang menjadi host.
waiting-for-players = Menunggu pemain. {$min} min, { $max } maks.
game-starting = Permainan dimulai!
table-listing = Meja { $host } ({ $count } pengguna)
table-listing-one = Meja { $host } ({ $count } pengguna)
table-listing-with = Meja { $host } ({ $count } pengguna) dengan { $members }
table-listing-game = { $game }: Meja { $host } ({ $count } pengguna)
table-listing-game-one = { $game }: Meja { $host } ({ $count } pengguna)
table-listing-game-with = { $game }: Meja { $host } ({ $count } pengguna) dengan { $members }
table-not-exists = Meja tidak ada lagi.
table-full = Meja penuh.
player-replaced-by-bot = { $player } pergi dan digantikan oleh bot.
player-took-over = { $player } mengambil alih dari bot.
spectator-joined = Bergabung ke meja { $host } sebagai penonton.

# Spectator mode
spectate = Tonton
now-playing = { $player } sekarang bermain.
now-spectating = { $player } sekarang menonton.
spectator-left = { $player } berhenti menonton.

# General
welcome = Selamat datang di PlayPalace!
goodbye = Sampai jumpa!

# User presence announcements
user-online = { $player } online.
user-offline = { $player } offline.
user-is-admin = { $player } adalah administrator PlayPalace.
user-is-server-owner = { $player } adalah pemilik server PlayPalace.
online-users-none = Tidak ada pengguna online.
online-users-one = 1 pengguna: { $users }
online-users-many = { $count } pengguna: { $users }
online-user-not-in-game = Tidak dalam permainan
online-user-waiting-approval = Menunggu persetujuan

# Options
language = Bahasa
language-option = Bahasa: { $language }
language-changed = Bahasa diatur ke { $language }.

# Boolean option states
option-on = Aktif
option-off = Nonaktif

# Sound options
turn-sound-option = Suara giliran: { $status }

# Dice options
clear-kept-option = Bersihkan dadu yang disimpan saat melempar: { $status }
dice-keeping-style-option = Gaya menyimpan dadu: { $style }
dice-keeping-style-changed = Gaya menyimpan dadu diatur ke { $style }.
dice-keeping-style-indexes = Indeks dadu
dice-keeping-style-values = Nilai dadu

# Bot names
cancel = Batal
no-bot-names-available = Tidak ada nama bot tersedia.
select-bot-name = Pilih nama untuk bot
enter-bot-name = Masukkan nama bot
no-options-available = Tidak ada pilihan tersedia.
no-scores-available = Tidak ada skor tersedia.

# Duration estimation
estimate-duration = Perkirakan durasi
estimate-computing = Menghitung perkiraan durasi permainan...
estimate-result = Rata-rata bot: { $bot_time } (± { $std_dev }). { $outlier_info }Perkiraan waktu manusia: { $human_time }.
estimate-error = Tidak dapat memperkirakan durasi.
estimate-already-running = Perkiraan durasi sudah berjalan.

# Save/Restore
saved-tables = Meja Tersimpan
no-saved-tables = Anda tidak memiliki meja tersimpan.
no-active-tables = Tidak ada meja aktif.
restore-table = Pulihkan
delete-saved-table = Hapus
saved-table-deleted = Meja tersimpan dihapus.
missing-players = Tidak dapat memulihkan: pemain ini tidak tersedia: { $players }
table-restored = Meja dipulihkan! Semua pemain telah dipindahkan.
table-saved-destroying = Meja disimpan! Kembali ke menu utama.
game-type-not-found = Tipe permainan tidak ada lagi.

# Action disabled reasons
action-not-your-turn = Bukan giliran Anda.
action-not-playing = Permainan belum dimulai.
action-spectator = Penonton tidak dapat melakukan ini.
action-not-host = Hanya host yang dapat melakukan ini.
action-game-in-progress = Tidak dapat melakukan ini saat permainan berlangsung.
action-need-more-players = Butuh lebih banyak pemain untuk memulai.
action-table-full = Meja sudah penuh.
action-no-bots = Tidak ada bot untuk dihapus.
action-bots-cannot = Bot tidak dapat melakukan ini.
action-no-scores = Belum ada skor tersedia.

# Dice actions
dice-not-rolled = Anda belum melempar.
dice-locked = Dadu ini terkunci.
dice-no-dice = Tidak ada dadu tersedia.

# Game actions
game-turn-start = Giliran { $player }.
game-no-turn = Tidak ada giliran sekarang.
table-no-players = Tidak ada pemain.
table-players-one = { $count } pemain: { $players }.
table-players-many = { $count } pemain: { $players }.
table-spectators = Penonton: { $spectators }.
game-leave = Tinggalkan
game-over = Permainan Berakhir
game-final-scores = Skor Akhir
game-points = { $count } { $count ->
    [one] poin
   *[other] poin
}
play = Main

# Leaderboards
leaderboards = Papan Peringkat
leaderboards-menu-title = Papan Peringkat
leaderboards-select-game = Pilih permainan untuk melihat papan peringkatnya
leaderboard-no-data = Belum ada data papan peringkat untuk permainan ini.

# Leaderboard types
leaderboard-type-wins = Pemimpin Kemenangan
leaderboard-type-rating = Rating Keterampilan
leaderboard-type-total-score = Total Skor
leaderboard-type-high-score = Skor Tertinggi
leaderboard-type-games-played = Permainan Dimainkan
leaderboard-type-avg-points-per-turn = Rata-rata Poin Per Giliran
leaderboard-type-best-single-turn = Giliran Tunggal Terbaik
leaderboard-type-score-per-round = Skor Per Ronde

# Leaderboard headers
leaderboard-wins-header = { $game } - Pemimpin Kemenangan
leaderboard-total-score-header = { $game } - Total Skor
leaderboard-high-score-header = { $game } - Skor Tertinggi
leaderboard-games-played-header = { $game } - Permainan Dimainkan
leaderboard-rating-header = { $game } - Rating Keterampilan
leaderboard-avg-points-header = { $game } - Rata-rata Poin Per Giliran
leaderboard-best-turn-header = { $game } - Giliran Tunggal Terbaik
leaderboard-score-per-round-header = { $game } - Skor Per Ronde

# Leaderboard entries
leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] kemenangan
   *[other] kemenangan
} { $losses } { $losses ->
    [one] kekalahan
   *[other] kekalahan
}, { $percentage }% winrate
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } rata-rata
leaderboard-games-entry = { $rank }. { $player }: { $value } permainan

# Player stats
leaderboard-player-stats = Statistik Anda: { $wins } kemenangan, { $losses } kekalahan ({ $percentage }% win rate)
leaderboard-no-player-stats = Anda belum memainkan permainan ini.

# Skill rating leaderboard
leaderboard-no-ratings = Belum ada data rating untuk permainan ini.
leaderboard-rating-entry = { $rank }. { $player }: { $rating } rating ({ $mu } ± { $sigma })
leaderboard-player-rating = Rating Anda: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = Anda belum memiliki rating untuk permainan ini.

# My Stats menu
my-stats = Statistik Saya
my-stats-select-game = Pilih permainan untuk melihat statistik Anda
my-stats-no-data = Anda belum memainkan permainan ini.
my-stats-no-games = Anda belum memainkan permainan apa pun.
my-stats-header = { $game } - Statistik Anda
my-stats-wins = Kemenangan: { $value }
my-stats-losses = Kekalahan: { $value }
my-stats-winrate = Win rate: { $value }%
my-stats-games-played = Permainan dimainkan: { $value }
my-stats-total-score = Total skor: { $value }
my-stats-high-score = Skor tertinggi: { $value }
my-stats-rating = Rating keterampilan: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = Belum ada rating keterampilan
my-stats-avg-per-turn = Rata-rata poin per giliran: { $value }
my-stats-best-turn = Giliran tunggal terbaik: { $value }

# Prediction system
predict-outcomes = Prediksi hasil
predict-header = Hasil yang Diprediksi (berdasarkan rating keterampilan)
predict-entry = { $rank }. { $player } (rating: { $rating })
predict-entry-2p = { $rank }. { $player } (rating: { $rating }, { $probability }% peluang menang)
predict-unavailable = Prediksi rating tidak tersedia.
predict-need-players = Butuh minimal 2 pemain manusia untuk prediksi.
action-need-more-humans = Butuh lebih banyak pemain manusia.
confirm-leave-game = Apakah Anda yakin ingin meninggalkan meja?
confirm-yes = Ya
confirm-no = Tidak

# Administration
administration = Administrasi
admin-menu-title = Administrasi

# Account approval
account-approval = Persetujuan Akun
account-approval-menu-title = Persetujuan Akun
no-pending-accounts = Tidak ada akun yang menunggu.
approve-account = Setujui
decline-account = Tolak
account-approved = Akun { $player } telah disetujui.
account-declined = Akun { $player } telah ditolak dan dihapus.

# Waiting for approval (shown to unapproved users)
waiting-for-approval = Akun Anda menunggu persetujuan oleh administrator.
account-approved-welcome = Akun Anda telah disetujui! Selamat datang di PlayPalace!
account-declined-goodbye = Permintaan akun Anda telah ditolak.
    Alasan:
account-banned = Akun Anda dibanned dan tidak dapat diakses.

# Login errors
incorrect-username = Nama pengguna yang Anda masukkan tidak ada.
incorrect-password = Kata sandi yang Anda masukkan salah.
already-logged-in = Akun ini sudah login.

# Validasi kredensial
credential-username-length = Nama pengguna harus antara { $min } dan { $max } karakter.
credential-password-length = Kata sandi harus antara { $min } dan { $max } karakter.

# Pembatasan kecepatan
rate-limit-login-ip = Terlalu banyak percobaan masuk dari alamat ini. Harap tunggu dan coba lagi.
rate-limit-login-user = Terlalu banyak percobaan masuk yang gagal untuk nama pengguna ini. Harap tunggu dan coba lagi.
rate-limit-registration = Terlalu banyak percobaan pendaftaran dari alamat ini. Harap tunggu dan coba lagi.
rate-limit-refresh = Terlalu banyak percobaan refresh dari alamat ini. Harap tunggu dan coba lagi.

# Kesalahan sesi dan autentikasi
account-not-found = Akun tidak ditemukan.
session-expired = Sesi telah berakhir. Silakan masuk kembali.
session-token-mismatch = Token sesi tidak cocok dengan nama pengguna.
refresh-token-expired = Token refresh telah kedaluwarsa. Silakan masuk kembali.
refresh-token-mismatch = Token refresh tidak cocok dengan nama pengguna.

# Pendaftaran
registration-success = Pendaftaran berhasil! Akun Anda sedang menunggu persetujuan.
registration-username-taken = Nama pengguna sudah digunakan. Silakan pilih nama pengguna yang berbeda.

# Nilai preferensi default
pref-invalid-value = Pilihan tidak valid, menggunakan nilai default.

# Decline reason
decline-reason-prompt = Masukkan alasan penolakan (atau tekan Escape untuk batal):
account-action-empty-reason = Tidak ada alasan diberikan.

# Admin notifications for account requests
account-request = permintaan akun
account-action = aksi akun diambil

# Admin promotion/demotion
promote-admin = Promosikan Admin
demote-admin = Turunkan Admin
promote-admin-menu-title = Promosikan Admin
demote-admin-menu-title = Turunkan Admin
no-users-to-promote = Tidak ada pengguna yang tersedia untuk dipromosikan.
no-admins-to-demote = Tidak ada admin yang tersedia untuk diturunkan.
confirm-promote = Apakah Anda yakin ingin mempromosikan { $player } menjadi admin?
confirm-demote = Apakah Anda yakin ingin menurunkan { $player } dari admin?
broadcast-to-all = Umumkan ke semua pengguna
broadcast-to-admins = Umumkan hanya ke admin
broadcast-to-nobody = Diam (tanpa pengumuman)
promote-announcement = { $player } telah dipromosikan menjadi admin!
promote-announcement-you = Anda telah dipromosikan menjadi admin!
demote-announcement = { $player } telah diturunkan dari admin.
demote-announcement-you = Anda telah diturunkan dari admin.
not-admin-anymore = Anda tidak lagi admin dan tidak dapat melakukan aksi ini.
not-server-owner = Hanya pemilik server yang dapat melakukan aksi ini.

# Server ownership transfer
transfer-ownership = Transfer Kepemilikan
transfer-ownership-menu-title = Transfer Kepemilikan
no-admins-for-transfer = Tidak ada admin yang tersedia untuk transfer kepemilikan.
confirm-transfer-ownership = Apakah Anda yakin ingin mentransfer kepemilikan server ke { $player }? Anda akan diturunkan menjadi admin.
transfer-ownership-announcement = { $player } sekarang menjadi pemilik server Play Palace!
transfer-ownership-announcement-you = Anda sekarang menjadi pemilik server Play palace!

# User banning
ban-user = Ban Pengguna
unban-user = Unban Pengguna
no-users-to-ban = Tidak ada pengguna yang tersedia untuk di-ban.
no-users-to-unban = Tidak ada pengguna yang di-ban untuk di-unban.
confirm-ban = Apakah Anda yakin ingin mem-ban { $player }?
confirm-unban = Apakah Anda yakin ingin meng-unban { $player }?
ban-reason-prompt = Masukkan alasan ban (opsional):
unban-reason-prompt = Masukkan alasan unban (opsional):
user-banned = { $player } telah di-ban.
user-unbanned = { $player } telah di-unban.
you-have-been-banned = Anda telah di-ban dari server ini.
    Alasan:
you-have-been-unbanned = Anda telah di-unban dari server ini.
    Alasan:
ban-no-reason = Tidak ada alasan diberikan.

# Virtual bots (server owner only)
virtual-bots = Bot Virtual
virtual-bots-fill = Isi Server
virtual-bots-clear = Bersihkan Semua Bot
virtual-bots-status = Status
virtual-bots-clear-confirm = Apakah Anda yakin ingin membersihkan semua bot virtual? Ini juga akan menghancurkan meja tempat mereka berada.
virtual-bots-not-available = Bot virtual tidak tersedia.
virtual-bots-filled = Menambahkan { $added } bot virtual. { $online } sekarang online.
virtual-bots-already-filled = Semua bot virtual dari konfigurasi sudah aktif.
virtual-bots-cleared = Membersihkan { $bots } bot virtual dan menghancurkan { $tables } { $tables ->
    [one] meja
   *[other] meja
}.
virtual-bot-table-closed = Meja ditutup oleh administrator.
virtual-bots-none-to-clear = Tidak ada bot virtual untuk dibersihkan.
virtual-bots-status-report = Bot Virtual: { $total } total, { $online } online, { $offline } offline, { $in_game } dalam permainan.
virtual-bots-guided-overview = Meja Terpandu
virtual-bots-groups-overview = Grup Bot
virtual-bots-profiles-overview = Profil
virtual-bots-guided-header = Meja terpandu: { $count } aturan. Alokasi: { $allocation }, fallback: { $fallback }, profil default: { $default_profile }.
virtual-bots-guided-empty = Tidak ada aturan meja terpandu yang dikonfigurasi.
virtual-bots-guided-status-active = aktif
virtual-bots-guided-status-inactive = nonaktif
virtual-bots-guided-table-linked = terhubung ke meja { $table_id } (host { $host }, pemain { $players }, manusia { $humans })
virtual-bots-guided-table-stale = meja { $table_id } hilang di server
virtual-bots-guided-table-unassigned = tidak ada meja yang saat ini dilacak
virtual-bots-guided-next-change = perubahan berikutnya dalam { $ticks } tick
virtual-bots-guided-no-schedule = tidak ada jendela penjadwalan
virtual-bots-guided-warning = ⚠ kurang terisi
virtual-bots-guided-line = { $table }: permainan { $game }, prioritas { $priority }, bot { $assigned } (min { $min_bots }, maks { $max_bots }), menunggu { $waiting }, tidak tersedia { $unavailable }, status { $status }, profil { $profile }, grup { $groups }. { $table_state }. { $next_change } { $warning_text }
virtual-bots-groups-header = Grup bot: { $count } tag, { $bots } bot dikonfigurasi.
virtual-bots-groups-empty = Tidak ada grup bot yang didefinisikan.
virtual-bots-groups-line = { $group }: profil { $profile }, bot { $total } (online { $online }, menunggu { $waiting }, dalam permainan { $in_game }, offline { $offline }), aturan { $rules }.
virtual-bots-groups-no-rules = tidak ada
virtual-bots-no-profile = default
virtual-bots-profile-inherit-default = mewarisi profil default
virtual-bots-profiles-header = Profil: { $count } didefinisikan (default: { $default_profile }).
virtual-bots-profiles-empty = Tidak ada profil yang didefinisikan.
virtual-bots-profiles-line = { $profile } ({ $bot_count } bot) override: { $overrides }.
virtual-bots-profiles-no-overrides = mewarisi konfigurasi dasar

localization-in-progress-try-again = Lokalisasi sedang diproses. Silakan coba lagi dalam satu menit.
