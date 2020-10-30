import logging
import pandas as pd
import requests
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import json
import matplotlib.pyplot as plt
import argparse


parser = argparse.ArgumentParser(description='Fetch Maker Data')

parser.add_argument(
    '-v', '--verbose',
    help="Be verbose",
    action="store_const", dest="loglevel", const=logging.INFO,
    default=logging.WARNING
)


args = parser.parse_args()    

logging.basicConfig(level=args.loglevel, format='%(message)s')
logger = logging.getLogger(__name__)


CDPS_URL = 'https://mkr.tools/api/v1/cdps'
BLOCKS_URL = 'https://mkr.tools/api/v1/blocks'
GRAPHQL_URL='https://sai-mainnet.makerfoundation.com/v1'

time_checkpoints = ["2015-01-01", "2019-04-01"]
#time_checkpoints = ["2018-01-01", "2019-04-01", "2019-07-01", "2019-10-01", "2020-01-01", "2020-04-01", "2020-10-15"]

def get_filter_criterion(start_time, end_time):
    return '{{time: {{lessThan: "{end_time}", greaterThanOrEqualTo: "{start_time}"}}}}'.format(start_time=start_time, end_time=end_time)

def fetch_data_from_web(filter_criterion):
    sample_transport=RequestsHTTPTransport(
    url=GRAPHQL_URL,
    retries=3,
    )

    client = Client(
        transport=sample_transport,
        fetch_schema_from_transport=True,
    )

    # (filter: {{ratio: {{lessThan: "{unsafe_ratio}"}}, art: {{greaterThanOrEqualTo: "{min_debt}"}}}})
    # allCupActs (filter: {{time: {{lessThan: "2020-03-16", greaterThan: "2020-03-03"}}}}) # actions_data.txt
    query_string = """
        query {{
          allCupActs (filter: {filter_criterion}) {{
            totalCount
            nodes {{
              id
              act
              arg
              lad
              art
              block
              deleted
              ink
              ire
              pip
              tab
              ratio
              time
              tx
            }}
          }}
        }}
    """.format(filter_criterion=filter_criterion)
    logger.info(query_string)

    query = gql(query_string)

    return client.execute(query)


def analyse(data):
    pass

def format_for_mev(action):
    if action['act'] == 'BITE':
        return
    owner = int(action['lad'], 16)
    if owner == 0:
        return
    print("// transaction {}".format(action['tx']))
    id = action['id']
    if action['act'] == 'OPEN':
        owner = int(action['lad'], 16)
        print("{} opens vault {};".format(owner, id))
    elif action['act'] == 'LOCK':
        print("{} locks {} collateral to vault {};".format(owner, int(float(action['arg']) * 1e18), id))
    elif action['act'] == 'DRAW':
        print("{} draws {} debt from vault {};".format(owner, int(float(action['arg']) * 1e18), id))
    elif action['act'] == 'WIPE':
        print("{} wipes {} debt from vault {};".format(owner, int(float(action['arg']) * 1e18), id))
    elif action['act'] == 'FREE':
        print("{} frees {} collateral from vault {};".format(owner, int(float(action['arg']) * 1e18), id))
    elif action['act'] == 'GIVE':
        print("{} is given vault {};".format(int(action['arg'], 16), id))


for i in range(len(time_checkpoints) - 1):
    start_time = time_checkpoints[i]
    end_time = time_checkpoints[i+1]

    logger.info("Fetching from {} to {} ...".format(start_time, end_time) )

    filter_criterion = get_filter_criterion(start_time, end_time)
    data = fetch_data_from_web(filter_criterion)
    #print(data)
    filename='actions-data-{start_time}-{end_time}.txt'.format(start_time=start_time, end_time=end_time)

    logger.info("Writing to {} ...".format(filename) )

    with open(filename, 'w') as outfile:
        json.dump(data, outfile)
'''

data = fetch_data_from_file('all_actions_data.txt')
'''

'''
df = pd.DataFrame(data['allCupActs']['nodes'])

numeric_cols = ['ratio', 'art', 'ink', 'ire', 'tab', 'pip', 'block', 'id']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col])

df.sort_values('block', inplace=True)
'''
#df.apply(format_for_mev, axis=1)
