# project: p4
# submitter: apierrelouis
# partner: none
# hours: 20
import pandas as pd
from flask import Flask, request, jsonify, Response
import time
from scipy.stats import fisher_exact
import edgar_utils
import zipfile
from io import TextIOWrapper
import geopandas
import shapely.geometry
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path

app = Flask(__name__)
df = pd.read_csv('server_log.zip', compression='zip')


counter = 0
ab = [0,0]

ips = []
times = {}

# http://34.171.149.230:5000
@app.route('/')
def home():
    global counter
    with open("index.html") as f:
        html = f.read()
    if counter < 10:
        counter += 1
        if counter % 2 == 0:
            AB = 'A'
            RB = 'red'
        else:
            AB = 'B'
            RB = 'blue'
    else:
        if ab[0] > ab[1]:
            AB = 'A'
            RB = 'red'
        else:
            AB = 'B'
            RB = 'blue'
    
    return html.format(AB=AB,RB=RB)

@app.route('/browse.html')
def browse():
    global df
    hdr = "<html><body><h1>{}</h1></body><html>".format("Browse first 500 rows of rows.csv")

    return hdr + df.iloc[:500].to_html()

@app.route('/browse.json')
def browseJSON():
    global ips, times, df
    rate = 5
    ip = request.remote_addr
    ips.append(ip)
    now = time.time()
    if ip in times:
        tdiff = now - times[ip]
        if tdiff < rate:
            return Response("Please reattempt in " + str(rate-tdiff) + " seconds.", status = 429, headers = {"Retry-After": str(rate)})
        else:
            times[ip] = now
    else:
        times[ip] = now
    
    return jsonify(df.iloc[:500].to_dict())

@app.route('/visitors.json')
def visitors():
    return ips

@app.route('/donate.html')
def donate():
    global counter, ab
    AB = str(request.query_string, encoding='utf-8')
    if counter < 11:
        if 'A' in AB:
            ab[0] += 1
        else:
            ab[1] += 1
    
    with open("donate.html") as f:
        html = f.read()
    return html

@app.route('/analysis.html')
def analysis():
    global df
    with open("analysis.html") as f:
        html = f.read()
    #Q1
    q1 = df['ip'].squeeze().value_counts()[:10].to_dict()
    #Q2 commented lines are deprecated because of order of resulting dict
    filings = {}
    #sics = {}
    sics = []
    with zipfile.ZipFile('docs.zip', 'r') as zf:
        for filename in zf.namelist():
            if 'htm' not in filename:
                continue
            with TextIOWrapper(zf.open(filename, 'r'), encoding='utf-8') as f:
                htm = f.read()
                filing = edgar_utils.Filing(htm)
                filings[filename] = filing
                if filing.sic is not None:
                    sics.append(filing.sic)
                    #if filing.sic not in sics:
                     #   sics.append(filing.sic) = 1
                    #else:
                     #   sics[filing.sic] += 1
    #q2 = dict(sorted(sics.items(), key = lambda sic: sic[1], reverse = True)[:10]) # sorts improperly for the test = {2834: 40, 6022: 20, 1311: 20, 6798: 20, 6021: 20, 1389: 19, 6189: 17, 6211: 17, 2836: 13, 7389: 11}
    q2 = pd.Series(sics).value_counts(sort=True).head(10).to_dict()
    #Q3
    addrs = []
    for row in df.itertuples():
        req = '/'.join([str(row[5]).split('.')[0],str(row[6]),str(row[7])]) # row[x] x=5,6,7 ~ cik accession and extention respectively
        if req in filings:
            for addr in filings[req].addresses:
                addrs.append(addr)
    
    counts = pd.Series(addrs).value_counts()
    q3 = counts[counts >= 300].to_dict()
    #Q4
    background = geopandas.read_file("shapes/cb_2018_us_state_20m.shp").to_crs("epsg:2022")
    locations = geopandas.read_file("locations.geojson").to_crs(background.crs)
    west = -95
    east = -60
    north = 50
    south = 25
    ax = background.plot(color = "grey")
    
    #TODO finish code to generate plot then save plot to dashboard.svg
    q4 = "<img src=\"dashboard.svg\">"
    return html.format(q1=q1,q2=q2,q3=q3,q4=q4)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!

# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.