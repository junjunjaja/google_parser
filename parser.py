from urllib.request import Request, urlopen
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import pandas as pd
def quilet_parse(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    res = urlopen(req).read()
    bs = BeautifulSoup(res, 'html.parser')
    prob = []
    sol = []
    n = 0
    for i in bs.findAll('span', attrs={'class': 'TermText notranslate lang-en'},recursive=True):
        if n%2 ==0:
            prob.append(i.text)
        else:
            sol.append(i.text)
        n+=1
    return pd.DataFrame([prob,sol]).T.rename(columns = {0:"prob",1:"sol"})

def word_count(data,Word):
    n = 0
    for d in Word:
        if d in data:
            n+=1
    return n

def get_prob_answer(url,state):
    plus = state
    Word = plus.split(" ")
    for i in Word:
        try:
            int(i)
            Word.remove(i)
        except:
            pass
    df = quilet_parse(url)
    pro = df.apply(lambda x: x.apply(lambda x: word_count(x,Word)))["prob"]
    sol = df.apply(lambda x: x.apply(lambda x: word_count(x,Word)))["sol"]
    pro_idx = pro[pro == pro.max()].index.values
    sol_idx = sol[sol == sol.max()].index.values
    def pprint(df,idx):
        for p_i in idx:
            print("Problem -------------------------------------------------")
            for i in df.loc[p_i]["prob"].split(". "):
                print(i, end=".")
                print()
            print("Solution -------------------------------------------------")
            for i in df.loc[p_i]["sol"].split(". "):
                print(i, end=".")
                print()
    if len(pro_idx) <= 2:
        pprint(df, pro_idx)
        return True
    else:
        pprint(df, pro_idx)
        print("Solution으로 찾기 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        pprint(df, sol_idx)
        return False
def google_search(state,get_url = False):
    baseUrl = 'https://www.google.com/search?q='
    plusUrl = "site:quizlet.com" +" "+ state
    url = baseUrl + quote_plus(plusUrl)
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    res = urlopen(req).read()
    bs = BeautifulSoup(res, 'html.parser')
    b = bs.findAll('div', attrs={'class': 'kCrYT'},recursive=True)
    links = []
    for b_ in b:
        for a in b_.find_all('a', href=True):
            if "https://quizlet.com/" in a["href"]:
                try:
                    link = a["href"].split("/url?q=")[1]
                except:
                    link = a["href"].split("/url?q=")[0]
                links.append(link)
                if get_url:
                    continue
                find_ =get_prob_answer(link, state)
                if find_:
                    return True
    if get_url:
        return links
    else:
        return False

if __name__ == "__main__":
    k = "a"
    state = None
    while k != "q":
        if state is None:
            state = input("검색하고자하는 질문 입력하세요 : ")
        google_search(state)
        k = input("Press q to quit 다른 결과는 else를 입력하세요 :")
        if k == "else":
            k2 = "a"
            n = 0
            while k2 != "q":
                n +=1
                link = google_search(state, get_url=True)
                try:
                    get_prob_answer(link[n], state)
                    k2 = input("Press q to quit or 다른 결과는 아무키나 입력하세요 :")
                except:
                    break
        if len(k) >=10:
            state = k
        else:
            state = None
    #url = input("quizlet URL 입력하세요 : ")
    #get_prob_answer(url,state)

else:
    state = "Why are the following “effects” considered efficient market anomalies? Are there rational explanations for these effec"
    l = google_search(state,get_url=True)
    url = l[1]
    get_prob_answer(url, state)

    #url = "https://quizlet.com/120507818/portfolio-analysis-final-1-flash-cards/"
    url = "https://quizlet.com/268677313/chapter-7-capital-asset-pricing-and-arbitrage-pricing-theory-flash-cards/"
    url = l[1]
    get_prob_answer(url, state)
