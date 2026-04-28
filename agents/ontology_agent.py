# ============================================================================
# ONTOLOGY AGENT — Extracts ontology-based context for scoring
# ============================================================================

import sys
import os
import re

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ontology.anuradhapura_ontology import build_ontology, query_ontology, get_ontology_context


class OntologyAgent:
    """
    Agent responsible for extracting relevant ontology-based context
    by analyzing keywords in the student's answer and question topic.
    """

    def __init__(self):
        """Initialize the OntologyAgent by building the ontology graph."""
        try:
            self.graph = build_ontology()
            print(f"OntologyAgent: Ontology loaded with {len(self.graph)} triples.")
        except Exception as e:
            print(f"OntologyAgent: Error building ontology: {e}")
            self.graph = None

    def _extract_keywords(self, text):
        """
        Extract potential keywords from text for ontology lookup.
        Looks for proper nouns, place names, historical terms, and
        key concepts related to Anuradhapura history.

        Args:
            text: Input text (can be Sinhala or English)

        Returns:
            List of keyword strings
        """
        keywords = []

        # Known entity names to look for (bilingual matching)
        known_entities = {
            # Rulers
            "devanampiya": "devanampiya",
            "tissa": "tissa",
            "dutugamunu": "dutugamunu",
            "dutthagamani": "dutugamunu",
            "valagamba": "valagamba",
            "vattagamani": "valagamba",
            "mahasen": "mahasen",
            "mahasena": "mahasen",
            "elara": "elara",
            "dhatusena": "dhatusena",
            "parakramabahu": "parakramabahu",
            "kavantissa": "kavantissa",
            "pandukabhaya": "pandukabhaya",
            # Monks
            "mahinda": "mahinda",
            "sanghamitta": "sanghamitta",
            "buddhaghosa": "buddhaghosa",
            "faxian": "faxian",
            # Places and structures
            "ruwanwelisaya": "ruwanwelisaya",
            "jetavanaramaya": "jetavanaramaya",
            "abhayagiri": "abhayagiri",
            "thuparamaya": "thuparamaya",
            "mirisavetiya": "mirisavetiya",
            "anuradhapura": "anuradhapura",
            "mihintale": "mihintale",
            "polonnaruwa": "polonnaruwa",
            # Irrigation
            "tissa wewa": "tissa",
            "nuwara wewa": "nuwara",
            "minneriya": "minneriya",
            "kala wewa": "kala",
            "basawakkulama": "basawakkulama",
            "bisokotuwa": "bisokotuwa",
            "yoda ela": "kala",
            # Religion
            "buddhism": "buddhism",
            "theravada": "theravada",
            "tipitaka": "tipitaka",
            "bodhi": "bodhi",
            "mahavihara": "mahavihara",
            "sangha": "sangha",
            # Sinhala keywords (common terms students might use)
            "දුටුගැමුණු": "dutugamunu",
            "මහින්ද": "mahinda",
            "බුද්ධාගමය": "buddhism",
            "බෝධිය": "bodhi",
            "රුවන්වැලි": "ruwanwelisaya",
            "ජේතවන": "jetavanaramaya",
            "අභයගිරි": "abhayagiri",
            "ථූපාරාම": "thuparamaya",
            "අනුරාධපුර": "anuradhapura",
            "දේවානම්පියතිස්ස": "devanampiya",
            "සංඝමිත්තා": "sanghamitta",
            "මිහින්තලේ": "mihintale",
            "තිස්ස වැව": "tissa",
            "මින්නේරිය": "minneriya",
            "ත්‍රිපිටකය": "tipitaka",
            "වාරිමාර්ග": "irrigation",
            "වැව": "wewa",
            "ස්තූප": "stupa",
            "දාගැබ": "stupa",
            "සඳකඩ පහන": "moonstone",
            "මුරගල": "guardstone",
            "ලෝහප්‍රාසාද": "ruwanwelisaya",
            "කාවන්තිස්ස": "kavantissa",
            "එළාර": "elara",
            "වලගම්බා": "valagamba",
            "මහසෙන්": "mahasen",
            "කළා වැව": "kala",
            "බසවක්කුලම": "basawakkulama",
            "බිසෝකොටුව": "bisokotuwa",
        }

        text_lower = text.lower()

        for pattern, keyword in known_entities.items():
            if pattern.lower() in text_lower or pattern in text:
                if keyword not in keywords:
                    keywords.append(keyword)

        # Also extract capitalized words as potential proper nouns (English)
        capitalized = re.findall(r'\b[A-Z][a-z]{3,}\b', text)
        for word in capitalized:
            word_lower = word.lower()
            if word_lower not in keywords and word_lower not in [
                "the", "this", "that", "what", "when", "where", "which",
                "about", "from", "with", "have", "been", "were", "they",
                "their", "also", "some", "each", "more", "most", "such",
                "very", "much", "many", "other"
            ]:
                keywords.append(word_lower)

        return keywords

    def get_context(self, question_topic, student_answer):
        """
        Get ontology context relevant to the question and student answer.

        Args:
            question_topic: The topic string of the question
            student_answer: The student's answer text

        Returns:
            Formatted string of relevant ontology concepts and relationships
        """
        try:
            if self.graph is None:
                return "Ontology not available."

            # Get topic-based context
            topic_context = get_ontology_context(question_topic, self.graph)

            # Extract keywords from student answer and query ontology
            answer_keywords = self._extract_keywords(student_answer)
            answer_context = ""
            if answer_keywords:
                print(f"OntologyAgent: Extracted keywords from answer: {answer_keywords}")
                answer_context = query_ontology(answer_keywords, self.graph)

            # Combine both contexts, removing duplicates
            combined = topic_context
            if answer_context and answer_context != "No matching ontology concepts found.":
                # Add answer-specific concepts that aren't already in topic context
                for line in answer_context.split("\n\n"):
                    if line.strip() and line.strip() not in combined:
                        combined += "\n\n" + line.strip()

            if not combined or combined.strip() == "No matching ontology concepts found.":
                return "No specific ontology concepts matched."

            print(f"OntologyAgent: Returning ontology context ({len(combined)} chars)")
            return combined

        except Exception as e:
            print(f"OntologyAgent error: {e}")
            return f"Ontology query failed: {str(e)}"
