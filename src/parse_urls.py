import requests
import re
import lxml
from collections import namedtuple
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse
import logging


def dict_merge(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.iteritems():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]
    return dct
    

def GetBaseSpecName(spec):
    specs = {
        "mesmer": ["chronomancer", "mirage"],
        "ranger": ["druid","soulbeast"],
        "warrior": ["berserker", "spellbreaker"],
        "guardian": ["firebrand","dragonhunter"],
        "revenant": ["renegade","herald"],
        "thief": ["daredevil","deadeye"],
        "engineer": ["scrapper","holosmith"],
        "elementalist": ["weaver","tempest"],
        "necromancer": ["scourge", "reaper"]
    }
    spec = spec.lower().strip()
    logger.warning("Compare data for base spec : " + spec)
    matchspec = False
    for base in specs:
        logger.debug("comparing " + spec + " with " + base + " elites specs")
        for elite in specs[base]:
            logger.debug("comparing " + spec + " with " +
                         elite)
            if spec == elite:
                logger.warning("elite found : " + elite)
                matchspec = base
    logger.warning("found base spec : " + matchspec)
    return matchspec

def GetEliteSpecName(data):
    specs = [
        "mesmer","chronomancer", "mirage",
        "ranger","druid","soulbeast",
        "warrior", "berserker", "spellbreaker",
        "guardian","firebrand","dragonhunter",
        "revenant","renegade","herald",
        "thief","daredevil","deadeye",
        "engineer","scrapper","holosmith",
        "elementalist","weaver","tempest",
        "necromancer","scourge","reaper",
    ]
    data = data.lower().strip()
    logger.warning("Compare data for elite spec : " + data)
    matchspec = False
    for elem in specs:
        logger.debug("compare with " + elem + ": " + str(data.find(elem)))
        if data.find(elem) > 0:
            matchspec = elem
    logger.warning("found elite spec : " + matchspec)
    return matchspec

def GetSnowcrows(url):
    request_body = requests.get(
        url).text
    GetSnowcrowsTitleBuild(request_body)
    #GetSnowcrowsBuild(request_body)

def GetSnowcrowsBuild(request_body):
    soup = BeautifulSoup(request_body, "lxml")
    for search in soup.find_all('input'):
    #print(str(search['value']))
        regexp = re.compile(r'\[\&.*\=\]')
        if bool(regexp.match(str(search['value']))):
            return(str(search['value']))

def GetSnowcrowsTitleBuild(request_body):
    soup = BeautifulSoup(request_body, "lxml")
    #print(soup)
    #search = soup.find_all("a", href=^"javascript://")
    #search = soup.find_all("a", {"href": "javascript://"})
    for a in soup.find_all(re.compile("^tabs")):
        print("Found the URL:", a)
    #if len(search) >= 1:
    #print(search)

def GetLuckyNoobsBuild(url):
    request_body = requests.get(
        url).text
    soup = BeautifulSoup(request_body, "lxml")
    builds = {}
    for search in soup.find_all('input'):
        id = search['id']
        tpl_code = search["value"]
        for button in soup.find_all("button", "ln-guide-button"):
            try:
                if re.match("onTemplateCopy(.*"+id+".*)", button['onclick']):
                    name = button.string.replace(" - Copy", "").strip()
                    logger.info("Found buildcode : " +
                                 tpl_code + "for build name : " + name)
                    builds[name] = tpl_code
            except:pass
    return builds

def ParseLuckyNoobsBuildsNavBar(url):
    logger.debug("Getting URL : " + url)
    request_body = requests.get(
        url).text
    soup = BeautifulSoup(request_body, "lxml")
    search = soup.find("div", "uk-navbar-center")
    logger.debug("Found navbar links" + str(search))
    spec = {}
    build_elite_spec = soup.find("h3", "ln-general-description-header2")
    elitespec = GetEliteSpecName(
        build_elite_spec.get_text().replace("-Overview", "").strip())
    logger.debug("Found EliteSpec : " + str(elitespec))
    spec[elitespec] = {}
    spec[elitespec]["raid"] = {}
    for build_type in search.find_all("a"):
        buildname = build_type.get_text().strip()
        buildurl = build_type.get('href')
        logger.info("Found buildname << " +
                     buildname + " >> at URL : " + buildurl)
        spec[elitespec]["raid"][buildname] = {}
        spec[elitespec]["raid"][buildname]["builds"] = GetLuckyNoobsBuild(buildurl)
        spec[elitespec]["raid"][buildname]["url"] = buildurl
    return spec

