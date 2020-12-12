import re

ALPHANUMERAL_AND_PUNCTUACTION = "[^A-Za-z0-9 .,?!']+"


def get_tts_compatible_version_of_text(text, filter_level=3):
    text = get_family_friendly_version_of_text(text, filter_level)
    text = get_text_without_special_characters(text)
    text = get_text_without_links(text)
    return text


def get_text_without_links(text):
    for word in text.split():
        if "http" in word:
            text = text.replace(word, "")
    return text


def get_text_without_special_characters(text):
    return re.sub(ALPHANUMERAL_AND_PUNCTUACTION, "", text)


def get_family_friendly_version_of_text(text, level=3):
    profanity_filter = _get_profanity_dict_strength(level)
    for word in text.split():
        if _word_in_filter(profanity_filter, word):
            text = text.replace(word, _get_replacement(profanity_filter, word))
    return text


def get_censored_version_of_text(text, level=3):
    profanity_filter = _get_profanity_dict_strength(level)
    for word in text.split():
        if _word_in_filter(profanity_filter, word):
            text = text.replace(word, _get_censored_word(word))
    return text


def _get_profanity_dict_strength(level):
    level = int(level)
    if level <= 1:
        return EXTREME_PROFANITIES_AND_REPLACEMENTS
    elif level == 2:
        return {
            **EXTREME_PROFANITIES_AND_REPLACEMENTS,
            **STRONG_PROFANITIES_AND_REPLACEMENTS,
        }
    else:
        return {
            **EXTREME_PROFANITIES_AND_REPLACEMENTS,
            **STRONG_PROFANITIES_AND_REPLACEMENTS,
            **LIGHT_PROFANITIES_AND_REPLACEMENTS,
        }


def _word_in_filter(profanity_filter, word):
    try:
        base_word = re.findall(r"\w+", word)[0]
    except:
        return False
    return base_word.lower() in profanity_filter


def _get_replacement(profanity_filter, word):
    prefix = re.findall(r"^\W+", word)
    prefix = prefix[0] if prefix else ""
    suffix = re.findall(r"\W+$", word)
    suffix = suffix[0] if suffix else ""
    base_word = re.findall(r"\w*", word)[0]
    if not base_word:
        return word
    if base_word[0].isupper():
        new_word = profanity_filter[base_word.lower()].capitalize()
    else:
        new_word = profanity_filter[base_word.lower()]
    return prefix + new_word + suffix


def _get_censored_word(word):
    return word[0] + "*" * (len(word) - 2) + word[-1]


# censored and replaced only when necessary
LIGHT_PROFANITIES_AND_REPLACEMENTS = {
    "biatch": "biaatch",
    "@$$": "butt",
    "ass": "butt",
    "carpetmuncher": "carpeteater",
    "clit": "clitoris",
    "goddamn": "godblessed",
    "shite": "poop",
    "shytty": "poopy",
    "bastard": "out-of-wedlock",
    "crap": "poop",
}

# censored and replaced in title, tumbnail and the first 30 seconds of the video
STRONG_PROFANITIES_AND_REPLACEMENTS = {
    "blowjob": "head",
    "fudgepacker": "Tom Cruise",
    "fuck": "F",
    "fucks": "Fs",
    "phuc": "F",
    "phuk": "F",
    "phuck": "F",
    "fukah": "lover",
    "fukker": "lover",
    "fucker": "lover",
    "phucker": "lover",
    "phuker": "lover",
    "phukker": "lover",
    "fucking": "effing",
    "fukking": "effing",
    "fukkin": "effing",
    "fukken": "effing",
    "lipshits": "lippies",
    "lipshitz": "lippies",
    "motherfucker": "motherlover",
    "mothafucker": "motherlover",
    "mothafuker": "motherlover",
    "mothafukkah": "motherlover",
    "motherfuker": "motherlover",
    "motherfukah": "motherlover",
    "motherfukkah": "motherlover",
    "muthafuka": "motherlover",
    "muthafucker": "motherlover",
    "muthafukah": "motherlover",
    "muthafukka": "motherlover",
    "motherfucking": "motherloving",
    "motherfukking": "motherloving",
    "motherfuking": "motherloving",
    "asshole": "jerk",
    "ahole": "jerk",
    "asshol": "jerk",
    "assh0le": "jerk",
    "assh0l": "jerk",
    "assmonkey": "buttmonkey",
    "assface": "buttface",
    "shit": "poop",
    "shyt": "poop",
    "shitty": "poopy",
    "skank": "smelly",
    "skanky": "smelly",
    "slutty": "slooty",
    "slut": "sloot",
    "assrammer": "buttlover",
    "bitch": "b-word",
    "b1tch": "b-word",
    "b17ch": "b-word",
    "bi7ch": "b-word",
    "biitch": "b-word",
    "bitches": "b-words",
    "b1tches": "b-words",
    "b17ches": "b-words",
    "bi7ches": "b-words",
    "cock": "penis",
    "c0ck": "penis",
    "c0k": "penis",
    "cok": "penis",
    "cocksucker": "penis licker",
    "jizz": "semen",
    "cum": "semen",
    "screw": "F",
    "screws": "Fs",
    "retard": "mentally challenged",
    "retarded": "mentally challenged",
    "retards": "mentally challenged",
}

# censored or replaced always
EXTREME_PROFANITIES_AND_REPLACEMENTS = {
    "nigger": "n-word",
    "nigga": "n-word",
    "nig": "n-word",
    "n1gger": "n-word",
    "n1gga": "n-word",
    "n1g": "n-word",
    "niggers": "n-words",
    "n1ggers": "n-words",
    "nigg3rs": "n-words",
    "n1gg3rs": "n-words",
    "n1ggas": "n-words",
    "niggas": "n-words",
    "nigs": "n-words",
    "n1gs": "n-words",
    "cunt": "c-word",
    "cunts": "c-words",
    "faggot": "homosexual",
    "faggots": "homosexuals",
    "fag": "homosexual",
    "fagit": "homosexual",
    "fag1t": "homosexual",
    "faget": "homosexual",
    "faggit": "homosexual",
    "fagg1t": "homosexual",
    "fags": "homosexuals",
    "fagz": "homosexuals",
    "whore": "prostitute",
    "wh0re": "prostitute",
    "whores": "prostitutes",
    "wh0res": "prostitutes",
    "dike": "lesbian",
    "dikes": "lesbians",
    "d1ke": "lesbian",
    "d1kes": "lesbians",
    "dyke": "lesbian",
    "dykes": "lesbians",
    "chink": "chinese",
    "chinks": "chinese",
    "gook": "asian",
    "gooks": "asian",
    "kike": "jew",
    "k1ke": "jew",
    "kikes": "jews",
    "k1kes": "jews",
}