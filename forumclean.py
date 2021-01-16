import datetime
import csv
import regex
import emoji
import pandas as pd
from lark import Lark


def clean_board_data(unclean_data, filepath=None):
    """
    Cleans scraped data from forum into more readable format
    :param unclean_data:
    :param filepath:
    :return: DataFrame of cleaned data
    """
    # TODO: potentially move clean_board_data() to the initial scraping step, break parse_title into own thing
    clean_data = pd.DataFrame()
    if type(unclean_data) is list and type(unclean_data[0]) is dict:
        unclean_data = pd.DataFrame(unclean_data)

    # parse for topic number
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

    if filepath:
        clean_data.to_csv(filepath)

    return clean_data


def parse_title(to_search, title_parser):
    """
    Finds thread type indicator, keyset infocodes, and keyset name from thread title
    :param to_search: str to parse as a title
    :param title_parser:
    :return: tuple(str thread type, str infocode, str set name)
    """
    # TODO: fix docstring for output
    title_tree = title_parser.parse(emoji.demojize(to_search)).children[0]

    print(title_tree.pretty())

    producttype = "unknown"
    threadtype = "unknown"
    infocodes = []
    setname = ""

    if title_tree.data == 'keycapthread':
        producttype = "keycaps"
        print("producttype " + producttype)

    for subtree in title_tree.children:
        if subtree.data == 'threadcode':
            threadtype = subtree.children[0].value
            print("threadtype " + threadtype)
        elif subtree.data == 'titlesection':
            for token in subtree.children:
                if token.type == 'ICODE':
                    infocodes.append(token.value)
                else:
                    setname = " ".join([setname, token.value])

            print("infocodes " + str(infocodes))
            print("setname " + setname)

    return producttype, threadtype, infocodes, setname


def parse_titles(titles):
    """
    Finds thread type indicator, keyset infocodes, and keyset name for list of thread titles
    :param titles: list[str]
    :return: tuple(list[str] thread type, list[str] infocode, list[str] set name)
    """
    # TODO: fix docstring for output
    # TODO: add tai-hao (and potential variations like SPSA) to list of infocodes
    title_grammar = r'''
        topic: keycapthread | otherthread
        keycapthread.2: threadcode? (titlesection | invtitlesection) endsection?      
        otherthread: threadcode? _ANYBLOCK+

        threadcode: _LEADBLOCK* _BRACO THCODE _BRACC
        titlesection: _LEADBLOCK* _infocode+ NAMEBLOCK+
        invtitlesection: INVNAMEBLOCK+ _infocode+
        endsection: (_SEPARATOR | notname) (_SEPARATOR | notname | MISCBLOCK)*

        _infocode.3: ICODE
        notname.2: GBSTATUS | /key(cap|set)*s*/i | /GB|groupbuy|(group buy)/i | /ready/i | /\w+shot/i | /update[ds]*/i

        MISCBLOCK: /\w+([\w.:,-\\\/]+\w)*/
        NAMEBLOCK: MISCBLOCK
        INVNAMEBLOCK: MISCBLOCK
        _LEADBLOCK: MISCBLOCK
        _ANYBLOCK: /[\w\W]+/

        ICODE: /GMK/i | /PBT/i | /ePBT/i | /EnjoyPBT/ | /IFK/i | /Infinikey/i
               | /MG/i | /Melgeek/i | /SA/ | /SP/i | /SPSA/i | /Signature Plastics/i
               | /HSA/i | /KAT/i | /KAM/i | /DSA/i | /JTK/i | /CRP/i
               | /MDA/i | /XDA/i | /DCS/i
        GBSTATUS: /ship(ping|ed)*/i | /live/i | /clos(ed|ing)*/i | /complet(ed|e|ing)/i | /cancel(ed|led)/i
               | /finish(ed|ing)*/i | /final(ized|izing)*/i | /sort(ed|ing)*/i
               | /production/i | /extras*/i
        THCODE: /\w+/

        _SEPARATOR: /[-:;,.\|~\\\/]+/
        // EMOJI: /:\w+:/
        _BRACO: /[\[{(<]/
        _BRACC: /[]})>]/

        %import common.WS
        %ignore WS
        %ignore /[!'"]/
    '''

    parser = Lark(title_grammar, start="topic", parser="earley")

    producttypes = []
    threadtypes = []
    icodes = []
    setnames = []

    for title in titles:
        parsed = parse_title(title, parser)
        producttypes.append(parsed[0])
        threadtypes.append(parsed[1])
        icodes.append(parsed[2])
        setnames.append(parsed[3])

    return producttypes, threadtypes, icodes, setnames
