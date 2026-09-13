"""
Diego Villalba 12-09-26

Shared representation for finite constraint satisfaction problems.
"""

from collections.abc import Callable, Hashable, Iterable, Mapping
from typing import Any


class CSP:
    def __init__(
        self,
        variables: tuple,
        domains: dict,
        is_consistent: Callable,
    ) -> None:
        self.variables = variables
        self.domains = domains
        self.is_consistent = is_consistent

    def describe(self):
        print("CSP")
