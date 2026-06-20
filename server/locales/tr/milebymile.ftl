# Mile by Mile oyun mesajları
# Not: Raund başlangıcı, tur başlangıcı, takım modu gibi ortak mesajlar games.ftl'de

# Oyun adı
game-name-milebymile = Mile by Mile

# Oyun seçenekleri
milebymile-set-distance = Yarış mesafesi: { $miles } mil
milebymile-enter-distance = Yarış mesafesini girin (300-3000)
milebymile-set-winning-score = Kazanma skoru: { $score } puan
milebymile-enter-winning-score = Kazanma skorunu girin (1000-10000)
milebymile-toggle-perfect-crossing = Tam bitiş gerekli: { $enabled }
milebymile-toggle-stacking = Saldırı yığınlamasına izin ver: { $enabled }
milebymile-toggle-reshuffle = Atık destesini yeniden karıştır: { $enabled }
milebymile-toggle-karma = Karma kuralı: { $enabled }
milebymile-set-rig = Deste hilesi: { $rig }
milebymile-select-rig = Deste hilesi seçeneğini seç

# Seçenek değişikliği duyuruları
milebymile-option-changed-distance = Yarış mesafesi { $miles } mil olarak ayarlandı.
milebymile-option-changed-winning = Kazanma skoru { $score } puan olarak ayarlandı.
milebymile-option-changed-crossing = Tam bitiş gerekli { $enabled }.
milebymile-option-changed-stacking = Saldırı yığınlamasına izin ver { $enabled }.
milebymile-option-changed-reshuffle = Atık destesini yeniden karıştır { $enabled }.
milebymile-option-changed-karma = Karma kuralı { $enabled }.
milebymile-option-changed-rig = Deste hilesi { $rig } olarak ayarlandı.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Durum
milebymile-status = { $name }: { $points } puan, { $miles } mil, Sorunlar: { $problems }, Güvenlikler: { $safeties }

# Kart eylemleri
milebymile-no-matching-safety = Eşleşen güvenlik kartın yok!
milebymile-cant-play = { $card } oynayamazsın çünkü { $reason }.
milebymile-no-card-selected = Atılacak kart seçilmedi.
milebymile-no-valid-targets = Bu tehlike için uygun hedef yok!
milebymile-you-drew = Çektin: { $card }
milebymile-discards = { $player } bir kart atıyor.
milebymile-select-target = Bir hedef seç

# Mesafe oynamaları
milebymile-plays-distance-individual = { $player } { $distance } mil oynuyor ve şimdi { $total } milde.
milebymile-plays-distance-team = { $player } { $distance } mil oynuyor; takımı şimdi { $total } milde.

# Yolculuk tamamlandı
milebymile-journey-complete-perfect-individual = { $player } mükemmel bir geçişle yolculuğu tamamladı!
milebymile-journey-complete-perfect-team = Takım { $team } mükemmel bir geçişle yolculuğu tamamladı!
milebymile-journey-complete-individual = { $player } yolculuğu tamamladı!
milebymile-journey-complete-team = Takım { $team } yolculuğu tamamladı!

# Tehlike oynamaları
milebymile-plays-hazard-individual = { $player } { $target }'a { $card } oynuyor.
milebymile-plays-hazard-team = { $player } Takım { $team }'e { $card } oynuyor.

# İlaç/Güvenlik oynamaları
milebymile-plays-card = { $player } { $card } oynuyor.
milebymile-plays-dirty-trick = { $player } { $card }'ı Kirli Numara olarak oynuyor!

# Deste
milebymile-deck-reshuffled = Atık destesi tekrar desteye karıştırıldı.

# Yarış
milebymile-new-race = Yeni yarış başlıyor!
milebymile-race-complete = Yarış tamamlandı! Skorlar hesaplanıyor...
milebymile-earned-points = { $name } bu yarışta { $score } puan kazandı: { $breakdown }.
milebymile-total-scores = Toplam skorlar:
milebymile-team-score = { $name }: { $score } puan

# Skorlama dökümü
milebymile-from-distance = Kat edilen mesafeden { $miles }
milebymile-from-trip = Yolculuğu tamamlamaktan { $points }
milebymile-from-perfect = Mükemmel geçişten { $points }
milebymile-from-safe = Güvenli yolculuktan { $points }
milebymile-from-shutout = Kapatmadan { $points }
milebymile-from-safeties = { $count } { $safeties ->
    [one] güvenlikten
    *[other] güvenlikten
} { $points }
milebymile-from-all-safeties = 4 güvenliğin hepsinden { $points }
milebymile-from-dirty-tricks = { $count } { $tricks ->
    [one] kirli numaradan
    *[other] kirli numaradan
} { $points }

# Oyun sonu
milebymile-wins-individual = { $player } oyunu kazandı!
milebymile-wins-team = Takım { $team } oyunu kazandı! ({ $members })
milebymile-final-score = Final skoru: { $score } puan

