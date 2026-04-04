import pytest
from src.services.progress_tracker import ProgressTracker


def test_progress_tracker_init():
    tracker = ProgressTracker()
    tracker.reset()
    assert tracker.get_progress()["percent"] == 0


def test_progress_start_step():
    tracker = ProgressTracker()
    tracker.reset()
    tracker.on_step_start("Searching ArXiv")
    progress = tracker.get_progress()
    found = False
    for step in progress["steps"]:
        if step["name"] == "Searching ArXiv":
            assert step["status"] == "running"
            found = True
    assert found


def test_progress_complete_step():
    tracker = ProgressTracker()
    tracker.reset()
    tracker.on_step_start("Searching ArXiv")
    tracker.on_step_complete("Searching ArXiv", "Found 20 papers")
    progress = tracker.get_progress()
    for step in progress["steps"]:
        if step["name"] == "Searching ArXiv":
            assert step["status"] == "completed"
            assert step["message"] == "Found 20 papers"


def test_progress_callback():
    tracker = ProgressTracker()
    tracker.reset()
    callback_data = {}

    def my_callback(data):
        callback_data.update(data)

    tracker.add_callback(my_callback)
    tracker.on_step_start("Searching ArXiv")
    assert "steps" in callback_data
