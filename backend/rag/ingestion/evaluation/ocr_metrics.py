
import unicodedata
import re


def normalize_for_evaluation(text: str) -> str:
    """
    Normalize text before OCR comparison.

    - Apply Unicode NFC normalization.
    - Normalize line endings.
    - Collapse repeated whitespace.
    - Preserve punctuation, digits and legal identifiers.
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    text = unicodedata.normalize("NFC", text)

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Treat all whitespace consistently.
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def levenshtein_distance(reference, hypothesis):
    """
    Calculate Levenshtein edit distance using dynamic programming.

    Supports strings and lists of tokens.
    """
    if len(reference) < len(hypothesis):
        reference, hypothesis = hypothesis, reference

    previous_row = list(range(len(hypothesis) + 1))

    for i, ref_item in enumerate(reference, start=1):
        current_row = [i]

        for j, hyp_item in enumerate(hypothesis, start=1):
            insertion = current_row[j - 1] + 1
            deletion = previous_row[j] + 1
            substitution = (
                previous_row[j - 1]
                + (ref_item != hyp_item)
            )

            current_row.append(
                min(insertion, deletion, substitution)
            )

        previous_row = current_row

    return previous_row[-1]


def calculate_cer(reference: str, hypothesis: str) -> float:
    """
    Character Error Rate.

    CER = character edit distance / reference character count.

    Uses Unicode code points, not grapheme clusters.
    """
    reference = normalize_for_evaluation(reference)
    hypothesis = normalize_for_evaluation(hypothesis)

    if not reference:
        raise ValueError("Reference text cannot be empty.")

    distance = levenshtein_distance(
        reference,
        hypothesis
    )

    return distance / len(reference)


def calculate_wer(reference: str, hypothesis: str) -> float:
    """
    Word Error Rate.

    WER = word edit distance / reference word count.

    Tokenization uses whitespace.
    Punctuation is preserved.
    """
    reference = normalize_for_evaluation(reference).split()
    hypothesis = normalize_for_evaluation(hypothesis).split()

    if not reference:
        raise ValueError("Reference text cannot be empty.")

    distance = levenshtein_distance(
        reference,
        hypothesis
    )

    return distance / len(reference)


def evaluate_ocr(reference: str, hypothesis: str) -> dict:
    """
    Calculate OCR evaluation metrics.

    Accuracy values are clipped to [0, 1].
    Error rates can exceed 1.0.
    """
    cer = calculate_cer(reference, hypothesis)
    wer = calculate_wer(reference, hypothesis)

    return {
        "cer": round(cer, 4),
        "wer": round(wer, 4),

        "character_accuracy": round(
            max(0.0, 1.0 - cer), 4
        ),

        "word_accuracy": round(
            max(0.0, 1.0 - wer), 4
        )
    }
