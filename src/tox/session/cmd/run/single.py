"""
Defines how to run a single tox environment.
"""
from typing import List, Tuple, cast

from tox.config.types import Command
from tox.execute.api import Outcome
from tox.tox_env.api import ToxEnv
from tox.tox_env.errors import Recreate
from tox.tox_env.runner import RunToxEnv


def run_one(tox_env: RunToxEnv, recreate: bool, no_test: bool) -> Tuple[int, List[Outcome]]:
    if recreate:
        tox_env.clean(package_env=recreate)
    try:
        tox_env.setup()
    except Recreate:
        tox_env.clean(package_env=False)  # restart creation once, no package please
        tox_env.setup()

    code, outcomes = run_commands(tox_env, no_test)
    return code, outcomes


def run_commands(tox_env: ToxEnv, no_test: bool) -> Tuple[int, List[Outcome]]:
    status = Outcome.OK  # assume all good
    outcomes: List[Outcome] = []
    if no_test is False:
        keys = ("commands_pre", "commands", "commands_post")
        for key in keys:
            for at, cmd in enumerate(cast(List[Command], tox_env.conf[key])):
                current_outcome = tox_env.execute(
                    cmd.args,
                    cwd=tox_env.conf["change_dir"],
                    allow_stdin=True,
                    show_on_standard=True,
                    run_id=f"{key}[{at}]",
                )
                outcomes.append(current_outcome)
                if cmd.ignore_exit_code:
                    continue
                try:
                    current_outcome.assert_success(tox_env.logger)
                except SystemExit as exception:
                    return exception.code, outcomes
    return status, outcomes


__all__ = ("run_one",)
