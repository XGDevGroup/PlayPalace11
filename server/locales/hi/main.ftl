# Main UI messages for PlayPalace

# Game categories
category-card-games = ताश के खेल
category-dice-games = पासे के खेल
category-rb-play-center = आरबी प्ले सेंटर
category-poker = पोकर
category-uncategorized = अवर्गीकृत

# Menu titles
main-menu-title = मुख्य मेनू
play-menu-title = खेलें
categories-menu-title = खेल श्रेणियाँ
tables-menu-title = उपलब्ध टेबल

# Menu items
play = खेलें
view-active-tables = सक्रिय टेबल देखें
options = विकल्प
logout = लॉगआउट
back = वापस
go-back = वापस जाएं
context-menu = संदर्भ मेनू।
no-actions-available = कोई क्रिया उपलब्ध नहीं है।
create-table = नई टेबल बनाएं
join-as-player = खिलाड़ी के रूप में शामिल हों
join-as-spectator = दर्शक के रूप में शामिल हों
leave-table = टेबल छोड़ें
start-game = खेल शुरू करें
add-bot = बॉट जोड़ें
remove-bot = बॉट हटाएं
actions-menu = क्रिया मेनू
save-table = टेबल सहेजें
whose-turn = किसकी बारी है
whos-at-table = टेबल पर कौन है
check-scores = स्कोर देखें
check-scores-detailed = विस्तृत स्कोर
check-game-options = खेल विकल्प देखें
no-game-options = कोई खेल विकल्प उपलब्ध नहीं है।

# Turn messages
game-player-skipped = { $player } को छोड़ दिया गया है।

# Table messages
table-created = { $host } ने एक नया { $game } टेबल बनाया।
table-joined = { $player } टेबल में शामिल हुए।
table-left = { $player } ने टेबल छोड़ दी।
new-host = { $player } अब होस्ट हैं।
waiting-for-players = खिलाड़ियों का इंतजार है। न्यूनतम {$min}, अधिकतम { $max }।
game-starting = खेल शुरू हो रहा है!
table-listing = { $host } की टेबल ({ $count } उपयोगकर्ता)
table-listing-one = { $host } की टेबल ({ $count } उपयोगकर्ता)
table-listing-with = { $host } की टेबल ({ $count } उपयोगकर्ता) { $members } के साथ
table-listing-game = { $game }: { $host } की टेबल ({ $count } उपयोगकर्ता)
table-listing-game-one = { $game }: { $host } की टेबल ({ $count } उपयोगकर्ता)
table-listing-game-with = { $game }: { $host } की टेबल ({ $count } उपयोगकर्ता) { $members } के साथ
table-not-exists = टेबल अब मौजूद नहीं है।
table-full = टेबल भरी हुई है।
player-replaced-by-bot = { $player } ने छोड़ दिया और एक बॉट द्वारा प्रतिस्थापित किया गया।
player-took-over = { $player } ने बॉट से पदभार संभाला।
spectator-joined = { $host } की टेबल में दर्शक के रूप में शामिल हुए।

# Spectator mode
spectate = देखें
now-playing = { $player } अब खेल रहे हैं।
now-spectating = { $player } अब देख रहे हैं।
spectator-left = { $player } ने देखना बंद कर दिया।

# General
welcome = प्लेपैलेस में आपका स्वागत है!
goodbye = अलविदा!

# User presence announcements
user-online = { $player } ऑनलाइन आए।
user-offline = { $player } ऑफलाइन हो गए।
user-is-admin = { $player } प्लेपैलेस के प्रशासक हैं।
user-is-server-owner = { $player } प्लेपैलेस के सर्वर स्वामी हैं।
online-users-none = कोई उपयोगकर्ता ऑनलाइन नहीं है।
online-users-one = 1 उपयोगकर्ता: { $users }
online-users-many = { $count } उपयोगकर्ता: { $users }
online-user-not-in-game = खेल में नहीं हैं
online-user-waiting-approval = अनुमोदन की प्रतीक्षा में

