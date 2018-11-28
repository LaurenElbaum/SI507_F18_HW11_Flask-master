import requests
import json
from flask import Flask, render_template
app = Flask(__name__)
from secrets import *
from datetime import datetime
now = datetime.now()
sec_since_epoch = now.timestamp()
MAX_STALENESS =30 ##30 seconds--only for lecture demo!









CACHE_FNAME = 'nyt_cache.json' #Make global variable uppercase. 
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

# if there was no file, no worries. There will be soon!
except:
    CACHE_DICTION = {}

# A helper function that accepts 2 parameters
# and returns a string that uniquely represents the request
# that could be made with this info (url + params)
def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_" + "_".join(res)

# The main cache function: it will always return the result for this
# url+params combo. However, it will first look to see if we have already
# cached the result and, if so, return the result from cache.
# If we haven't cached the result, it will get a new one (and cache it)
def make_request_using_cache(baseurl, params):
    unique_ident = params_unique_combination(baseurl, params)

    ## first, look in the cache to see if we already have this data
    if unique_ident in CACHE_DICTION:
        if is_fresh(CACHE_DICTION[unique_ident]): #This is new
            print("Getting cached data...")
        return CACHE_DICTION[unique_ident]
    else:
        pass

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    print("Making a request for new data...")
    # Make the request and cache the new data
    resp = requests.get(baseurl, params)
    CACHE_DICTION[unique_ident] = json.loads(resp.text)

    CACHE_DICTION[unique_ident]['cache_timestamp']= datetime.now().timestamp() 
    dumped_json_cache = json.dumps(CACHE_DICTION) 
    fw = open(CACHE_FNAME,"w") 
    fw.write(dumped_json_cache) 
    fw.close()# Close the open filereturn CACHE_DICTION[unique_ident]
    return CACHE_DICTION[unique_ident]


def is_fresh(cache_entry): 
    now = datetime.now().timestamp() 
    staleness = now - cache_entry['cache_timestamp']
    print("Retrieved new data..............")
    return staleness < MAX_STALENESS



# gets stories from a particular section of NY times
def get_stories(section):
    baseurl = 'https://api.nytimes.com/svc/topstories/v2/'
    extendedurl = baseurl + section + '.json'
    params={'api-key': nyt_key}
    return make_request_using_cache(extendedurl, params)

def get_headlines(nyt_results_dict):
    results = nyt_results_dict['results']
    headlines = []
    for r in results:
        headlines.append(r['title'])
    return headlines

story_list_json = get_stories('technology')
headlines = get_headlines(story_list_json)
for h in headlines[:5]:
    print(h)




# print("---"*20)
# print(headlines[:6])


@app.route('/name/<nm>')
def hello_name(nm):
    return render_template('user.html', name=nm, my_list = headlines[:5])

if __name__ == '__main__':  
    print('starting Flask app', app.name)  
    app.run(debug=True)