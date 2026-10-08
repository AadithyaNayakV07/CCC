import threading
from azure.storage.blob import BlobServiceClient
from PIL import Image
import io

# Azure connection
connection_string = ""
container_name = "images"

blob_service_client = BlobServiceClient.from_connection_string(
    connection_string
)


def process_image(blob_name):
    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=blob_name
    )

    # Download image
    data = blob_client.download_blob().readall()
    stream = io.BytesIO(data)

    # Open and resize
    img = Image.open(stream)
    img = img.resize((200, 200))

    # Save processed image
    output = io.BytesIO()
    img.save(output, format="JPEG")
    output.seek(0)

    # Upload processed image
    new_name = "processed_" + blob_name

    blob_service_client.get_blob_client(
        container=container_name,
        blob=new_name
    ).upload_blob(output, overwrite=True)

    print(f"Processed: {blob_name}")


def main():

    container_client = blob_service_client.get_container_client(
        container_name
    )

    blobs = container_client.list_blobs()

    threads = []

    # Create threads
    for blob in blobs:

        # Don't process already processed images
        if blob.name.startswith("processed_"):
            continue

        t = threading.Thread(
            target=process_image,
            args=(blob.name,)
        )

        threads.append(t)
        t.start()

    # Wait for all threads
    for t in threads:
        t.join()

    print("All images processed successfully")


if __name__ == "__main__":
    main()


#pip install azure-storage-blob pillow
