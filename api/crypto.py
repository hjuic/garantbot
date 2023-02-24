import requests
from configparser import ConfigParser

config = ConfigParser()


def create_invoice(amount, asset):
    config.read('config/config.ini')
    headers = {'Crypto-Pay-API-Token': f'{config["pay"]["cryptobot"]}'}
    r = requests.get(f'https://pay.crypt.bot/api/createInvoice?asset={asset}&amount={amount}', headers=headers)
    return r.json()['result']


def check_invoice(id):
    headers = {'Crypto-Pay-API-Token': f'{config["pay"]["cryptobot"]}'}
    r = requests.get(f'https://pay.crypt.bot/api/getInvoices?invoice_ids={id}&status=paid', headers=headers)
    return r.text


def get_rate(asset):
    r = requests.get(f'https://api.coincap.io/v2/rates/{asset}')
    return r.json()['data']['rateUsd']


def get_currency():
    r = requests.get('https://currate.ru/api/?get=rates&pairs=USDRUB&key=420feea99b30fc7f3841523033e257fc')
    return r.json()['data']['USDRUB']
