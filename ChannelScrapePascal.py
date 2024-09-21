from bs4 import BeautifulSoup 
import requests as Req 
import numpy
import json

def GetChannelName(IsShootmania: bool = False):
    Out = ""

    Web = Req.get('https://maniaplanet.com/') 
    S = BeautifulSoup(Web.text, 'lxml') 
    N = "1" if IsShootmania else "2"
    Tags = S.select_one(f"div.col-md-6:nth-of-type({N})").select("span.mp-format")[0].children

    for Tag in Tags:
        Out += Tag.get_text()

    return Out

def GetChannelNameFromId(Id: int = 1):
    try:
        return GetCacheNames()[str(Id)]
    except:
        pass
    Temp = ""
    Web = Req.get(f'https://maniaplanet.com/channels/programs/{Id}')
    S = BeautifulSoup(Web.text, 'lxml') 
    Tag = S.select("div.card-footer")[0].select("a")[0].select("span")[0]
    Tog = Tag.children
    for Elem in Tog:
        Temp += Elem.get_text()
    return Temp

def GetChannelAuthorFromId(Id: int = 1):
    Temp = ""
    Web = Req.get(f'https://maniaplanet.com/channels/programs/{Id}')
    S = BeautifulSoup(Web.text, 'lxml') 
    Tag = S.select("div.d-flex.justify-content-between.align-items-center.small")[0].select("span")[0]
    Tog = Tag.children
    for Elem in Tog:
        Temp += Elem.get_text()
    return Temp.replace('\n', '')

def GetChannelGameFromId(Id: int = 1):
    Web = Req.get(f'https://maniaplanet.com/channels/programs/{Id}')
    S = BeautifulSoup(Web.text, 'lxml') 
    Tag = S.select("h1.d-inline-block.p-1.bg-faded.display-4")[0]
    return "Shootmania" in Tag.get_text()

def GetChannelImageURL(IsShootmania: bool = False):
    CleanImgs = []

    Web = Req.get('https://maniaplanet.com/') 
    S = BeautifulSoup(Web.text, 'lxml') 
    N = 0 if IsShootmania else 1
    Imgs = S.select("img.w-100")

    for Img in Imgs:
        if ("programs" in Img.attrs["src"]):
            CleanImgs.append(Img)

    return CleanImgs[N].attrs["src"]

def GetImageURLFromChannelId(Id: int):
    try:
        return GetCacheURLs()[str(Id)]
    except:
        pass
    Web = Req.get(f'https://maniaplanet.com/channels/programs/{Id}')
    S = BeautifulSoup(Web.text, 'lxml') 
    Tag = S.select("img.w-100")[0]

    return Tag.attrs["src"]

def GetCacheNames():
    with open("cache_names.json") as CacheNamesFile:
        return json.load(CacheNamesFile)

def GetCacheURLs():
    with open("cache_urls.json") as CacheURLsFile:
        return json.load(CacheURLsFile)

def GetSched(IsShootmania: bool = False):
    CacheNames = {}
    CacheURLs = {}
    Out = []
    OutReal = []
    Urls = []
    OutRealButActuallyThisTime: dict[str, list[dict[str, dict[str, str]]]] = {}
    
    try:
        CacheNames = GetCacheNames()
        CacheURLs = GetCacheURLs()
    except:
        pass

    Web = Req.get('https://maniaplanet.com/channels/trackmania' if not IsShootmania else 'https://maniaplanet.com/channels/shootmania')
    S = BeautifulSoup(Web.text, 'lxml') 
    Tags = S.select("table")[0].select("a")

    for Elem in Tags:
        Out.append(int(Elem.attrs["href"][-3:].replace("/", "")))
    
    print("done getting urls")

    for Num in Out:
        Temp = ""

        try:
            Urls.append(CacheURLs[str(Num)])
            print(f"using cacheurls: {CacheURLs[str(Num)]} ({Num})")
        except KeyError:
            CacheURLs[str(Num)] = GetImageURLFromChannelId(Num)
            Urls.append(CacheURLs[str(Num)])

        try:
            Temp = CacheNames[str(Num)]
            print(f"using cachenames: {Temp} ({Num})")
            OutReal.append(Temp)
        except KeyError:
            Web = Req.get(f'https://maniaplanet.com/channels/programs/{Num}')
            print(f"getting channel {Num}")
            S = BeautifulSoup(Web.text, 'lxml') 
            Tag = S.select("div.card-footer")[0].select("a")[0].select("span")[0]
            Tog = Tag.children
            for Elem in Tog:
                Temp += Elem.get_text()
            print(f"DONE: {Temp}")
            CacheNames[str(Num)] = Temp
            OutReal.append(Temp)
    
    OutReal = numpy.reshape(OutReal, (24, 7))
    Urls = numpy.reshape(Urls, (24, 7))

    for I in range(24):
        for J in range(7):
            try:
                OutRealButActuallyThisTime[J].append({str(I): {OutReal[I][J]: Urls[I][J]}})
            except:
                OutRealButActuallyThisTime[J] = [{str(I): {OutReal[I][J]: Urls[I][J]}}]
        
            OutRealButActuallyThisTime[J].sort(key=lambda Y: int(list(Y)[0]))

    with open("cache_names.json", "w") as CacheNamesFile:
        Dump = json.dumps(CacheNames, indent=4)
        CacheNamesFile.write(Dump)
    
    with open("cache_urls.json", "w") as CacheURLsFile:
        Dump = json.dumps(CacheURLs, indent=4)
        CacheURLsFile.write(Dump)

    return OutRealButActuallyThisTime

def IdExists(Id: int = 1):
    Web = Req.get(f'https://maniaplanet.com/channels/programs/{Id}')
    if Web.status_code == 200:
        return True
    return False