# Options
language = भाषा
language-option = भाषा: { $language }
language-changed = भाषा { $language } पर सेट की गई।

# Boolean option states
option-on = चालू
option-off = बंद

# Sound options
turn-sound-option = बारी की ध्वनि: { $status }

# Dice options
clear-kept-option = पासा फेंकते समय रखे गए पासे साफ़ करें: { $status }
dice-keeping-style-option = पासा रखने की शैली: { $style }
dice-keeping-style-changed = पासा रखने की शैली { $style } पर सेट की गई।
dice-keeping-style-indexes = पासा सूचकांक
dice-keeping-style-values = पासा मान

# Bot names
cancel = रद्द करें
no-bot-names-available = कोई बॉट नाम उपलब्ध नहीं है।
select-bot-name = बॉट के लिए एक नाम चुनें
enter-bot-name = बॉट का नाम दर्ज करें
no-options-available = कोई विकल्प उपलब्ध नहीं है।
no-scores-available = कोई स्कोर उपलब्ध नहीं है।

# Duration estimation
estimate-duration = अनुमानित अवधि
estimate-computing = अनुमानित खेल अवधि की गणना की जा रही है...
estimate-result = बॉट औसत: { $bot_time } (± { $std_dev })। { $outlier_info }अनुमानित मानव समय: { $human_time }।
estimate-error = अवधि का अनुमान नहीं लगाया जा सका।
estimate-already-running = अवधि अनुमान पहले से ही प्रगति में है।

# Save/Restore
saved-tables = सहेजी गई टेबल
no-saved-tables = आपके पास कोई सहेजी गई टेबल नहीं है।
no-active-tables = कोई सक्रिय टेबल नहीं है।
restore-table = पुनर्स्थापित करें
delete-saved-table = हटाएं
saved-table-deleted = सहेजी गई टेबल हटाई गई।
missing-players = पुनर्स्थापित नहीं किया जा सकता: ये खिलाड़ी उपलब्ध नहीं हैं: { $players }
table-restored = टेबल पुनर्स्थापित! सभी खिलाड़ियों को स्थानांतरित कर दिया गया है।
table-saved-destroying = टेबल सहेजी गई! मुख्य मेनू पर लौट रहे हैं।
game-type-not-found = खेल प्रकार अब मौजूद नहीं है।

# Action disabled reasons
action-not-your-turn = यह आपकी बारी नहीं है।
action-not-playing = खेल शुरू नहीं हुआ है।
action-spectator = दर्शक यह नहीं कर सकते।
action-not-host = केवल होस्ट ही यह कर सकता है।
action-game-in-progress = खेल चल रहे समय ऐसा नहीं किया जा सकता।
action-need-more-players = शुरू करने के लिए अधिक खिलाड़ियों की आवश्यकता है।
action-table-full = टेबल भरी हुई है।
action-no-bots = हटाने के लिए कोई बॉट नहीं है।
action-bots-cannot = बॉट यह नहीं कर सकते।
action-no-scores = अभी तक कोई स्कोर उपलब्ध नहीं है।

# Dice actions
dice-not-rolled = आपने अभी तक पासा नहीं फेंका है।
dice-locked = यह पासा बंद है।
dice-no-dice = कोई पासा उपलब्ध नहीं है।

# Game actions
game-turn-start = { $player } की बारी।
game-no-turn = अभी किसी की बारी नहीं है।
table-no-players = कोई खिलाड़ी नहीं।
table-players-one = { $count } खिलाड़ी: { $players }।
table-players-many = { $count } खिलाड़ी: { $players }।
table-spectators = दर्शक: { $spectators }।
game-leave = छोड़ें
game-over = खेल समाप्त
game-final-scores = अंतिम स्कोर
game-points = { $count } { $count ->
    [one] अंक
   *[other] अंक
}
play = खेलें

