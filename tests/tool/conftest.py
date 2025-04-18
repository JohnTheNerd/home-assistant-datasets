"""Pytest fixtures for exercising the eval report."""

import pathlib
from dataclasses import dataclass
from typing import Any

import pytest

from home_assistant_datasets.tool.data_model import EvalMetric
from home_assistant_datasets.tool.eval_report import EvalReport, exception_repr


@dataclass(kw_only=True)
class FakeEvalMetric(EvalMetric):
    """Test EvalMetric for the eval report."""

    some_value: float | None = None
    details: str | None = None


eval_metric_stash_key = pytest.StashKey[FakeEvalMetric]()
"""Stash key for the eval metric."""


def pytest_addoption(parser: Any) -> None:
    """Pytest arguments passed from the `eval` action to the test."""
    parser.addoption("--model_output_dir", default=None)


def pytest_configure(config: Any) -> None:
    """Register a plugin that generates the results of the eval."""
    model_output_dir = config.getoption("model_output_dir")
    if model_output_dir is not None:
        report = EvalReport(pathlib.Path(model_output_dir), FakeEvalMetric)
        config.pluginmanager.register(report)


def pytest_generate_tests(metafunc: Any) -> None:
    """Generate test parameters for the evaluation from flags.

    This will add a mode that causes test_eval_report to have a failing test
    case that will make the report more useful.
    """
    model_output_dir = metafunc.config.getoption("--model_output_dir")
    values = [True]
    if model_output_dir is not None:
        values.append(False)
    metafunc.parametrize("success", values)


@pytest.fixture(autouse=True)
def consume_success_fixture(success: Any) -> None:
    """Consume the success value.

    This is used to consume this parameter for other tests besides `test_eval_report`
    """
    pass


@pytest.fixture(name="eval_metric", autouse=True)
def eval_metric_fixture(pytestconfig: Any) -> FakeEvalMetric:
    """Add details to the eval reports."""
    eval_metric = FakeEvalMetric(uuid="1234", task_id="task-id", model_id="model_id")
    pytestconfig.stash[eval_metric_stash_key] = eval_metric
    yield eval_metric
    del pytestconfig.stash[eval_metric_stash_key]


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Any, call: Any):
    """Attach additional fixture data to the report."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        report.eval_metric = item.config.stash.get(eval_metric_stash_key, None)
        if report.failed:
            report.eval_metric.details = exception_repr(report.longreprtext)
