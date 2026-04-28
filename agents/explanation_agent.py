# ============================================================================
# EXPLANATION AGENT — Generates clear explanations of scoring results
# Uses OLLAMA (Tharusha_Dilhara_Jayadeera/singemma:latest) via raw HTTP requests
# ============================================================================

import requests
import json


# OLLAMA configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "Tharusha_Dilhara_Jayadeera/singemma:latest"
OLLAMA_TIMEOUT = 180


class ExplanationAgent:
    """
    Agent responsible for generating clear, readable explanations
    of how a student's answer was scored.
    """

    def __init__(self):
        """Initialize the ExplanationAgent."""
        self.url = OLLAMA_URL
        self.model = OLLAMA_MODEL
        self.timeout = OLLAMA_TIMEOUT

    def explain(self, question, student_answer, total_score, criteria_scores,
                retrieved_chunks, ontology_facts):
        """
        Generate an explanation of the scoring results.

        Args:
            question: The question text
            student_answer: Student's answer
            total_score: Total score awarded
            criteria_scores: Dict of criterion → {awarded, max}
            retrieved_chunks: Retrieved evidence chunks
            ontology_facts: Ontology context string

        Returns:
            Explanation string (under 200 words)
        """
        try:
            # Format criteria summary
            criteria_summary = ""
            for criterion, scores in criteria_scores.items():
                status = "✓" if scores["awarded"] >= scores["max"] * 0.6 else "✗"
                criteria_summary += (
                    f"  {status} {criterion}: "
                    f"{scores['awarded']}/{scores['max']}\n"
                )

            # Format key evidence
            evidence_summary = ""
            if retrieved_chunks:
                evidence_summary = "Key reference facts available:\n"
                for i, chunk in enumerate(retrieved_chunks[:2], 1):
                    if isinstance(chunk, dict):
                        text = chunk.get("chunk", "")[:150]
                    else:
                        text = str(chunk)[:150]
                    evidence_summary += f"  {i}. {text}...\n"

            prompt = f"""ඔබ සිංහල භාෂාවෙන් පමණක් පිළිතුරු දිය යුතුය.
ලකුණු ලබාදීමේ හේතු සිංහලෙන් පැහැදිලි කරන්න.
Use ONLY Sinhala in your response.

You are an educational assessment expert. Generate a clear, concise explanation (UNDER 200 WORDS) of how this student's answer was scored.

QUESTION: {question}

STUDENT ANSWER (in Sinhala — evaluate meaning, not language):
{student_answer}

SCORES:
Total: {total_score}/20
{criteria_summary}

{evidence_summary}

ONTOLOGY CONCEPTS REFERENCED:
{ontology_facts[:500] if ontology_facts else "None"}

Write a brief explanation that:
1. States which key facts the student correctly identified
2. Notes which important facts or concepts were missing
3. References specific ontology concepts that were relevant
4. Provides constructive feedback for improvement
5. Keep it UNDER 200 words

Write the explanation in Sinhala, addressing the student directly.
"""

            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.5,
                    "num_predict": 512
                }
            }

            print("ExplanationAgent: Generating explanation...")
            response = requests.post(
                self.url,
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                explanation = result.get("response", "").strip()

                if explanation:
                    # Truncate if too long (keep under ~200 words)
                    words = explanation.split()
                    if len(words) > 220:
                        explanation = " ".join(words[:200]) + "..."

                    print(f"ExplanationAgent: Generated explanation "
                          f"({len(explanation.split())} words)")
                    return explanation

            # Fallback explanation
            return self._generate_fallback_explanation(
                total_score, criteria_scores
            )

        except requests.exceptions.Timeout:
            print("ExplanationAgent: OLLAMA timed out")
            return self._generate_fallback_explanation(
                total_score, criteria_scores
            )
        except requests.exceptions.ConnectionError:
            print("ExplanationAgent: Cannot connect to OLLAMA")
            return self._generate_fallback_explanation(
                total_score, criteria_scores
            )
        except Exception as e:
            print(f"ExplanationAgent error: {e}")
            return self._generate_fallback_explanation(
                total_score, criteria_scores
            )

    def _generate_fallback_explanation(self, total_score, criteria_scores):
        """
        Generate a simple explanation when OLLAMA is unavailable.

        Args:
            total_score: Total score
            criteria_scores: Criterion scores dict

        Returns:
            Fallback explanation string
        """
        explanation = f"Your answer scored {total_score}/20. "

        strong_areas = []
        weak_areas = []

        for criterion, scores in criteria_scores.items():
            percentage = scores["awarded"] / scores["max"] if scores["max"] > 0 else 0
            if percentage >= 0.7:
                strong_areas.append(criterion)
            elif percentage < 0.5:
                weak_areas.append(criterion)

        if strong_areas:
            explanation += "You performed well on: " + ", ".join(strong_areas) + ". "

        if weak_areas:
            explanation += "Areas for improvement: " + ", ".join(weak_areas) + ". "

        if total_score >= 14:
            explanation += "Overall, this is a good answer showing solid understanding."
        elif total_score >= 10:
            explanation += "Your answer shows some understanding but could include more specific details and facts."
        else:
            explanation += "Consider reviewing the topic and including more specific historical facts, names, dates, and details in your answer."

        return explanation
