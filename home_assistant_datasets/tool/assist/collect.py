"""Collect data from the assistant tools for a conversation agent.

See docs/eval.md for a user guide.

```
usage: home-assistant-datasets assist collect [-h] [--dry_run] --models MODELS [--dataset DATASET] --model_output_dir MODEL_OUTPUT_DIR
                                              [--categories CATEGORIES] [--collect-only] [--disable-random] [-s] [--verbose | --verbosity N]
                                              [--count N]
                                              [test_path]

positional arguments:
  test_path             A pytest pass through flag optional path for collection actions to perform or full test node.

options:
  -h, --help            show this help message and exit
  --dry_run             Only validate the fixtures without actually collecting data.
  --models MODELS       Specifies models to load from the models.yaml file
  --dataset DATASET     Specifies the test dataset to load for evaluation
  --model_output_dir MODEL_OUTPUT_DIR
                        Specifies the directory where output data from the model is stored.
  --categories CATEGORIES
                        Limit evaluation tasks to a specific category
  --collect-only        A pytest pass through flag to only collect the list of tests without actually running them.
  --disable-random      Disable randomized ordering of tests, useful for testing prompt caching.
  -s                    A pytest pass through flag to show streaming test output.
  --verbose, -v         A pytest pass through flag to increase verbosity.
  --verbosity N         A pytest pass through flag to set verbosity. Default is 0
  --count N             The number of collections to perform.
```
"""

import argparse
import logging


from home_assistant_datasets.plugins.fixtures import run_pytest_main

__all__ = []

_LOGGER = logging.getLogger(__name__)

DEFAULT_DATASET = "datasets/assist"


def create_arguments(args: argparse.ArgumentParser) -> None:
    """Get parsed passed in arguments."""
    args.add_argument(
        "--dry_run",
        action="store_true",
        help="Only validate the fixtures without actually collecting data.",
    )
    args.add_argument(
        "--models",
        type=str,
        help="Specifies models to load from the models.yaml file",
        required=True,
    )
    args.add_argument(
        "--dataset",
        type=str,
        help="Specifies the test dataset to load for evaluation",
        default=DEFAULT_DATASET,
    )
    args.add_argument(
        "--model_output_dir",
        type=str,
        help="Specifies the directory where output data from the model is stored.",
        required=True,
    )
    args.add_argument(
        "--categories",
        type=str,
        help="Limit evaluation tasks to a specific category",
    )
    args.add_argument(
        "--disable-random",
        action="store_true",
        help="Disable randomized ordering of tests, useful for testing prompt caching.",
    )
    args.add_argument(
        "--count",
        action="store",
        type=int,
        metavar="N",
        dest="count",
        help="The number of collections to perform.",
    )

    # Flags consistent with pytest for pass through
    args.add_argument(
        "test_path",
        help="A pytest pass through flag optional path for collection actions to perform or full test node.",
        type=str,
        default="home_assistant_datasets/tool/assist/collect_tests/test_collect.py",
        nargs="?",
    )
    verbosity_group = args.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        "--verbose",
        "-v",
        action="count",
        dest="verbosity",
        help="A pytest pass through flag to increase verbosity.",
    )
    verbosity_group.add_argument(
        "--verbosity",
        action="store",
        type=int,
        metavar="N",
        dest="verbosity",
        help="A pytest pass through flag to set verbosity. Default is 0",
    )
    args.add_argument(
        "-s",
        action="store_true",
        help="A pytest pass through flag to show streaming test output.",
    )
    args.add_argument(
        "--collect-only",
        action="store_true",
        help="A pytest pass through flag to only collect the list of tests without actually running them.",
    )
    args.set_defaults(verbosity=0)


def run(args: argparse.Namespace) -> int:
    verbosity = args.verbosity

    pytest_args = [
        # See flags defined in conftest.py
        f"--models={args.models or ''}",
        f"--dataset={args.dataset or ''}",
        f"--model_output_dir={args.model_output_dir or ''}",
        f"--categories={args.categories or ''}",
    ]
    if args.verbosity:
        pytest_args.extend(
            [
                "--verbosity",
                str(verbosity),
            ]
        )
    if not args.disable_random:
        pytest_args.append("--random-order-seed=42")
    if args.count:
        pytest_args.append(f"--count={args.count}")
    if args.test_path:
        pytest_args.append(args.test_path)
    if args.collect_only:
        pytest_args.append("--collect-only")
    if args.s:
        pytest_args.append("-s")
    return run_pytest_main(
        pytest_args, "home_assistant_datasets/tool/assist/collect_tests"
    )
