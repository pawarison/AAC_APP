import gcsfs
import pyarrow.parquet as pq
import pyarrow as pa
from google.cloud import storage
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r'credential.json'

def list_objects(bucket_name): 
    client = storage.Client()
    file_list = client.list_blobs(bucket_name)
    file_list = [file.name for file in file_list]
    return file_list

def save_csv_gcs(data = '', file_name = 'price_data.csv',bucket_name = 'aac_bucket'):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    bucket.blob(file_name).upload_from_string(data.to_csv(), 'csv')

def read_csv_gcs(file_name = 'price_data.csv',bucket_name = 'aac_bucket'):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    # Get a reference to the blob (file) within the bucket
    blob = bucket.blob(file_name)
    # Download the blob's contents as bytes
    blob_content = blob.download_as_bytes()
    # Use pandas to read the CSV data from the bytes content
    csv_data = pd.read_csv(BytesIO(blob_content))
    return csv_data   

def save_parquet_gcs(df='', file_path='', bucket_name=''):
    # Save DataFrame to a Parquet file in memory
    table = pa.Table.from_pandas(df)
    with pa.BufferOutputStream() as os:
        with pa.parquet.ParquetWriter(os, table.schema) as writer:
            writer.write_table(table)
        buffer = os.getvalue()
    # Upload the Parquet file to GCS
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    blob.upload_from_string(buffer.to_pybytes(), content_type='application/octet-stream')

def read_parquet_gcs(path = 'gs://aac_bucket/price_df.parquet', to_pandas=True):
    """
    Reads multiple (partitioned) parquet files from a GS directory
    e.g. 'gs://aac_bucket/price_df.parquet'
    """
    gs = gcsfs.GCSFileSystem()
    arrow_df = pq.ParquetDataset(path, filesystem=gs)
    if to_pandas:
        return arrow_df.read_pandas().to_pandas()
    return arrow_df   