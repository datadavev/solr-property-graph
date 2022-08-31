# Some data documents to mess with
docs = [
    {
        "id":"a",
        "name_t":"parent a",
        "is_s":"sample"
    },
    {
        "id":"b",
        "name_t":"parent b",
        "is_s":"sample"
    },
    {
        "id":"c",
        "name_t":"independent c",
        "is_s":"sample"
    },
    {
        "id":"aa",
        "name_t":"sub aa",
        "edges":[
            {
                "id":"111",
                "relation_type_s":"subsample-of",
                "target_s":"a"
            }
        ],
        "is_s":"sample"
    },
    {
        "id":"aa2",
        "name_t":"sub aa2",
        "edges":[
            {
                "id":"1111",
                "relation_type_s":"subsample-of",
                "target_s":"aa"
            }
        ],
        "is_s":"sample"
    },
    {
        "id":"ab",
        "name_t":"sub ab",
        "edges":[
            {
                "id":"112",
                "relation_type_s":"subsample-of",
                "target_s":"a"
            }
        ],
        "is_s":"sample"
    },
    {
        "id":"aaa",
        "name_t":"analysis aaa",
        "edges":[
            {
                "id":"113",
                "relation_type_s":"analysis-of",
                "target_s":"aa"
            },
            {
                "id":"114",
                "relation_type_s":"analysis-of",
                "target_s":"aa2"
            }
        ],
        "is_s":"analysis"
    },
    {
        "id":"aab",
        "name_t":"sub aab",
        "edges":[
            {
                "id":"120",
                "relation_type_s":"subsample-of",
                "target_s":"ab"
            }
        ],
        "is_s":"sample"
    },
    {
        "id":"ba",
        "name_t":"sub ba",
        "edges":[
            {
                "id":"114",
                "relation_type_s":"subsample-of",
                "target_s":"b"
            }
        ],
        "is_s":"sample"
    },
    {
        "id":"baa",
        "name_t":"analysis baa",
        "edges":[
            {
                "id":"115",
                "relation_type_s":"analysis-of",
                "target_s":"ba"
            }
        ],
        "is_s":"analysis"
    },
    {
        "id":"aaba",
        "name_t":"sub aaba",
        "edges":[
            {
                "id":"1151",
                "relation_type_s":"analysis-of",
                "target_s":"aab"
            }
        ],
        "is_s":"analysis"
    },
    {
        "id":"bb",
        "name_t":"sub bb",
        "edges":[
            {
                "id":"121",
                "relation_type_s":"subsample-of",
                "target_s":"b"
            }
        ],
        "is_s":"sample"
    },
    {
        "id":"ccc",
        "name_t": "publication",
        "edges":[
            {
                "id":"ccc1",
                "relation_type_s":"references",
                "target_s":"aaa"
            },
            {
                "id":"ccc2",
                "relation_type_s":"references",
                "target_s":"baa"
            }
        ],
        "is_s":"publication"
    },
    {
        "id":"ddd",
        "name_t": "publication",
        "edges":[
            {
                "id":"ddd1",
                "relation_type_s":"references",
                "target_s":"ccc"
            },
            {
                "id":"ddd2",
                "relation_type_s":"references",
                "target_s":"aaba"
            }
        ],
        "is_s":"publication"
    },
]