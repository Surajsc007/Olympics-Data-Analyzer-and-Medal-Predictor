import streamlit as st
import pandas as pd
import preprocessor,helper
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import pickle
import numpy as np
import time
#from tensorflow import keras


modelrfc = pickle.load(open("modelrfc.pkl","rb"))
modellr = pickle.load(open("modellr.pkl","rb"))
#modelnn = pickle.load(open("modelnn.pkl","rb"))
transformer = pickle.load(open("transformer.pkl","rb"))

df = pd.read_csv("athlete_events.csv")
region_df = pd.read_csv("noc_regions.csv")

df = preprocessor.preprocess(df,region_df)

st.sidebar.title("Olympics Data Analyzer and Predictor")
st.sidebar.image('https://camo.githubusercontent.com/d7a9083432f8e475816a51ccc485dfabf2c50e81b44996014ddefc2abe40f5e7/68747470733a2f2f75706c6f61642e77696b696d656469612e6f72672f77696b6970656469612f636f6d6d6f6e732f7468756d622f352f35632f4f6c796d7069635f72696e67735f776974686f75745f72696d732e7376672f3132303070782d4f6c796d7069635f72696e67735f776974686f75745f72696d732e7376672e706e67')
user_menu = st.sidebar.radio(
    'Select an Option',
    ('Medal Tally',"Medal Predictor",'Overall Analysis','Country-wise Analysis','Athlete-wise Analysis',"About")
)


if user_menu == "Medal Tally":
    st.header("Medal Tally (From Athens 1896 to Rio 2016)")
    years,country = helper.country_year_list(df)
    selected_year = st.selectbox("Select Year",years)
    selected_country = st.selectbox("Select Country", country)

    medal_tally = helper.fetch_medal_tally(df,selected_year,selected_country)
    medal_tally.rename(columns = {"region":"Country"},inplace=True)
    if selected_year == "Overall" and selected_country == "Overall":
        st.title("Overall Medal Tally")
    if selected_year != "Overall" and selected_country == "Overall":
        st.title("Medal Tally in " + str(selected_year) + " Olympics")
    if selected_year == "Overall" and selected_country != "Overall":
        st.title(selected_country + " overall performance in Olympics")
    if selected_year != "Overall" and selected_country != "Overall":
        st.title(selected_country + " performance in " + str(selected_year) + " Olympics")

    st.table(medal_tally)

if user_menu == "Overall Analysis":
    editions = df['Year'].unique().shape[0] - 1
    cities = df['City'].unique().shape[0]
    sports = df['Sport'].unique().shape[0]
    events = df['Event'].unique().shape[0]
    athletes = df['Name'].unique().shape[0]
    nations = df['region'].unique().shape[0]

    st.title("Top Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Hosts")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Nations")
        st.title(nations)
    with col3:
        st.header("Athletes")
        st.title(athletes)

    nations_over_time = helper.data_over_time(df,col="region")
    fig = px.line(nations_over_time, x="Edition", y="region")
    st.title("Participating Nations over the years")
    st.plotly_chart(fig)

    events_over_time = helper.data_over_time(df,col="Event")
    fig = px.line(events_over_time, x="Edition", y="Event")
    st.title("Events over the years")
    st.plotly_chart(fig)

    athlete_over_time = helper.data_over_time(df, col="Name")
    fig = px.line(athlete_over_time, x="Edition", y="Name")
    st.title("No of athletes participated over the years")
    st.plotly_chart(fig)

    st.title("No. of Events over time(Every Sports)")
    fig,ax = plt.subplots(figsize=(20,20))
    x = df.drop_duplicates(["Year", "Sport", "Event"])
    ax = sns.heatmap(x.pivot_table(index="Sport", columns="Year", values="Event", aggfunc="count").fillna(0).astype("int"),
    annot=True, cmap="cubehelix")
    st.pyplot(fig)

    st.title("Most successfull Athletes")
    sport_list = df["Sport"].unique().tolist()
    sport_list.sort()
    sport_list.insert(0,"Overall")

    selected_sport = st.selectbox("Select a Sport",sport_list)
    x = helper.most_successful(df,selected_sport)
    st.table(x)

