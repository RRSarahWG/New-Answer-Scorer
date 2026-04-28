# ============================================================================
# SCORING AGENT — Scores student answers using OLLAMA (Tharusha_Dilhara_Jayadeera/singemma:latest)
# Uses raw HTTP requests to localhost:11434
# ============================================================================

import re
import requests
import json


# OLLAMA configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "Tharusha_Dilhara_Jayadeera/singemma:latest"
OLLAMA_TIMEOUT = 180  # FIX 3: Increased from 120 to 180 for criterion-level evaluation


class ScoringAgent:
    """
    Agent responsible for scoring student answers using the OLLAMA LLM.
    Sends a structured prompt with question, marking guide, retrieved
    knowledge, and ontology context to score each criterion separately.
    """

    def __init__(self):
        """Initialize the ScoringAgent."""
        self.url = OLLAMA_URL
        self.model = OLLAMA_MODEL
        self.timeout = OLLAMA_TIMEOUT

    def _build_prompt(self, question, marking_guide, student_answer,
                      retrieved_chunks, ontology_facts):
        """
        Build the scoring prompt for the LLM.

        Args:
            question: The question text
            marking_guide: List of dicts with criteria and marks
            student_answer: Student's answer (may be in Sinhala)
            retrieved_chunks: List of relevant knowledge chunks
            ontology_facts: String of relevant ontology concepts

        Returns:
            Formatted prompt string
        """
        # Format marking guide text
        marking_guide_text = ""
        for i, c in enumerate(marking_guide, 1):
            marking_guide_text += (
                f"\nCriterion {i}: {c['criterion']}\n"
                f"  Maximum Marks: {c['marks']}\n"
                f"  Details: {c['details']}\n"
            )

        # Format retrieved knowledge
        retrieved_context = ""
        if retrieved_chunks:
            for i, chunk in enumerate(retrieved_chunks, 1):
                if isinstance(chunk, dict):
                    retrieved_context += f"\n--- Evidence {i} (relevance: {chunk.get('score', 'N/A'):.3f}) ---\n"
                    retrieved_context += chunk.get("chunk", "") + "\n"
                else:
                    retrieved_context += f"\n--- Evidence {i} ---\n{chunk}\n"

        if not retrieved_context:
            retrieved_context = "No specific evidence retrieved."

        if not ontology_facts:
            ontology_facts = "No specific ontology concepts available."

        # FIX 1: Improved structured prompt
        prompt = f"""ඔබ සිංහල භාෂාවෙන් පමණක් පිළිතුරු දිය යුතුය.
You are an expert examiner for Ancient Sri Lankan History.
The student has answered in Sinhala. Evaluate based on meaning and content.

QUESTION: {question}

MARKING GUIDE:
{marking_guide_text}

STUDENT ANSWER: {student_answer}

RETRIEVED KNOWLEDGE: {retrieved_context}

ONTOLOGY FACTS: {ontology_facts}

You MUST score each criterion separately.
For EACH criterion, respond in EXACTLY this format:
CRITERION: [criterion name]
SCORE: [number awarded] / [maximum marks]
REASON: [brief reason in Sinhala]

After all criteria, write:
TOTAL: [sum] / 20

Be strict but fair. Give 0 if not mentioned at all.
Give full marks only if clearly and correctly explained.
Give partial marks for partially correct answers.
"""
        return prompt

    def _parse_scores(self, response_text, marking_guide, student_answer=""):
        """
        Parse the LLM response to extract scores per criterion.
        Uses multiple fallback strategies if parsing fails.

        Args:
            response_text: Raw LLM response
            marking_guide: Marking criteria list
            student_answer: Student's answer for heuristic fallback

        Returns:
            Dict with criteria_scores and total_score
        """
        criteria_scores = {}
        total_score = 0

        # FIX 2: Try to find TOTAL first
        total_match = re.search(
            r'TOTAL[:\s]+(\d+(?:\.\d+)?)\s*/\s*20',
            response_text, re.IGNORECASE
        )

        # FIX 2: Parse individual criterion scores using SCORE: X/Y format
        criterion_pattern = re.findall(
            r'SCORE[:\s]+(\d+(?:\.\d+)?)\s*/\s*(\d+)',
            response_text, re.IGNORECASE
        )

        if criterion_pattern:
            for i, (awarded, maximum) in enumerate(criterion_pattern):
                if i < len(marking_guide):
                    criterion_name = marking_guide[i].get('criterion',
                                     f'නිර්ණායකය {i+1}')
                    max_marks = marking_guide[i].get('marks', int(float(maximum)))
                    awarded_marks = min(float(awarded), max_marks)
                    awarded_marks = max(0, awarded_marks)
                    criteria_scores[criterion_name] = {
                        'awarded': round(awarded_marks, 1),
                        'max': max_marks
                    }
                    total_score += awarded_marks

        # Also try old CRITERION_N: X/Y format as secondary fallback
        if not criteria_scores:
            score_patterns = [
                r'CRITERION_(\d+)\s*:\s*(\d+(?:\.\d+)?)\s*/\s*(\d+)',
                r'Criterion\s*(\d+)\s*:\s*(\d+(?:\.\d+)?)\s*/\s*(\d+)',
            ]
            found_scores = {}
            for pattern in score_patterns:
                matches = re.findall(pattern, response_text, re.IGNORECASE)
                for match in matches:
                    crit_num = int(match[0])
                    awarded = float(match[1])
                    max_marks = float(match[2])
                    found_scores[crit_num] = (awarded, max_marks)

            if found_scores:
                for i, c in enumerate(marking_guide, 1):
                    criterion_name = c["criterion"]
                    max_marks = c["marks"]
                    if i in found_scores:
                        awarded = min(found_scores[i][0], max_marks)
                        awarded = max(0, awarded)
                        criteria_scores[criterion_name] = {
                            "awarded": round(awarded, 1),
                            "max": max_marks
                        }
                        total_score += awarded

        # Also try generic X/Y patterns (any number/number near text)
        if not criteria_scores:
            generic_scores = re.findall(
                r'(\d+(?:\.\d+)?)\s*/\s*(\d+)',
                response_text
            )
            # Filter: keep only scores where max matches a known criterion max
            known_maxes = [c['marks'] for c in marking_guide]
            matched = []
            for awarded, maximum in generic_scores:
                max_val = int(float(maximum))
                if max_val in known_maxes and max_val != 20:  # Skip TOTAL line
                    matched.append((float(awarded), max_val))

            if len(matched) >= len(marking_guide):
                # We found enough scores
                used_indices = set()
                for awarded, max_val in matched:
                    # Find the criterion matching this max
                    for i, c in enumerate(marking_guide):
                        if i not in used_indices and c['marks'] == max_val:
                            criterion_name = c["criterion"]
                            awarded_marks = min(awarded, max_val)
                            awarded_marks = max(0, awarded_marks)
                            criteria_scores[criterion_name] = {
                                "awarded": round(awarded_marks, 1),
                                "max": max_val
                            }
                            total_score += awarded_marks
                            used_indices.add(i)
                            break

        # FIX 2: Use TOTAL line if found and criteria parsing failed
        if total_match and not criteria_scores:
            total_score = float(total_match.group(1))
            total_score = min(total_score, 20)
            total_score = max(0, total_score)
            # Distribute proportionally across criteria
            for criterion in marking_guide:
                name = criterion.get('criterion', 'නිර්ණායකය')
                max_m = criterion.get('marks', 4)
                proportion = max_m / 20
                criteria_scores[name] = {
                    'awarded': round(total_score * proportion, 1),
                    'max': max_m
                }

        # FIX 2: Last resort fallback — analyze answer length and keywords
        if not criteria_scores or total_score == 0:
            answer_length = len(student_answer.split()) if student_answer else 0
            if answer_length < 20:
                total_score = 3
            elif answer_length < 50:
                total_score = 8
            elif answer_length < 100:
                total_score = 13
            else:
                total_score = 16

            print(f"ScoringAgent: Using heuristic fallback (answer length={answer_length}, "
                  f"score={total_score})")

            criteria_scores = {}
            for criterion in marking_guide:
                name = criterion.get('criterion', 'නිර්ණායකය')
                max_m = criterion.get('marks', 4)
                proportion = max_m / 20
                criteria_scores[name] = {
                    'awarded': round(total_score * proportion, 1),
                    'max': max_m
                }

        # Use explicit TOTAL if found and reasonable
        if total_match:
            explicit_total = float(total_match.group(1))
            if 0 <= explicit_total <= 20:
                total_score = explicit_total

        # Cap total at 20
        total_score = min(round(total_score, 1), 20)
        total_score = max(0, total_score)

        return {
            'total_score': total_score,
            'criteria_scores': criteria_scores,
            'raw_response': response_text
        }

    def score(self, question, marking_guide, student_answer,
              retrieved_chunks, ontology_facts):
        """
        Score a student's answer using OLLAMA.

        Args:
            question: Question text
            marking_guide: List of dicts with criteria and marks
            student_answer: Student's answer text
            retrieved_chunks: Retrieved knowledge chunks
            ontology_facts: Ontology context string

        Returns:
            Dict with total_score, criteria_scores, raw_response
        """
        try:
            # Build the prompt
            prompt = self._build_prompt(
                question, marking_guide, student_answer,
                retrieved_chunks, ontology_facts
            )

            print(f"ScoringAgent: Sending prompt to {self.model} "
                  f"({len(prompt)} chars)...")

            # Call OLLAMA via raw HTTP request
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Low temperature for consistent scoring
                    "num_predict": 1024  # Limit response length
                }
            }

            response = requests.post(
                self.url,
                json=payload,
                timeout=self.timeout
            )

            if response.status_code != 200:
                print(f"ScoringAgent: OLLAMA returned status {response.status_code}")
                return self._fallback_score(marking_guide, student_answer,
                                            f"OLLAMA error: {response.status_code}")

            result = response.json()
            response_text = result.get("response", "")

            if not response_text:
                print("ScoringAgent: Empty response from OLLAMA")
                return self._fallback_score(marking_guide, student_answer,
                                            "Empty response from OLLAMA")

            print(f"ScoringAgent: Got response ({len(response_text)} chars)")
            print(f"ScoringAgent: Raw response preview: {response_text[:300]}...")

            # Parse scores from response
            scores = self._parse_scores(response_text, marking_guide, student_answer)
            return scores

        except requests.exceptions.Timeout:
            print("ScoringAgent: OLLAMA request timed out")
            return self._fallback_score(marking_guide, student_answer,
                                        "OLLAMA request timed out. "
                                        "CPU processing takes time.")
        except requests.exceptions.ConnectionError:
            print("ScoringAgent: Cannot connect to OLLAMA")
            return self._fallback_score(marking_guide, student_answer,
                                        "Cannot connect to OLLAMA. "
                                        "Make sure OLLAMA is running.")
        except Exception as e:
            print(f"ScoringAgent error: {e}")
            return self._fallback_score(marking_guide, student_answer, str(e))

    def _fallback_score(self, marking_guide, student_answer="", error_msg=""):
        """
        Generate fallback scores using answer-length heuristic when OLLAMA fails.

        Args:
            marking_guide: Marking criteria list
            student_answer: Student's answer for length analysis
            error_msg: Error message to include

        Returns:
            Score dict with heuristic-based values
        """
        # Use answer length heuristic instead of flat 50%
        answer_length = len(student_answer.split()) if student_answer else 0
        if answer_length < 20:
            total = 3
        elif answer_length < 50:
            total = 8
        elif answer_length < 100:
            total = 13
        else:
            total = 16

        criteria_scores = {}
        for c in marking_guide:
            proportion = c["marks"] / 20
            awarded = round(total * proportion, 1)
            criteria_scores[c["criterion"]] = {
                "awarded": awarded,
                "max": c["marks"]
            }

        return {
            "total_score": min(total, 20),
            "criteria_scores": criteria_scores,
            "raw_response": f"[FALLBACK SCORING] Error: {error_msg}\n"
                           f"Score based on answer length heuristic ({answer_length} words)."
        }

    @staticmethod
    def check_ollama_status():
        """
        Check if OLLAMA is reachable and the model is available.

        Returns:
            Tuple of (is_reachable: bool, status_message: str)
        """
        try:
            response = requests.get(
                "http://localhost:11434/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                if any(OLLAMA_MODEL in name for name in model_names):
                    return True, f"OLLAMA running, {OLLAMA_MODEL} available"
                else:
                    return True, (f"OLLAMA running but {OLLAMA_MODEL} not found. "
                                  f"Run: ollama pull {OLLAMA_MODEL}")
            return False, f"OLLAMA returned status {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "OLLAMA not running. Start with: ollama serve"
        except Exception as e:
            return False, f"Error checking OLLAMA: {e}"
