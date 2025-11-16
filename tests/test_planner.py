from orchestrator.planner import plan_from_instruction


def test_planner_basic():
    assert plan_from_instruction("please sanitize and analyze logs") == ["sanitizer", "log_analyst"]
    assert plan_from_instruction("generate report summary") == ["report_gen"]
    assert plan_from_instruction("sanitize, analyze and create a report") == ["sanitizer", "log_analyst", "report_gen"]