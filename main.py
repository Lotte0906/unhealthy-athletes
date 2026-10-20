
from olympic_data import OlympicData
from filtering import (
    get_medal_winners,
    filter_by_year_range,
    get_first_n_names,
    filter_by_names,
)


def main():
    """Run the Olympic data workflow."""
    olympics = OlympicData("data/athlete_events.csv")
    olympics.load_and_prepare()

    # Select all medal-winning records
    medal_winners = get_medal_winners(olympics.data)

    # Select medal-winning records from 1950 through 1960
    medal_winners_1950_1960 = filter_by_year_range(
        medal_winners,
        start_year=1950,
        end_year=1960,
    )

    # Get the first 20 unique names in this filtered dataset
    names = get_first_n_names(
        medal_winners_1950_1960,
        n=20,
    )

    # Select all records belonging to those names
    selected_athletes = filter_by_names(
        medal_winners_1950_1960,
        names,
    )

    print(f"Total records: {len(olympics.data)}")
    print(f"Medal-winning records: {len(medal_winners)}")
    print(
        "Medal-winning records from 1950–1960: "
        f"{len(medal_winners_1950_1960)}"
    )
    print(f"Selected athlete records: {len(selected_athletes)}")


if __name__ == "__main__":
    main()
