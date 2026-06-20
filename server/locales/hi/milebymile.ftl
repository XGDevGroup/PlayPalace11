# Mile by Mile game messages
# Note: Common messages like round-start, turn-start, team-mode are in games.ftl

# Game name
game-name-milebymile = माइल बाय माइल

# Game options
milebymile-set-distance = दौड़ की दूरी: { $miles } मील
milebymile-enter-distance = दौड़ की दूरी दर्ज करें (300-3000)
milebymile-set-winning-score = जीत का स्कोर: { $score } अंक
milebymile-enter-winning-score = जीत का स्कोर दर्ज करें (1000-10000)
milebymile-toggle-perfect-crossing = सटीक समाप्ति की आवश्यकता: { $enabled }
milebymile-toggle-stacking = स्टैकिंग हमलों की अनुमति: { $enabled }
milebymile-toggle-reshuffle = डिस्कार्ड पाइल को फिर से फेंटें: { $enabled }
milebymile-toggle-karma = कर्म नियम: { $enabled }
milebymile-set-rig = डेक रिगिंग: { $rig }
milebymile-select-rig = डेक रिगिंग विकल्प चुनें

# Option change announcements
milebymile-option-changed-distance = दौड़ की दूरी { $miles } मील पर सेट की गई।
milebymile-option-changed-winning = जीत का स्कोर { $score } अंकों पर सेट किया गया।
milebymile-option-changed-crossing = सटीक समाप्ति की आवश्यकता { $enabled }।
milebymile-option-changed-stacking = स्टैकिंग हमलों की अनुमति { $enabled }।
milebymile-option-changed-reshuffle = डिस्कार्ड पाइल को फिर से फेंटना { $enabled }।
milebymile-option-changed-karma = कर्म नियम { $enabled }।
milebymile-option-changed-rig = डेक रिगिंग { $rig } पर सेट किया गया।

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $points } अंक, { $miles } मील, समस्याएं: { $problems }, सुरक्षाएं: { $safeties }

# Card actions
milebymile-no-matching-safety = आपके पास मेल खाता सुरक्षा कार्ड नहीं है!
milebymile-cant-play = आप { $card } नहीं खेल सकते क्योंकि { $reason }।
milebymile-no-card-selected = डिस्कार्ड करने के लिए कोई कार्ड चयनित नहीं।
milebymile-no-valid-targets = इस खतरे के लिए कोई वैध लक्ष्य नहीं!
milebymile-you-drew = आपने ड्रॉ किया: { $card }
milebymile-discards = { $player } एक कार्ड डिस्कार्ड करता है।
milebymile-select-target = एक लक्ष्य चुनें

# Distance plays
milebymile-plays-distance-individual = { $player } { $distance } मील खेलता है, और अब { $total } मील पर है।
milebymile-plays-distance-team = { $player } { $distance } मील खेलता है; उनकी टीम अब { $total } मील पर है।

# Journey complete
milebymile-journey-complete-perfect-individual = { $player } ने सटीक क्रॉसिंग के साथ यात्रा पूरी की है!
milebymile-journey-complete-perfect-team = टीम { $team } ने सटीक क्रॉसिंग के साथ यात्रा पूरी की है!
milebymile-journey-complete-individual = { $player } ने यात्रा पूरी की है!
milebymile-journey-complete-team = टीम { $team } ने यात्रा पूरी की है!

# Hazard plays
milebymile-plays-hazard-individual = { $player } { $target } पर { $card } खेलता है।
milebymile-plays-hazard-team = { $player } टीम { $team } पर { $card } खेलता है।

# Remedy/Safety plays
milebymile-plays-card = { $player } { $card } खेलता है।
milebymile-plays-dirty-trick = { $player } { $card } को डर्टी ट्रिक के रूप में खेलता है!

# Deck
milebymile-deck-reshuffled = डिस्कार्ड पाइल को डेक में वापस फेंट दिया गया।

# Race
milebymile-new-race = नई दौड़ शुरू होती है!
milebymile-race-complete = दौड़ पूरी हुई! स्कोर की गणना...
milebymile-earned-points = { $name } ने इस दौड़ में { $score } अंक अर्जित किए: { $breakdown }।
milebymile-total-scores = कुल स्कोर:
milebymile-team-score = { $name }: { $score } अंक

# Scoring breakdown
milebymile-from-distance = यात्रा की गई दूरी से { $miles }
milebymile-from-trip = यात्रा पूरी करने से { $points }
milebymile-from-perfect = सटीक क्रॉसिंग से { $points }
milebymile-from-safe = सुरक्षित यात्रा से { $points }
milebymile-from-shutout = शटआउट से { $points }
milebymile-from-safeties = { $count } { $safeties ->
    [one] सुरक्षा
    *[other] सुरक्षाओं
} से { $points }
milebymile-from-all-safeties = सभी 4 सुरक्षाओं से { $points }
milebymile-from-dirty-tricks = { $count } { $tricks ->
    [one] डर्टी ट्रिक
    *[other] डर्टी ट्रिक्स
} से { $points }

# Game end
milebymile-wins-individual = { $player } खेल जीतता है!
milebymile-wins-team = टीम { $team } खेल जीतती है! ({ $members })
milebymile-final-score = अंतिम स्कोर: { $score } अंक

