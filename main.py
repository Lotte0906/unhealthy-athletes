from workflow import prepare_athletes, run_scraping


def main():
    olympic_data, all_athletes = prepare_athletes()

    run_scraping(
        olympic_data,
        all_athletes,
        n_batches=500
    )


if __name__ == "__main__":
    main()