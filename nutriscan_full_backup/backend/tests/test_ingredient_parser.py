from __future__ import annotations

from app.infrastructure.parser.ingredient_parser import parse_ingredients

SPEC_TEXT = """Ingredients:
Sugar, Wheat Flour (Maida), Palm Oil,
Salt, INS 322, INS 500(ii),
Artificial Flavour (Vanilla)"""


class TestSpecExample:
    def test_matches_spec_output_exactly(self) -> None:
        result = parse_ingredients(SPEC_TEXT)
        assert result.ingredients == [
            "Sugar", "Wheat Flour", "Palm Oil", "Salt", "INS 322",
            "INS 500(ii)", "Artificial Flavour", "Vanilla",
        ]
        assert result.count == 8


class TestSplitting:
    def test_comma_separated(self) -> None:
        result = parse_ingredients("Sugar, Salt, Water")
        assert result.ingredients == ["Sugar", "Salt", "Water"]

    def test_semicolon_separated(self) -> None:
        result = parse_ingredients("Sugar; Salt; Water")
        assert result.ingredients == ["Sugar", "Salt", "Water"]

    def test_bullet_separated(self) -> None:
        result = parse_ingredients("• Sugar\n• Salt\n• Water")
        assert result.ingredients == ["Sugar", "Salt", "Water"]

    def test_line_breaks(self) -> None:
        result = parse_ingredients("Sugar\nSalt\nWater")
        assert result.ingredients == ["Sugar", "Salt", "Water"]

    def test_multiple_spaces_collapsed(self) -> None:
        result = parse_ingredients("Sugar,    Salt   ,Water")
        assert result.ingredients == ["Sugar", "Salt", "Water"]


class TestDuplicates:
    def test_duplicate_ingredients_removed(self) -> None:
        result = parse_ingredients("Sugar, Salt, Sugar, SALT")
        assert result.ingredients == ["Sugar", "Salt"]
        assert result.count == 2


class TestOcrNoise:
    def test_garbage_tokens_dropped(self) -> None:
        result = parse_ingredients("Sugar, ---, Salt, ***, Water")
        assert result.ingredients == ["Sugar", "Salt", "Water"]

    def test_empty_values_dropped(self) -> None:
        result = parse_ingredients("Sugar,, Salt,   ,Water")
        assert result.ingredients == ["Sugar", "Salt", "Water"]


class TestStandardization:
    def test_maida_standalone(self) -> None:
        result = parse_ingredients("Maida")
        assert result.ingredients == ["Refined Wheat Flour"]

    def test_vit_c(self) -> None:
        result = parse_ingredients("Vit C")
        assert result.ingredients == ["Vitamin C"]

    def test_ins_hyphen_normalized(self) -> None:
        result = parse_ingredients("INS-322")
        assert result.ingredients == ["INS 322"]


class TestEmptyInput:
    def test_empty_string(self) -> None:
        result = parse_ingredients("")
        assert result.ingredients == []
        assert result.count == 0

    def test_whitespace_only(self) -> None:
        result = parse_ingredients("   \n  ")
        assert result.ingredients == []
        assert result.count == 0