# Karma messages - clash (both lose karma)
milebymile-karma-clash-you-target = आप और आपका लक्ष्य दोनों को दरकिनार किया गया है! हमला निष्प्रभावी हो गया है।
milebymile-karma-clash-you-attacker = आप और { $attacker } दोनों को दरकिनार किया गया है! हमला निष्प्रभावी हो गया है।
milebymile-karma-clash-others = { $attacker } और { $target } दोनों को दरकिनार किया गया है! हमला निष्प्रभावी हो गया है।
milebymile-karma-clash-your-team = आपकी टीम और आपका लक्ष्य दोनों को दरकिनार किया गया है! हमला निष्प्रभावी हो गया है।
milebymile-karma-clash-target-team = आप और टीम { $team } दोनों को दरकिनार किया गया है! हमला निष्प्रभावी हो गया है।
milebymile-karma-clash-other-teams = टीम { $attacker } और टीम { $target } दोनों को दरकिनार किया गया है! हमला निष्प्रभावी हो गया है।

# Karma messages - attacker shunned
milebymile-karma-shunned-you = आपकी आक्रामकता के लिए आपको दरकिनार किया गया है! आपका कर्म खो गया है।
milebymile-karma-shunned-other = { $player } को उनकी आक्रामकता के लिए दरकिनार किया गया है!
milebymile-karma-shunned-your-team = आपकी टीम को उसकी आक्रामकता के लिए दरकिनार किया गया है! आपकी टीम का कर्म खो गया है।
milebymile-karma-shunned-other-team = टीम { $team } को उसकी आक्रामकता के लिए दरकिनार किया गया है!

# False Virtue
milebymile-false-virtue-you = आप झूठा सदाचार खेलते हैं और अपना कर्म पुनः प्राप्त करते हैं!
milebymile-false-virtue-other = { $player } झूठा सदाचार खेलता है और अपना कर्म पुनः प्राप्त करता है!
milebymile-false-virtue-your-team = आपकी टीम झूठा सदाचार खेलती है और अपना कर्म पुनः प्राप्त करती है!
milebymile-false-virtue-other-team = टीम { $team } झूठा सदाचार खेलती है और अपना कर्म पुनः प्राप्त करती है!

# Problems/Safeties (for status display)
milebymile-none = कोई नहीं

# Unplayable card reasons
milebymile-reason-not-on-team = आप टीम में नहीं हैं
milebymile-reason-stopped = आप रुके हुए हैं
milebymile-reason-has-problem = आपके पास एक समस्या है जो ड्राइविंग को रोकती है
milebymile-reason-speed-limit = गति सीमा सक्रिय है
milebymile-reason-exceeds-distance = यह { $miles } मील से अधिक हो जाएगा
milebymile-reason-no-targets = कोई वैध लक्ष्य नहीं हैं
milebymile-reason-no-speed-limit = आप गति सीमा के अंतर्गत नहीं हैं
milebymile-reason-has-right-of-way = राइट ऑफ वे आपको हरी बत्तियों के बिना जाने देता है
milebymile-reason-already-moving = आप पहले से ही चल रहे हैं
milebymile-reason-must-fix-first = आपको पहले { $problem } को ठीक करना होगा
milebymile-reason-has-gas = आपकी कार में गैस है
milebymile-reason-tires-fine = आपके टायर ठीक हैं
milebymile-reason-no-accident = आपकी कार किसी दुर्घटना में नहीं हुई है
milebymile-reason-has-safety = आपके पास पहले से ही वह सुरक्षा है
milebymile-reason-has-karma = आपके पास अभी भी आपका कर्म है
milebymile-reason-generic = यह अभी नहीं खेला जा सकता

# Card names
milebymile-card-out-of-gas = आउट ऑफ गैस
milebymile-card-flat-tire = फ्लैट टायर
milebymile-card-accident = दुर्घटना
milebymile-card-speed-limit = गति सीमा
milebymile-card-stop = रुकें
milebymile-card-gasoline = पेट्रोल
milebymile-card-spare-tire = स्पेयर टायर
milebymile-card-repairs = मरम्मत
milebymile-card-end-of-limit = सीमा का अंत
milebymile-card-green-light = हरी बत्ती
milebymile-card-extra-tank = अतिरिक्त टैंक
milebymile-card-puncture-proof = पंक्चर प्रूफ
milebymile-card-driving-ace = ड्राइविंग ऐस
milebymile-card-right-of-way = राइट ऑफ वे
milebymile-card-false-virtue = झूठा सदाचार
milebymile-card-miles = { $miles } मील

# Disabled action reasons
milebymile-no-dirty-trick-window = कोई डर्टी ट्रिक विंडो सक्रिय नहीं है।
milebymile-not-your-dirty-trick = यह आपकी टीम की डर्टी ट्रिक विंडो नहीं है।
milebymile-between-races = अगली दौड़ शुरू होने की प्रतीक्षा करें।

# Validation errors
milebymile-error-karma-needs-three-teams = कर्म नियम के लिए कम से कम 3 अलग-अलग कारों/टीमों की आवश्यकता है।

milebymile-you-play-safety-with-effect = आप { $card } खेलते हैं। { $effect }
milebymile-player-plays-safety-with-effect = { $player } { $card } खेलता है। { $effect }
milebymile-you-play-dirty-trick-with-effect = आप { $card } को गंदी चाल के रूप में खेलते हैं। { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } { $card } को गंदी चाल के रूप में खेलता है। { $effect }
milebymile-safety-effect-extra-tank = अब ईंधन खत्म होने से सुरक्षित।
milebymile-safety-effect-puncture-proof = अब पंक्चर से सुरक्षित।
milebymile-safety-effect-driving-ace = अब दुर्घटना से सुरक्षित।
milebymile-safety-effect-right-of-way = अब रुकावट और गति सीमा से सुरक्षित।
