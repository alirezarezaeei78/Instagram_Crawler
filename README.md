# Instagram Follower Collection Experiments

Selenium and Jupyter notebook experiments for collecting Instagram follower lists and exporting them to CSV for research workflows.

This repository preserves multiple exploratory implementations. Instagram's interface and login flow can change, so selectors and browser behavior may require maintenance.

## Contents

| File | Purpose |
| --- | --- |
| `instagram_scraping.ipynb` | Three alternative versions of the login, follower-list, and CSV-export workflow |
| `Untitled-1.ipynb` | Additional login and browser-driver experiments |
| `chromedriver-mac-arm64/` | A historical macOS ARM driver bundle; most setups should use the driver manager in the notebooks |

## Local setup

Use Python, Google Chrome, and a local Jupyter environment.

```sh
git clone https://github.com/alirezarezaeei78/Instagram_Crawler.git
cd Instagram_Crawler
python -m venv .venv
```

Activate the environment, then install dependencies:

```sh
python -m pip install -r requirements.txt
python -m notebook
```

Set `INSTAGRAM_USERNAME` and `INSTAGRAM_PASSWORD` in the environment used to launch Jupyter. Additional experiments use `USERNAME` and `PASSWORD`. Do not put real credentials in notebook cells or commit them to Git.

Read the selected cell, configure the target account and output location, and run **one implementation at a time**. The main notebook's cells are alternatives rather than a sequential pipeline.

## Use and limitations

Use your own authorized account and collect only data you are permitted to access. Follow platform terms and applicable privacy requirements. Login challenges require manual handling; the notebooks do not provide a stable collection API or completeness guarantees.

Review outputs before sharing them. Environment files and CSV exports are excluded from version control by `.gitignore`.

## Maintainer

[Alireza Rezaei](https://www.linkedin.com/in/alireza-rezaei-24963a210/) — applied machine learning and web development.

## Maintained entry point

Copy `.env.example` to `.env` and fill in your own credentials and `TARGET_USER`. Run `python crawler.py` to start one browser session. The main notebook imports this implementation and defaults to `RUN_CRAWLER = False`, avoiding repeated logins when Run All is used. `Untitled-1.ipynb` retains callable exploratory demos and closes their drivers.

Driver discovery uses [Selenium Manager](https://www.selenium.dev/documentation/selenium_manager/). Follower links are validated as Instagram profile URLs, results are sorted, scrolling is bounded, and the browser closes on failure. Run `python -m unittest discover -s tests -v` for offline URL and configuration checks. Live collection has not been tested against the current Instagram layout.
