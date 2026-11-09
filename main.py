
# from workflow import prepare_athletes, run_scraping


# def main():
#     """Run the Olympic athlete biography workflow."""
#     try:
#         # Load Olympic data and match athletes to Olympedia.
#         olympic_data, all_athletes = prepare_athletes()

#         # Scrape Wikidata and process the results.
#         run_scraping(
#             olympic_data,
#             all_athletes,
#             n_batches=49
#         )

#     except Exception as e:
#         print(f"Workflow stopped: {type(e).__name__}: {e}")
#         raise


# if __name__ == "__main__":
#     main()

from workflow import prepare_athletes

olympic_data, all_athletes = prepare_athletes()

print(all_athletes["errormessage"].value_counts(dropna=False))
print(olympic_data.head())