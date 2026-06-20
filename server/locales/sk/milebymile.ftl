# Mile by Mile game messages
# Note: Common messages like round-start, turn-start, team-mode are in games.ftl

# Game name
game-name-milebymile = Míľa za Míľou

# Game options
milebymile-set-distance = Vzdialenosť pretekov: { $miles } míľ
milebymile-enter-distance = Zadajte vzdialenosť pretekov (300-3000)
milebymile-set-winning-score = Víťazné skóre: { $score } bodov
milebymile-enter-winning-score = Zadajte víťazné skóre (1000-10000)
milebymile-toggle-perfect-crossing = Vyžadovať presný cieľ: { $enabled }
milebymile-toggle-stacking = Povoliť hromadenie útokov: { $enabled }
milebymile-toggle-reshuffle = Zamiešať odkladací balíček: { $enabled }
milebymile-toggle-karma = Pravidlo karmy: { $enabled }
milebymile-set-rig = Manipulácia balíčka: { $rig }
milebymile-select-rig = Vyberte možnosť manipulácie balíčka

# Option change announcements
milebymile-option-changed-distance = Vzdialenosť pretekov nastavená na { $miles } míľ.
milebymile-option-changed-winning = Víťazné skóre nastavené na { $score } bodov.
milebymile-option-changed-crossing = Vyžadovať presný cieľ { $enabled }.
milebymile-option-changed-stacking = Povoliť hromadenie útokov { $enabled }.
milebymile-option-changed-reshuffle = Zamiešať odkladací balíček { $enabled }.
milebymile-option-changed-karma = Pravidlo karmy { $enabled }.
milebymile-option-changed-rig = Manipulácia balíčka nastavená na { $rig }.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $points } bodov, { $miles } míľ, Problémy: { $problems }, Ochrany: { $safeties }

# Card actions
milebymile-no-matching-safety = Nemáte zodpovedajúcu ochrannú kartu!
milebymile-cant-play = Nemôžete zahrať { $card }, pretože { $reason }.
milebymile-no-card-selected = Nie je vybraná karta na odhodenie.
milebymile-no-valid-targets = Žiadne platné ciele pre toto nebezpečenstvo!
milebymile-you-drew = Ťahli ste: { $card }
milebymile-discards = { $player } odhadzuje kartu.
milebymile-select-target = Vyberte cieľ

# Distance plays
milebymile-plays-distance-individual = { $player } hrá { $distance } míľ a je teraz na { $total } míľach.
milebymile-plays-distance-team = { $player } hrá { $distance } míľ; ich tím je teraz na { $total } míľach.

# Journey complete
milebymile-journey-complete-perfect-individual = { $player } dokončil cestu s dokonalým prejazdom!
milebymile-journey-complete-perfect-team = Tím { $team } dokončil cestu s dokonalým prejazdom!
milebymile-journey-complete-individual = { $player } dokončil cestu!
milebymile-journey-complete-team = Tím { $team } dokončil cestu!

# Hazard plays
milebymile-plays-hazard-individual = { $player } hrá { $card } na { $target }.
milebymile-plays-hazard-team = { $player } hrá { $card } na Tím { $team }.

# Remedy/Safety plays
milebymile-plays-card = { $player } hrá { $card }.
milebymile-plays-dirty-trick = { $player } hrá { $card } ako Špinavý Trik!

# Deck
milebymile-deck-reshuffled = Odkladací balíček zamiešaný späť do balíčka.

# Race
milebymile-new-race = Začínajú nové preteky!
milebymile-race-complete = Preteky dokončené! Výpočet skóre...
milebymile-earned-points = { $name } získal { $score } bodov v týchto pretekoch: { $breakdown }.
milebymile-total-scores = Celkové skóre:
milebymile-team-score = { $name }: { $score } bodov

# Scoring breakdown
milebymile-from-distance = { $miles } z prejdenej vzdialenosti
milebymile-from-trip = { $points } za dokončenie cesty
milebymile-from-perfect = { $points } za dokonalý prejazd
milebymile-from-safe = { $points } za bezpečnú cestu
milebymile-from-shutout = { $points } za úplné zatvorenie
milebymile-from-safeties = { $points } z { $count } { $safeties ->
    [one] ochrany
    [few] ochrán
    [many] ochrán
    *[other] ochrán
}
milebymile-from-all-safeties = { $points } zo všetkých 4 ochrán
milebymile-from-dirty-tricks = { $points } z { $count } { $tricks ->
    [one] špinavý trik
    [few] špinavé triky
    [many] špinavých trikov
    *[other] špinavých trikov
}

# Game end
milebymile-wins-individual = { $player } vyhráva hru!
milebymile-wins-team = Tím { $team } vyhráva hru! ({ $members })
milebymile-final-score = Konečné skóre: { $score } bodov

