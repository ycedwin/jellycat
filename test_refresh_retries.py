#!/usr/bin/env python3
"""Retry helper: 403/5xx retry, then raise; 200 returns."""

from refresh_official_catalog import get_with_retry


class FakeResponse:
    def __init__(self, status_code):
        self.status_code = status_code
        self.text = ""

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeScraper:
    def __init__(self, codes):
        self.codes = list(codes)
        self.gets = 0

    def get(self, url, timeout=60):
        self.gets += 1
        return FakeResponse(self.codes.pop(0))


def test_retries_then_ok():
    scrapers = [FakeScraper([403]), FakeScraper([200])]
    waits = []
    scraper, response = get_with_retry(
        "https://example",
        scrapers[0],
        attempts=4,
        sleep=waits.append,
        new_scraper=lambda: scrapers[1],
    )
    assert response.status_code == 200
    assert scraper is scrapers[1]
    assert waits == [1]
    assert scrapers[0].gets == 1
    assert scrapers[1].gets == 1


def test_gives_up_on_403():
    scraper = FakeScraper([403, 403, 403])
    try:
        get_with_retry(
            "https://example",
            scraper,
            attempts=3,
            sleep=lambda _: None,
            new_scraper=lambda: scraper,
        )
    except RuntimeError as exc:
        assert "403" in str(exc)
    else:
        raise AssertionError("expected HTTP 403")


if __name__ == "__main__":
    test_retries_then_ok()
    test_gives_up_on_403()
    print("ok")