def ParseLuckyNoobSite():
    logger.info("Parsing Lucky Noob Website")
    f = open('lucky-noobs-urls.json', "r")
    datas = json.loads(f.read())
    roles = {}
    for data in datas.items():
        role = data[0]
        logger.info("Parsing now Role : " + role)
        roles[role] = ParseLuckyNoobsBuildsNavBar(data[1])
        logger.info("Ended Parsing Role : " + role)
        logger.info("-----------------------------------")
    return roles

#def BuildJson():
#    outputdict = {}
#    f = open('url_list.json', "r")
#    BuildsUrlListData = json.loads(f.read())
#    for role in BuildsUrlListData:
#        print("Role : " + role)
#        outputdict[role] = {}
#        for spec in BuildsUrlListData[role]:
#            #print("Spec : " + spec)
#            outputdict[role][spec] = {}
#            for gamemode in BuildsUrlListData[role][spec]:
#                #print("Gamemode : " + gamemode)
#                outputdict[role][spec][gamemode] = {}
#                for url in BuildsUrlListData[role][spec][gamemode]:
#                    #results = GetBuildsFromSite(url)
#                    #print(results)
#                    #outputdict[role][spec][gamemode] = results
#    f.close()
#    outputjson = json.dumps(outputdict, indent=4)
#    print(outputjson)

def ParseDiscretizeSite():
    logger.info("Parsing Discretize Website")
    baseurl = "https://discretize.eu"
    urlbuilds = "https://discretize.eu/builds"
    logger.debug("Getting URL : " + urlbuilds)
    request_body = requests.get(
        urlbuilds).text
    soup = BeautifulSoup(request_body, "lxml")
    search = soup.select('a[href^="/builds/"]')
    #logger.debug("Found URLs matching builds : " + str(search))
    with open('builds_tpl.json') as json_file:
        build = json.load(json_file)
    for url in search:
        link = url.get('href')
        logger.info("Found build to parse at url : " + baseurl + link)
        buildname = BuildNameDiscretize(baseurl + link)
        elitespec = GetEliteSpecName(buildname)
        basespec = GetBaseSpecName(elitespec)
        logger.info("Found buildname " + buildname + " with elitespec : " + elitespec + " and basespec " + basespec)
        build[basespec][elitespec]["fractals"][buildname] = {}
        build[basespec][elitespec]["fractals"][buildname]["builds"] = {}
        build[basespec][elitespec]["fractals"][buildname]["builds"][buildname] = ParseDiscretizeBuildCode(
            baseurl + link)
        build[basespec][elitespec]["fractals"][buildname]["url"] = baseurl + link
    return build

def BuildNameDiscretize(url):
    request_body = requests.get(
        url).text
    soup = BeautifulSoup(request_body, "lxml")
    search = soup.select_one('h1[class*="jss98"]')
    buildname = search.get_text()
    return buildname

def ParseDiscretizeBuildCode(url):
    request_body = requests.get(
        url).text
    soup = BeautifulSoup(request_body, "lxml")
    search = soup.select_one('h1[class*="jss98"]')
    buildname = search.get_text()
    code = soup.find('code', 'jss166').get_text()
    logger.info("Found buildcode : " + code)
    return code

def ppjson(data):
    print(json.dumps(data, indent=4))

# create logger
logger = logging.getLogger('URL_PARSER')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

allbuilds = {}

LuckyNoobsBuilds = ParseLuckyNoobSite()
print(json.dumps(LuckyNoobsBuilds, indent=4))
DiscretizeBuilds = ParseDiscretizeSite()
print(json.dumps(DiscretizeBuilds, indent=4))

#allbuilds.update(LuckyNoobsBuilds)
#allbuilds.update(DiscretizeBuilds)
#print(json.dumps(allbuilds, indent=4))