# Karma messages - clash (both lose karma)
milebymile-karma-clash-you-target = Vy a váš cieľ ste obaja zavrhnutí! Útok je neutralizovaný.
milebymile-karma-clash-you-attacker = Vy a { $attacker } ste obaja zavrhnutí! Útok je neutralizovaný.
milebymile-karma-clash-others = { $attacker } a { $target } sú obaja zavrhnutí! Útok je neutralizovaný.
milebymile-karma-clash-your-team = Váš tím a váš cieľ sú obaja zavrhnutí! Útok je neutralizovaný.
milebymile-karma-clash-target-team = Vy a Tím { $team } ste obaja zavrhnutí! Útok je neutralizovaný.
milebymile-karma-clash-other-teams = Tím { $attacker } a Tím { $target } sú obaja zavrhnutí! Útok je neutralizovaný.

# Karma messages - attacker shunned
milebymile-karma-shunned-you = Boli ste zavrhnutý za svoju agresiu! Vaša karma je stratená.
milebymile-karma-shunned-other = { $player } bol zavrhnutý za svoju agresiu!
milebymile-karma-shunned-your-team = Váš tím bol zavrhnutý za svoju agresiu! Karma vášho tímu je stratená.
milebymile-karma-shunned-other-team = Tím { $team } bol zavrhnutý za svoju agresiu!

# False Virtue
milebymile-false-virtue-you = Hráte Falošnú Cnosť a získavate späť svoju karmu!
milebymile-false-virtue-other = { $player } hrá Falošnú Cnosť a získava späť svoju karmu!
milebymile-false-virtue-your-team = Váš tím hrá Falošnú Cnosť a získava späť svoju karmu!
milebymile-false-virtue-other-team = Tím { $team } hrá Falošnú Cnosť a získava späť svoju karmu!

# Problems/Safeties (for status display)
milebymile-none = žiadne

# Unplayable card reasons
milebymile-reason-not-on-team = nie ste v tíme
milebymile-reason-stopped = ste zastavený
milebymile-reason-has-problem = máte problém, ktorý bráni jazde
milebymile-reason-speed-limit = rýchlostný limit je aktívny
milebymile-reason-exceeds-distance = prekročilo by { $miles } míľ
milebymile-reason-no-targets = nie sú žiadne platné ciele
milebymile-reason-no-speed-limit = nie ste pod rýchlostným limitom
milebymile-reason-has-right-of-way = Prednosť v jazde umožňuje jazdu bez zelených svetiel
milebymile-reason-already-moving = už sa pohybujete
milebymile-reason-must-fix-first = musíte najprv opraviť { $problem }
milebymile-reason-has-gas = vaše auto má benzín
milebymile-reason-tires-fine = vaše pneumatiky sú v poriadku
milebymile-reason-no-accident = vaše auto nemalo nehodu
milebymile-reason-has-safety = už máte túto ochranu
milebymile-reason-has-karma = stále máte svoju karmu
milebymile-reason-generic = nemôže byť zahraná teraz

# Card names
milebymile-card-out-of-gas = Dochádza Benzín
milebymile-card-flat-tire = Defekt
milebymile-card-accident = Nehoda
milebymile-card-speed-limit = Rýchlostný Limit
milebymile-card-stop = Stop
milebymile-card-gasoline = Benzín
milebymile-card-spare-tire = Náhradná Pneumatika
milebymile-card-repairs = Opravy
milebymile-card-end-of-limit = Koniec Limitu
milebymile-card-green-light = Zelené Svetlo
milebymile-card-extra-tank = Extra Nádrž
milebymile-card-puncture-proof = Odolné Voči Defektu
milebymile-card-driving-ace = Majster Jazdy
milebymile-card-right-of-way = Prednosť v Jazde
milebymile-card-false-virtue = Falošná Cnosť
milebymile-card-miles = { $miles } míľ

# Disabled action reasons
milebymile-no-dirty-trick-window = Žiadne aktívne okno špinavého triku.
milebymile-not-your-dirty-trick = To nie je okno špinavého triku vášho tímu.
milebymile-between-races = Počkajte na začiatok ďalších pretekov.

# Validation errors
milebymile-error-karma-needs-three-teams = Pravidlo karmy vyžaduje aspoň 3 odlišné autá/tímy.

milebymile-you-play-safety-with-effect = Hrali ste { $card }. { $effect }
milebymile-player-plays-safety-with-effect = { $player } hrá { $card }. { $effect }
milebymile-you-play-dirty-trick-with-effect = Hrali ste { $card } ako Špinavý trik. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } hrá { $card } ako Špinavý trik. { $effect }
milebymile-safety-effect-extra-tank = Teraz chránení pred Bez paliva.
milebymile-safety-effect-puncture-proof = Teraz chránení pred Defektom.
milebymile-safety-effect-driving-ace = Teraz chránení pred Nehodou.
milebymile-safety-effect-right-of-way = Teraz chránení pred Stopkou a Obmedzením rýchlosti.
