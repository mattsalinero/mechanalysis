import datetime
import csv
import regex
import emoji
import pandas as pd
from lark import Lark


def clean_board_data(in_data=None, in_filepath=None, out_filepath=None, return_df=True):
    """
    Cleans scraped data from forum into more readable format
    :param in_data:
    :param in_filepath:
    :param out_filepath:
    :param return_df:
    :return: pandas DataFrame of cleaned data
    """
    # TODO: potentially move clean_board_data() to the initial scraping step, break parse_title(s) into own thing

    clean_data = pd.DataFrame()
    if in_data:
        if type(in_data) is list and type(in_data[0]) is dict:
            unclean_data = pd.DataFrame(in_data)
    elif in_filepath:
        unclean_data = pd.read_csv(in_filepath)
    else:
        # TODO: error handling for improper input
        pass

    print(f"Parsing {len(unclean_data.index)} records")

    # TODO: use from_dict or from_record to actually create the dataframe or just implement this not using
    #  dataframes/pandas -> I don't think it's needed in this case, can also move to a per-record basis for parsing
    #  and only consolidate at the end
    clean_data['topic_id'] = unclean_data['topiclink'].apply(lambda x: x.split('=')[-1].split('.')[0])

    # parse information from title
    clean_data['product_type'], clean_data['thread_type'], clean_data['info_codes'], clean_data['set_name'] \
        = parse_titles(unclean_data['title'])

    # parse for creator info
    clean_data['creator'] = unclean_data['creator']
    clean_data['creator_id'] = \
        unclean_data['creatorlink'].loc[unclean_data['creatorlink'].notna()].apply(lambda x: x.split('=')[-1])

    # parse for stats
    clean_data['views'] = unclean_data['views'].apply(lambda x: int(x.split()[0]))
    clean_data['replies'] = unclean_data['replies'].apply(lambda x: int(x.split()[0]))

    # parse for board number
    clean_data['board'] = unclean_data['url'].apply(lambda x: x.split("board=")[-1].split('.')[0])

    clean_data['access_date'] = unclean_data['accessed']
    clean_data['title'] = unclean_data['title']

    print(f"Parsed {len(clean_data.index)} records")
    if out_filepath:
        clean_data.to_csv(out_filepath)
        print(f"Saved to {out_filepath}")

    if return_df:
        return clean_data
    else:
        return


def parse_title(to_search, title_parser):
    """
    Finds thread type indicator, keyset infocodes, and keyset name from thread title
    :param to_search: str to parse as a title
    :param title_parser:
    :return: tuple(str thread type, str infocode, str set name)
    """
    # TODO: fix docstring for output
    # TODO: add handler for empty string input

    title_tree = title_parser.parse(emoji.demojize(to_search)).children[0]
    # TODO: Move the actual parsing call into the calling function, call this traverse_parsed_title or something

    title_data = {'product_type': None, 'thread_type': None, 'info_codes': None, 'set_name': None}

    if title_tree.data == 'keycapthread':
        title_data['product_type'] = "keycaps"

    for subtree in title_tree.children:
        if subtree.data == 'threadcode':
            title_data['thread_type'] = subtree.children[0].value.upper()
        elif subtree.data == 'titlesection' or subtree.data == 'invtitlesection':
            for section in subtree.children:
                if section.data == 'icodes':
                    infocodes = []
                    for icode in section.children:
                        infocodes.append(icode.data.upper())
                    title_data['info_codes'] = infocodes
                else:
                    title_data['set_name'] = " ".join([namepart for namepart in section.children])

    return title_data


def parse_titles(titles):
    """
    Finds thread type indicator, keyset infocodes, and keyset name for list of thread titles
    :param titles: list[str]
    :return: tuple(list[str] thread type, list[str] infocode, list[str] set name)
    """
    # TODO: fix docstring for output
    # TODO: add tai-hao (and potential variations like SPSA) to list of infocodes

    parser = Lark.open("gb_title.lark", start="topic", parser="earley")

    titles_data = []

    for title in titles:
        titles_data.append(parse_title(title, parser))

    return titles_data


def parse_basic_row(in_row):
    # TODO: add docstring
    basic_data = {'topic_id': None, 'creator': None, 'creator_id': None, 'views': None, 'replies': None, 'board': None,
                  'access_date': None, 'title': None}

    # parse for topic id
    if 'topiclink' in in_row and in_row['topiclink']:
        basic_data['topic_id'] = in_row['topiclink'].split('=')[-1].split('.')[0]
    else:
        raise ValueError("missing required topic id")

    # parse for creator info
    if 'creator' in in_row and in_row['creator']:
        basic_data['creator'] = in_row['creator']
    if 'creatorlink' in in_row and in_row['creatorlink']:
        basic_data['creator_id'] = in_row['creatorlink'].split('=')[-1]

    # parse for topic stats
    if 'views' in in_row and in_row['views']:
        basic_data['views'] = int(in_row['views'].split()[0])
    if 'replies' in in_row and in_row['replies']:
        basic_data['replies'] = int(in_row['replies'].split()[0])

    # parse for board number
    if 'url' in in_row and in_row['url']:
        basic_data['board'] = in_row['url'].split("board=")[-1].split('.')[0]

    # parse for access data and title
    if 'accessed' in in_row and in_row['accessed']:
        basic_data['access_date'] = in_row['accessed']
    if 'title' in in_row and in_row['title']:
        basic_data['title'] = in_row['title']

    return basic_data
