

from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template, request

def getandTransform(url):

    def cleanConvert(toConvert):
      converter = ""
      for line in toConvert:
          converter += line.strip("\n") + "\n"
      output = converter.splitlines(True)
      return(output)

    def rmNonBreaking(toConvert):
      output = []
      for line in toConvert:
          output.append(line.replace("\xa0", " "))
      return(output)

    # lav formaterede lister til identifikation og eksklusion
    def makeList(mode, clss, tag, attr, soup):

      listClear = []

      if mode == "attr":
          tagObj = soup.find_all(tag, class_=clss)
          for line in tagObj:
              listClear.append(line.get(attr))
      elif mode == "class":
          if clss == "embed-link":  # nødvendig til link navn
              tagObj = soup.find_all(class_=clss)
              for line in tagObj:
                  listClear.append(line.get_text())
          else:
              # bruges kun til alm. article body
              for classLine in soup.find_all(class_=clss):
                  for pLine in classLine.find_all(['p', 'li', 'h2']):
                      listClear.append(pLine.get_text())
      elif mode == "tag":
          tagObj = soup.find_all(tag)
          for line in tagObj:
              listClear.append(line.get_text())
      elif mode == "classTag":
          for classLine in soup.find_all(class_=clss):
              for pLine in classLine.find_all(tag):
                  listClear.append(pLine.get_text())


      returnList = cleanConvert(listClear)

      return(returnList)

    #url = 'https://videnskab.dk/forskerzonen/naturvidenskab/forhistoriske-froeer-i-massegrav-doede-af-for-meget-sex'

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
    AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15'}

    # retrieve page html
    all_html = requests.get(url, headers=headers)

    # filter text html
    text_html = all_html.text

    # parse text html.
    soup = BeautifulSoup(text_html, 'html.parser')

    # save headline
    if "field field-title-field article-content__title" in text_html:
      headline = soup.title
      headline = headline.string
    elif "field field-field-body other-media__body" in text_html:
      tempString = ""
      headline = makeList('classTag', 'field field-title-field other-media__title', 'div', '', soup)
      if len(headline) == 2:  # if div results in two copies, delete one
          headline.pop(-1)
      for line in headline:
          tempString += line.strip("\n")
      headline = tempString
    # save author name
    noAuthor = 0
    if "author-line__name" in text_html:
      author = soup.find(class_="author-line__name")
      author = author.get_text()
      author = author.strip("\n")
    if author == "Videnskab.dk redaktion":
      author = "Af: Videnskab.dk\n\n"
      noAuthor = 1

    # save subheader name
    if "field field-field-lead article-content__summary" in text_html:
      undRubrik = soup.find(class_="field field-field-lead article-content__summary")
      undRubrik = undRubrik.get_text()
      undRubrik = undRubrik.strip("\n")
    else:
      undRubrik = ""

    # extract full article body
    detectAS = 0
    if "field field-field-body article-content__body" in text_html:
      fullParagraph = soup.find(
          'div', class_="field field-field-body article-content__body").find_all(['p', 'h2', 'li'])
    elif "field field-field-body other-media__body" in text_html:
      fullParagraph = soup.find(
          'div', class_="field field-field-body other-media__body").find_all(['p', 'h2', 'li'])
      detectAS = 1  # inform if article is AS

    # extract specialized lists using makeList()
    liParagraph = makeList('tag', '', 'li', '', soup)  # identify list items
    urlNameList = makeList('class', 'embed-link', '', '', soup)  # identify link names
    urlList = makeList('attr', 'node-embed', 'a', 'href', soup)  # identify link urls
    h2List = makeList('tag', '', 'h2', '', soup)  # identify h2 sections

    # remove empty newlines in liParagraph
    liParagraph[:] = [item for item in liParagraph if item != '\n']

    # extract exclusion lists using makeList()
    exclusionList = []
    exclusionList += makeList('class', 'factbox factbox--accordion', '', '', soup) # add factboxes to exclusion
    exclusionList += makeList('class', 'factbox is-open', '', '', soup) # add tweets to exclusion
    exclusionList += makeList('class', 'twitter-tweet', '', '', soup) # add tweet list to exclusion
    exclusionList += makeList('class', 'twitter-timeline twitter-timeline-rendered', '', '', soup)
    exclusionList += makeList('class', 'instagram-media', '', '', soup) # add media12 to exclusion
    exclusionList += makeList('class', 'media media-element-container media-columns_12_12', '', '', soup) # add media 6 to exclusion
    exclusionList += makeList('class', 'media media-element-container media-columns_6_12', '', '', soup) # add 'Annonce' to exclusion
    exclusionList += makeList('class', 'disclaimer', '', '', soup)
    #RIDDLE TING BLIVER IKKE FJERNET...

    # remove tags+newlines from main list
    cleaner = []
    for line in fullParagraph:
      cleaner.append(line.get_text())
    cleaner = cleanConvert(cleaner)

    # replace non-breaking space
    cleaner = rmNonBreaking(cleaner)
    exclusionList = rmNonBreaking(exclusionList)
    liParagraph = rmNonBreaking(liParagraph)
    h2List = rmNonBreaking(h2List)
    urlNameList = rmNonBreaking(urlNameList)
    urlList = rmNonBreaking(urlList)

    # apply exclusion list to main list
    formatList = []
    for line in cleaner:
      if line not in exclusionList:
          formatList.append(line)

    # perform key word based exclusion
    formatList[:] = [item for item in formatList if 'Meningsmålingsgenerator - kørt af Riddle' not in item]
    formatList[:] = [item for item in formatList if 'A Twitter List by' not in item]
    formatList[:] = [item for item in formatList if 'Annonce:' not in item]
    formatList[:] = [item for item in formatList if 'Foto:' not in item]
    formatList[:] = [item for item in formatList if 'Fotos:' not in item]
    formatList[:] = [item for item in formatList if 'Grafik:' not in item]
    formatList[:] = [item for item in formatList if 'Figur:' not in item]
    formatList[:] = [item for item in formatList if 'Illustration:' not in item]
    formatList[:] = [item for item in formatList if 'Billede:' not in item]
    formatList[:] = [item for item in formatList if 'Billeder:' not in item]
    formatList[:] = [item for item in formatList if 'Video:' not in item]
    formatList[:] = [item for item in formatList if 'Klik her' not in item]
    formatList[:] = [item for item in formatList if 'marketing-cookies' not in item]
    formatList[:] = [item for item in formatList if 'Kilde:' not in item]

    # add dots before list items(ordered/unordered)
    liWarn = 0
    for count, line in enumerate(formatList):
      if line in liParagraph:
          formatList[count] = "• " + line
          liWarn = 1

    # add https to urls
    for count, line in enumerate(urlList):
      urlList[count] = "https:" + line

    # unify urlList + urlNameList
    readAlsoList = []
    linksFound = 0
    for count in range(len(urlNameList)):
      readAlsoList.append(urlNameList[count] + urlList[count])
      linksFound = 1

    # capitalize h2 sections, insert links above them
    readAlsoCounter = 0
    if detectAS == 0:
      h2count = 0
      for count, line in enumerate(formatList):
          if line in h2List:
              # formatList[count] = line.isupper()
              h2count += 1
              formatList[count] = "\n" + line
              if readAlsoCounter <= len(readAlsoList)-1:
                  formatList.insert(
                      count, "\nLæs mere på Videnskab.dk: " + readAlsoList[readAlsoCounter])
                  readAlsoCounter += 1

    # if AS, insert two links 1/3 and 6/7 through article
    elif detectAS == 1:
      firstLinkIndex = int(len(formatList)*(1/3))  # first link 1/3 through
      if len(formatList) in range(0, 6):
          secondLinkIndex = int(len(formatList)*(6/7))
      elif len(formatList) in range(7, 11): # insert 2nd link further up in longer articles
          secondLinkIndex = int(len(formatList)*(5/6))
      else:
          secondLinkIndex = int(len(formatList)*(3/4))
      for count in range(1):
          if readAlsoCounter <= len(readAlsoList)-1:
              formatList.insert(firstLinkIndex, "\nLæs mere på Videnskab.dk: " + readAlsoList[readAlsoCounter] + "\n")
              readAlsoCounter += 1
              # if len(formatList) <= 7:
              formatList.insert(secondLinkIndex, "\nLæs mere på Videnskab.dk: " + readAlsoList[readAlsoCounter] + "\n")
              # else:
              #     formatList.insert(secondLinkIndex, "\nLæs mere på Videnskab.dk: " + readAlsoList[readAlsoCounter] + "\n")
              readAlsoCounter += 1

    # put surplus embed links at end of formatList
    remainingLinks = len(readAlsoList) - readAlsoCounter
    if remainingLinks > 0:
      formatList.append("\nAndre artikler på Videnskab.dk:\n")
      for count in range(remainingLinks):
          formatList.append("\n" + readAlsoList[-1])
          readAlsoList.pop(-1)

    # insert header,subheader,author
    if noAuthor != 1:
      formatList.insert(0, f"Af: {author}, Videnskab.dk\n\n")
    else:
      formatList.insert(0, author)
    formatList.insert(0, f"{undRubrik}\n\n")
    formatList.insert(0, f"{headline}\n\n")

    # remove leading spaces
    for count, line in enumerate(formatList):
      formatList[count] = line.strip(" ")
    # remove lone newlines
    formatList[:] = [item for item in formatList if item != '\n']
    formatList[:] = [item for item in formatList if item != '\n\n']
    formatList[:] = [item for item in formatList if item != '\n\n\n']

    # create string from formatList
    formatString = ""
    for line in formatList:
      formatString += line

    # check/construct warnings
    warnings = ""
    if detectAS == 1:
      warnings += "Artiklen er behandlet som en AS\n\n"
    if headline == "":
      warnings += "Ingen overskrift fundet\n\n"
    if undRubrik == "":
      if detectAS == 0:
          warnings += "Ingen underrubrik fundet\n\n"
    if author == "":
      warnings += "Forfatter angivet som Videnskab.dk\n\n"
    if h2List == "":
      warnings += "Ingen mellemrubrikker fundet (og ingen 'Læs også'-links indsat)\n\n"
    if linksFound == 0:
      warnings += "Ingen 'Læs også'-links fundet\n\n"
    if detectAS == 0:
      if len(readAlsoList) < h2count:
          warnings += "Der er indsat færre 'Læs også'-links end mellemrubrikker\n\n"
    if liWarn == 1:
      warnings += "Artiklen indeholder liste-elementer, markeret med •\n\n"
    if author == "Thomas Hoffmann":
      warnings += "FORFATTEREN ER THOMAS! STOL IKKE PÅ LORTET!!"
    if warnings == "":
      warnings += "Ingen bemærkninger fundet"

    # if formatString != "":
      # output.insert(1.0, warnings)


    return(formatString)

app = Flask(__name__)

@app.route('/', methods = ['GET','POST'])

def geturl():
    return render_template('geturl.html')

@app.route('/showresult', methods = ['GET','POST'])

def showresult():
    url = request.form['url']
    output = getandTransform(url)
    return render_template('result.html', output=output)

if __name__ == "__main__":
    app.run(debug=True)
