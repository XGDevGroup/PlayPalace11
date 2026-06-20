# Mile by Mile - České zprávy hry

# Název hry
game-name-milebymile = Mile by Mile

# Herní možnosti
milebymile-set-distance = Vzdálenost závodu: { $miles } mil
milebymile-enter-distance = Zadejte vzdálenost závodu (300-3000)
milebymile-set-winning-score = Vítězné skóre: { $score } bodů
milebymile-enter-winning-score = Zadejte vítězné skóre (1000-10000)
milebymile-toggle-perfect-crossing = Vyžadovat přesný cíl: { $enabled }
milebymile-toggle-stacking = Povolit skládání útoků: { $enabled }
milebymile-toggle-reshuffle = Zamíchat odhazovací balíček: { $enabled }
milebymile-toggle-karma = Pravidlo karmy: { $enabled }
milebymile-set-rig = Úprava balíčku: { $rig }
milebymile-select-rig = Vyberte možnost úpravy balíčku

# Oznámení změn možností
milebymile-option-changed-distance = Vzdálenost závodu nastavena na { $miles } mil.
milebymile-option-changed-winning = Vítězné skóre nastaveno na { $score } bodů.
milebymile-option-changed-crossing = Vyžadovat přesný cíl { $enabled }.
milebymile-option-changed-stacking = Povolit skládání útoků { $enabled }.
milebymile-option-changed-reshuffle = Zamíchat odhazovací balíček { $enabled }.
milebymile-option-changed-karma = Pravidlo karmy { $enabled }.
milebymile-option-changed-rig = Úprava balíčku nastavena na { $rig }.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Stav
milebymile-status = { $name }: { $points } bodů, { $miles } mil, Problémy: { $problems }, Bezpečnosti: { $safeties }

# Akce s kartami
milebymile-no-matching-safety = Nemáte odpovídající bezpečnostní kartu!
milebymile-cant-play = Nemůžete hrát { $card }, protože { $reason }.
milebymile-no-card-selected = Nebyla vybrána žádná karta k odhození.
milebymile-no-valid-targets = Žádné platné cíle pro toto nebezpečí!
milebymile-you-drew = Lízl jste: { $card }
milebymile-discards = { $player } odhazuje kartu.
milebymile-select-target = Vyberte cíl

# Hrání vzdálenosti
milebymile-plays-distance-individual = { $player } hraje { $distance } mil a je nyní na { $total } milích.
milebymile-plays-distance-team = { $player } hraje { $distance } mil; jeho tým je nyní na { $total } milích.

# Dokončení cesty
milebymile-journey-complete-perfect-individual = { $player } dokončil cestu s dokonalým přechodem!
milebymile-journey-complete-perfect-team = Tým { $team } dokončil cestu s dokonalým přechodem!
milebymile-journey-complete-individual = { $player } dokončil cestu!
milebymile-journey-complete-team = Tým { $team } dokončil cestu!

# Hrání nebezpečí
milebymile-plays-hazard-individual = { $player } hraje { $card } na { $target }.
milebymile-plays-hazard-team = { $player } hraje { $card } na tým { $team }.

# Hrání náprav/bezpečností
milebymile-plays-card = { $player } hraje { $card }.
milebymile-plays-dirty-trick = { $player } hraje { $card } jako Špinavý trik!

# Balíček
milebymile-deck-reshuffled = Odhazovací balíček zamíchán zpět do balíčku.

# Závod
milebymile-new-race = Začíná nový závod!
milebymile-race-complete = Závod dokončen! Počítání skóre...
milebymile-earned-points = { $name } získal { $score } bodů v tomto závodě: { $breakdown }.
milebymile-total-scores = Celková skóre:
milebymile-team-score = { $name }: { $score } bodů

# Rozložení skóre
milebymile-from-distance = { $miles } z ujeté vzdálenosti
milebymile-from-trip = { $points } za dokončení cesty
milebymile-from-perfect = { $points } za dokonalý přechod
milebymile-from-safe = { $points } za bezpečnou cestu
milebymile-from-shutout = { $points } za vynulování
milebymile-from-safeties = { $points } ze { $count } { $safeties ->
    [one] bezpečnosti
    [few] bezpečností
    [many] bezpečnosti
   *[other] bezpečností
}
milebymile-from-all-safeties = { $points } ze všech 4 bezpečností
milebymile-from-dirty-tricks = { $points } z { $count } { $tricks ->
    [one] špinavého triku
    [few] špinavých triků
    [many] špinavého triku
   *[other] špinavých triků
}

# Konec hry
milebymile-wins-individual = { $player } vyhrává hru!
milebymile-wins-team = Tým { $team } vyhrává hru! ({ $members })
milebymile-final-score = Konečné skóre: { $score } bodů

