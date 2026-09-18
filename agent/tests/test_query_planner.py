"""Tests for the deterministic query planner."""
import pytest

from agent.query_planner import DeterministicQueryPlanner
from agent.models import QueryType


@pytest.fixture
def planner():
    return DeterministicQueryPlanner()


class TestCurrentQueryPlanning:
    def test_currently_use(self, planner):
        plan = planner.plan("What do I currently use?")
        assert plan.query_type == QueryType.CURRENT

    def test_using_now(self, planner):
        plan = planner.plan("What am I using now?")
        assert plan.query_type == QueryType.CURRENT

    def test_current_keyword(self, planner):
        plan = planner.plan("What is my current editor?")
        assert plan.query_type == QueryType.CURRENT


class TestHistoricalQueryPlanning:
    def test_before(self, planner):
        plan = planner.plan("What did I use before?")
        assert plan.query_type == QueryType.HISTORICAL

    def test_previously(self, planner):
        plan = planner.plan("What did I previously use?")
        assert plan.query_type == QueryType.HISTORICAL

    def test_used_to(self, planner):
        plan = planner.plan("I used to prefer Java.")
        assert plan.query_type == QueryType.HISTORICAL


class TestTimelineQueryPlanning:
    def test_changed_over_time(self, planner):
        plan = planner.plan("How has this changed over time?")
        assert plan.query_type == QueryType.TIMELINE

    def test_show_history(self, planner):
        plan = planner.plan("Show me the history.")
        assert plan.query_type == QueryType.TIMELINE

    def test_history_of(self, planner):
        plan = planner.plan("What is the history of my tools?")
        assert plan.query_type == QueryType.TIMELINE


class TestGeneralQueryPlanning:
    def test_what_do_you_remember(self, planner):
        plan = planner.plan(
            "What do you remember about my projects?"
        )
        assert plan.query_type == QueryType.GENERAL

    def test_tell_me_about(self, planner):
        plan = planner.plan("Tell me about my preferences.")
        assert plan.query_type == QueryType.GENERAL

    def test_list_my(self, planner):
        plan = planner.plan("List my skills.")
        assert plan.query_type == QueryType.GENERAL


class TestAmbiguousQueryPlanning:
    def test_unclassifiable(self, planner):
        plan = planner.plan("Apples are red.")
        assert plan.query_type == QueryType.AMBIGUOUS


class TestFalsePositives:
    """Queries that should NOT accidentally match a category."""

    def test_bare_is_not_current(self, planner):
        """'The dish is great' contains 'is' but is not a
        CURRENT memory query."""
        plan = planner.plan("The dish is great.")
        assert plan.query_type != QueryType.CURRENT

    def test_presently_without_pattern(self, planner):
        plan = planner.plan("I presently have a cat.")
        assert plan.query_type == QueryType.AMBIGUOUS


class TestSubjectExtraction:
    def test_projects_extracted(self, planner):
        plan = planner.plan(
            "What do you remember about my projects?"
        )
        assert "projects" in plan.extracted_subjects
