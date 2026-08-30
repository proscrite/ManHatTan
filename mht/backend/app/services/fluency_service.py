from typing import Dict, Tuple

CEFR_INT_TO_LABEL: Dict[int, str] = {
    1: "A1",
    2: "A2",
    3: "B1",
    4: "B2",
    5: "C1",
    6: "C2",
}

CEFR_GUARDRAILS: Dict[int, str] = {
    1: "Target Level: A1. Use only present tense, active voice, and simple SVO structures. Avoid complex subordinate clauses. Strictly NO passive voice.",
    2: "Target Level: A2. Use simple present and basic past tenses. Active voice only. Avoid complex subordinate clauses. Strictly NO passive voice.",
    3: "Target Level: B1. Standard conversational grammar. Use common idioms and basic future/conditional forms. Keep clauses clear. Strictly NO passive voice.",
    4: "Target Level: B2. Advanced conversational grammar. Passive voice and subordinate clauses are permitted.",
    5: "Target Level: C1. Complex literary/academic structures, nuanced idioms, and high syntactic variety permitted.",
    6: "Target Level: C2. Full native mastery and complex stylistic expressions permitted."
}

def resolve_course_cefr(cefr_level: int) -> Tuple[str, str]:
    """
    Converts discrete DB integer level into (CEFR_label, prompt_guardrails).
    """
    label = CEFR_INT_TO_LABEL.get(cefr_level, "A1")
    guardrail = CEFR_GUARDRAILS.get(cefr_level, CEFR_GUARDRAILS[1])
    return label, guardrail