# Leaderboards
leaderboards = लीडरबोर्ड
leaderboards-menu-title = लीडरबोर्ड
leaderboards-select-game = लीडरबोर्ड देखने के लिए एक खेल चुनें
leaderboard-no-data = इस खेल के लिए अभी तक कोई लीडरबोर्ड डेटा नहीं है।

# Leaderboard types
leaderboard-type-wins = जीत के नेता
leaderboard-type-rating = कौशल रेटिंग
leaderboard-type-total-score = कुल स्कोर
leaderboard-type-high-score = उच्च स्कोर
leaderboard-type-games-played = खेले गए खेल
leaderboard-type-avg-points-per-turn = प्रति बारी औसत अंक
leaderboard-type-best-single-turn = सर्वश्रेष्ठ एकल बारी
leaderboard-type-score-per-round = प्रति राउंड स्कोर

# Leaderboard headers
leaderboard-wins-header = { $game } - जीत के नेता
leaderboard-total-score-header = { $game } - कुल स्कोर
leaderboard-high-score-header = { $game } - उच्च स्कोर
leaderboard-games-played-header = { $game } - खेले गए खेल
leaderboard-rating-header = { $game } - कौशल रेटिंग
leaderboard-avg-points-header = { $game } - प्रति बारी औसत अंक
leaderboard-best-turn-header = { $game } - सर्वश्रेष्ठ एकल बारी
leaderboard-score-per-round-header = { $game } - प्रति राउंड स्कोर

# Leaderboard entries
leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] जीत
   *[other] जीत
} { $losses } { $losses ->
    [one] हार
   *[other] हार
}, { $percentage }% जीत दर
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } औसत
leaderboard-games-entry = { $rank }. { $player }: { $value } खेल

# Player stats
leaderboard-player-stats = आपके आंकड़े: { $wins } जीत, { $losses } हार ({ $percentage }% जीत दर)
leaderboard-no-player-stats = आपने अभी तक यह खेल नहीं खेला है।

# Skill rating leaderboard
leaderboard-no-ratings = इस खेल के लिए अभी तक कोई रेटिंग डेटा नहीं है।
leaderboard-rating-entry = { $rank }. { $player }: { $rating } रेटिंग ({ $mu } ± { $sigma })
leaderboard-player-rating = आपकी रेटिंग: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = इस खेल के लिए आपकी अभी तक कोई रेटिंग नहीं है।

# My Stats menu
my-stats = मेरे आंकड़े
my-stats-select-game = अपने आंकड़े देखने के लिए एक खेल चुनें
my-stats-no-data = आपने अभी तक यह खेल नहीं खेला है।
my-stats-no-games = आपने अभी तक कोई खेल नहीं खेला है।
my-stats-header = { $game } - आपके आंकड़े
my-stats-wins = जीत: { $value }
my-stats-losses = हार: { $value }
my-stats-winrate = जीत दर: { $value }%
my-stats-games-played = खेले गए खेल: { $value }
my-stats-total-score = कुल स्कोर: { $value }
my-stats-high-score = उच्च स्कोर: { $value }
my-stats-rating = कौशल रेटिंग: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = अभी तक कोई कौशल रेटिंग नहीं
my-stats-avg-per-turn = प्रति बारी औसत अंक: { $value }
my-stats-best-turn = सर्वश्रेष्ठ एकल बारी: { $value }

# Prediction system
predict-outcomes = परिणामों की भविष्यवाणी करें
predict-header = अनुमानित परिणाम (कौशल रेटिंग के अनुसार)
predict-entry = { $rank }. { $player } (रेटिंग: { $rating })
predict-entry-2p = { $rank }. { $player } (रेटिंग: { $rating }, { $probability }% जीत की संभावना)
predict-unavailable = रेटिंग भविष्यवाणियाँ उपलब्ध नहीं हैं।
predict-need-players = भविष्यवाणियों के लिए कम से कम 2 मानव खिलाड़ियों की आवश्यकता है।
action-need-more-humans = अधिक मानव खिलाड़ियों की आवश्यकता है।
confirm-leave-game = क्या आप वाकई टेबल छोड़ना चाहते हैं?
confirm-yes = हाँ
confirm-no = नहीं

