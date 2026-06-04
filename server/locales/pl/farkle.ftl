# Farkle game messages

# Game info
game-name-farkle = Farkle

# Actions - Roll and Bank
farkle-roll = Rzuć { $count } { $count ->
    [one] kostką
   *[other] kostkami
}
farkle-bank = Bankuj { $points } punktów

# Scoring combination actions (matching v10 exactly)
farkle-take-single-one = As za { $points } punktów
farkle-take-single-five = Pojedyncza 5 za { $points } punktów
farkle-take-three-kind = Trzy { $number } za { $points } punktów
farkle-take-four-kind = Cztery { $number } za { $points } punktów
farkle-take-five-kind = Pięć { $number } za { $points } punktów
farkle-take-six-kind = Sześć { $number } za { $points } punktów
farkle-take-small-straight = Mały strit za { $points } punktów
farkle-take-large-straight = Duży strit za { $points } punktów
farkle-take-three-pairs = Trzy pary za { $points } punktów
farkle-take-double-triplets = Podwójny triplet za { $points } punktów
farkle-take-full-house = Full za { $points } punktów

# Game events (matching v10 exactly)
farkle-rolls = { $player } rzuca { $count } { $count ->
    [one] kostką
   *[other] kostkami
}...
farkle-you-roll = Rzucasz { $count } { $count ->
    [one] kostką
   *[other] kostkami
}...
farkle-roll-result = { $dice }
farkle-farkle = FARKLE! { $player } traci { $points } punktów
farkle-you-farkle = FARKLE! Tracisz { $points } punktów
farkle-takes-combo = { $player } bierze { $combo } za { $points } punktów
farkle-you-take-combo = Bierzesz { $combo } za { $points } punktów
farkle-hot-dice = Gorące kości!
farkle-banks = { $player } bankuje { $points } punktów, łącznie ma { $total }
farkle-you-bank = Bankujesz { $points } punktów, łącznie masz { $total }
farkle-winner = { $player } wygrywa z wynikiem { $score } punktów!
farkle-you-win = Wygrywasz z wynikiem { $score } punktów!
farkle-winners-tie = Mamy remis! Wygrywają: { $players }

# Check turn score action
farkle-turn-score = { $player } ma { $points } punktów w tej turze.
farkle-no-turn = Obecnie nikt nie ma tury.

# Farkle-specific options
farkle-set-target-score = Maksymalna liczba punktów: { $score }
farkle-enter-target-score = Podaj maksymalną liczbę punktów (między 500 a 5000):
farkle-option-changed-target = Maksymalna liczba punktów została ustawiona na { $score }.

# Disabled action reasons
farkle-must-take-combo = Najpierw musisz wybrać punktującą kombinację.
farkle-cannot-bank = Nie możesz teraz zabankować.

# Additional Farkle options
farkle-set-initial-bank-score = Początkowy próg bankowania: { $score }
farkle-enter-initial-bank-score = Wpisz początkowy próg bankowania (między 0 a 1000):
farkle-option-changed-initial-bank-score = Początkowy próg bankowania został ustawiony na { $score }.
farkle-toggle-hot-dice-multiplier = Mnożnik gorących kości: { $enabled }
farkle-option-changed-hot-dice-multiplier = Mnożnik gorących kości został ustawiony na { $enabled }.

# Action feedback
farkle-minimum-initial-bank-score = Minimalny początkowy próg bankowania wynosi { $score }.
