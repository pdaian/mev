import csv, os
from google.cloud import bigquery


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "bq.json"
client = bigquery.Client()


uniswapv2_relayers = open('latest-data/uniswapv2_relayers').read().strip().splitlines()
sushiswap_relayers = open('latest-data/sushiswap_relayers').read().strip().splitlines()


query = """SELECT log_index,transaction_hash,logs.transaction_index,address,data,topics,logs.block_timestamp,logs.block_number,gas,gas_price,receipt_gas_used FROM 
  `bigquery-public-data.crypto_ethereum.logs` AS logs
  JOIN `bigquery-public-data.crypto_ethereum.transactions` AS transactions ON logs.transaction_hash = transactions.hash
WHERE
  logs.address in UNNEST(@relayers) ORDER BY block_number ASC, transaction_index ASC"""

for exchange_relayers in (('sushiswap', sushiswap_relayers), ('uniswapv2', uniswapv2_relayers)):
    aqp = bigquery.ArrayQueryParameter('relayers', 'STRING', exchange_relayers[1])
    query_params = [aqp]
    job_config = bigquery.QueryJobConfig()
    job_config.query_parameters = query_params
    query_job = client.query(
        query,
        # Location must match that of the dataset(s) referenced in the query.
        location='US',
        job_config=job_config)  # API request - starts the query
    with open('latest-data/all_logs_%s.csv' % (exchange_relayers[0]), 'w') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)

        spamwriter.writerow("log_index,transaction_hash,transaction_index,address,data,topics,block_timestamp,block_number,gas,gas_price,receipt_gas_used".split(","))
        for item in query_job:
            spamwriter.writerow(item)

    assert query_job.state == 'DONE'
    print("Wrote all logs for %s" %(exchange_relayers[0]) )

