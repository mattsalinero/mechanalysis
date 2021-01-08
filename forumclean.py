import datetime
import csv
import regex
import pandas as pd


def clean_board_data(unclean_data, filepath=None):

    clean_data = pd.DataFrame()
    print(str(type(unclean_data)) + str(type(unclean_data[0])))
    if type(unclean_data) is list and type(unclean_data[0]) is dict:
        unclean_data = pd.DataFrame(unclean_data)

    # parse for topic number
    clean_data['topic_id'] = unclean_data['topiclink'].apply(lambda x: x.split('=')[-1].split('.')[0])

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

    print(clean_data.head())
    print(clean_data.info())

    return clean_data


def parse_title(to_search):

    # find bracketed type indicator
    gbreg = regex.compile(r"[[{(](\w*)[]})]")
    gbtype = gbreg.match(to_search)
    if gbtype:
        gbreturn = gbtype.group(1)

    else:
        gbreturn = 'unknown'

    type_set = ['GMK', 'PBT', 'ePBT', 'SA', 'HSA', 'KAT', 'KAM', 'DSA', 'IFK', 'JTK', 'CRP', 'SP', 'MDA', 'XDA', 'MG',
                'INFINIKEY', 'MELGEEK', 'ENJOYPBT']

    sep_set = [r"[:;,.]\s", r"\s[|-~/\\]", r"\sround", r"\sr\d"]

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

    if typereturn:
        sepreg = regex.compile(r"\L<sep_set>",regex.IGNORECASE, sep_set=sep_set)
        sep = sepreg.search(to_search, pos=captype.end())
        titlelimit = [0, len(to_search)]
        if gbtype:
            titlelimit[0] = gbtype.end()
        if sep:
            titlelimit[1] = sep.start()

        title = (to_search[titlelimit[0]:captype.start()] + to_search[captype.end():titlelimit[1]]).strip()

        if not sep:
            title = title.split()[0]

        # define separator regex
        # find separator (if exists)
        # if it exists, grab stripped string between separator and type as title
        # else just grab one word past the type
        # if we can't find anything, set to 'unknown'
        titlereturn = title
    else:
        titlereturn = None

    return gbreturn, typereturn, titlereturn
