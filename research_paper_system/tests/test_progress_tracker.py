import pytest
from src.services.progress_tracker import ProgressTracker


def test_progress_tracker_init():
    tracker = ProgressTracker()
    assert tracker.get_progress()["percentage"] == 0


def test_progress_start_step():
    tracker = ProgressTracker()
    tracker.start_step("arxiv_search")
    progress = tracker.get_progress()
    found = False
    for step in progress["steps"]:
        if step["name"] == "arxiv_search":
            assert step["status"] == "running"
            found = True
    assert found


def test_progress_complete_step():
    tracker = ProgressTracker()
    tracker.start_step("arxiv_search")
    tracker.complete_step("arxiv_search", "Found 20 papers")
    progress = tracker.get_progress()
    for step in progress["steps"]:
        if step["name"] == "arxiv_search":
            assert step["status"] == "completed"
            assert step["message"] == "Found 20 papers"


def test_progress_callback():
    tracker = ProgressTracker()
    callback_data = {}

    def my_callback(data):
        callback_data.update(data)

    tracker.add_callback(my_callback)
    tracker.start_step("arxiv_search")
    assert "steps" in callback_data
