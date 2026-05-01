from datetime import date, datetime

import pytest

from market_agent.clients.finance_data_reader_market import FinanceDataReaderKoreaMarketDataClient


class FakeTail:
    def __init__(self, rows):
        self.rows = rows

    def iterrows(self):
        return iter(self.rows)


class FakeFrame:
    def __init__(self, rows):
        self.rows = rows

    def tail(self, count):
        assert count == 2
        return FakeTail(self.rows[-2:])


class FakeListingFrame:
    def __init__(self, rows):
        self.rows = rows

    def to_dict(self, orient):
        assert orient == "records"
        return self.rows


def test_finance_data_reader_market_context_normalizes_previous_korea_index_data() -> None:
    def fake_reader(symbol: str, start: str, end: str):
        assert symbol in {"KS11", "KQ11"}
        assert start < end
        return FakeFrame(
            [
                (datetime(2026, 4, 29), {"Close": 100.0}),
                (datetime(2026, 4, 30), {"Close": 110.0}),
            ]
        )

    snapshots = FinanceDataReaderKoreaMarketDataClient(data_reader=fake_reader).get_market_context()

    assert snapshots[0].source == "FinanceDataReader"
    assert snapshots[0].market_date == date(2026, 4, 30)
    assert snapshots[0].data_timestamp.isoformat() == "2026-04-30T15:30:00+09:00"
    assert snapshots[0].change_percent == 10.0
    assert not snapshots[0].is_mock
    assert not snapshots[0].collection_failed


def test_finance_data_reader_market_context_reports_collection_failure() -> None:
    def fake_reader(symbol: str, start: str, end: str):
        raise TimeoutError("timeout")

    snapshots = FinanceDataReaderKoreaMarketDataClient(data_reader=fake_reader).get_market_context()

    assert all(snapshot.collection_failed for snapshot in snapshots)
    assert all("데이터 수집 실패" in snapshot.summary for snapshot in snapshots)
    assert all(snapshot.source == "FinanceDataReader" for snapshot in snapshots)


def test_finance_data_reader_market_context_rejects_invalid_close() -> None:
    def fake_reader(symbol: str, start: str, end: str):
        return FakeFrame(
            [
                (datetime(2026, 4, 29), {"Close": 100.0}),
                (datetime(2026, 4, 30), {"Close": 0.0}),
            ]
        )

    snapshots = FinanceDataReaderKoreaMarketDataClient(data_reader=fake_reader).get_market_context()

    assert all(snapshot.collection_failed for snapshot in snapshots)
    assert all("close must be positive" in snapshot.summary for snapshot in snapshots)


def test_finance_data_reader_uses_live_krx_universe_candidates() -> None:
    def fake_listing(market: str):
        assert market == "KRX"
        return FakeListingFrame(
            [
                {"Code": "005930", "Name": "삼성전자", "Market": "KOSPI", "Close": 80000, "ChagesRatio": 1.2, "Volume": 1000, "Amount": 1_000_000_000_000},
                {"Code": "069500", "Name": "KODEX 200", "Market": "ETF", "Close": 40000, "ChagesRatio": -0.4, "Volume": 2000, "Amount": 500_000_000_000},
            ]
        )

    candidates = FinanceDataReaderKoreaMarketDataClient(stock_listing=fake_listing).get_candidates()

    assert candidates[0].ticker == "005930"
    assert candidates[0].source == "FinanceDataReader"
    assert candidates[0].universe_status == "live"
    assert not candidates[0].is_mock
    assert candidates[0].previous_close == 80000
    assert candidates[0].trading_value == 1_000_000_000_000
    assert candidates[1].asset_type == "etf"


def test_finance_data_reader_candidate_failure_marks_fallback() -> None:
    def fake_listing(market: str):
        raise TimeoutError("timeout")

    candidates = FinanceDataReaderKoreaMarketDataClient(stock_listing=fake_listing).get_candidates()

    assert candidates
    assert all(candidate.universe_status == "fallback_used" for candidate in candidates)
    assert all(candidate.is_mock for candidate in candidates)
    assert "fallback" in candidates[0].source
