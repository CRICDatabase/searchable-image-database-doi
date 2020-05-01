"""
Read the database and upload images to figshare
"""
import sys
import argparse
import hashlib
import os
import json
import re

import pymysql
import requests

# Function to log requests to Node.js REST API
def debug(r, *args, **kwargs):
    print(
        """URL: {}\n"""
        """\t{}""".format(
            r.url,
            r.text
        )
    )

# REST API
FIGSHARE_BASE_URL = "https://api.figshare.com/v2"
headers = {}

# Open database connection
db = pymysql.connect(
    "0.0.0.0",
    "root",
    "123.456",
    "cric"
)

FUNDING_TITLES = [
    "CNPq 304673/2011-0",
    "CNPq 472565/2011-7",
    "CNPq 401120/2013-9",
    "CNPq 444784/2014-4",
    "CNPq 306600/2016-1",
    "CAPES/CNPq-PVE 401442/2014-4",
    "CAPES/CNPq-PVE 207307/2015-6",
    "CAPES/CNPq-PVE 207306/2015-0",
    "FAPEMIG APQ-00802-11",
    "FAPEMIG APQ-02369-14",
    "PPSUS/FAPEMIG APQ-03740-17",
    "PROPPI/UFOP",
    "UFOP 23109.003209/2016-98",
    "UFOP 23109.003515/2018-96",
    "UFOP 23109.003517/2018-85",
    "Office of Science, U.S. Department of Energy (DOE) under Contract No. DE-AC02- 05CH11231 Moore-Sloan Foundation",
]

def get_funding():
    fundings = []
    endpoint = '{}/account/funding/search'.format(
        FIGSHARE_BASE_URL
    )

    for funding in FUNDING_TITLES:
        response = requests.post(
            '{}'.format(
                endpoint
            ),
            headers=headers,
            json={
                "search_for": funding
            },
            hooks={'response': debug}
        )
        response_json = response.json()
        fundings.append(
            {
                "id": response_json[0]["id"],
                "title": response_json[0]["title"],
            }
        )

    return fundings

def store_doi(image_id, doi):
    cursor.execute(
        """UPDATE imagem """
        """SET doi = "{}" """
        """WHERE id = {};""".format(
            doi,
            image_id
        )
    )
    db.commit()

def sync_doi():
    # fundings = get_funding()
    fundings = []

    # Get Own Articles
    endpoint = '{}/account/articles'.format(
        FIGSHARE_BASE_URL
    )
    query_string = "?page_size=400"
    response = requests.get(
        '{}{}'.format(
            endpoint,
            query_string
        ),
        headers=headers,
        hooks={'response': debug}
    )

    for article in response.json():
        image_id = re.search(
            r'(?<=#)\d+',
            article["title"]
        ).group(0)        

        # Remove Raniere from author
        endpoint = '{}/account/articles/{}/authors/{}'.format(
            FIGSHARE_BASE_URL,
            article["id"],
            4181932
        )
        requests.delete(
            '{}'.format(
                endpoint
            ),
            json={
                "funding_list": fundings
            },
            headers=headers,
            hooks={'response': debug}
        )

        # Update details
        endpoint = '{}/account/articles/'.format(
            FIGSHARE_BASE_URL
        )
        requests.put(
            '{}{}'.format(
                endpoint,
                article["id"],
            ),
            json={
                "title": "CRIC Cervix Microscope Slide Image #{}".format(image_id),
                "description": "Image {} Image ID from microscope slides of the uterine cervix using the conventional smear (Pap smear). Data visualisation of classification available at http://database.cric.com.br/classification/image/{}.".format(image_id, image_id),
                "funding_list": fundings
            },
            headers=headers,
            hooks={'response': debug}
        )

        # Reserve DOI
        endpoint = '{}/account/articles/{}/reserve_doi'.format(
            FIGSHARE_BASE_URL,
            article["id"]
        )
        doi_response = requests.post(
            '{}'.format(
                endpoint
            ),
            json={
                "funding_list": fundings
            },
            headers=headers,
            hooks={'response': debug}
        )
        # Save DOI
        store_doi(
            image_id,
            doi_response.json()["doi"]
        )
        
        # Publish article
        endpoint = '{}/account/articles/{}/publish'.format(
            FIGSHARE_BASE_URL,
            article["id"]
        )
        requests.post(
            '{}'.format(
                endpoint
            ),
            headers=headers,
            hooks={'response': debug}
        )

    # Add articles to collection
    # Note: expecting a maximum of 10 articles ids
    articles_id = []
    article_counter = 0
    endpoint = '{}/account/collections/{}/articles'.format(
        FIGSHARE_BASE_URL,
        4960286
    )
    for article in response.json():
        articles_id.append(article["id"])
        article_counter = article_counter + 1

        if article_counter == 10:
            requests.post(
                '{}'.format(
                    endpoint
                ),
                json={
                    "articles": articles_id
                },
                headers=headers,
                hooks={'response': debug}
            )
            articles_id = []
            article_counter = 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload images to figshare.')
    parser.add_argument(
        '--token',
        help='Personal token. See https://figshare.com/account/applications for more information.'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Sync DOI for all images'
    )
    args = parser.parse_args()

    if args.token is None:
        print("Token is missing.")
    else:
        headers["Authorization"] = "token {}".format(args.token)
        
        cursor = db.cursor()

        if args.all:
            sync_doi()

        db.close()
