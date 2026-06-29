# Chameleon game messages

# Game info
game-name-chameleon = Chameleon

# Options
chameleon-desc-target-score = The score needed to win the game

# Turn prompts
chameleon-your-turn-clue = Give a clue
chameleon-your-turn-vote = Vote for the Chameleon
chameleon-your-turn-guess = Guess the secret word
chameleon-enter-clue = Enter a one-word clue:
chameleon-enter-guess = Enter the secret word:
chameleon-select-suspect = Select who you think is the Chameleon.

# Private information
chameleon-topic-private = Topic: { $topic }
chameleon-you-are-chameleon = You are the Chameleon.
chameleon-you-see-topic = You know the topic, but not the secret word.
chameleon-you-are-not-chameleon = You are not the Chameleon.
chameleon-secret-word = Secret word: { $word }

# Round flow
chameleon-round-start = Chameleon round { $round }.
chameleon-clue-given = { $player } gives the clue: { $clue }.
chameleon-vote-recorded = { $player } has voted.
chameleon-vote-reveal = { $player } voted for { $target }.
chameleon-caught = { $player } was caught as the Chameleon.
chameleon-guess-correct = { $player } guessed the secret word correctly.
chameleon-guess-wrong = { $player } guessed the wrong word.
chameleon-not-caught = The Chameleon escaped suspicion.
chameleon-round-points = { $player } scores { $points } { $points ->
    [one] point
   *[other] points
}.

# Scores and results
chameleon-scoreboard = Current Chameleon scores:
chameleon-scores-header = Chameleon scores:
chameleon-score-line = { $player }: { $score } { $score ->
    [one] point
   *[other] points
}
chameleon-game-winner = { $player } wins Chameleon with { $score } { $score ->
    [one] point
   *[other] points
}!
chameleon-final-word = The secret word was { $word } in topic { $topic }.

# Validation
chameleon-invalid-clue = Please enter a one-word clue.
chameleon-invalid-vote = Please choose a valid player.
chameleon-invalid-guess = Please enter a guess.
