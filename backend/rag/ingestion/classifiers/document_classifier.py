import re
import unicodedata
from enum import StrEnum


class DocumentType(StrEnum):

    ACT = "act"
    BILL = "bill"
    JUDGMENT = "judgment"
    AFFIDAVIT = "affidavit"
    PRESENTATION = "presentation"
    GENERAL = "general"


class DocumentClassifier:

    PATTERNS = {
        DocumentType.BILL: [
            (r"\bbill\s+no\.?\s*\d+", 5),
            (r"as introduced in (lok sabha|rajya sabha)", 5),
            (r"arrangement of clauses", 4),
            (r"statement of objects and reasons", 2),
        ],

        DocumentType.ACT: [
            (r"arrangement of sections", 5),
            (r"\bact no\.?\s*\d+", 5),
            (r"be it enacted by parliament", 5),
            (r"an act to\b", 2),
            (r"short title.*commencement", 2),
            (r"अधिनियम संख्या", 5),
        ],

        DocumentType.JUDGMENT: [
            (r"in the supreme court of india", 4),
            (r"in the high court of", 4),
            (r"criminal appeal no", 3),
            (r"civil appeal no", 3),
            (r"\bcoram\b", 2),
            (r"\bjudgment\b", 1),
            (r"न्यायालय", 1),
            (r"निर्णय", 2),
        ],

        DocumentType.AFFIDAVIT: [
            (r"\baffidavit\b", 3),
            (r"solemnly affirm", 4),
            (r"\bdeponent\b", 3),
            (r"शपथ पत्र", 4),
            (r"शपथपत्र", 4),
        ],

        DocumentType.PRESENTATION: [
            (r"landmark judgments", 3),
            (r"learning objectives", 3),
            (r"prepared by", 2),
            (r"presented by", 3),
            (r"table of contents", 1),
        ],
    }

    MIN_SCORE = 5

    def classify(self, pages: list) -> dict:

        text = "\n".join(
            page.get("layout_text") or page.get("text", "")
            for page in pages[:5]
        )

        text = unicodedata.normalize("NFKC", text)
        text = re.sub(r"\s+", " ", text).lower()

        scores = {
            doc_type.value: 0
            for doc_type in self.PATTERNS
        }

        matched_patterns = {
            doc_type.value: []
            for doc_type in self.PATTERNS
        }

        for doc_type, patterns in self.PATTERNS.items():

            for pattern, weight in patterns:

                if re.search(pattern, text):

                    scores[doc_type.value] += weight

                    matched_patterns[doc_type.value].append(
                        pattern
                    )

        ranked = sorted(
            scores,
            key=scores.get,
            reverse=True
        )

        best_type = ranked[0]
        best_score = scores[best_type]

        if (
            best_score < self.MIN_SCORE
            or best_score == scores[ranked[1]]
        ):
            return {
                "document_type": DocumentType.GENERAL.value,
                "score": best_score,
                "scores": scores,
                "matched_patterns": []
            }

        return {
            "document_type": best_type,
            "score": best_score,
            "scores": scores,
            "matched_patterns": matched_patterns[best_type]
        }