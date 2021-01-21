import csv, os
from google.cloud import bigquery
from exchanges import uniswap_relayers

FIELDS_TO_GRAB = 'block_number,transaction_hash,to_address,from_address,address,num_logs,gas,gas_price,receipt_gas_used,input,transaction_index'

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "etharbskey.json"
client = bigquery.Client()


query = """SELECT log_index,transaction_hash,logs.transaction_index,address,data,topics,logs.block_timestamp,logs.block_number,gas,gas_price,receipt_gas_used FROM 
  `bigquery-public-data.crypto_ethereum.logs` AS logs
  JOIN `bigquery-public-data.crypto_ethereum.transactions` AS transactions ON logs.transaction_hash = transactions.hash
WHERE
  logs.address in UNNEST(@uniswap_relayers) ORDER BY block_number ASC, transaction_index ASC"""

aqp = bigquery.ArrayQueryParameter('uniswap_relayers', 'STRING', uniswap_relayers)
query_params = [aqp]
job_config = bigquery.QueryJobConfig()
job_config.query_parameters = query_params
query_job = client.query(
    query,
    # Location must match that of the dataset(s) referenced in the query.
    location='US',
    job_config=job_config)  # API request - starts the query


with open('latest-data/all_logs_uniswap.csv', 'w') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

    spamwriter.writerow("log_index,transaction_hash,transaction_index,address,data,topics,block_timestamp,block_number,gas,gas_price,receipt_gas_used".split(","))
    for item in query_job:
        spamwriter.writerow(item)

assert query_job.state == 'DONE'
print("[database fetcher] Wrote all logs")

