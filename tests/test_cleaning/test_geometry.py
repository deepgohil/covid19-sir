#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import pytest
from covsirphy import Geometry, Term


class TestGeometry(object):
    def test_layer(self):
        day0, day1 = pd.to_datetime("2022-01-01"), pd.to_datetime("2022-01-02")
        raw = pd.DataFrame(
            {
                Term.COUNTRY: [*["UK" for _ in range(4)], *["Japan" for _ in range(10)]],
                Term.PROVINCE: [
                    "England", "England", *[Term.NA for _ in range(4)],
                    *["Tokyo" for _ in range(4)], *["Kanagawa" for _ in range(4)]],
                Term.CITY: [
                    *[Term.NA for _ in range(8)], "Chiyoda", "Chiyoda", "Yokohama", "Yokohama", "Kawasaki", "Kawasaki"],
                Term.DATE: [day0, day1] * 7,
                Term.C: range(14),
            }
        )
        geometry = Geometry(layers=[Term.COUNTRY, Term.PROVINCE, Term.CITY])
        # When `geo=None` or `geo=(None,)`, returns country-level data.
        df = pd.DataFrame(
            {
                Term.COUNTRY: ["UK", "UK", "Japan", "Japan"],
                Term.PROVINCE: [Term.NA for _ in range(4)],
                Term.CITY: [Term.NA for _ in range(4)],
                Term.DATE: [day0, day1] * 2,
                Term.C: [2, 3, 4, 5],
            }
        )
        assert geometry.layer(data=raw, geo=None).equals(df)
        assert geometry.layer(data=raw, geo=(None,)).equals(df)
        # When `geo=("Japan",)`, returns province-level data in Japan.
        df = pd.DataFrame(
            {
                Term.COUNTRY: ["Japan" for _ in range(2)],
                Term.PROVINCE: ["Tokyo", "Tokyo"],
                Term.CITY: [Term.NA for _ in range(2)],
                Term.DATE: [day0, day1],
                Term.C: [6, 7],
            }
        )
        assert geometry.layer(data=raw, geo=("Japan",)).equals(df)
        # When `geo=(["Japan", "UK"],)`, returns province-level data in Japan and UK.
        df = pd.DataFrame(
            {
                Term.COUNTRY: ["UK", "UK", "Japan", "Japan"],
                Term.PROVINCE: ["England", "England", "Tokyo", "Tokyo"],
                Term.CITY: [Term.NA for _ in range(4)],
                Term.DATE: [day0, day1] * 2,
                Term.C: [0, 1, 6, 7],
            }
        )
        assert geometry.layer(data=raw, geo=(["Japan", "UK"],)).equals(df)
        # When `geo=("Japan", "Kanagawa")`, returns city-level data in Kanagawa/Japan.
        df = pd.DataFrame(
            {
                Term.COUNTRY: ["Japan" for _ in range(4)],
                Term.PROVINCE: ["Kanagawa" for _ in range(4)],
                Term.CITY: ["Yokohama", "Yokohama", "Kawasaki", "Kawasaki"],
                Term.DATE: [day0, day1] * 2,
                Term.C: [10, 11, 12, 13],
            }
        )
        assert geometry.layer(data=raw, geo=("Japan", "Kanagawa")).equals(df)
        # When `geo=("Japan", ["Tokyo", "Kanagawa"])`, returns city-level data in Tokyo/Japan and Kanagawa/Japan.
        df = pd.DataFrame(
            {
                Term.COUNTRY: ["Japan" for _ in range(6)],
                Term.PROVINCE: ["Tokyo", "Tokyo", *["Kanagawa" for _ in range(4)]],
                Term.CITY: ["Chiyoda", "Chiyoda", "Yokohama", "Yokohama", "Kawasaki", "Kawasaki"],
                Term.DATE: [day0, day1] * 3,
                Term.C: [8, 9, 10, 11, 12, 13],
            }
        )
        assert geometry.layer(data=raw, geo=("Japan", ["Tokyo", "Kanagawa"])).equals(df)
        # Errors
        with pytest.raises(TypeError):
            geometry.layer(data=raw, geo="a")
        with pytest.raises(TypeError):
            geometry.layer(data=raw, geo=(1,))
        with pytest.raises(ValueError):
            geometry.layer(data=raw, geo=("The Earth", "Japan", "Tokyo", "Chiyoda"))

    def test_filter(self):
        day0, day1 = pd.to_datetime("2022-01-01"), pd.to_datetime("2022-01-02")
        raw = pd.DataFrame(
            {
                Term.COUNTRY: [*["UK" for _ in range(4)], *["Japan" for _ in range(10)]],
                Term.PROVINCE: [
                    "England", "England", *[Term.NA for _ in range(4)],
                    *["Tokyo" for _ in range(4)], *["Kanagawa" for _ in range(4)]],
                Term.CITY: [
                    *[Term.NA for _ in range(8)], "Chiyoda", "Chiyoda", "Yokohama", "Yokohama", "Kawasaki", "Kawasaki"],
                Term.DATE: [day0, day1] * 7,
                Term.C: range(14),
            }
        )
        geometry = Geometry(layers=[Term.COUNTRY, Term.PROVINCE, Term.CITY])
        # When `geo = None` or `geo = (None,)`, returns all country-level data.
        df = pd.DataFrame(
            {
                Term.COUNTRY: ["UK", "UK", "Japan", "Japan"],
                Term.PROVINCE: [Term.NA for _ in range(4)],
                Term.CITY: [Term.NA for _ in range(4)],
                Term.DATE: [day0, day1] * 2,
                Term.C: [2, 3, 4, 5],
            }
        )
        assert geometry.filter(data=raw, geo=None).equals(df)
        assert geometry.filter(data=raw, geo=(None,)).equals(df)
        # When `geo = ("Japan",)`, returns country-level data in Japan.
        df = pd.DataFrame(
            {
                Term.COUNTRY: ["Japan", "Japan"],
                Term.PROVINCE: [Term.NA for _ in range(2)],
                Term.CITY: [Term.NA for _ in range(2)],
                Term.DATE: [day0, day1],
                Term.C: [4, 5],
            }
        )
        assert geometry.filter(data=raw, geo=("Japan",)).equals(df)
        # When `geo = (["Japan", "UK"],)`, returns country-level data of Japan and UK.
        df = pd.DataFrame(
            {
                Term.COUNTRY: ["UK", "UK", "Japan", "Japan"],
                Term.PROVINCE: [Term.NA for _ in range(4)],
                Term.CITY: [Term.NA for _ in range(4)],
                Term.DATE: [day0, day1] * 2,
                Term.C: [2, 3, 4, 5],
            }
        )
        assert geometry.filter(data=raw, geo=(["Japan", "UK"],)).equals(df)
        # When `geo = ("Japan", "Tokyo")`, returns province - level data of Tokyo/Japan.
        df = pd.DataFrame(
            {
                Term.COUNTRY: ["Japan", "Japan"],
                Term.PROVINCE: ["Tokyo", "Tokyo"],
                Term.CITY: [Term.NA for _ in range(2)],
                Term.DATE: [day0, day1],
                Term.C: [6, 7],
            }
        )
        assert geometry.filter(data=raw, geo=("Japan", "Tokyo")).equals(df)
        # When `geo = ("Japan", ["Tokyo", "Kanagawa"])`, returns province-level data of Tokyo/Japan and Kanagawa/Japan.
        # Note that the example raw data does not include province-level data of Kanagawa/Japan.
        df = pd.DataFrame(
            {
                Term.COUNTRY: ["Japan", "Japan"],
                Term.PROVINCE: ["Tokyo", "Tokyo"],
                Term.CITY: [Term.NA for _ in range(2)],
                Term.DATE: [day0, day1],
                Term.C: [6, 7],
            }
        )
        assert geometry.filter(data=raw, geo=("Japan", ["Tokyo", "Kanagawa"])).equals(df)
        # When `geo = ("Japan", "Kanagawa", "Yokohama")`, returns city-level data of Yokohama/Kanagawa/Japan.
        df = pd.DataFrame(
            {
                Term.COUNTRY: ["Japan", "Japan"],
                Term.PROVINCE: ["Kanagawa", "Kanagawa"],
                Term.CITY: ["Yokohama", "Yokohama"],
                Term.DATE: [day0, day1],
                Term.C: [10, 11],
            }
        )
        assert geometry.filter(data=raw, geo=("Japan", "Kanagawa", "Yokohama")).equals(df)
        # When `geo = (("Japan", "Kanagawa", ["Yokohama", "Kawasaki"])`, returns city-level data of Yokohama/Kanagawa/Japan and Kawasaki / Kanagawa / Japan.
        df = pd.DataFrame(
            {
                Term.COUNTRY: ["Japan", "Japan", "Japan", "Japan"],
                Term.PROVINCE: ["Kanagawa", "Kanagawa", "Kanagawa", "Kanagawa"],
                Term.CITY: ["Yokohama", "Yokohama", "Kawasaki", "Kawasaki"],
                Term.DATE: [day0, day1] * 2,
                Term.C: [10, 11, 12, 13],
            }
        )
        assert geometry.filter(data=raw, geo=("Japan", "Kanagawa", ["Yokohama", "Kawasaki"])).equals(df)
        # Errors
        with pytest.raises(TypeError):
            geometry.filter(data=raw, geo="a")
        with pytest.raises(TypeError):
            geometry.filter(data=raw, geo=(1,))
        with pytest.raises(ValueError):
            geometry.filter(data=raw, geo=("The Earth", "Japan", "Tokyo", "Chiyoda"))
