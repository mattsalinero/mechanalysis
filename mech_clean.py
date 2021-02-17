import datetime
import csv
import regex
from pathlib import Path
import emoji
import pandas as pd
import mech_io
from lark import Lark


def clean_board_data(in_data=None, in_filepath=None, out_filepath=None, out_db=None):
    """
    Processes raw data scraped from board index page
    :param in_data: list[dict] each element is extracted data for one topic on board index page
     (priority over in_filepath)
    :param in_filepath: filepath to csv equivalent of in_data
    :param out_filepath: (optional) filepath to save resulting data
    :param out_db: (optional) filepath to sqlite database to save resulting data
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
        raw_data = mech_io.read_csv(in_filepath)
    else:
        raise ValueError("no valid input provided")

    print(f"Parsing {len(raw_data)} records")

    # parse received data
    out_data = parse_board_data(raw_data)
    print(f"Parsed {len(out_data)} records")

    if out_filepath:
        # save data to csv - note this does not include an index field other than topic id
        fields = ['topic_id', 'product_type', 'thread_type', 'info_codes', 'set_name', 'creator', 'creator_id', 'views',
                  'replies', 'board', 'board_accessed', 'title']
        mech_io.write_csv(out_data, out_filepath, fields)

        print(f"Saved to {out_filepath}")

    # TODO: update unit test to include saving to database
    if out_db:
        mech_io.db_insert_board_clean(out_data, out_db)
        print(f"Added to {out_db}")

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
    Parses topic title to derive relevant information (notably set name)
    :param input_title: string of title to parse
    :param title_parser: LARK parser used to interpret title
    :return: dict containing extracted data (values set to None if unparseable)
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
    Parses basic data from topic information available in board index (excluding title information)
    :param input_topic: dict containing extracted data for one topic
    :return: dict containing extracted data (values set to None if unparseable)
    """
    basic_data = {'topic_id': None, 'creator': None, 'creator_id': None, 'views': None, 'replies': None, 'board': None,
                  'board_accessed': None, 'title': None}

    # parse for topic id
    if 'topic_link' in input_topic and input_topic['topic_link']:
        basic_data['topic_id'] = input_topic['topic_link'].split('=')[-1].split('.')[0]
    else:
        raise ValueError("missing required topic id")

    # parse for creator info
    if 'creator' in input_topic and input_topic['creator']:
        basic_data['creator'] = input_topic['creator']
    if 'creator_link' in input_topic and input_topic['creator_link']:
        basic_data['creator_id'] = input_topic['creator_link'].split('=')[-1]

    # parse for topic stats
    if 'views' in input_topic and input_topic['views']:
        basic_data['views'] = int(input_topic['views'].split()[0])
    if 'replies' in input_topic and input_topic['replies']:
        basic_data['replies'] = int(input_topic['replies'].split()[0])

    # parse for board number
    if 'url' in input_topic and input_topic['url']:
        basic_data['board'] = input_topic['url'].split("board=")[-1].split('.')[0]

    # parse for access data and title
    if 'board_accessed' in input_topic and input_topic['board_accessed']:
        basic_data['board_accessed'] = input_topic['board_accessed']
    if 'title' in input_topic and input_topic['title']:
        basic_data['title'] = input_topic['title']

    return basic_data


def clean_topic_data(in_topics=None, in_folder=None, in_filepaths=None, out_filepath=None, out_db=None):
    # TODO: update insert functions and schema to handle new stats
    # TODO: unit test
    for topic in in_topics:
        topic_data = mech_io.read_post_json(topic, in_folder)



    pass


def _find_links(raw_links, raw_images):
    out_links = []
    for link in raw_links:
        if link in raw_images:
            continue
        else:
            out_links.append(link)
    return out_links


def find_post_stats(post_data):
    # TODO: docstring
    # TODO: unit test
    num_posts = len(post_data)

    # calculate stats about post creator
    creator_id = post_data[0]['poster_id']
    num_creator_posts = 0
    for post in post_data:
        if post['poster_id'] == creator_id:
            num_creator_posts += 1

    percent_creator_posts = num_creator_posts/num_posts

    num_posters = len({post['poster_id'] for post in post_data})

    # calculate stats for reaching certain post milestones
    topic_created_date = datetime.datetime.fromisoformat(post_data[0]['post_date'])
    post_25_delta = None
    post_50_delta = None
    if len(post_data) >= 25:
        post_25_date = datetime.datetime.fromisoformat(post_data[24]['post_date'])
        post_25_delta = post_25_date - topic_created_date
    if len(post_data) >= 50:
        post_50_date = datetime.datetime.fromisoformat(post_data[49]['post_date'])
        post_50_delta = post_50_date - topic_created_date

    post_stats = {'num_posts': num_posts,
                  'num_posters': num_posters,
                  'num_creator_posts': num_creator_posts,
                  'percent_creator_posts': percent_creator_posts,
                  'post_25_delta': str(post_25_delta),
                  'post_50_delta': str(post_50_delta)}

    return post_stats
