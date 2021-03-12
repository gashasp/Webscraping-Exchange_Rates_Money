from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content,"html.parser")

table = soup.find("table", attrs={"class" : "table table-striped table-hover table-hover-solid-row table-simple history-data"})
tr = table.find_all('tr')
temp = [] #initiating a tuple

for i in range(0, 12):
#insert the scrapping process here
    row = table.find_all("tr")[i]

    date = row.find_all("td")[0].text
    date = date.strip()
    
    day = row.find_all("td")[1].text
    day = day.strip()
    
    inflation = row.find_all("td")[2].text
    inflation = inflation.strip()
    
    temp.append((date,day,inflation))

for i in range(14, 36):
    row = table.find_all("tr")[i]

    date = row.find_all("td")[0].text
    date = date.strip()
    
    day = row.find_all("td")[1].text
    day = day.strip()
    
    inflation = row.find_all("td")[2].text
    inflation = inflation.strip()
    
    temp.append((date,day,inflation))

for i in range(38, 134):
    row = table.find_all("tr")[i]

    date = row.find_all("td")[0].text
    date = date.strip()
    
    day = row.find_all("td")[1].text
    day = day.strip()
    
    inflation = row.find_all("td")[2].text
    inflation = inflation.strip()
    
    temp.append((date,day,inflation))

temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns = ('date','day',"inflation"))
df["inflation"] = df["inflation"].str.replace(" IDR","")
df["inflation"] = df["inflation"].str.replace(",","")
df["date"] = pd.to_datetime(df["date"], dayfirst=True)
df["inflation"] = df["inflation"].astype("float64")
df["date"] = df["date"].dt.strftime('%d-%m-%Y')
pd.set_option('display.float_format', lambda x: '%.3f' % x)

#insert data wrangling here (graph 1)
wday = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
wrg = pd.crosstab(index=df["day"],
           columns="Inflations",
            values=df["inflation"],
            aggfunc="mean")
wrg = wrg.reindex(wday)
wrg.columns.name="Data"

#graph2
wrg2 = df.copy()
wrg2["date"] = pd.to_datetime(wrg2["date"])
wrg2["date"] = wrg2["date"].dt.to_period("M")
wrg2 = pd.crosstab(index=wrg2["date"],
                   columns="Inflationss",
                   values = wrg2["inflation"],
                   aggfunc="mean")
wrg2.columns.name="Data"

#grpah3
wrg3 = pd.crosstab(index=df["date"],
           columns="Inflasi",
            values=df["inflation"],
            aggfunc="mean")
wrg3.columns.name="Data"

#end of data wranggling 

@app.route("/")
def index(): 
	card_data = f'USD {df["inflation"].mean().round(2)}'
	
	# generate plot
	ax = wrg.plot(xlabel="Day",ylabel="Inflation Value",figsize = (8,4))
	# Rendering plot
	# Do not change this	
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# graph 2
	ax = wrg2.plot(xlabel="Month",ylabel="Inflation Value",figsize = (8,4))
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result2 = str(figdata_png)[2:-1]

	#graph 3
	ax = wrg3.plot(xlabel="Date",ylabel="Inflation Value",figsize = (12,4))
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result3 = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data,
		plot_result=plot_result,
		plot_result2=plot_result2,
		plot_result3=plot_result3
		)


if __name__ == "__main__": 
    app.run(debug=True)
