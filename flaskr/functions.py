### INF601 - Advanced Programming in Python
### Justin Stewart
### Final Project
### functions.py

import configparser
import requests
import time
import os
import logging

#   [Portable]
#   Starts logging
def start_logging():
    log_file = "log.csv"
    create_log_file(log_file)
    logging.basicConfig(
                        filename=log_file,
                        filemode='w',
                        format='%(asctime)s.%(msecs)03d,%(levelname)s,%(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO
                        )

#   [Portable]
#   Creates a log file if one does not exist and writes headers
def create_log_file(log_filename):
    if not os.path.exists(log_filename):
        with open(log_filename, 'w') as f:
            f.write("Timestamp,Level,Message\n")

#   [Portable]
#   This function reads the config file and returns headers as a dictionary
#   that can be passed to API requests
def return_headers_configparser(configfile):
    config = configparser.ConfigParser()
    config.read([configfile])
    headers = {
        'X-CP-API-ID': config['KEYS']['x-cp-api-id'],
        'X-CP-API-KEY': config['KEYS']['x-cp-api-key'],
        'X-ECM-API-ID': config['KEYS']['x-ecm-api-id'],
        'X-ECM-API-KEY': config['KEYS']['x-ecm-api-key'],
        'Content-Type': 'application/json'
    }
    return headers

#   [Portable]
#   This function attempts a get with 5 retries, Rate Limits do not affect the retry counter.
def get_with_retry(url, headers):

    count = 0
    while count < 5:
        try:
            #logging.info(f'Get attempt {count}/5 on "{url}"')
            response = requests.get(url=url, headers=headers)
            status_code = response.status_code
            if status_code == 200:
                logging.info(f'GET successful on url "{url}". status code = {status_code}')
                return response
            elif status_code == 429:
                time.sleep(2)
                count += 1
                logging.warning(f'Status code: {status_code}. Rate limit reached. Retrying: {count}/5')
            elif status_code == 403:
                logging.error(f'Unauthorized api keys on "{url}". status code = {status_code}')
                return None
            elif status_code == 404:
                logging.error(f'Bad Url "{url}". status code = {status_code}')
                return None
            elif status_code == 500:
                count = count + 1
                time.sleep(1)
                logging.warning(f'Internal Server error on "{url}". Status code = {status_code}. Retrying: {count}/5')
            elif count == 4:
                logging.error(f'Status code: {status_code} GET failed on "{url}"')
                return None
            else:
                count = count + 1
                logging.error(f'Unexpected status code:{status_code} for GET on "{url}". Retrying: {count}/5')
        except Exception as e:
            logging.critical(f'Exception on "{url}" as {e}// {count}/5')
            count += 1

    logging.error(f'Failed to GET a response on "{url}" after 5 attempts.')
    return None