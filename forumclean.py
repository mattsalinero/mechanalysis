import datetime
import csv
import pandas as pd


def clean_board_data(unclean_data, filepath=None):

    clean_data = pd.DataFrame()
    print(str(type(unclean_data)) + str(type(unclean_data[0])))
    if type(unclean_data) is list and type(unclean_data[0]) is dict:
        unclean_data = pd.DataFrame(unclean_data)

    # parse for topic number
    clean_data['topic_id'] = unclean_data['topiclink'].apply(lambda x: int(x.split('=')[-1].split('.')[0]))

    # parse for creator info
    clean_data['creator'] = unclean_data['creator']
    clean_data['creator_id'] = unclean_data['creatorlink'].apply(lambda x: int(x.split('=')[-1]))

    # parse for stats
    clean_data['views'] = unclean_data['views'].apply(lambda x: int(x.split()[0]))
    clean_data['replies'] = unclean_data['replies'].apply(lambda x: int(x.split()[0]))

    print(clean_data.head())

    return clean_data
