
import json


class AnswerQualityEvaluator:

    def __init__(self, client, model: str):
        self.client = client
        self.model = model

    def evaluate(
        self,
        question: str,
        answer: str,
        ground_truth: str,
        key_points: list[str],
        context: str
    ) -> dict:

        # Step 1: Validate inputs
        if not answer or not answer.strip():
            raise ValueError("Generated answer cannot be empty.")

        if not ground_truth or not ground_truth.strip():
            raise ValueError("Ground truth cannot be empty.")

        if not key_points:
            raise ValueError("Key points cannot be empty.")

        if not context or not context.strip():
            raise ValueError("Evaluation context cannot be empty.")

        evaluation_prompt = """
You are an impartial evaluator for an Indian legal RAG system.

Evaluate the generated answer using the question, reference answer,
expected key points, and supplied legal context.

Scoring criteria:

1. correctness:
   Does the answer accurately reflect the reference answer?
   Penalize incorrect or contradictory legal claims.

2. relevance:
   Does the answer directly address the question?
   Penalize irrelevant or unrelated content.

3. completeness:
   Does the answer cover the expected key points?
   Assess coverage, not writing length.

4. Evidence-based correctness:
   Every factual legal claim must be supported by the supplied context.
   Penalize claims that go beyond or contradict the supplied evidence.
   A legally correct statement is not necessarily supported by this document.

A claim must satisfy BOTH reference correctness and contextual support
to receive full correctness credit.

Do not reward unsupported legal claims.
Do not assume a claim is correct merely because it sounds convincing.

Give each score as a number between 0 and 1.

Return ONLY valid JSON in this exact structure:

{
    "correctness": 0.0,
    "relevance": 0.0,
    "completeness": 0.0,
    "reasoning": "Brief explanation of the scores"
}
"""

        # Step 2: Call LLM judge
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": evaluation_prompt
                    },
                    {
                        "role": "user",
                        "content": json.dumps({
                            "question": question,
                            "generated_answer": answer,
                            "ground_truth": ground_truth,
                            "key_points": key_points,
                            "context": context
                        })
                    }
                ],
                temperature=0,
                max_tokens=1000
            )

        except Exception as exc:
            raise RuntimeError(
                f"LLM judge API request failed: {exc}"
            ) from exc

        # Step 3: Validate completion choices
        if not response.choices:
            print("\nLLM Judge Debug Information:")
            print("Model:", self.model)
            print("Usage:", response.usage)
            print("Response:", response)

            raise ValueError(
                "LLM judge returned no completion choices."
            )

        choice = response.choices[0]
        raw_result = choice.message.content

        # Step 4: Validate response content
        if not raw_result or not raw_result.strip():
            print("\nLLM Judge Debug Information:")
            print("Model:", self.model)
            print("Finish reason:", choice.finish_reason)
            print("Usage:", response.usage)
            print("Response:", response)

            raise ValueError(
                "LLM judge returned an empty response."
            )

        # Step 5: Parse JSON
        try:
            result = json.loads(raw_result.strip())

        except json.JSONDecodeError as exc:
            print("\nLLM Judge returned invalid JSON:")
            print(raw_result)

            raise ValueError(
                f"LLM judge returned invalid JSON: {exc}"
            ) from exc

        # Step 6: Validate response structure
        required_fields = {
            "correctness",
            "relevance",
            "completeness",
            "reasoning"
        }

        if not isinstance(result, dict):
            raise ValueError(
                "LLM judge response must be a JSON object."
            )

        missing_fields = required_fields - result.keys()

        if missing_fields:
            raise ValueError(
                f"LLM judge response is missing fields: "
                f"{', '.join(sorted(missing_fields))}"
            )

        # Step 7: Validate individual scores
        for metric in (
            "correctness",
            "relevance",
            "completeness"
        ):
            score = result[metric]

            if (
                isinstance(score, bool)
                or not isinstance(score, (int, float))
                or not 0 <= score <= 1
            ):
                raise ValueError(
                    f"Invalid {metric} score: {score}"
                )

            result[metric] = float(score)

        # Step 8: Validate reasoning
        if (
            not isinstance(result["reasoning"], str)
            or not result["reasoning"].strip()
        ):
            raise ValueError(
                "Evaluation reasoning must be a non-empty string."
            )

        return result
