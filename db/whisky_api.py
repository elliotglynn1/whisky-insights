import polars as pl
import requests


def auctions_data() -> pl.DataFrame:
    response = requests.get("https://whiskyhunter.net/api/auctions_data/")
    return pl.DataFrame(response.json())


def auctions_info() -> pl.DataFrame:
    response = requests.get("https://whiskyhunter.net/api/auctions_info")
    return pl.DataFrame(response.json())


def distilleries_info() -> pl.DataFrame:
    response = requests.get("https://whiskyhunter.net/api/distilleries_info/")
    return pl.DataFrame(response.json())


def distillery_data(distillery_slug) -> pl.DataFrame:
    response = requests.get(
        f"https://whiskyhunter.net/api/distillery_data/{distillery_slug}/"
    )
    return pl.DataFrame(response.json())
