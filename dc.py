#!/usr/bin/python3

import pandas as pd
import argparse

IDFCFIRSTB_SKIPROWS = 12
IDFCFIRSTB_SKIPFOOTER = 8
HDFC_SKIPROWS = 20
HDFC_SKIPFOOTER = 26

def dividend(credit):
    if credit < 5000:
        return credit
    else:
        return (credit * 1.0) / 0.925

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help = 'bank statement file to parse for dividend')
    return parser.parse_args()

#args = parseArgs()
bankStatementFilePath = '/mnt/c/Users/jayra/Downloads/IDFCFIRSTBankStatement_FY2020_2021.xlsx'
bankStatementFilePath = '/mnt/c/Users/jayra/Downloads/IDFCFIRSTBankStatement_FY2021_2022.xlsx'
skipRows = 0
skipFooter = 0
sep = '/'
idfcStatement = True

if idfcStatement:
    skipRows = IDFCFIRSTB_SKIPROWS
    skipFooter = IDFCFIRSTB_SKIPFOOTER
    sep = '/'
else:
    skipRows = HDFC_SKIPROWS
    skipFooter = HDFC_SKIPFOOTER
    sep = '-'
    bankStatementFilePath = '/mnt/c/Users/jayra/Downloads/50100144257742_1630677971740.xls'

df = pd.read_excel(bankStatementFilePath,
                   thousands = ',',
                   skiprows = skipRows,
                   skipfooter = skipFooter)

# Align HDFC Statement column name to IDFCFIRSTB
if not idfcStatement:
    df['Particulars'] = df['Narration']
    df['Credit'] = df['Deposit Amt.']
    df['Transaction Date'] = df['Date']

# Keep a copy for SGB calculation later.
df0 = df
sgbRows = df0.Particulars.str.contains('CMS')

df = df[['Particulars', 'Transaction Date', 'Credit']]
# Reddit discusion said to search for ACH|CMS.
# Although my research shows it is NACH for Equity and CMS for SGB
df = df[df.Particulars.str.contains('ACH|DIV')]

# Rows with TDS.
tdsRows = df.Credit.gt(5000)

# Calculate Dividend based on Credit
# Assuming no TDS, Credit eq Dividend
df['Dividend'] = df.Credit
# Fix Dividend where 7.5 percent TDS is deducted
df.loc[tdsRows, 'Dividend'] = df.Credit.mul(1.0).div(1.0 - 0.075)

# Print Summary
print('SUMMARY:')
print('DIV = {:.2f}'.format(df.Dividend.sum()))
print('TAX = {:.2f}'.format(df.Dividend.mul(30).div(100).sum()))
print('TDS = {:.2f}'.format(df[tdsRows].Dividend.mul(7.5).div(100).sum()))
print('SGB = {:.2f}'.format(df0[sgbRows].Credit.sum()))
print('TAX = {:.2f}'.format(df0[sgbRows].Credit.mul(30).div(100).sum()))
if idfcStatement:
    interestRows = df0.Particulars.str.contains('INTEREST CREDIT')
    print('INT = {:.2f}'.format(df0[interestRows].Credit.sum()))
    print('TAX = {:.2f}'.format(df0[interestRows].Credit.mul(30).div(100).sum()))

# Print CSV for ClearTax after adding Narration 
df['Narration'] = df.Particulars.str.rsplit(sep, 2).str[1]
df['Transaction Date'] = pd.to_datetime(df['Transaction Date'])
#print(df.to_csv(columns = ['Narration','Transaction Date', 'Dividend'], date_format="%d/%m/%Y"))

