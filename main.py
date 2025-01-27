import csv
from datetime import datetime

import requests
from rich import print

USE_PROXY = True

URL = f"https://app.ether.fi/api/portfolio/v3/"

with open("addresses.txt") as file:
    addresses = [row.strip() for row in file]

with open("proxies.txt") as file:
    proxies = [f"http://{row.strip()}" for row in file]


def write_to_csv(address, ethfi, symbiotic, lombard):
    file_name = f"s4-{len(addresses)}-accs-{datetime.now():%Y-%m-%d}.csv"

    with open(file_name, "a", newline="") as file:
        writer = csv.writer(file)

        if file.tell() == 0:
            writer.writerow(["Wallet", "ETHFI", "Symbiotic", "Lombard"])

        writer.writerow(
            [
                address,
                f"{ethfi / 1000:.0f}K",
                f"{symbiotic:.1f}",
                f"{lombard:.1f}",
            ]
        )


def main():
    for index, address in enumerate(addresses):
        proxy = proxies[index % len(proxies)] if USE_PROXY else None

        resp = requests.get(
            f"{URL}/{address}",
            proxies={"http": proxy, "https": proxy},
            headers={
                "accept": "*/*",
                "referer": "https://app.ether.fi/portfolio",
            },
        )
        data = resp.json()

        if not data:
            raise Exception("Could not fetch data")

        ethfi, symbiotic, lombard = (
            data.get("totalPointsSummaries", {})
            .get("LOYALTY", {})
            .get("CurrentPoints", 0),
            data.get("totalPointsSummaries", {})
            .get("SYMBIOTIC", {})
            .get("TotalPoints", 0),
            data.get("totalPointsSummaries", {})
            .get("LOMBARD", {})
            .get("TotalPoints", 0),
        )

        print(f"{address} | ETHFI {ethfi / 1000:>4.0f}K | Symbiotic {symbiotic:>4.1f} | Lombard {lombard:>5.1f}")  # fmt: skip
        write_to_csv(address, ethfi, symbiotic, lombard)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Cancelled by user")
    except Exception as err:
        print(f"An error occured: {err}")
