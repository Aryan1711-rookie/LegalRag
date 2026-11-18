
import re
from collections import defaultdict

class DocumentClassifier:

    PATTERNS = {
        "judgment": [
            r"\bJUDGMENT\b",
            r"\bJUDGMENT AND ORDER\b",
            r"\bIN THE SUPREME COURT OF INDIA\b",
            r"\bHIGH COURT OF\b",
            r"\bAPPELLANT\b",
            r"\bRESPONDENT\b",
            r"\bCORAM\b",
        ],

        "bare_act": [
            r"\bACT NO\.\s*\d+",
            r"\bBE IT ENACTED\b",
            r"\bAN ACT TO\b",
            r"\bSECTION\s+\d+",
            r"\bSHORT TITLE AND COMMENCEMENT\b",
            r"\bIN THIS ACT\b",
        ],

        "contract": [
            r"\bAGREEMENT\b",
            r"\bWHEREAS\b",
            r"\bPARTY OF THE FIRST PART\b",
            r"\bPARTY OF THE SECOND PART\b",
            r"\bTERMS AND CONDITIONS\b",
            r"\bIN WITNESS WHEREOF\b",
        ],

        "legal_notice": [
            r"\bLEGAL NOTICE\b",
            r"\bNOTICE TO\b",
            r"\bHEREBY CALLED UPON\b",
            r"\bCEASE AND DESIST\b",
            r"\bFAILING WHICH\b",
        ],

        "petition": [
            r"\bWRIT PETITION\b",
            r"\bPETITIONER\b",
            r"\bPRAYER\b",
            r"\bAFFIDAVIT IN SUPPORT\b",
            r"\bIN THE HIGH COURT\b",
        ],

        "affidavit": [
            r"\bAFFIDAVIT\b",
            r"\bDEPONENT\b",
            r"\bSOLEMNLY AFFIRM\b",
            r"\bVERIFICATION\b",
        ],

        "case_summary": [
            r"\bCASE SUMMARY\b",
            r"\bFACTS OF THE CASE\b",
            r"\bISSUES FOR CONSIDERATION\b",
            r"\bLEGAL ANALYSIS\b",
        ]
    }

    def classify(self, text: str):

        text = text.upper()

        scores = defaultdict(int)

        for doc_type, patterns in self.PATTERNS.items():

            for pattern in patterns:

                matches = re.findall(pattern, text)

                if matches:
                    scores[doc_type] += len(matches)

        if not scores:
            return {
                "document_type": "other",
                "confidence": 0.0
            }

        ranked = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True
        )

        best_type, best_score = ranked[0]

        total_score = sum(scores.values())

        confidence = best_score / total_score

        return {
            "document_type": best_type,
            "confidence": round(confidence, 2),
            "scores": dict(scores)
        }
