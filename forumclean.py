import datetime
import csv
import regex
import emoji
import pandas as pd
from lark import Lark


def clean_board_data(unclean_data=None, infilepath=None, outfilepath=None, returndf=True):
    """
    Cleans scraped data from forum into more readable format
    :param unclean_data:
    :param infilepath:
    :param outfilepath:
    :param returndf:
    :return: pandas DataFrame of cleaned data
    """
    # TODO: potentially move clean_board_data() to the initial scraping step, break parse_title(s) into own thing

    clean_data = pd.DataFrame()
    if unclean_data:
        if type(unclean_data) is list and type(unclean_data[0]) is dict:
            unclean_data = pd.DataFrame(unclean_data)
    elif infilepath:
        unclean_data = pd.read_csv(infilepath)
    else:
        # TODO: error handling for improper input
        pass

    print(f"Parsing {len(unclean_data.index)} records")

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

    print(f"Parsed {len(clean_data.index)} records")
    if outfilepath:
        clean_data.to_csv(outfilepath)
        print(f"Saved to {outfilepath}")

    if returndf:
        return clean_data
    else:
        return


def parse_title(to_search, title_parser, ic_map):
    """
    Finds thread type indicator, keyset infocodes, and keyset name from thread title
    :param to_search: str to parse as a title
    :param title_parser:
    :param ic_map: dict for changing representation of some infocodes
    :return: tuple(str thread type, str infocode, str set name)
    """
    # TODO: fix docstring for output
    title_tree = title_parser.parse(emoji.demojize(to_search)).children[0]

    producttype = "unknown"
    threadtype = "unknown"
    infocodes = []
    setname = ""

    if title_tree.data == 'keycapthread':
        producttype = "keycaps"
        # print("producttype " + producttype)

    for subtree in title_tree.children:
        if subtree.data == 'threadcode':
            threadtype = subtree.children[0].value.upper()
            # print("threadtype " + threadtype)
        elif subtree.data == 'titlesection':
            for token in subtree.children:
                if token.type == 'ICODE':
                    if token.value.upper() in ic_map:
                        infocodes.append(ic_map[token.value.upper()])
                    else:
                        infocodes.append(token.value.upper())
                else:
                    setname = " ".join([setname, token.value])

            # print("infocodes " + str(infocodes))
            # print("setname " + setname)

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

        threadcode.2: _LEADBLOCK* _BRACO THCODE _BRACC
        titlesection: _LEADBLOCK* _infocode+ NAMEBLOCK+
        invtitlesection: INVNAMEBLOCK+ _infocode+
        endsection.2: (_SEPARATOR | notname) (_SEPARATOR | notname | _ANYBLOCK)*

        _infocode.3: ICODE 
        notname.2: GBSTATUS | /key(cap|set)*s*/i | /GB|groupbuy|(group buy)/i | /ready/i | /\w+shot/i | /update[ds]*/i

        MISCBLOCK: /[\w&]+([\w.:*,&-\\\/]+\w)*/
        NAMEBLOCK: MISCBLOCK
        INVNAMEBLOCK: MISCBLOCK
        _LEADBLOCK: MISCBLOCK
        _ANYBLOCK: /[\w\W]+/

        ICODE: /GMK/i | /PBT/i | /ePBT/i | /EnjoyPBT/i | /IFK/i | /Infinikey/i
               | /MG(?=\W)/i | /Melgeek/i | /SA(?=\W)/i | /SP(?=\W)/i | /SPSA(?=\W)/i | /Signature Plastics/i
               | /HSA/i | /KAT(?=\W)/i | /KAM(?=\W)/i | /DSA/i | /JTK/i | /CRP/i
               | /MDA/i | /XDA/i | /DCS/i
        GBSTATUS: /ship(ping|ed)*/i | /live/i | /clos(ed|ing)*/i | /complet(ed|e|ing)/i | /cancel(ed|led)/i
               | /finish(ed|ing)*/i | /final(ized|izing)*/i | /sort(ed|ing)*/i
               | /production/i | /extras*/i | /hold/i
        THCODE: /\w+/

        _SEPARATOR: /[-:;,+*.\|~\\\/]+/ | _BRACO | _BRACC
        // EMOJI: /:\w+:/
        _BRACO: /[\[{(<「]/
        _BRACC: /[]})>」]/

        %import common.WS
        %ignore WS
        %ignore /[!'"█]/
    '''

    ic_map = {"EPBT": "ePBT", "ENJOYPBT": "ePBT", "INFINIKEY": "IFK", "MELGEEK": "MG", "SPSA": "SA",
              "SIGNATURE PLASTICS": "SP"}

    parser = Lark(title_grammar, start="topic", parser="earley")

    producttypes = []
    threadtypes = []
    icodes = []
    setnames = []

    for title in titles:
        parsed = parse_title(title, parser, ic_map)
        producttypes.append(parsed[0])
        threadtypes.append(parsed[1])
        icodes.append(parsed[2])
        setnames.append(parsed[3])

    return producttypes, threadtypes, icodes, setnames
