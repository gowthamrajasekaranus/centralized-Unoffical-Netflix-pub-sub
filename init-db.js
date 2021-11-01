//Initializes Mongodb database "database" and collection documents.
db = db.getSiblingDB("database");
//Collection document for storing all the Published events.
db.post_details.insertMany([
    {
        "subscriber_name": "test",
        "post": "not yet added"
    },
]);

//collection for storing all the subscription details.
db.subscription_details.insertMany([
    {
        "topic": "expiringUS",
        "subs": ['placeholder1','placeholder2'],
        "emails" : []
    },
        {
        "topic": "expiringUK",
        "subs": [],
        "emails": []
    },
        {
        "topic": "new_releasesUS",
        "subs": [],
        "emails": []
    },
        {
        "topic": "new_releasesUK",
        "subs": [],
        "emails": []
    },
        {
        "topic": "deleted_titlesUS",
        "subs": [],
        "emails": []
    },
            {
        "topic": "deleted_titlesUK",
        "subs": [],
        "emails": []
    },
        {
        "topic": "season_changesUS",
        "subs": [],
        "emails": []
    },
            {
        "topic": "season_changesUK",
        "subs": [],
        "emails": []
    },

]);

