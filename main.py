import csv
from datetime import datetime

import requests

USE_PROXY = True

URL = f"https://app.ether.fi/api/portfolio/v3/"

with open("addresses.txt") as file:
    addresses = [row.strip() for row in file]

with open("proxies.txt") as file:
    proxies = [f"http://{row.strip()}" for row in file]


def write_to_csv(address, ethfi, symbiotic, lombard):
    date = datetime.today().strftime("%Y-%m-%d")
    file_name = f"s4-{len(addresses)}-accs-{date}.csv"

    with open(file_name, "a", newline="") as file:
        writer = csv.writer(file)

        if file.tell() == 0:
            writer.writerow(["Wallet", "ETHFI", "Symbiotic", "Lombard"])

        writer.writerow(
            [
                address,
                f"{ethfi / 1000:.0f}K",
                f"{round(symbiotic, 1)}",
                f"{round(lombard, 1)}",
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

        print(f"{address} | ETHFI {ethfi / 1000:.0f}K | Symbiotic {symbiotic:.1f} | Lombard {lombard:.1f}")  # fmt: skip
        write_to_csv(address, ethfi, symbiotic, lombard)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Cancelled by user")
    except Exception as err:
        print(f"An error occured: {err}")
