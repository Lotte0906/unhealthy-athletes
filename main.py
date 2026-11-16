from datetime import date

from unhealthy_athletes.workflow import prepare_athletes, run_scraping


def main():
    olympic_data, all_athletes = prepare_athletes()

    run_scraping(
        olympic_data,
        all_athletes,
        n_batches=500,
        reference_date=date(2026, 11, 13),
        adopt_legacy=False,
    )


if __name__ == "__main__":
    main()