# Administration
administration = प्रशासन
admin-menu-title = प्रशासन

# Account approval
account-approval = खाता अनुमोदन
account-approval-menu-title = खाता अनुमोदन
no-pending-accounts = कोई लंबित खाता नहीं है।
approve-account = अनुमोदित करें
decline-account = अस्वीकार करें
account-approved = { $player } के खाते को अनुमोदित कर दिया गया है।
account-declined = { $player } के खाते को अस्वीकार कर दिया गया है और हटा दिया गया है।

# Waiting for approval (shown to unapproved users)
waiting-for-approval = आपका खाता प्रशासक द्वारा अनुमोदन की प्रतीक्षा में है।
account-approved-welcome = आपके खाते को अनुमोदित कर दिया गया है! प्लेपैलेस में आपका स्वागत है!
account-declined-goodbye = आपके खाते के अनुरोध को अस्वीकार कर दिया गया है।
    कारण:
account-banned = आपका खाता प्रतिबंधित है और इसे एक्सेस नहीं किया जा सकता।

# Login errors
incorrect-username = आपके द्वारा दर्ज किया गया उपयोगकर्ता नाम मौजूद नहीं है।
incorrect-password = आपके द्वारा दर्ज किया गया पासवर्ड गलत है।
already-logged-in = यह खाता पहले से लॉग इन है।

# क्रेडेंशियल सत्यापन
credential-username-length = उपयोगकर्ता नाम { $min } से { $max } अक्षरों के बीच होना चाहिए।
credential-password-length = पासवर्ड { $min } से { $max } अक्षरों के बीच होना चाहिए।

# दर सीमा
rate-limit-login-ip = इस पते से बहुत अधिक लॉगिन प्रयास किए गए हैं। कृपया प्रतीक्षा करें और पुनः प्रयास करें।
rate-limit-login-user = इस उपयोगकर्ता नाम के लिए बहुत अधिक विफल लॉगिन प्रयास किए गए हैं। कृपया प्रतीक्षा करें और पुनः प्रयास करें।
rate-limit-registration = इस पते से बहुत अधिक पंजीकरण प्रयास किए गए हैं। कृपया प्रतीक्षा करें और पुनः प्रयास करें।
rate-limit-refresh = इस पते से बहुत अधिक रिफ्रेश प्रयास किए गए हैं। कृपया प्रतीक्षा करें और पुनः प्रयास करें।

# सत्र और प्रमाणीकरण त्रुटियाँ
account-not-found = खाता नहीं मिला।
session-expired = सत्र समाप्त हो गया। कृपया पुनः लॉग इन करें।
session-token-mismatch = सत्र टोकन उपयोगकर्ता नाम से मेल नहीं खाता।
refresh-token-expired = रिफ्रेश टोकन समाप्त हो गया। कृपया पुनः लॉग इन करें।
refresh-token-mismatch = रिफ्रेश टोकन उपयोगकर्ता नाम से मेल नहीं खाता।

# पंजीकरण
registration-success = पंजीकरण सफल! आपका खाता अनुमोदन की प्रतीक्षा में है।
registration-username-taken = यह उपयोगकर्ता नाम पहले से लिया जा चुका है। कृपया कोई अलग उपयोगकर्ता नाम चुनें।

# प्राथमिकता वापसी
pref-invalid-value = अमान्य चयन, डिफ़ॉल्ट का उपयोग किया जा रहा है।

# Decline reason
decline-reason-prompt = अस्वीकार करने का कारण दर्ज करें (या रद्द करने के लिए Escape दबाएं):
account-action-empty-reason = कोई कारण नहीं दिया गया।

# Admin notifications for account requests
account-request = खाता अनुरोध
account-action = खाता कार्रवाई की गई

