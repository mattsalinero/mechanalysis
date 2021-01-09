import datetime
import csv
import regex
import pandas as pd


def clean_board_data(unclean_data, filepath=None):
    """
    Cleans scraped data from forum into more readable format
    :param unclean_data:
    :param filepath:
    :return: DataFrame of cleaned data
    """
    clean_data = pd.DataFrame()
    print(str(type(unclean_data)) + str(type(unclean_data[0])))
    if type(unclean_data) is list and type(unclean_data[0]) is dict:
        unclean_data = pd.DataFrame(unclean_data)

    # parse for topic number
    clean_data['topic_id'] = unclean_data['topiclink'].apply(lambda x: x.split('=')[-1].split('.')[0])

    # parse information from title
    clean_data['thread_type'], clean_data['code'], clean_data['name'] = parse_titles(unclean_data['title'])

    # parse for creator info
    clean_data['creator'] = unclean_data['creator']
    clean_data['creator_id'] = unclean_data['creatorlink'].apply(lambda x: x.split('=')[-1])

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


def parse_title(to_search):
    """
    Finds thread type indicator, keyset infocodes, and keyset name from thread title
    :param to_search: str to parse as a title
    :return: tuple(str thread type, str infocode, str set name)
    """
    # TODO: improve implementation to use actual parser with more sophisticated grammar
    to_search = to_search.strip('" ')

    # find bracketed type indicator
    gbreg = regex.compile(r"[[{(](\w*)[]})]")
    gbtype = gbreg.match(to_search)
    if gbtype:
        gbreturn = gbtype.group(1)

    else:
        gbreturn = 'unknown'

    # TODO: add tai-hao (and potential variations like SPSA) to list of infocodes
    type_set = ['GMK', 'PBT', 'ePBT', 'SA', 'HSA', 'KAT', 'KAM', 'DSA', 'IFK', 'JTK', 'CRP', 'SP', 'MDA', 'XDA', 'MG',
                'INFINIKEY', 'MELGEEK', 'ENJOYPBT']

    sep_set = [r"[:;,.]\s", r"\s[-|~/\\[{(]", r"\sround", r"\sr\d"]

    # find main/first info code (for keycap)
    # TODO: add support for multiple infocodes
    typereg = regex.compile(r"\b\L<type_set>\b", regex.IGNORECASE, type_set=type_set)
    captype = typereg.search(to_search)
    if captype:
        typereturn = captype.group()
    else:
        typereturn = None
    # types = typereg.finditer(to_search)
    # typereturn = []
    # for captype in types:
    #     typereturn.append(captype.group())

    # if we found a code, find likely keyset name in title
    if typereturn:
        # tries to find likely separator between set name and status updates
        # sepreg = regex.compile(r"\L<sep_set>", regex.IGNORECASE, sep_set=sep_set)
        sepreg = regex.compile(r"\s[-|~/\\[{(]|[:;,.]\s", regex.IGNORECASE)
        sep = sepreg.search(to_search, pos=5)

        # get string between initial [] identifier and separator(if any), excluding info code
        titlelimit = [0, len(to_search)]
        if gbtype:
            titlelimit[0] = gbtype.end()
        if sep:
            titlelimit[1] = sep.start()
        setname = (to_search[titlelimit[0]:captype.start()] + to_search[captype.end():titlelimit[1]]).strip()

        # if no separator, just take first word
        if sep is None:
            setname = setname.split()[0]

        namereturn = setname
    else:
        namereturn = None

    return gbreturn, typereturn, namereturn


def parse_titles(titles):
    """
    Finds thread type indicator, keyset infocodes, and keyset name for list of thread titles
    :param titles: list[str]
    :return: tuple(list[str] thread type, list[str] infocode, list[str] set name)
    """
    threadtypes = []
    capcodes = []
    setnames = []

    for title in titles:
        parsed = parse_title(title)
        threadtypes.append(parsed[0])
        capcodes.append(parsed[1])
        setnames.append(parsed[2])

    return threadtypes, capcodes, setnames
