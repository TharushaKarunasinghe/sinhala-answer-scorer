from owlready2 import get_ontology, default_world
import os

ONTO_PATH = "ontology/colonial_ontology.owl"

# Sinhala keyword → ontology individual ID mapping
KEYWORD_MAP = {
    # Colonial Powers
    "පෘතුගීසි": "Portuguese",
    "පෘතුගීසීන්": "Portuguese",
    "ලන්දේසි": "Dutch",
    "ලන්දේසීන්": "Dutch",
    "බ්‍රිතාන්‍ය": "British",
    "බ්‍රිතාන්‍යයන්": "British",

    # Battles
    "මුල්ලේරියා": "BattleOfMulleriyawa",
    "දන්තුරේ": "BattleOfDanture",
    "රන්දෙනිවෙල": "BattleOfRandeniwela",
    "ඌව": "UvaWellassaRebellion",
    "වෙල්ලස්ස": "UvaWellassaRebellion",
    "මාතලේ": "MataleRebellion",

    # Treaties
    "වෙස්ටර්වෝල්ඩ්": "TreatyOfWesterwolt1638",
    "හඟුරන්කෙත": "TreatyOfHanguranketa1766",
    "උඩරට ගිවිසුම": "KandyanConvention1815",
    "1815": "KandyanConvention1815",

    # Persons
    "ධර්මපාල": "DharmapalaDonJohn",
    "රාජසිංහ": "Rajasinha1",
    "විමලධර්මසූරිය": "Vimaladharmasuriya1",
    "සෙනරත්": "Senarat",
    "කැප්පෙටිපොල": "Keppetipola",
    "පුරන් අප්පු": "PuranAppu",
    "ජේම්ස් ටේලර්": "JamesTaylor",
    "සේනානායක": "DSSenanayake",
    "අනගාරික": "AnagarikaDharmapala",

    # Reforms
    "කෝල්බෲක්": "ColbrookeCameronReforms",
    "කෝල්බ්‍රෝක්": "ColbrookeCameronReforms",
    "ඩොනමෝර්": "DonoughmorConstitution",
    "සෝල්බරි": "SoulburyConstitution",
    "තොම්බු": "TomboSystem",

    # Economic
    "කුළුබඩු": "SpiceMonopoly",
    "VOC": "VOCTradeSystem",
    "වතු": "PlantationEconomy",
    "කෝෆි": "CoffeePlantation",
    "කෝපි": "CoffeePlantation",
    "තේ": "TeaPlantation",
    "මුඩුබිම්": "CrownLandsOrdinance",

    # Religious
    "කතෝලික": "CatholicMissions",
    "ප්‍රොතෙස්තන්ත්": "ProtestantMissions",
    "බෞද්ධ පුනරුදය": "BuddhistRevival",

    # Legal
    "රෝම-ලන්දේසි": "RomanDutchLaw",
    "රෝමානු-ලන්දේසි": "RomanDutchLaw",

    # Infrastructure
    "ගාල්ල": "GalleDutchFort",
    "දුම්රිය": "RailwaySystem",
    "ඕලන්ද ඇළ": "DutchCanal",

    # Social
    "බර්ගර්": "BurgherCommunity",
    "ඉන්දියානු": "IndianTamilLabourers",
    "ශ්‍රමිකයන්": "IndianTamilLabourers",
}


class OntologyAgent:
    def __init__(self):
        onto_abs = os.path.abspath(ONTO_PATH)
        self.onto = get_ontology(onto_abs).load()
        self.ns = self.onto.get_namespace("http://colonial-sl.org/onto#")

    def check_concepts(self, student_answer: str) -> list[dict]:
        """
        Scan student answer for known ontology concepts.
        Returns list of matched concepts with their era and class type.
        """
        found = []
        seen_ids = set()

        for keyword, individual_id in KEYWORD_MAP.items():
            if keyword in student_answer:
                if individual_id in seen_ids:
                    continue
                individual = self.ns[individual_id]
                if individual is None:
                    continue

                # Get era label
                era_links = []
                if hasattr(individual, "belongsToEra"):
                    for era in individual.belongsToEra:
                        era_links.append(str(era.label.first() or era.name))
                if hasattr(individual, "hasEra"):
                    for era in individual.hasEra:
                        era_links.append(str(era.label.first() or era.name))

                # Get class type
                types = [
                    str(t.label.first() or t.name)
                    for t in individual.is_a
                    if hasattr(t, "label")
                ]

                found.append({
                    "keyword":    keyword,
                    "concept_id": individual_id,
                    "label":      str(individual.label.first() or individual_id),
                    "type":       types[0] if types else "නොදන්නා",
                    "eras":       era_links,
                })
                seen_ids.add(individual_id)

        return found

    def format_for_prompt(self, concepts: list[dict]) -> str:
        """Format matched concepts into a readable string for the LLM prompt."""
        if not concepts:
            return "ශිෂ්‍ය පිළිතුරේ කිසිදු ඔන්ටොලොජි සංකල්පයක් හඳුනා නොගැනිණි."

        lines = []
        for c in concepts:
            era_str = ", ".join(c["eras"]) if c["eras"] else "යුගය නොදනී"
            lines.append(
                f"• {c['label']} [{c['type']}] — යුගය: {era_str}"
            )
        return "\n".join(lines)

    def detect_era_mismatches(self, concepts: list[dict], question_era: str) -> list[str]:
        """
        Flag concepts that belong to a different era than the question.
        Used to detect when a student confuses eras.
        """
        era_map = {
            "portuguese": ["පෘතුගීසි", "1505", "1658"],
            "dutch":      ["ලන්දේසි", "1658", "1796"],
            "british":    ["බ්‍රිතාන්‍ය", "1796", "1948"],
        }
        warnings = []
        if question_era not in era_map:
            return warnings

        expected_keywords = era_map[question_era]
        for c in concepts:
            era_match = any(
                any(kw in era for era in c["eras"])
                for kw in expected_keywords
            )
            if c["eras"] and not era_match:
                warnings.append(
                    f"'{c['label']}' {c['eras']} යුගයට අයත් නමුත් "
                    f"ප්‍රශ්නය '{question_era}' යුගය ගැන ය."
                )
        return warnings