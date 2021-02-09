import datetime
import csv
import regex
from pathlib import Path
import emoji
import pandas as pd
from lark import Lark


def clean_board_data(in_data=None, in_filepath=None, out_filepath=None):
    """
    Cleans scraped data from board index page into more readable format, supports reading from and saving to files
    :param in_data: list[dict] each element is extracted data for one topic on board index page
     (priority over in_filepath)
    :param in_filepath: filepath to csv equivalent of in_data
    :param out_filepath: (optional) filepath to save resulting data
    :return: list[dict] of cleaned data
    """
    # TODO: make another function to deal with DataFrame input (clean_board_dataframe()?), leave this one for list[dict]
    #  can also have clean_board_database() eventually
    if in_data:
        if type(in_data) is list and type(in_data[0]) is dict:
            raw_data = in_data
        else:
            raise ValueError("improperly formatted input data")
    elif in_filepath:
        with open(in_filepath, 'r', encoding="utf-8", newline='') as in_csv:
            in_reader = csv.DictReader(in_csv)
            raw_data = [csv_topic for csv_topic in in_reader]
    else:
        raise ValueError("no valid input provided")

    print(f"Parsing {len(raw_data)} records")

    # parse received data
    out_data = parse_board_data(raw_data)
    print(f"Parsed {len(out_data)} records")

    if out_filepath:
        # save data to csv - note this does not include an index field other than topic id
        fields = ['topic_id', 'product_type', 'thread_type', 'info_codes', 'set_name', 'creator', 'creator_id', 'views',
                  'replies', 'board', 'access_date', 'title']
        with open(out_filepath, 'w', encoding="utf-8", newline='') as out_csv:
            # TODO: implement a check if this file exists already, maybe a parameter to control if it overwrites
            out_writer = csv.DictWriter(out_csv, fieldnames=fields)
            out_writer.writeheader()
            out_writer.writerows(out_data)

        print(f"Saved to {out_filepath}")

    return out_data


def parse_board_data(input_topics):
    """
    Extracts topic information available in board index for list of topics
    :param input_topics: list[dict] each element is extracted data for one topic
    :return: list[dict] containing extracted data for each topic
    """
    # set up parser using grammar file
    grammar = Path(__file__).parent / "title_gram.lark"
    parser = Lark.open(grammar, start="topic", parser="earley")

    # extract and aggregate relevant data
    topic_index_data = []
    for topic in input_topics:
        topic_data = parse_basic(topic)
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


def parse_basic(input_topic):
    """
    Parses basic data from topic information available in board index. Does not do complex parsing on title
    :param input_topic: dict containing extracted data for one topic
    :return: dict containing topic id, creator (name), creator id, views, replies, board, access date, and raw title
    """
    basic_data = {'topic_id': None, 'creator': None, 'creator_id': None, 'views': None, 'replies': None, 'board': None,
                  'access_date': None, 'title': None}

    # parse for topic id
    if 'topiclink' in input_topic and input_topic['topiclink']:
        basic_data['topic_id'] = input_topic['topiclink'].split('=')[-1].split('.')[0]
    else:
        raise ValueError("missing required topic id")

    # parse for creator info
    if 'creator' in input_topic and input_topic['creator']:
        basic_data['creator'] = input_topic['creator']
    if 'creatorlink' in input_topic and input_topic['creatorlink']:
        basic_data['creator_id'] = input_topic['creatorlink'].split('=')[-1]

    # parse for topic stats
    if 'views' in input_topic and input_topic['views']:
        basic_data['views'] = int(input_topic['views'].split()[0])
    if 'replies' in input_topic and input_topic['replies']:
        basic_data['replies'] = int(input_topic['replies'].split()[0])

    # parse for board number
    if 'url' in input_topic and input_topic['url']:
        basic_data['board'] = input_topic['url'].split("board=")[-1].split('.')[0]

    # parse for access data and title
    if 'accessed' in input_topic and input_topic['accessed']:
        basic_data['access_date'] = input_topic['accessed']
    if 'title' in input_topic and input_topic['title']:
        basic_data['title'] = input_topic['title']

    return basic_data
