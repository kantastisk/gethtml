from flask import Flask
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

@app.route('/')

def getandTransform():

    secList = []
    pList = []
    sidestObj = []
    sidestList = []
    allFactBoxObj = []
    paragraphs = []
    notagList = []
    linkNameList = []
    linkNameObj = []
    credObj = []
    credList = []
    urlList = []
    mergedLinkList = []
    liList = []
    liObj = []
    tweetObj = []
    tweetList = []

    url = 'https://videnskab.dk/teknologi-innovation/nedstyrtende-rumskrot-risikerer-at-ramme-os-hvad-kan-vi-goere-og-hvad-siger'

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)\
     AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15'}

    #retrieve page html
    all_html = requests.get(url, headers=headers)

    #filter text html
    text_html = all_html.text

    #parse text html.
    soup=BeautifulSoup(text_html,'html.parser')

    #save headline
    headline = soup.title
    headline = headline.string

    #save author name
    author = soup.find(class_="author-line__name")
    author = author.get_text()
    author = author.strip("\n")

    #save subheader name
    undRubrik = soup.find(class_="field field-field-lead article-content__summary")
    undRubrik = undRubrik.get_text()
    undRubrik = undRubrik.strip("\n")

    #create h2 sections list
    converter = ""
    secList = soup.find_all("h2")
    for line in secList:
        converter += line.get_text() + "\n"
    secList = converter.splitlines(False)

    #remove unneeded h2 section list items
    for i in reversed(secList):
        if i != "Kilder":
            secList.pop(-1)
        else:
            secList.pop(-1)
            break

    #remove non breaking space in h2 sections list

    secList = [item.replace("\xa0", " ") for item in secList]

    #list all paragraphs + h2 (create list from obj)
    converter = ""
    pObj = soup.find_all(['p','h2','li'])
    for line in pObj:
        converter += line.get_text() + "\n"
    pList = converter.splitlines(True)

    #create list of specific bullet list items
    converter = ""
    ariaObj = soup.find_all(attrs={"aria-level" : "1"})
    for line in ariaObj:
        converter += line.get_text() + "\n"
    ariaList = converter.splitlines(True)

    #create list of all li items
    converter = ""
    liObj = soup.find_all('li')
    for line in liObj:
        converter += line.get_text() + "\n"
    liList = converter.splitlines(True)

    #create removal list as liList - ariaList
    toRm = []
    for line in liList:
        if line not in ariaList:
            toRm.append(line)

    #filter pList by removal list
    ppList = []
    for line in pList:
        if line not in toRm:
            ppList.append(line)
    pList = ppList

    #create fact box list (list from obj)
    converter = ""
    if "factbox factbox--accordion" in text_html:
        allFactBoxObj = soup.find_all(class_="factbox factbox--accordion")
    for line in allFactBoxObj:
        converter += line.get_text() + "\n"
    allFactBoxList = converter.splitlines(True)

    #create tweet list (list from obj)
    converter = ""
    if "class=\"twitter-tweet\"" in text_html:
        tweetObj = soup.find_all(class_="twitter-tweet")
    for line in tweetObj:
        converter += line.get_text() + "\n"
    tweetList = converter.splitlines(True)

    #create side story list (list from obj)
    converter = ""
    if "field field-field-side-story side-story" in text_html:
        sidestObj = soup.find(class_="field field-field-side-story side-story").find_all("p")
    for line in sidestObj:
        converter += line.get_text() + "\n"
    sidestList = converter.splitlines(True)

    #create evidensbaromter list (from obj)
    converter = ""
    if "field credibility field-field-credibility-source" in text_html:
        credObj = soup.find(class_="field credibility field-field-credibility-source").find_all("p")
    for line in credObj:
        converter += line.get_text() + "\n"
    credList = converter.splitlines(True)

    #create link name list
    converter = ""
    for link in soup.find_all("a", class_="node-embed"):
        linkNameObj.append(link)
    for linkname in linkNameObj:
        converter += linkname.get_text() + "\n"
    linkNameList = converter.splitlines(False)

    #remove empty link name items, if any
    linkNameList[:] = [item for item in linkNameList if item != '']

    #create link url list
    for link in linkNameObj:
        urlList.append("https:" + link.get('href'))

    #remove empty link url items, if any
    urlList[:] = [item for item in urlList if item != '']

    #remove empty evidens list items, if any
    credList[:] = [item for item in credList if item != '']

    #merge name- and url lists
    for linknumber in range(len(linkNameList)):
        combine = linkNameList[linknumber] + "\n" + urlList[linknumber] + "\n\n"
        mergedLinkList.append(combine)

    #exclude factbox + side story + evidensbarometer list
    for line in pList:
        if line not in allFactBoxList:
            if line not in sidestList:
                if line not in credList:
                    if line not in tweetList:
                        notagList.append(line)

    #remove extra newline
    notagList[:] = [item for item in notagList if item != '\n']

    #remove all below Kilder
    for i in reversed(notagList):
        if i != "Kilder\n":
            notagList.pop(-1)
        else:
            notagList.pop(-1)
            break

    #insert bullets in front of aria elements
    for line in range(len(notagList)):
        if notagList[line] in ariaList:
            notagList[line] = "• " + notagList[line]

    #remove baddies
    notagList[:] = [item for item in notagList if 'Annonce:' not in item]
    notagList[:] = [item for item in notagList if 'Foto:' not in item]
    notagList[:] = [item for item in notagList if 'Grafik:' not in item]
    notagList[:] = [item for item in notagList if 'Figur:' not in item]
    notagList[:] = [item for item in notagList if 'Illustration:' not in item]
    notagList[:] = [item for item in notagList if 'Billede:' not in item]
    notagList[:] = [item for item in notagList if 'Video:' not in item]
    notagList[:] = [item for item in notagList if 'Klik her' not in item]
    notagList[:] = [item for item in notagList if 'marketing-cookies' not in item]
    notagList[:] = [item for item in notagList if 'Kilde:' not in item]

    #remove unicode nbsp in result list
    for line in range(len(notagList)):
        notagList[line] = notagList[line].replace("\xa0", " ")

    #capitalize h2 sections + add links above them
    h2Index = []
    counter = 0
    secList = [item + "\n" for item in secList] #needed for full match
    for line in range(len(notagList)):
        for h2 in secList:
            if h2 == notagList[line]:
                capitalize = notagList[line]
                notagList[line] = capitalize.upper()
                h2Index.append(line)
                if len(mergedLinkList) >= counter+1:
                    notagList.insert(line,mergedLinkList[counter])
                counter += 1

    #add newlines above h2 sections
    counter = 0
    for i in h2Index:
        notagList.insert(i+counter,"\n")
        counter += 1

    #add author, undRubrik, headline
    notagList.insert(0, "Af: " + author + ", Videnskab.dk" + "\n\n")
    notagList.insert(0, undRubrik + "\n\n")
    notagList.insert(0, headline + "\n\n")

    #convert to string
    notagStr = ""
    for i in notagList:
        notagStr += i

    #fix no break space + trailing newlines + læs også
    notagStr = notagStr.replace("\xa0"," ")
    notagStr = notagStr.replace("Læs også:","Læs mere på Videnskab.dk:")
    notagStr = notagStr.strip("\n")

    return(notagStr)

if __name__ == '__main__':
    app.run()