if user_menu == "Country-wise Analysis":

    st.title("Country-wise Analysis")

    country_list = df["region"].dropna().unique().tolist()
    country_list.sort()

    selected_country = st.selectbox("Select a Country",country_list)

    country_df = helper.yearwise_medal_tally(df,selected_country)

    fig = px.line(country_df, x="Year", y="Medal")
    st.title(selected_country + " Medal Tally over the years")
    st.plotly_chart(fig)

    st.title(selected_country + " excels in the following sports")
    pt = helper.country_event_heatmap(df,selected_country)
    fig, ax = plt.subplots(figsize=(20, 20))
    ax = sns.heatmap(pt,annot=True,cmap="cubehelix")
    st.pyplot(fig)

    st.title("Top 10 athletes of " + selected_country)
    top10_df = helper.most_successful_countrywise(df,selected_country)
    st.table(top10_df)

if user_menu == "Athlete-wise Analysis":
    athlete_df = df.drop_duplicates(subset=["Name", "region"])

    x1 = athlete_df["Age"].dropna()
    x2 = athlete_df[athlete_df["Medal"] == "Gold"]["Age"].dropna()
    x3 = athlete_df[athlete_df["Medal"] == "Silver"]["Age"].dropna()
    x4 = athlete_df[athlete_df["Medal"] == "Bronze"]["Age"].dropna()

    fig = ff.create_distplot([x1, x2, x3, x4], ["Overall Age", "Gold Medalist", "Silver Medalist", "Bronze Medalist"],
                             show_hist=False, show_rug=False)
    #fig.update_layout(autosize=False,width=1000,height=600)
    st.title("Distribution of Age")
    st.plotly_chart(fig)

    x = []
    name = []
    famous_sports = ['Basketball', 'Judo', 'Football', 'Tug-Of-War', 'Athletics',
                     'Swimming', 'Badminton', 'Sailing', 'Gymnastics',
                     'Art Competitions', 'Handball', 'Weightlifting', 'Wrestling',
                     'Water Polo', 'Hockey', 'Rowing', 'Fencing',
                     'Shooting', 'Boxing', 'Taekwondo', 'Cycling', 'Diving', 'Canoeing',
                     'Tennis', 'Golf', 'Softball', 'Archery',
                     'Volleyball', 'Synchronized Swimming', 'Table Tennis', 'Baseball',
                     'Rhythmic Gymnastics', 'Rugby Sevens',
                     'Beach Volleyball', 'Triathlon', 'Rugby', 'Polo', 'Ice Hockey']
    for sport in famous_sports:
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        x.append(temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna())
        name.append(sport)

    fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
    #fig.update_layout(autosize=False, width=1000, height=600)
    st.title("Distribution of Age wrt Sports(Gold Medalist)")
    st.plotly_chart(fig)

    st.title("Height-Vs-Weight")
    sport_list = df["Sport"].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')
    selected_sport = st.selectbox("Select a Sport",sport_list)
    temp_df = helper.weight_v_height(df,selected_sport)
    fig,ax = plt.subplots(figsize=(10,10))
    ax = sns.scatterplot(x=temp_df["Weight"],y=temp_df["Height"],hue=temp_df["Medal"],style=temp_df["Sex"],s=100)
    st.pyplot(fig)

    st.title("Men Vs Women Participation Over the Years")
    final = helper.men_vs_women(df)
    fig = px.line(final, x="Year", y=["Male", "Female"])
    #fig.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig)

