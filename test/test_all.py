from pathlib import Path
import typy.engine
import pytest
import ast

THIS_FOLDER = Path(__file__).parent
TEST_FILES = THIS_FOLDER / 'files'

engines = typy.engine.modules

@pytest.mark.parametrize('engine', engines)
class TestRevealType:
    def test_reveal_type_var(self, engine: typy.engine.base.EngineModule):
        var = TEST_FILES / 'reveal_type_var.py'
        result = engine.report(files=[var])
        
        issues = result.issues
        reveal_types = [engine.parse_reveal_type(issue.description) for issue in issues]
        reveal_types = [*filter(bool, reveal_types)]
        assert len(reveal_types) == 1
        
        reveal_type = reveal_types[0]
        
        assert reveal_type.typ in (
            'Literal[1]',
            'int',
            'builtins.int',
        )

        if reveal_type.sym:
            assert reveal_type.sym in (
                'x',
            )

    def test_reveal_type_walrus(self, engine: typy.engine.base.EngineModule):
        walrus = TEST_FILES / 'reveal_type_walrus.py'
        result = engine.report(files=[walrus])
        
        issues = result.issues
        reveal_types = [engine.parse_reveal_type(issue.description) for issue in issues]
        reveal_types = [*filter(bool, reveal_types)]
        assert len(reveal_types) == 1

        reveal_type = reveal_types[0]

        assert reveal_type.typ in (
            'Literal[1]',
            'Literal[1]?',
            'int',
            'builtins.int',
        )

        if reveal_type.sym:
            assert reveal_type.sym in (
                'x := 1',
            )

    def test_reveal_type_constant(self, engine: typy.engine.base.EngineModule):
        constant = TEST_FILES / 'reveal_type_constant.py'
        result = engine.report(files=[constant])

        issues = result.issues
        reveal_types = [engine.parse_reveal_type(issue.description) for issue in issues]

        reveal_types = [*filter(bool, reveal_types)]
        assert len(reveal_types) == 1

        reveal_type = reveal_types[0]

        assert reveal_type.typ in (
            'Literal[1]',
            'Literal[1]?',
            'int',
            'builtins.int',
        )

        if reveal_type.sym:
            assert reveal_type.sym in (
                '1',
            )

    def test_reveal_type_func(self, engine: typy.engine.base.EngineModule):
        func = TEST_FILES / 'reveal_type_func.py'

        result = engine.report(files=[func])

        issues = result.issues
        reveal_types = [engine.parse_reveal_type(issue.description) for issue in issues]
        reveal_types = [*filter(bool, reveal_types)]
        
        assert len(reveal_types) == 1

        reveal_type = reveal_types[0]

        assert reveal_type.typ in (
            'def foo(x: int) -> str',
            '(x: int) -> str',
            'def (x: builtins.int) -> builtins.str',
        )

        if reveal_type.sym:
            assert reveal_type.sym in (
                'foo',
            )