# Karma mesajları - çatışma (ikisi de karma kaybeder)
milebymile-karma-clash-you-target = Sen ve hedefin ikiniz de dışlandınız! Saldırı etkisiz hale geldi.
milebymile-karma-clash-you-attacker = Sen ve { $attacker } ikiniz de dışlandınız! Saldırı etkisiz hale geldi.
milebymile-karma-clash-others = { $attacker } ve { $target } ikisi de dışlandı! Saldırı etkisiz hale geldi.
milebymile-karma-clash-your-team = Takımın ve hedefin ikisi de dışlandı! Saldırı etkisiz hale geldi.
milebymile-karma-clash-target-team = Sen ve Takım { $team } ikiniz de dışlandınız! Saldırı etkisiz hale geldi.
milebymile-karma-clash-other-teams = Takım { $attacker } ve Takım { $target } ikisi de dışlandı! Saldırı etkisiz hale geldi.

# Karma mesajları - saldırgan dışlandı
milebymile-karma-shunned-you = Saldırganlığın için dışlandın! Karman kayboldu.
milebymile-karma-shunned-other = { $player } saldırganlığı için dışlandı!
milebymile-karma-shunned-your-team = Takımın saldırganlığı için dışlandı! Takımının karması kayboldu.
milebymile-karma-shunned-other-team = Takım { $team } saldırganlığı için dışlandı!

# Sahte Erdem
milebymile-false-virtue-you = Sahte Erdem oynuyorsun ve karmanı geri kazanıyorsun!
milebymile-false-virtue-other = { $player } Sahte Erdem oynuyor ve karmasını geri kazanıyor!
milebymile-false-virtue-your-team = Takımın Sahte Erdem oynuyor ve karmasını geri kazanıyor!
milebymile-false-virtue-other-team = Takım { $team } Sahte Erdem oynuyor ve karmasını geri kazanıyor!

# Sorunlar/Güvenlikler (durum gösterimi için)
milebymile-none = yok

# Oynanamaz kart nedenleri
milebymile-reason-not-on-team = bir takımda değilsin
milebymile-reason-stopped = durduruldun
milebymile-reason-has-problem = sürüşü engelleyen bir sorunun var
milebymile-reason-speed-limit = hız sınırı aktif
milebymile-reason-exceeds-distance = { $miles } mili aşar
milebymile-reason-no-targets = uygun hedef yok
milebymile-reason-no-speed-limit = hız sınırı altında değilsin
milebymile-reason-has-right-of-way = Geçiş Hakkı yeşil ışık olmadan gitmene izin veriyor
milebymile-reason-already-moving = zaten hareket halındesin
milebymile-reason-must-fix-first = önce { $problem }'ı tamir etmelisin
milebymile-reason-has-gas = arabanın benzini var
milebymile-reason-tires-fine = lastiklerin iyi
milebymile-reason-no-accident = araban kaza yapmadı
milebymile-reason-has-safety = zaten o güvenliğe sahipsin
milebymile-reason-has-karma = hâlâ karman var
milebymile-reason-generic = şu anda oynanamaz

# Kart adları
milebymile-card-out-of-gas = Benzin Bitti
milebymile-card-flat-tire = Patlak Lastik
milebymile-card-accident = Kaza
milebymile-card-speed-limit = Hız Sınırı
milebymile-card-stop = Dur
milebymile-card-gasoline = Benzin
milebymile-card-spare-tire = Yedek Lastik
milebymile-card-repairs = Tamir
milebymile-card-end-of-limit = Sınır Sonu
milebymile-card-green-light = Yeşil Işık
milebymile-card-extra-tank = Ekstra Depo
milebymile-card-puncture-proof = Delinmez
milebymile-card-driving-ace = Sürüş Asından
milebymile-card-right-of-way = Geçiş Hakkı
milebymile-card-false-virtue = Sahte Erdem
milebymile-card-miles = { $miles } mil

# Devre dışı eylem nedenleri
milebymile-no-dirty-trick-window = Kirli numara penceresi aktif değil.
milebymile-not-your-dirty-trick = Takımının kirli numara penceresi değil.
milebymile-between-races = Sonraki yarışın başlamasını bekle.

# Doğrulama hataları
milebymile-error-karma-needs-three-teams = Karma kuralı en az 3 farklı araba/takım gerektirir.

milebymile-you-play-safety-with-effect = { $card } oynuyorsun. { $effect }
milebymile-player-plays-safety-with-effect = { $player } { $card } oynuyor. { $effect }
milebymile-you-play-dirty-trick-with-effect = { $card } kartını Kirli Numara olarak oynuyorsun. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } { $card } kartını Kirli Numara olarak oynuyor. { $effect }
milebymile-safety-effect-extra-tank = Artık Benzinsiz Kalma'ya karşı korumalı.
milebymile-safety-effect-puncture-proof = Artık Lastik Patlaması'na karşı korumalı.
milebymile-safety-effect-driving-ace = Artık Kaza'ya karşı korumalı.
milebymile-safety-effect-right-of-way = Artık Dur ve Hız Sınırı'na karşı korumalı.