if user_menu == "Medal Predictor":
    st.title("Olympics Medal Predictor")
    selected_col = ["Sex" , "region" ,"Sport","Height" , "Weight" , "Age" ]
    sport = ['Aeronautics', 'Alpine Skiing', 'Alpinism', 'Archery', 'Art Competitions', 'Athletics', 'Badminton', 'Baseball', 'Basketball', 'Basque Pelota', 'Beach Volleyball', 'Biathlon', 'Bobsleigh', 'Boxing', 'Canoeing', 'Cricket', 'Croquet', 'Cross Country Skiing', 'Curling', 'Cycling', 'Diving', 'Equestrianism', 'Fencing', 'Figure Skating', 'Football', 'Freestyle Skiing', 'Golf', 'Gymnastics', 'Handball', 'Hockey', 'Ice Hockey', 'Jeu De Paume', 'Judo', 'Lacrosse', 'Luge', 'Military Ski Patrol', 'Modern Pentathlon', 'Motorboating', 'Nordic Combined', 'Polo', 'Racquets', 'Rhythmic Gymnastics', 'Roque', 'Rowing', 'Rugby', 'Rugby Sevens', 'Sailing', 'Shooting', 'Short Track Speed Skating', 'Skeleton', 'Ski Jumping', 'Snowboarding', 'Softball', 'Speed Skating', 'Swimming', 'Synchronized Swimming', 'Table Tennis', 'Taekwondo', 'Tennis', 'Trampolining', 'Triathlon', 'Tug-Of-War', 'Volleyball', 'Water Polo', 'Weightlifting', 'Wrestling']
    country = ['Afghanistan', 'Albania', 'Algeria', 'American Samoa', 'Andorra', 'Angola', 'Antigua', 'Argentina', 'Armenia', 'Aruba', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bermuda', 'Bhutan', 'Boliva', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cambodia', 'Cameroon', 'Canada', 'Cape Verde', 'Cayman Islands', 'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 'Comoros', 'Cook Islands', 'Costa Rica', 'Croatia', 'Cuba', 'Curacao', 'Cyprus', 'Czech Republic', 'Democratic Republic of the Congo', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Ethiopia', 'Fiji', 'Finland', 'France', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada', 'Guam', 'Guatemala', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Honduras', 'Hungary', 'Iceland', 'India', 'Individual Olympic Athletes', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy', 'Ivory Coast', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kosovo', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Macedonia', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius', 'Mexico', 'Micronesia', 'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'North Korea', 'Norway', 'Oman', 'Pakistan', 'Palau', 'Palestine', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Puerto Rico', 'Qatar', 'Republic of Congo', 'Romania', 'Russia', 'Rwanda', 'Saint Kitts', 'Saint Lucia', 'Saint Vincent', 'Samoa', 'San Marino', 'Sao Tome and Principe', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 'South Korea', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Swaziland', 'Sweden', 'Switzerland', 'Syria', 'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Timor-Leste', 'Togo', 'Tonga', 'Trinidad', 'Tunisia', 'Turkey', 'Turkmenistan', 'UK', 'USA', 'Uganda', 'Ukraine', 'United Arab Emirates', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Venezuela', 'Vietnam', 'Virgin Islands, British', 'Virgin Islands, US', 'Yemen', 'Zambia', 'Zimbabwe']
    with st.form("my_form"):
        Sex = st.selectbox("Select Sex",["M","F"])
        Age = st.slider("Select Age",10,97)
        Height = st.slider("Select Height(In centimeters)",127,226)
        Weight = st.slider("Select Weight(In kilograms)",25,214)
        region = st.selectbox("Select Country",country)
        Sport = st.selectbox("Select Sport",sport)
        input_model = st.selectbox("Select Prediction Model",["Random Forest Classifier","Logistic Regression"])


        
        submitted = st.form_submit_button("Submit")
        if submitted:
            inputs = [Sex,region,Sport,Height,Weight,Age]
            inputs = pd.DataFrame([inputs],columns=selected_col)
            inputs = transformer.transform(inputs)
            if input_model == "Random Forest Classifier":
                model = modelrfc
            if input_model == "Logistic Regression":
                model = modellr
            prediction = model.predict(inputs)
            #prediction = np.argmax(prediction[0])
            with st.spinner('Predicting output...'):
                time.sleep(1)
                if prediction[0] == 0 :
                    ans = "Low"
                    st.warning("Medal winning probability is {}".format(ans),icon="⚠️")
                else :
                    ans = "High"
                    st.success("Medal winning probability is {}".format(ans),icon="✅")

if user_menu == "About":
    
    lt = ["Identified the most successful countries and athletes in terms of medal count.",
          "Performed deeper analyses on specific countries or athletes to explore their performance over time.",
          "Determined if certain countries or athletes have dominant sports where they excel.",
          "Plotted trends over time, such as the number of participants, gender ratio, or medal distributions.",
          "Visualized the success of countries or athletes based on the number of medals won.",
          ]
    st.header("120 years of Olympic history: athletes and results")

    st.markdown("For this Web Application , I have used a historical dataset on the modern Olympic Games,"
                "including all the Games from Athens 1896 to Rio 2016. I got this data set from Kaggle whose link is given below:")
    st.write("Dataset : [Link](https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results)")
    st.header("About Olympics Data Analysis:")
    st.write("I have,")
    for item in lt:
        st.markdown("* " + item )
    st.header("About Olympics Medal Predictor:")   
    selected_col = ["Sex" , "Region" ,"Sport","Height" , "Weight" , "Age" ]
    st.write("I made a Olympic Medal predictor which can predict the possibility of an athlete",
             "winning an Olympics Medal on the basis of his/her: " + str(selected_col))
    #for item in selected_col:
    #st.markdown(selected_col)
    st.write("In this Medal Predictor, I have used two Maching Learning algorithms and a Artificial Neural Network (Deep Learning) namely:")
    model = ["Random Forest Classifier","Logistic Regression","Neutral Network"]
    for item in model:
        st.markdown("* " + item )   
     
    
    








