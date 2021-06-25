# analyticsvidhya.com/blog/2021/04/whatsapp-group-chat-analyzer-using-python/

import re
import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def startsWithDateAndTime(text: str):
    pattern ='^([0-9]{2})-([0-9]{2})-([0-9]{4}) ([0-9]{2}):([0-9]{2}) -'
    result = re.match(pattern, text)
    if result:
        return True
    return False

def FindAuthor(s):
    result = re.search(":", s)
    if result:
        return True
    return False

def getDataPoint(line):
    splitLine = line.split(' - ')
    dateTime = splitLine[0]
    date, time = dateTime.split(' ')
    message = ' '.join(splitLine[1:]).replace('\u200e', '')
    if FindAuthor(message):
        splitMessage = message.split(': ')
        author = splitMessage[0]
        message = ' '.join(splitMessage[1:])
    else:
        author = None
    return date, time, author, message

def check_feli(word_list: list, message: str) -> bool:
    for word in word_list:
        if word.lower() in message.lower():
            return True
    return False


st.set_page_config(layout="wide", page_title="Whatsapp felicitatie checker")
st.title("Whatsapp felicitatie checker")

uploaded_file = st.file_uploader("Upload Files", type=['txt'])
#raw_text = open('WhatsApp-chat met DBS Selectie 2020_2021.txt', 'r', encoding='utf-8').read()

word_list = ['gefeliciteerd', 'proficiat']


if uploaded_file is not None:
    parsedData = [] # List to keep track of data so it can be used by a Pandas dataframe
    raw_text = str(uploaded_file.read(), "utf-8")
    #st.write(raw_text)  # works
    lines = raw_text.split('\n')

    lines = lines[3:]
    date_list = []
    time_list = []
    author_list = []
    message_list = []

    for line in lines:
        messageBuffer = []
        date, time, author = None, None, None
        line = line.strip()
        if startsWithDateAndTime(line):
            date, time, author, message = getDataPoint(line)
            date_list.append(date)
            time_list.append(time)
            author_list.append(author)
            message_list.append(message)

    df = pd.DataFrame({"Date": date_list, "Time": time_list, "Author": author_list, "Message": message_list}) # Initialising a pandas Dataframe.

    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')




    df['Felicitatie'] = df['Message'].map(lambda x: check_feli(word_list=word_list, message=x))


    c1, c2, c3 = st.beta_columns(3)

    #with c1:
    #    #  messages over time
    #    z = df['Date'].value_counts().sort_index()
    #    fig, ax = plt.subplots()
    #    ax.set_title('Aantal berichtjes')
    #    ax.plot(z)

    #    st.pyplot(fig)

    with c1:
        # highest absolute feli
        feli_names_abs = (df.loc[df['Felicitatie']]
                          .groupby(['Author'])
                          .size()
                          .reset_index(name='Naam')
                          .sort_values('Naam', ascending=False)
                          .head(10)
                          .sort_values('Naam', ascending=True)
                          .set_index('Author'))

        fig, ax = plt.subplots()
        ax.set_title('Hoogst absoluut aantal felicitaties')
        ax.barh(feli_names_abs.index, feli_names_abs['Naam'])
        ax.set_xlabel('Aantal felicitaties')

        st.pyplot(fig)

    with c2:
        # highest relative feli
        nd_names = len(df['Author'].unique())
        feli_names_rel = (df
                          .groupby('Author')
                          .agg({'Felicitatie': [np.mean, np.sum],
                                "Date": 'count'})
                          .sort_values(('Date', 'count'), ascending=False)
                          .head(int(nd_names / 2)) # in top 50% of most messages
                          .sort_values(('Felicitatie', 'mean'), ascending=False)
                          .head(10)
                          .sort_values(('Felicitatie', 'mean'), ascending=True)
                          )

        fig, ax = plt.subplots()
        ax.set_title('Hoogste percentage felicitaties')
        ax.barh(feli_names_rel.index, feli_names_rel[('Felicitatie', 'mean')]*100)
        ax.set_xlabel('Percentage van de berichten dat felicitatie is')
        fig.show()

        st.pyplot(fig)


    with c3:
        st.markdown('**Hork van de selectie**: veel berichtjes, weinig felicitaties')
        feli_names_hork = (df
                      .groupby('Author')
                       .agg({'Felicitatie': [np.mean, np.sum],
                             "Date": 'count'})
                       .sort_values(('Date', 'count'), ascending=False)
                      .head(int(nd_names / 2)) # in top 50% of most messages
                      .sort_values(('Felicitatie', 'sum'), ascending=True)
                      .head(5)
                      .sort_values(('Felicitatie', 'mean'), ascending=True)
                      )
        feli_names_hork = feli_names_hork.loc[feli_names_hork[('Felicitatie', 'mean')]<=0.20]

        feli_names_hork.columns = ['% feli', 'Aantal feli', 'Aantal berichten']
        feli_names_hork = feli_names_hork[['Aantal berichten', 'Aantal feli', '% feli']]



        st.dataframe(feli_names_hork)

