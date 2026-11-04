from olympic_data import OlympicData
from prepare_for_scraping import get_first_n_names, filter_by_names
from biography_scraper_finding_errors import find_wikidata_entry, get_wikidata_claims
from processing_finding_errors import convert_dict_to_pd_df, merge_dataframes, convert_dates, add_age
import datetime
import numpy as np

def main():
    """Run the Olympic data workflow."""
    try:
        olympics = OlympicData("data/athlete_events.csv")
        olympics.load_and_prepare()

        n_batches = 49
        all_names = olympics.data["Name"].drop_duplicates().tolist()
        total_names = len(all_names)

        currentdate = datetime.date.today()

        for batch_num in range(n_batches):
            start = batch_num * total_names // n_batches
            end = (batch_num + 1) * total_names // n_batches

            listofnames = all_names[start:end]
            print(f"Processing batch {batch_num + 1}/{n_batches} "
                  f"({len(listofnames)} athletes)")

            # Prepare for scraping
            originaldf = filter_by_names(olympics.data, listofnames)

            # Scrape data of athletes from Wikidata
            name_list = []
            for name in listofnames:
                name_list.append(
                    get_wikidata_claims(find_wikidata_entry(name))
                )

            # Process the data
            newdf = convert_dict_to_pd_df(name_list)
            df = merge_dataframes(originaldf, newdf)
            df = convert_dates(df)
            df = add_age(df, currentdate)

            # Save results
            df.to_csv(
                f"data/entries{batch_num + 1}of{n_batches}.csv",
                index=False
            )

    except Exception as e:
        print(f"Workflow stopped: {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()