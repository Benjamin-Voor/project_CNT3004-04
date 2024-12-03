import time


# Dictionary to store start and end times of operations
operation_times = {
    "upload_start": None,
    "upload_end": None,
    "download_start": None,
    "download_end": None,
    "response_start": None,
    "response_end": None
}


# Function to record the start time of an upload
def start_upload():
    operation_times["upload_start"] = time.time()


# Function to record the end time of an upload
def end_upload():
    operation_times["upload_end"] = time.time()


# Function to record the start time of a download
def start_download():
    operation_times["download_start"] = time.time()


# Function to record the end time of a download
def end_download():
    operation_times["download_end"] = time.time()


# Function to get the elapsed time for upload
def get_upload_time():
    if operation_times["upload_start"] is not None and operation_times["upload_end"] is not None:
        return operation_times["upload_end"] - operation_times["upload_start"]
    else:
        return None


# Function to get the elapsed time for download
def get_download_time():
    if operation_times["download_start"] is not None and operation_times["download_end"] is not None:
        return operation_times["download_end"] - operation_times["download_start"]
    else:
        return None


# Function to record the start time of a response
def start_response():
    operation_times["response_start"] = time.time()


# Function to record the end time of a response
def end_response():
    operation_times["response_end"] = time.time()


# Function to get the elapsed time for response
def get_response_time():
    if operation_times["response_start"] is not None and operation_times["response_end"] is not None:
        return operation_times["response_end"] - operation_times["response_start"]
    else:
        return None


# Function to calculate the average rate of transmission
def calculate_rate(file_size, elapsed_time):
    if elapsed_time > 0:
        # Convert file size to megabytes and elapsed time to seconds
        file_size_mb = file_size / (1024 * 1024)
        rate = file_size_mb / elapsed_time
        return rate
    else:
        return None


# Function to print start and end times for upload, download, and response
def print_times():
    if operation_times["upload_start"] is not None and operation_times["upload_end"] is not None:
        print(f"Upload started at: {time.ctime(operation_times['upload_start'])}")
        print(f"Upload ended at: {time.ctime(operation_times['upload_end'])}")
    if operation_times["download_start"] is not None and operation_times["download_end"] is not None:
        print(f"Download started at: {time.ctime(operation_times['download_start'])}")
        print(f"Download ended at: {time.ctime(operation_times['download_end'])}")
    if operation_times["response_start"] is not None and operation_times["response_end"] is not None:
        print(f"Response started at: {time.ctime(operation_times['response_start'])}")
        print(f"Response ended at: {time.ctime(operation_times['response_end'])}")
