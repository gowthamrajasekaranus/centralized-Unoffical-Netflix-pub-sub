from flask import Flask, render_template, request
from pymongo import MongoClient
from collections import defaultdict
import smtplib
import requests
import sys

"Holy waters"
app = Flask(__name__)

topics = ["new_releases", "expiring", "deleted_titles", "season_changes"]
subscribers = []
publishers = []
subscriptions = defaultdict(list)
url = "https://unogs-unogs-v1.p.rapidapi.com/aaapi.cgi"
advertisement_switch = False


# Method to make GET requests call to the RAPID API(uNoGS) to retrieve Top New releases from NETFLIX US/UK.
def new_releases(country):
    if country == "US":
        ans = "The Top 10 new releases in US are: \n"
        querystring = {"q": "get:new7:US", "p": "1", "t": "ns", "st": "adv"}
    if country == "UK":
        ans = "The Top 10 new releases in UK are: \n"
        querystring = {"q": "get:new7:UK", "p": "1", "t": "ns", "st": "adv"}
    headers = {
        'x-rapidapi-host': "unogs-unogs-v1.p.rapidapi.com",
        'x-rapidapi-key': "d50cb8a400msh4744ffd83f27e95p152fc1jsn9b9ca0573fdb"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    a = response.json()
    x = a['ITEMS']
    for lis in x[:10]:
        ans += lis['title'] + "\n"
    return ans


# Method to make GET requests call to the RAPID API(uNoGS) to retrieve soon to be Expired title.
def expiring(country):
    if country == "US":
        querystring = {"q": "get:exp:US", "t": "ns", "st": "adv", "p": "1"}
        ans = "Expiring from Netflix US this week are: \n"
    if country == "UK":
        querystring = {"q": "get:exp:UK", "t": "ns", "st": "adv", "p": "1"}
        ans = "Expiring from Netflix UK this week are: \n"
    headers = {
        'x-rapidapi-host': "unogs-unogs-v1.p.rapidapi.com",
        'x-rapidapi-key': "d50cb8a400msh4744ffd83f27e95p152fc1jsn9b9ca0573fdb"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    a = response.json()
    x = a['ITEMS']
    for lis in x[:10]:
        ans += lis['title'] + "\n"
    return ans


# Method to make GET requests call to the RAPID API(uNoGS) to retrieve Recent Deleted title for the country selected.
def deleted_titles(country):
    if country == "US":
        querystring = {"t": "deleted", "cl": "US", "st": "{daysback}"}
        ans = "Recent Deleted Titles from Netflix US are: \n"
    if country == "UK":
        querystring = {"t": "deleted", "cl": "UK", "st": "{daysback}"}
        ans = "Recent Deleted Titles from Netflix UK are: \n"

    headers = {
        'x-rapidapi-host': "unogs-unogs-v1.p.rapidapi.com",
        'x-rapidapi-key': "d50cb8a400msh4744ffd83f27e95p152fc1jsn9b9ca0573fdb"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    a = response.json()
    x = a['ITEMS']
    if len(x) == 0:
        return "No Title has been removed recently for Netflix " + country
    for lis in x[:10]:
        ans += lis['title'] + "\n"
    return ans


# Method to make GET requests call to the RAPID API(uNoGS) to retrieve the seasonal changes for the country selected.
def season_changes(country):
    if country == "US":
        querystring = {"q": "get:seasons5:US", "p": "1", "t": "ns", "st": "adv"}
        ans = "Recently updated Netflix US TV shows: \n"

    if country == "UK":
        querystring = {"q": "get:seasons5:UK", "p": "1", "t": "ns", "st": "adv"}
        ans = "Recently updated Netflix UK TV shows: \n"
    headers = {
        'x-rapidapi-host': "unogs-unogs-v1.p.rapidapi.com",
        'x-rapidapi-key': "d50cb8a400msh4744ffd83f27e95p152fc1jsn9b9ca0573fdb"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    a = response.json()
    x = a['ITEMS']
    if len(x) == 0:
        return "No TV show season has been updated recently for Netflix " + country
    for lis in x[:10]:
        temp_splitter = lis["synopsis"].split('<b>')
        string = str(temp_splitter[1])
        temp2_splitter = string.split('</b>')
        val = str(temp2_splitter[0])
        ans += "TV Show Name: " + lis['title'] + "------" + "Change: " + val + "\n"
    return ans


# Method to notify the subscribers for the topic, through email.
def notify(emails_list, value):

    # Email-Id and password for configuring the mail server for sending notification, the publisher2222 doesnt mean that
    # this mail is being sent by publisher 2, publishers and subscribers are decoupled
    _email = "publisher22222@gmail.com"
    _password = "Publisher22222*"
    sent_from = _email
    to = emails_list
    value = "-->" + value
    subject = 'POST NOTIFICATIONS'
    email_text = """\
    Subject: %s

    %s
    """ % (subject, value)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(_email, _password)
        server.sendmail(sent_from, to, email_text)
        server.close()

    except:
        print('error in E-Mail', file=sys.stdout)


def setter(boolean):
    global advertisement_switch
    if boolean is True:
        advertisement_switch = True
    else:
        advertisement_switch=False

#Renders the HTMl page for the Netflix pub-sub.
@app.route('/')
def home():
    return render_template("home.html")


# Renders the HTMl page for the Publisher page after a click from the Home page for GET method.
@app.route('/publish',  methods=["GET"])
def publish_get():
    return render_template("publish.html")


# Renders the HTMl page for the Publisher page after a click from the Home page for POST method.
@app.route('/publish', methods=["POST"])
def publish_post():
    subs_list = []
    emails_list = []
    publisher_name = request.form['publisher_name']
    topic_to_be_published = request.form['topic_to_be_published']
    country1 = request.form['country']

    # publisher 1 can only publish data from new_releasesUS, expiringUS.
    # publisher 2 can only publish data from new_releasesUK, expiringUK.
    # publisher 3 can only publish data from deleted_titlesUS, deleted_titlesUK, season_changesUS and season_changesUK.
    # configure Topic data from the publisher
    if publisher_name == "pub1":
        country = "US"

    elif publisher_name == "pub2":
        country = "UK"

    if topic_to_be_published == "new_releases":
        topic_to_be_published += country
        value = new_releases(country)

    elif topic_to_be_published == "expiring":
        topic_to_be_published += country
        value = expiring(country)

    elif topic_to_be_published == "deleted_titles" and publisher_name == "pub3":
        topic_to_be_published += country1
        value = deleted_titles(country1)

    elif topic_to_be_published == "season_changes" and publisher_name == "pub3":
        topic_to_be_published += country1
        value = season_changes(country1)

    else:
        return render_template("publish.html", topic_to_be_published="Please Enter a Valid Topic")

    # Retrieve the list of subscriber names and emails for the topic from subscription_details collection in MongoDB.
    client = MongoClient(host='Netflix_DB', port=27017, username='root', password='pass', authSource="admin")
    query_result = client["database"]["subscription_details"].find({"topic": topic_to_be_published})
    for record in query_result:
        subs_list = list(record['subs'])
        emails_list = list(record['emails'])

    # we have two medium of posting
    # First way is to Email the published event to the subscribers.
    # Second way is we update another document in the DB were we store the events published to each subscriber, --
    # --so that when the user clicks on posts he can view all the events that were published for his subscriptions.
    notify(emails_list, value)

    # Storing event data into MongoDB
    for subs in subs_list:
        client["database"]["post_details"].insert({"subscriber_name": subs, "post": value})
    return render_template("publish.html", publisher_name=publisher_name, topic_to_be_published=topic_to_be_published)


# Renders the HTMl page for the Subscriber page after a click from the Home page for GET method.
@app.route('/subscribe', methods=["GET"])
def subscribe_get():
    return render_template("subscribe.html")


# Renders the HTMl page for the Subscriber page after a click from the Home page for POST method.
@app.route('/subscribe', methods=["POST"])
def subscribe_post():
    subscriber_name = request.form['subscriber_name']
    email_id = request.form['email_id']
    topic = request.form['topic']
    country = request.form['country']
    adv_code = request.form['adv_code']
    subscribe_or_unsubscribe = request.form['sub_or_unsub']

    # Store the Subscriber's name, Email in the subscriptions list in the form given below.
    # {"topic": "expiringUS",
    # "subs": ['placeholder1', 'placeholder2'],
    # "emails": [placeholder1@gmail.com, placeholder2@gmail.com]} represents a document for expiringUS.
    client = MongoClient(host='Netflix_DB', port=27017, username='root', password='pass', authSource="admin")
    topic += country
    if subscribe_or_unsubscribe == "subscribe":
        x = []
        y = []
        query_result = client["database"]["subscription_details"].find({"topic": topic})
        for record in query_result:
            x = list(record['subs'])
            y = list(record['emails'])
            x.append(subscriber_name)
            y.append(email_id)
        client["database"]["subscription_details"].update_one({"topic": topic}, {"$set": {"subs": x, "emails": y}})

    # Remove the subscribers name and email from the subscriptions list of the given topic.
    elif subscribe_or_unsubscribe == "unsubscribe":
        query_result = client["database"]["subscription_details"].find({"topic": topic})
        for record in query_result:
            x = list(record['subs'])
            y = list(record['emails'])
            x.remove(subscriber_name)
            y.remove(email_id)
        client["database"]["subscription_details"].update_one({"topic": topic}, {"$set": {"subs": x, "emails": y}})

    ''' Special case for Advertise, We design the interface in a way that publisher 3 advertises/notifies the
        Subscribers of Deleted titles from US through email that if Subscribe to Deleted titles from UK and get free
        subscription to Season changes from US and UK. Enter the code PUB_SUB"  '''

    # so if the user enters the correct code when the Advertisement is still valid(not de-advertised) and if topic is
    # from deleted_titlesUK, the user also gets free subscriptions to season_changesUS and season_changesUK.
    if adv_code == "PUB_SUB" and advertisement_switch is True and topic == "deleted_titlesUK":
        x1 = []
        y1 = []
        query_result = client["database"]["subscription_details"].find({"topic": "season_changesUS"})
        for record in query_result:
            x1 = list(record['subs'])
            y1 = list(record['emails'])
            x1.append(subscriber_name)
            y1.append(email_id)
        client["database"]["subscription_details"].update_one({"topic": "season_changesUS"}, {"$set": {"post": x1, "emails": y1}})
        query_result = client["database"]["subscription_details"].find({"topic": "season_changesUK"})
        for record in query_result:
            x1 = list(record['subs'])
            y1 = list(record['emails'])
            x1.append(subscriber_name)
            y1.append(email_id)
        client["database"]["subscription_details"].update_one({"topic": "season_changesUK"}, {"$set": {"subs": x1, "emails": y1}})

    return render_template("subscribe.html", topic=topic, email_id=email_id, subscriber_name=subscriber_name)

# Renders the HTMl page for the Advertisement page after a click from the Home page for GET method.
@app.route('/ad', methods=["GET"])
def ad():
    return render_template("advertise.html")


# Renders the HTMl page for the Advertise page after a click from the Home page for GET method.
# We design the interface in a way that publisher 3 advertises/notifies the
# Subscribers of Deleted titles from US through email that if Subscribe to Deleted titles from UK and get free
# subscription to Season changes from US and UK. Enter the code PUB_SUB"
@app.route('/advertise', methods=["GET"])
def advertise_get():
    emails_list = []
    value = "Advertisement: Subscribe to Deleted titles from UK and get free subscription to Season changes from US and UK and view up to date information on all the season changes happening in both Netflix US and UK. Enter the code PUB_SUB."
    # Set offer to True
    setter(True)
    client = MongoClient(host='Netflix_DB', port=27017, username='root', password='pass', authSource="admin")

    query_result = client["database"]["subscription_details"].find({"topic": "deleted_titlesUS"})
    for record in query_result:
        emails_list = list(record['emails'])

    notify(emails_list, value)
    return render_template("advertise.html")


# Renders the HTMl page for the DE-Advertisement page after a click from the Home page for GET method.
# Notifies the users about the advertisement or offer no longer being valid.
@app.route('/deadvertise', methods=["GET"])
def deadvertise_get():
    emails_list = []
    value = "Deadvertisement: The Offer advertised previously is no longer available. You cannot redeem the code anymore."
    # Set offer to False
    setter(False)
    client = MongoClient(host='Netflix_DB', port=27017, username='root', password='pass', authSource="admin")
    query_result = client["database"]["subscription_details"].find({"topic": "deleted_titlesUS"})
    for record in query_result:
        emails_list = list(record['emails'])
    notify(emails_list, value)
    return render_template("advertise.html")


# Renders the HTMl page for the Subscribers posts page after a click from the Home page for GET method.
@app.route('/posts', methods=["GET"])
def posts_get():
    return render_template("posts.html")


# Renders the HTMl page for the Subscribers posts page after a click from the Home page for POST method.
@app.route('/posts', methods=["POST"])
def posts_post():
    # Page where a subscriber can view all posts published for his subscriptions till date.
    subscriber_name = request.form['subscriber_name']
    client = MongoClient(host='Netflix_DB', port=27017, username='root', password='pass', authSource="admin")
    db = client["database"]
    pushed_messages = ""
    count = 0
    query_result = db.post_details.find({"subscriber_name": subscriber_name})
    for record in query_result:
        count += 1
        pushed_messages += "POST NO " + str(count) + "\n" + record["post"]+"\n"
    return render_template("posts.html", topic=pushed_messages, subscriber_name=subscriber_name)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
