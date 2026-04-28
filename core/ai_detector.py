"""AI-text heuristic detector — local, no external API.

Heuristics inspired by GPTZero / DetectGPT / Originality.ai public papers:
1. Burstiness — variance of sentence lengths (humans write with high variance, AI low).
2. Lexical diversity — unique-words / total-words ratio (AI tends to repeat).
3. N-gram repetition — count of repeating bigram/trigrams (AI repeats catchphrases).
4. Sentence-starter homogeneity — same opener words ("The", "However", "Moreover").
5. Average word length (AI uses more 'sophisticated' filler words).

Returns a 0-100 score where:
    100 = very human-sounding
    0   = very AI-sounding

This is a heuristic — not a substitute for paid services, but useful as a directional
signal during the rewrite step. Scores < 60 → suggest re-running dehumanize().
"""
from __future__ import annotations

import re
import statistics
from collections import Counter

# Common AI tells (English) — the more of these, the lower the score
AI_TELL_PHRASES_EN = [
    "delve into", "tapestry", "in conclusion", "in essence", "it's important to note",
    "navigate the", "ever-evolving", "in today's", "nestled in", "in the realm of",
    "stands as a testament", "let us delve", "a beacon of", "underscore",
    "moreover", "furthermore", "however,", "in summary", "to summarize",
    "it is worth noting", "elevate your", "unleash", "harness the power",
]

AI_TELL_PHRASES_JA = [
    "重要なのは", "結論として", "要するに", "言うまでもなく", "ご存知のように",
]

AI_TELL_PHRASES_KR = [
    "결론적으로", "요약하자면", "중요한 것은", "다시 말해", "강조하고 싶은",
]


def _split_sentences(text: str) -> list[str]:
    sents = re.split(r"(?<=[.!?。！？])\s+|\n+", text.strip())
    return [s.strip() for s in sents if s.strip()]


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def _ngrams(tokens: list[str], n: int) -> list[tuple]:
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def burstiness_score(text: str) -> float:
    """High variance in sentence length → high burstiness → human-like."""
    sents = _split_sentences(text)
    if len(sents) < 4:
        return 50.0
    lens = [len(_tokenize(s)) for s in sents]
    mean = statistics.mean(lens)
    if mean == 0:
        return 50.0
    stdev = statistics.stdev(lens)
    coef_var = stdev / mean  # coefficient of variation
    # human writing typically has CV > 0.6; AI hovers around 0.3
    return min(100.0, max(0.0, coef_var * 130))


def lexical_diversity(text: str) -> float:
    tokens = _tokenize(text)
    if len(tokens) < 50:
        return 50.0
    # type-token ratio over a sliding window of 100 tokens (more stable)
    window = 100
    ratios = []
    for i in range(0, len(tokens) - window, window // 2):
        chunk = tokens[i : i + window]
        ratios.append(len(set(chunk)) / len(chunk))
    if not ratios:
        ratios = [len(set(tokens)) / len(tokens)]
    avg = statistics.mean(ratios)
    # human ~0.65-0.75, AI ~0.55-0.65
    return min(100.0, max(0.0, (avg - 0.45) * 250))


def ngram_repetition_score(text: str) -> float:
    """Lower repetition → higher score."""
    tokens = _tokenize(text)
    if len(tokens) < 20:
        return 50.0
    bigrams = _ngrams(tokens, 2)
    trigrams = _ngrams(tokens, 3)
    if not bigrams or not trigrams:
        return 50.0
    bg_counts = Counter(bigrams)
    tg_counts = Counter(trigrams)
    repeat_bg = sum(c for c in bg_counts.values() if c > 2)
    repeat_tg = sum(c for c in tg_counts.values() if c > 1)
    repeat_ratio = (repeat_bg + 2 * repeat_tg) / max(1, len(tokens))
    # human < 0.05, AI > 0.1
    return min(100.0, max(0.0, (1 - repeat_ratio * 8) * 100))


def starter_homogeneity(text: str) -> float:
    """Are sentences starting with the same words too often?"""
    sents = _split_sentences(text)
    if len(sents) < 5:
        return 50.0
    starters = [_tokenize(s)[:1][0] if _tokenize(s) else "" for s in sents]
    starters = [s for s in starters if s]
    if not starters:
        return 50.0
    counts = Counter(starters)
    most = counts.most_common(1)[0][1]
    homogeneity = most / len(starters)
    # human < 0.15, AI often > 0.2
    return min(100.0, max(0.0, (1 - homogeneity * 4) * 100))


def ai_phrase_score(text: str, lang: str = "en") -> float:
    """Count of AI-tell phrases (lower count = higher score)."""
    if lang == "ja":
        phrases = AI_TELL_PHRASES_JA
    elif lang == "kr":
        phrases = AI_TELL_PHRASES_KR
    else:
        phrases = AI_TELL_PHRASES_EN

    text_lower = text.lower()
    count = sum(text_lower.count(p) for p in phrases)
    tokens = max(1, len(_tokenize(text)))
    rate = count / (tokens / 1000)  # per 1k tokens
    return min(100.0, max(0.0, (1 - rate / 5) * 100))


def detect(text: str, lang: str = "en") -> dict:
    """Run all heuristics and return composite human-likeness score (0-100).

    Returns:
        {
          "score": 0-100 (higher = more human-like),
          "verdict": "Human-like" | "Mixed" | "AI-like",
          "components": {name: score},
          "suggestions": [str, ...],
        }
    """
    components = {
        "burstiness": burstiness_score(text),
        "lexical_diversity": lexical_diversity(text),
        "ngram_repetition": ngram_repetition_score(text),
        "starter_homogeneity": starter_homogeneity(text),
        "ai_phrases": ai_phrase_score(text, lang),
    }
    weights = {
        "burstiness": 0.25,
        "lexical_diversity": 0.20,
        "ngram_repetition": 0.20,
        "starter_homogeneity": 0.15,
        "ai_phrases": 0.20,
    }
    score = sum(components[k] * weights[k] for k in components)
    score = round(score, 1)

    if score >= 75:
        verdict = "Human-like"
    elif score >= 55:
        verdict = "Mixed"
    else:
        verdict = "AI-like"

    suggestions: list[str] = []
    if components["burstiness"] < 50:
        suggestions.append("Sentence length too uniform — vary between very short and long sentences.")
    if components["lexical_diversity"] < 50:
        suggestions.append("Vocabulary repetitive — paraphrase recurring nouns/verbs.")
    if components["ngram_repetition"] < 50:
        suggestions.append("Same phrases repeat too often — break up catchphrases.")
    if components["starter_homogeneity"] < 50:
        suggestions.append("Many sentences start with the same word — vary openers.")
    if components["ai_phrases"] < 60:
        suggestions.append("Detected AI-tell phrases — replace 'in conclusion', 'delve into', etc.")

    return {
        "score": score,
        "verdict": verdict,
        "components": {k: round(v, 1) for k, v in components.items()},
        "suggestions": suggestions,
    }