# Admin promotion/demotion
promote-admin = प्रशासक पदोन्नत करें
demote-admin = प्रशासक पदावनत करें
promote-admin-menu-title = प्रशासक पदोन्नत करें
demote-admin-menu-title = प्रशासक पदावनत करें
no-users-to-promote = पदोन्नत करने के लिए कोई उपयोगकर्ता उपलब्ध नहीं है।
no-admins-to-demote = पदावनत करने के लिए कोई प्रशासक उपलब्ध नहीं है।
confirm-promote = क्या आप वाकई { $player } को प्रशासक के रूप में पदोन्नत करना चाहते हैं?
confirm-demote = क्या आप वाकई { $player } को प्रशासक से पदावनत करना चाहते हैं?
broadcast-to-all = सभी उपयोगकर्ताओं को घोषित करें
broadcast-to-admins = केवल प्रशासकों को घोषित करें
broadcast-to-nobody = मौन (कोई घोषणा नहीं)
promote-announcement = { $player } को प्रशासक के रूप में पदोन्नत किया गया है!
promote-announcement-you = आपको प्रशासक के रूप में पदोन्नत किया गया है!
demote-announcement = { $player } को प्रशासक से पदावनत कर दिया गया है।
demote-announcement-you = आपको प्रशासक से पदावनत कर दिया गया है।
not-admin-anymore = आप अब प्रशासक नहीं हैं और यह कार्रवाई नहीं कर सकते।
not-server-owner = केवल सर्वर स्वामी ही यह कार्रवाई कर सकता है।

# Server ownership transfer
transfer-ownership = स्वामित्व स्थानांतरित करें
transfer-ownership-menu-title = स्वामित्व स्थानांतरित करें
no-admins-for-transfer = स्वामित्व स्थानांतरित करने के लिए कोई प्रशासक उपलब्ध नहीं है।
confirm-transfer-ownership = क्या आप वाकई { $player } को सर्वर स्वामित्व स्थानांतरित करना चाहते हैं? आपको प्रशासक के रूप में पदावनत कर दिया जाएगा।
transfer-ownership-announcement = { $player } अब प्ले पैलेस सर्वर स्वामी हैं!
transfer-ownership-announcement-you = आप अब प्ले पैलेस सर्वर स्वामी हैं!

# User banning
ban-user = उपयोगकर्ता प्रतिबंधित करें
unban-user = उपयोगकर्ता प्रतिबंध हटाएं
no-users-to-ban = प्रतिबंधित करने के लिए कोई उपयोगकर्ता उपलब्ध नहीं है।
no-users-to-unban = प्रतिबंध हटाने के लिए कोई प्रतिबंधित उपयोगकर्ता नहीं है।
confirm-ban = क्या आप वाकई { $player } को प्रतिबंधित करना चाहते हैं?
confirm-unban = क्या आप वाकई { $player } का प्रतिबंध हटाना चाहते हैं?
ban-reason-prompt = प्रतिबंध के लिए कारण दर्ज करें (वैकल्पिक):
unban-reason-prompt = प्रतिबंध हटाने के लिए कारण दर्ज करें (वैकल्पिक):
user-banned = { $player } को प्रतिबंधित कर दिया गया है।
user-unbanned = { $player } का प्रतिबंध हटा दिया गया है।
you-have-been-banned = आपको इस सर्वर से प्रतिबंधित कर दिया गया है।
    कारण:
you-have-been-unbanned = आपका इस सर्वर से प्रतिबंध हटा दिया गया है।
    कारण:
ban-no-reason = कोई कारण नहीं दिया गया।

