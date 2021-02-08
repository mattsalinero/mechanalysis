import datetime
import csv
import regex
from pathlib import Path
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
        = parse_topic_data(unclean_data['title'])

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


def parse_topic_data(topics):
    """
    Finds thread type indicator, keyset infocodes, and keyset name for list of thread titles
    :param topics: list[str]
    :return: tuple(list[str] thread type, list[str] infocode, list[str] set name)
    """
    # TODO: fix docstring in general
    # TODO: add tai-hao (and potential variations like SPSA) to list of infocodes

    grammar = Path(__file__).parent / "gb_title.lark"
    parser = Lark.open(grammar, start="topic", parser="earley")

    topic_index_data = []
    for topic in topics:
        topic_data = parse_basic_row(topic)
        topic_data.update(parse_title(topic['title'], parser))
        topic_index_data.append(topic_data)

    return topic_index_data


def parse_title(input_title, title_parser):
    """
    Parses topic title to determine product type (keycap or unknown), thread_type (group buy, interest check),
    info codes (GMK, SA, etc.), and the name of the set (if applicable)
    :param input_title: str title to parse
    :param title_parser: LARK parser used to interpret title
    :return: dict containing product_type, thread_type, info_codes, set_name (all default to None)
    """

    if not input_title:
        raise ValueError("invalid/empty input title")

    # parse input_title (replacing emojis with unicode string)
    title_tree = title_parser.parse(emoji.demojize(input_title)).children[0]

    title_data = {'product_type': None, 'thread_type': None, 'info_codes': None, 'set_name': None}

    # extract relevant data from parse tree
    if title_tree.data == 'keycapthread':
        title_data['product_type'] = "keycaps"
    for subtree in title_tree.children:
        if subtree.data == 'threadcode':
            title_data['thread_type'] = subtree.children[0].value.upper()
        elif subtree.data == 'titlesection' or subtree.data == 'invtitlesection':
            for section in subtree.children:
                if section.data == 'icodes':
                    title_data['info_codes'] = [icode.data.upper() for icode in section.children]
                else:
                    title_data['set_name'] = " ".join([namepart for namepart in section.children])

    return title_data


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
