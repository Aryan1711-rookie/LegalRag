
import unittest

from rag.ingestion.evaluation.ocr_metrics import (
    levenshtein_distance,
    calculate_cer,
    calculate_wer,
    evaluate_ocr,
)


class TestLevenshteinDistance(unittest.TestCase):

    def test_identical_strings(self):
        self.assertEqual(
            levenshtein_distance("legal", "legal"),
            0
        )

    def test_substitution(self):
        self.assertEqual(
            levenshtein_distance("cat", "bat"),
            1
        )

    def test_insertion(self):
        self.assertEqual(
            levenshtein_distance("cat", "cats"),
            1
        )

    def test_deletion(self):
        self.assertEqual(
            levenshtein_distance("cats", "cat"),
            1
        )

    def test_multiple_edits(self):
        self.assertEqual(
            levenshtein_distance("kitten", "sitting"),
            3
        )

    def test_token_lists(self):
        self.assertEqual(
            levenshtein_distance(
                ["यह", "आदेश", "है"],
                ["यह", "निर्णय", "है"]
            ),
            1
        )


class TestOCRMetrics(unittest.TestCase):

    def test_perfect_transcription(self):
        result = evaluate_ocr(
            "यह न्यायालय आदेश पारित करता है।",
            "यह न्यायालय आदेश पारित करता है।"
        )

        self.assertEqual(result["cer"], 0.0)
        self.assertEqual(result["wer"], 0.0)
        self.assertEqual(result["character_accuracy"], 1.0)
        self.assertEqual(result["word_accuracy"], 1.0)

    def test_hindi_character_error(self):
        cer = calculate_cer("राम", "रम")

        self.assertAlmostEqual(cer, 1 / 3, places=4)

    def test_word_substitution(self):
        wer = calculate_wer(
            "यह आदेश सही है",
            "यह आदेश गलत है"
        )

        self.assertEqual(wer, 0.25)

    def test_word_insertion(self):
        wer = calculate_wer(
            "यह आदेश है",
            "यह नया आदेश है"
        )

        self.assertAlmostEqual(wer, 1 / 3, places=4)

    def test_whitespace_normalization(self):
        result = evaluate_ocr(
            "यह   न्यायालय\nआदेश है",
            "यह न्यायालय आदेश है"
        )

        self.assertEqual(result["cer"], 0.0)
        self.assertEqual(result["wer"], 0.0)

    def test_punctuation_is_preserved(self):
        cer = calculate_cer(
            "आदेश।",
            "आदेश"
        )

        self.assertGreater(cer, 0.0)

    def test_empty_reference_raises_error(self):
        with self.assertRaises(ValueError):
            calculate_cer("", "कुछ पाठ")

        with self.assertRaises(ValueError):
            calculate_wer("", "कुछ पाठ")


if __name__ == "__main__":
    unittest.main(verbosity=2)
