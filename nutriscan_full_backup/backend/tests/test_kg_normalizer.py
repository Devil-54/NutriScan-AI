from __future__ import annotations

from app.infrastructure.knowledge_graph.normalizer import (
    normalize_e_to_ins,
    normalize_ins_spacing,
    normalize_name,
    resolve_canonical_name,
)


class TestNormalizeName:
    def test_collapses_whitespace(self) -> None:
        assert normalize_name("Wheat   Flour") == "Wheat Flour"

    def test_strips_edges(self) -> None:
        assert normalize_name("  Sugar  ") == "Sugar"

    def test_empty_input(self) -> None:
        assert normalize_name("") == ""


class TestInsNormalization:
    def test_hyphenated_ins_code(self) -> None:
        assert normalize_ins_spacing("INS-322") == "INS 322"

    def test_no_space_ins_code(self) -> None:
        assert normalize_ins_spacing("INS322") == "INS 322"

    def test_already_normalized(self) -> None:
        assert normalize_ins_spacing("INS 322") == "INS 322"


class TestENumberConversion:
    def test_e_number_to_ins(self) -> None:
        assert normalize_e_to_ins("E322") == "INS 322"

    def test_e_number_hyphen(self) -> None:
        assert normalize_e_to_ins("E-500") == "INS 500"


class TestResolveCanonicalName:
    def test_sucrose_maps_to_sugar(self) -> None:
        assert resolve_canonical_name("Sucrose") == "Sugar"

    def test_brown_sugar_maps_to_sugar(self) -> None:
        assert resolve_canonical_name("Brown Sugar") == "Sugar"

    def test_ins322_maps_to_lecithin(self) -> None:
        assert resolve_canonical_name("INS322") == "Lecithin"

    def test_unmapped_name_passthrough(self) -> None:
        assert resolve_canonical_name("Palm Oil") == "Palm Oil"
