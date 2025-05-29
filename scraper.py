#!/usr/bin/env python

import json
import logging
import os
from time import sleep
from urllib.parse import urljoin

import click
import requests
from dateutil.parser import parse
from tqdm import tqdm

BASE_URL = "https://2025electionresults.comelec.gov.ph/"
DESC_LENGTH = 20


def load_or_download(session, file_path, url, download_delay):
    """Read file_path if it exists, download from url if it doesn't"""
    logging.debug(f"In load_or_download: {file_path}, {url}")
    if os.path.exists(file_path):
        logging.debug(f"{file_path} exists, loading...")
        with open(file_path) as f:
            data = json.load(f)
    else:
        logging.debug(
            f"{file_path} doesn't exist, " f"downloading from {url}..."
        )
        response = session.get(url)
        # no results yet
        if response.status_code != 200:
            return None

        data = response.json()
        sleep(download_delay)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        logging.debug(f"file path: {os.path.dirname(file_path)}")
        with open(file_path, "w") as f:
            json.dump(data, f)

        # make timestamp match last modified time
        ts = parse(response.headers["Last-Modified"]).astimezone().timestamp()
        os.utime(file_path, (ts, ts))
    return data


def download_data(
    session,
    code,
    base_url,
    base_dir,
    cat_pbar,
    type="region",
    download_delay=0.5,
):
    """Recursively download data, skipping already downloaded files

    Parameters
    ----------
    session : requests.Session
        requests session to use
    code : str
        region or clustered precinct code
    base_url : str
        parent url of this region or ER
    cat_bar : dict
        dictionary of tqdm progress bar for each category code
    type : `region` or `er`
        whether a region or er is being downloaded
    download_delay : float
        minimum delay between successive downloads
    """
    logging.debug("\t".join((code, base_url, base_dir, type)))
    if type == "region":
        data = load_or_download(
            session,
            os.path.join(base_dir, "info.json"),
            urljoin(base_url, f"{code}.json"),
            download_delay,
        )
        # no data yet
        if not data:
            return

        regions = data["regions"]
        cat = regions[0].get("categoryCode")
        pbar = cat_pbar[cat]
        pbar.reset(len(regions))
        for region in regions:
            if region["categoryCode"]:
                pbar.set_description(region["name"].ljust(DESC_LENGTH))
                target_dir = os.path.join(
                    base_dir, region["name"].replace("/", "_").strip()
                )
                os.makedirs(target_dir, exist_ok=True)
                # barangay
                if region["categoryCode"] == "5":
                    download_data(
                        session,
                        region["code"],
                        urljoin(
                            BASE_URL,
                            f"data/regions/precinct/{region['code'][:2]}/",
                        ),
                        target_dir,
                        download_delay=download_delay,
                        cat_pbar=cat_pbar,
                    )
                else:
                    download_data(
                        session,
                        region["code"],
                        urljoin(base_url, f"{code}.json"),
                        target_dir,
                        download_delay=download_delay,
                        cat_pbar=cat_pbar,
                    )
            # ER
            else:
                pbar.set_description(region["code"].ljust(DESC_LENGTH))
                download_data(
                    session,
                    region["code"],
                    urljoin(BASE_URL, f"data/er/{region['code'][:3]}/"),
                    base_dir,
                    type="er",
                    download_delay=download_delay,
                    cat_pbar=cat_pbar,
                )
            pbar.update()

        # download COC for city/municipality and above
        if cat and int(cat) < 4:
            load_or_download(
                session,
                os.path.join(base_dir, "coc.json"),
                urljoin(BASE_URL, f"data/coc/{code}.json"),
                download_delay,
            )
    elif type == "er":
        load_or_download(
            session,
            os.path.join(base_dir, f"{code}.json"),
            urljoin(base_url, f"{code}.json"),
            download_delay,
        )


@click.command()
@click.option(
    "-b",
    "--base-dir",
    default="data",
    help="directory from which all downloaded data will be stored",
)
@click.option(
    "-d",
    "--download-delay",
    type=click.FLOAT,
    default=0.5,
    help="minimum delay between successive downloads",
)
@click.option(
    "-l",
    "--log-level",
    help="log output level",
    type=click.Choice(["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]),
    default="INFO",
)
def main(base_dir, download_delay, log_level):
    logging.basicConfig(level=log_level)
    sess = requests.Session()
    sess.headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/136.0.0.0 Safari/537.36"
    }

    cat_pbar = {str(cat): tqdm(leave=False) for cat in range(1, 6)}
    cat_pbar[None] = tqdm(leave=False)

    top_regions = ["local", "overseas"]
    pbar = cat_pbar["1"]
    pbar.reset(len(top_regions))
    for top_region in top_regions:
        pbar.set_description(top_region.ljust(DESC_LENGTH))
        download_data(
            sess,
            "0",
            urljoin(BASE_URL, f"data/regions/{top_region}/"),
            os.path.join(base_dir, top_region),
            download_delay=download_delay,
            cat_pbar=cat_pbar,
        )
        pbar.update()


if __name__ == "__main__":
    main()
