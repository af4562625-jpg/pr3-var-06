"""Каждый BDD-сценарий выполняется на пустом независимом каталоге."""
from implementation import LibraryManager


def before_scenario(context, scenario):
    context.library = LibraryManager()
    context.error = None
    context.result = None
