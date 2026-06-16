# Humanity Cards - English localization

# Options
hc-set-winning-score = Rezultat za pobedu: { $score }
hc-enter-winning-score = Upišite rezultat za pobedu:
hc-option-changed-winning-score = Rezultat za pobedu podešen na { $score }.

hc-set-hand-size = Veličina ruke: { $count }
hc-enter-hand-size = Upišite veličinu ruke:
hc-option-changed-hand-size = Veličina ruke podešena na { $count }.

hc-set-card-packs = Paketi karata ({ $count } od { $total } izabrano)
hc-option-changed-card-packs = Izbor paketa karata promenjen.

hc-set-czar-selection = Izbor karata: { $mode }
hc-select-czar-selection = Izaberite režim izbora karata
hc-option-changed-czar-selection = Izbor karata podešen na { $mode }.

hc-set-num-judges = Broj sudija: { $count }
hc-enter-num-judges = Upišite broj sudija:
hc-option-changed-num-judges = Broj sudija podešen na { $count }.

hc-czar-rotating = Rotirajući
hc-czar-random = Nasumičan
hc-czar-winner = Poslednji pobednik

# Game flow
hc-game-starting = Mešanje špilova...
hc-dealing-cards = Deljenje { $count } karata svakom igraču.
hc-round-start = Runda { $round }.

# Judge announcement
hc-judge-is = { $player } { $count ->
    [one] je sudija
   *[other] i { $others } su sudije
}.
hc-you-are-judge = Vi ste sudija u ovoj rundi.
hc-you-are-not-judge = Niste sudija u ovoj rundi.

# Black card
hc-black-card = Rečenica je: { $text }
hc-black-card-pick = Izaberite { $count }.
hc-view-black-card = Pogledaj kartu pitanja

# Submission phase
hc-select-cards = Izaberite { $count } { $count ->
    [one] kartu
    [few] karte
   *[other] karata
} iz vaše ruke.
hc-card-selected = { $text }, izabrano
hc-card-not-selected = { $text }
hc-submit-cards = Pošalji ({ $selected } od { $required } izabrano)
hc-submitted = Stavili ste vaše karte.
hc-player-submitted = { $player } stavlja svoje karte.
hc-submission-progress = { $submitted } od { $total } igrača je stavilo svoje karte.
hc-waiting-for-submissions = Čekanje na karte...
hc-already-submitted = Već ste stavili vaše karte.
hc-wrong-card-count = Morate da izaberete tačno { $count } { $count ->
    [one] kartu
    [few] karte
   *[other] karata
}.

# Judging phase
hc-judging-start = Sve karte su stavljene! vreme je da se ocene.
hc-select-winner-prompt = Izaberite pobednički predlog
hc-submission-option = { $text }

# Results
hc-winner-announcement = { $player } dobija rundu! Rezultat: { $score }.
hc-winner-card = Pobednički odgovor: { $text }
hc-round-scores = Rezultat nakon runde { $round }:
hc-score-line = { $player }: { $score } { $score ->
    [one] poen
   *[other] poena
}
hc-all-submissions = Drugi predlozi:
hc-submission-reveal = { $player }: { $text }

# View
hc-preview-submission = Pogledaj svoj preglod
hc-view-submission = Pogledaj svoj predlog
hc-preview-submission-text = Pregled: { $text }
hc-your-submission = Vaš predlog: { $text }
hc-select-cards-first = Prvo izaberite bar jednu kartu.

# Win
hc-game-winner = { $player } pobeđuje sa { $score } poena!
hc-you-win = Pobeđujete sa { $score } poena!

# Deck management
hc-deck-reshuffled = Odbačene bele karte su promešane nazad u špil.
hc-black-deck-reshuffled = Odbačene crne karte su promešane nazad u špil.
hc-not-enough-cards = Nema dovoljno karata. Pokušajte da omogućite više paketa.

# Hand management
hc-view-hand = Pogledaj ruku

# Scores
hc-view-scores = Pogledaj rezultat
hc-no-scores = Još uvek nema rezultata.

# Whose turn / whose judge
hc-whose-judge = Ko je sudija
hc-waiting-for = Čeka se da { $names } igraju.
hc-all-submitted-waiting-judge = Svi igrači su poslali svoje predloge. Čeka se da { $judge } sudi.
