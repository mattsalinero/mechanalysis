from mech_scrape import *
from mech_clean import *
from mech_io import *
import datetime
from pathlib import Path


def main():
    mech_db = Path(__file__).parent / "data" / "database" / "mech_db.db"
    page_limit = 70
    # TODO: Implement a config file of some kind to store filepaths, page_limit settings etc.

    print("scraping data for " + datetime.datetime.today().isoformat())

    if input("set up new database? (REPLACE/N): ").upper() == "REPLACE":
        mech_io.db_setup(mech_db, overwrite=True)

    if input("scrape group buy forum? (Y/N): ").upper() == "Y":
        gb_raw_filepath = mech_io.gen_csvpath("gb_raw")
        gb_clean_filepath = mech_io.gen_csvpath("gb_clean")
        scrape_board("geekhack.org", "70", page_limit=page_limit, request_interval=20, filepath=gb_raw_filepath)
        clean_board_data(in_filepath=gb_raw_filepath, out_filepath=gb_clean_filepath, out_db=mech_db)

    if input("scrape interest check forum? (Y/N): ").upper() == "Y":
        ic_raw_filepath = mech_io.gen_csvpath("ic_raw")
        ic_clean_filepath = mech_io.gen_csvpath("ic_clean")
        scrape_board("geekhack.org", "132", page_limit=page_limit, request_interval=20, filepath=ic_raw_filepath)
        clean_board_data(in_filepath=ic_raw_filepath, out_filepath=ic_clean_filepath, out_db=mech_db)

    if input("scrape groupbuy topics? (Y/N): ").upper() == "Y":
        post_dir = Path(__file__).parent / "data" / "post_data"

        topic_list = mech_io.db_query_keycap_topics(mech_db, "70", "new")
        segment_size = 25
        # split full topic list into segments based on segment_size
        topic_segments = [topic_list[i:i+segment_size] for i in range(0, len(topic_list), segment_size)]

        for segment in topic_segments:
            scrape_topics("geekhack.org", segment, topic_limit=25, post_dir=post_dir, request_interval=20)
            clean_topic_data(segment, in_folder=post_dir, out_db=mech_db)
            time.sleep(30)
    
    if input("rebuild database? (REBUILD/N): ").upper() == "REBUILD":
        date_string = input("date string of scraped data? (YYYY-MM-DD): ")

        # rebuild topic index portion of db
        gb_raw_filepath = mech_io.gen_csvpath("gb_raw", date=date_string)
        gb_clean_filepath = mech_io.gen_csvpath("gb_clean", date=date_string)
        ic_raw_filepath = mech_io.gen_csvpath("ic_raw", date=date_string)
        ic_clean_filepath = mech_io.gen_csvpath("ic_clean", date=date_string)

        print("reset db")
        mech_io.db_setup(mech_db, overwrite=True)
        
        print("add gb and ic topic index data")
        clean_board_data(in_filepath=gb_raw_filepath, out_filepath=gb_clean_filepath, out_db=mech_db)
        clean_board_data(in_filepath=ic_raw_filepath, out_filepath=ic_clean_filepath, out_db=mech_db)

        # rebuild topic page portion of db
        post_dir = Path(__file__).parent / "data" / "post_data"

        print("add gb topic page data")
        topic_list = mech_io.db_query_keycap_topics(mech_db, "70", "new")
        segment_size = 50
        # split full topic list into segments based on segment_size
        topic_segments = [topic_list[i:i+segment_size] for i in range(0, len(topic_list), segment_size)]

        for segment in topic_segments:
            print(f"rebuilding database for segment starting with {segment[0]}")
            clean_topic_data(segment, in_folder=post_dir, out_db=mech_db)

    return


if __name__ == '__main__':
    main()
