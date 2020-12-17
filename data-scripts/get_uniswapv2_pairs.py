#0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9

#0xc0aee478e3658e2610c5f7a4a2e1777ce9e4f2ac Sushiswap factory
#0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f Uniswapv2 factory

import csv, os
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "bq.json"
client = bigquery.Client()


event_signature = "0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9" #PairCreated from V2 factory

query = """SELECT log_index,transaction_hash,address,data,topics,logs.block_timestamp,logs.block_number FROM `bigquery-public-data.crypto_ethereum.logs` AS logs JOIN UNNEST(topics) AS topic WHERE topic IN UNNEST(@topics) ORDER BY block_number ASC"""


topics = set([event_signature])
aqp = bigquery.ArrayQueryParameter('topics', 'STRING', topics)
query_params = [aqp]
job_config = bigquery.QueryJobConfig()
job_config.query_parameters = query_params
query_job = client.query(
    query,
    # Location must match that of the dataset(s) referenced in the query.
    location='US',
    job_config=job_config)  # API request - starts the query


with open('latest-data/all_logs_uniswapv2_factory.csv', 'w') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

    spamwriter.writerow("log_index,transaction_hash,address,data,topics,block_timestamp,block_number".split(","))
    for item in query_job:
        spamwriter.writerow(item)

assert query_job.state == 'DONE'
print("[database fetcher] Wrote all logs")

