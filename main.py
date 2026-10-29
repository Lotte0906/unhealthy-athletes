from olympic_data import OlympicData
from prepare_for_scraping import get_first_n_names, filter_by_names
from biography_scraper import find_wikidata_entry, get_wikidata_claims
from processing import convert_dict_to_pd_df, merge_dataframes, convert_dates, add_age
import datetime


def main():
    """Run the Olympic data workflow."""
    olympics = OlympicData("data/athlete_events.csv")
    olympics.load_and_prepare()

    # prepare for scraping
    n = 20
    listofnames = get_first_n_names(olympics.data, n)
    originaldf = filter_by_names(olympics.data, n)
    
    # scrape data of athletes from wikidata
    name_list = []
    for name in listofnames:
        name_list.append(get_wikidata_claims(find_wikidata_entry(name)))
    
    # process the data
    newdf = convert_dict_to_pd_df(name_list)
    df = merge_dataframes(originaldf, newdf)
    df = convert_dates(df)
    
    currentdate = datetime.date.today()
    df = add_age(df, currentdate)
    df.head()

if __name__ == "__main__":
    main()