# Zprávy o karmě - střet (oba ztrácejí karmu)
milebymile-karma-clash-you-target = Vy i váš cíl jste opovrženi! Útok je neutralizován.
milebymile-karma-clash-you-attacker = Vy i { $attacker } jste opovrženi! Útok je neutralizován.
milebymile-karma-clash-others = { $attacker } i { $target } jsou opovrženi! Útok je neutralizován.
milebymile-karma-clash-your-team = Váš tým i váš cíl jsou opovrženi! Útok je neutralizován.
milebymile-karma-clash-target-team = Vy i tým { $team } jste opovrženi! Útok je neutralizován.
milebymile-karma-clash-other-teams = Tým { $attacker } i tým { $target } jsou opovrženi! Útok je neutralizován.

# Zprávy o karmě - útočník opovržen
milebymile-karma-shunned-you = Byli jste opovrženi za svou agresi! Vaše karma je ztracena.
milebymile-karma-shunned-other = { $player } byl opovržen za svou agresi!
milebymile-karma-shunned-your-team = Váš tým byl opovržen za svou agresi! Karma vašeho týmu je ztracena.
milebymile-karma-shunned-other-team = Tým { $team } byl opovržen za svou agresi!

# Falešná ctnost
milebymile-false-virtue-you = Hrajete Falešnou ctnost a znovu získáváte svou karmu!
milebymile-false-virtue-other = { $player } hraje Falešnou ctnost a znovu získává svou karmu!
milebymile-false-virtue-your-team = Váš tým hraje Falešnou ctnost a znovu získává svou karmu!
milebymile-false-virtue-other-team = Tým { $team } hraje Falešnou ctnost a znovu získává svou karmu!

# Problémy/Bezpečnosti (pro zobrazení stavu)
milebymile-none = žádné

# Důvody nehratelné karty
milebymile-reason-not-on-team = nejste v týmu
milebymile-reason-stopped = jste zastaveni
milebymile-reason-has-problem = máte problém, který brání v jízdě
milebymile-reason-speed-limit = je aktivní rychlostní limit
milebymile-reason-exceeds-distance = by to přesáhlo { $miles } mil
milebymile-reason-no-targets = nejsou žádné platné cíle
milebymile-reason-no-speed-limit = nejste pod rychlostním limitem
milebymile-reason-has-right-of-way = Přednost v jízdě vám umožňuje jet bez zelených světel
milebymile-reason-already-moving = už jedete
milebymile-reason-must-fix-first = musíte nejprve opravit { $problem }
milebymile-reason-has-gas = vaše auto má benzín
milebymile-reason-tires-fine = vaše pneumatiky jsou v pořádku
milebymile-reason-no-accident = vaše auto nemělo nehodu
milebymile-reason-has-safety = už máte tuto bezpečnost
milebymile-reason-has-karma = stále máte svou karmu
milebymile-reason-generic = momentálně to nelze hrát

# Názvy karet
milebymile-card-out-of-gas = Vybitý benzín
milebymile-card-flat-tire = Píchnutá pneumatika
milebymile-card-accident = Nehoda
milebymile-card-speed-limit = Rychlostní limit
milebymile-card-stop = Stop
milebymile-card-gasoline = Benzín
milebymile-card-spare-tire = Náhradní pneumatika
milebymile-card-repairs = Opravy
milebymile-card-end-of-limit = Konec limitu
milebymile-card-green-light = Zelená světla
milebymile-card-extra-tank = Extra nádrž
milebymile-card-puncture-proof = Odolné proti propíchnutí
milebymile-card-driving-ace = Řidičské eso
milebymile-card-right-of-way = Přednost v jízdě
milebymile-card-false-virtue = Falešná ctnost
milebymile-card-miles = { $miles } mil

# Důvody zakázaných akcí
milebymile-no-dirty-trick-window = Není aktivní žádné okno špinavého triku.
milebymile-not-your-dirty-trick = Není to okno špinavého triku vašeho týmu.
milebymile-between-races = Počkejte na start dalšího závodu.

# Chyby validace
milebymile-error-karma-needs-three-teams = Pravidlo karmy vyžaduje alespoň 3 různá auta/týmy.

milebymile-you-play-safety-with-effect = Hrajete { $card }. { $effect }
milebymile-player-plays-safety-with-effect = { $player } hraje { $card }. { $effect }
milebymile-you-play-dirty-trick-with-effect = Hrajete { $card } jako Špinavý trik. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } hraje { $card } jako Špinavý trik. { $effect }
milebymile-safety-effect-extra-tank = Nyní jste chráněni před Nedostatkem paliva.
milebymile-safety-effect-puncture-proof = Nyní jste chráněni před Defektem pneumatiky.
milebymile-safety-effect-driving-ace = Nyní jste chráněni před Nehodou.
milebymile-safety-effect-right-of-way = Nyní jste chráněni před Stopkou a Omezením rychlosti.
