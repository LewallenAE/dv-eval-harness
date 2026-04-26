from __future__ import annotations

from typing import Protocol
from pydantic import BaseModel, Field

from app.schemas.hardware import DVCase
from app.tools import run_mock_simulator


class SimulationResult(BaseModel):
    log: str
    coverage: float
    pass_rate: float
    simulator_name: str
    raw_artifacts: dict[str, str] = Field(default_factory=dict)


class SimulatorAdapter(Protocol):
    """Common interface for mock and future commercial simulator integrations."""

    def run(self, case: DVCase, rtl: str) -> SimulationResult:
        """Run a case against the provided RTL and return normalized results."""


class MockSimulatorAdapter:
    """Deterministic adapter used for demo and interview environments.

    A future `QuestaSimulatorAdapter` or `VCSSimulatorAdapter` would implement the
    same `run(case, rtl) -> SimulationResult` contract while invoking external EDA
    tooling and collecting artifacts like logs, waveforms, and coverage reports.
    """

    simulator_name = "mock"

    def run(self, case: DVCase, rtl: str) -> SimulationResult:
        result = run_mock_simulator(case, rtl)
        return SimulationResult(
            log=result["log"],
            coverage=result["coverage"],
            pass_rate=result["pass_rate"],
            simulator_name=self.simulator_name,
            raw_artifacts={},
        )


def get_simulator_adapter(name: str = "mock") -> SimulatorAdapter:
    normalized_name = name.lower().strip()

    if normalized_name == "mock":
        return MockSimulatorAdapter()

    raise ValueError(f"Unsupported simulator adapter: {name}")
