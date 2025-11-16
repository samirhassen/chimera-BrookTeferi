from typing import List


def plan_from_instruction(instruction: str) -> List[str]:
    """
    Simple rule-based planner that returns an ordered list of agent keys to invoke.
    Agent keys: 'sanitizer', 'log_analyst', 'report_gen'
    """
    i = (instruction or "").lower()
    flow = []


    if any(k in i for k in ("sanitize", "sanitiz", "mask", "redact")):
        flow.append("sanitizer")


    if any(k in i for k in ("log", "logs", "analyze", "analyse", "error", "warning")):
        flow.append("log_analyst")


    if any(k in i for k in ("report", "summary", "visual", "brief")):
        flow.append("report_gen")



    seen = set()
    ordered = []
    for a in flow:
        if a not in seen:
            ordered.append(a)
            seen.add(a)
    return ordered