# Virtual bots (server owner only)
virtual-bots = आभासी बॉट
virtual-bots-fill = सर्वर भरें
virtual-bots-clear = सभी बॉट साफ़ करें
virtual-bots-status = स्थिति
virtual-bots-clear-confirm = क्या आप वाकई सभी आभासी बॉट साफ़ करना चाहते हैं? इससे वे सभी टेबल भी नष्ट हो जाएंगे जिनमें वे हैं।
virtual-bots-not-available = आभासी बॉट उपलब्ध नहीं हैं।
virtual-bots-filled = { $added } आभासी बॉट जोड़े गए। { $online } अब ऑनलाइन हैं।
virtual-bots-already-filled = कॉन्फ़िगरेशन से सभी आभासी बॉट पहले से ही सक्रिय हैं।
virtual-bots-cleared = { $bots } आभासी बॉट साफ़ किए गए और { $tables } { $tables ->
    [one] टेबल
   *[other] टेबल
} नष्ट की गईं।
virtual-bot-table-closed = टेबल प्रशासक द्वारा बंद की गई।
virtual-bots-none-to-clear = साफ़ करने के लिए कोई आभासी बॉट नहीं है।
virtual-bots-status-report = आभासी बॉट: { $total } कुल, { $online } ऑनलाइन, { $offline } ऑफलाइन, { $in_game } खेल में।
virtual-bots-guided-overview = निर्देशित टेबल
virtual-bots-groups-overview = बॉट समूह
virtual-bots-profiles-overview = प्रोफाइल
virtual-bots-guided-header = निर्देशित टेबल: { $count } नियम। आवंटन: { $allocation }, फ़ॉलबैक: { $fallback }, डिफ़ॉल्ट प्रोफाइल: { $default_profile }।
virtual-bots-guided-empty = कोई निर्देशित टेबल नियम कॉन्फ़िगर नहीं किए गए हैं।
virtual-bots-guided-status-active = सक्रिय
virtual-bots-guided-status-inactive = निष्क्रिय
virtual-bots-guided-table-linked = टेबल { $table_id } से जुड़ा (होस्ट { $host }, खिलाड़ी { $players }, मानव { $humans })
virtual-bots-guided-table-stale = टेबल { $table_id } सर्वर पर गायब है
virtual-bots-guided-table-unassigned = वर्तमान में कोई टेबल ट्रैक नहीं की गई है
virtual-bots-guided-next-change = अगला परिवर्तन { $ticks } टिक में
virtual-bots-guided-no-schedule = कोई शेड्यूलिंग विंडो नहीं
virtual-bots-guided-warning = ⚠ कम भरा हुआ
virtual-bots-guided-line = { $table }: खेल { $game }, प्राथमिकता { $priority }, बॉट { $assigned } (न्यूनतम { $min_bots }, अधिकतम { $max_bots }), प्रतीक्षारत { $waiting }, अनुपलब्ध { $unavailable }, स्थिति { $status }, प्रोफाइल { $profile }, समूह { $groups }। { $table_state }। { $next_change } { $warning_text }
virtual-bots-groups-header = बॉट समूह: { $count } टैग, { $bots } कॉन्फ़िगर किए गए बॉट।
virtual-bots-groups-empty = कोई बॉट समूह परिभाषित नहीं हैं।
virtual-bots-groups-line = { $group }: प्रोफाइल { $profile }, बॉट { $total } (ऑनलाइन { $online }, प्रतीक्षारत { $waiting }, खेल में { $in_game }, ऑफलाइन { $offline }), नियम { $rules }।
virtual-bots-groups-no-rules = कोई नहीं
virtual-bots-no-profile = डिफ़ॉल्ट
virtual-bots-profile-inherit-default = डिफ़ॉल्ट प्रोफाइल विरासत में मिलता है
virtual-bots-profiles-header = प्रोफाइल: { $count } परिभाषित (डिफ़ॉल्ट: { $default_profile })।
virtual-bots-profiles-empty = कोई प्रोफाइल परिभाषित नहीं हैं।
virtual-bots-profiles-line = { $profile } ({ $bot_count } बॉट) ओवरराइड: { $overrides }।
virtual-bots-profiles-no-overrides = आधार कॉन्फ़िगरेशन विरासत में मिलता है

localization-in-progress-try-again = स्थानीयकरण जारी है। कृपया एक मिनट बाद फिर प्रयास करें।
