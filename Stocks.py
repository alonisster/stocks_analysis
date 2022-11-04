import yfinance as yf
import numpy as np
import requests
import statistics
import csv
import matplotlib.pyplot as plt
from symbols import SP500_symbol, nasdaq_symbols


def getSingleDayDifferences(hist):
    diffsInPercentage = getDiffsInPercentage(hist)
    diffsInPercentageValues = diffsInPercentage.values
    dayOfTheWeek = diffsInPercentage.index.dayofweek
    aggregatedDiffs = clusterDiffsToDays(diffsInPercentageValues, dayOfTheWeek);
    return aggregatedDiffs


def filterEmptyArr(arr):
    return arr.length != 0


def getDiffsInPercentage(hist):
    open_price = hist.Open
    close_price = hist.Close
    diffs = close_price - open_price
    diffsInPercentage = (diffs / open_price) * 100
    for i in range(len(diffsInPercentage)):
        if np.isinf(diffsInPercentage[i]):
            diffsInPercentage[i] = 0

    return diffsInPercentage


# returns single stock data by month.
def clusterDiffsToMonths(diffsInPercentageValues, related_month_array):
    aggregatedDiffs = np.zeros(12, dtype=float)
    for i in range(len(related_month_array)):
        curMonth = related_month_array[i]
        # -1 because month is 1-12 and arr is 0-11
        aggregatedDiffs[curMonth - 1] += diffsInPercentageValues[i]
    return aggregatedDiffs;


def clusterDiffsToDays(diffsInPercentageValues, dayOfTheWeek):
    aggregatedDiffs = np.zeros(6, dtype=float)
    for i in range(len(dayOfTheWeek)):
        curDay = dayOfTheWeek[i]
        aggregatedDiffs[curDay] += diffsInPercentageValues[i]
    # now aggregatedDiffs contains all the data by Day.
    return aggregatedDiffs;


def getTickers(stock_symbols_arr):
    delimiter = " "
    stocks_string = delimiter.join(stock_symbols_arr)
    tickers = yf.Tickers(stocks_string)
    return tickers


def getAllDayDifferences(stock_hists_arr):
    all_tickers_differences_sum = np.zeros(6)
    for hist in stock_hists_arr:
        single_stock_data = getSingleDayDifferences(hist)
        if not np.isnan(single_stock_data).any():
            all_tickers_differences_sum += single_stock_data
        # else:
        #     print("diff is nan")
    stocks_count = len(stock_hists_arr)
    avgDiffs = all_tickers_differences_sum / stocks_count
    return avgDiffs;


def getSingleStockMonthDifference(hist):
    if hist.empty:
        print("Problem occured: empty hist!!!")
        return np.zeros(6)
    diffsInPercentage = getDiffsInPercentage(hist)
    diffsInPercentageValues = diffsInPercentage.values
    related_months = diffsInPercentage.index.month
    aggregatedDiffs = clusterDiffsToMonths(diffsInPercentageValues, related_months)
    return aggregatedDiffs


def clusterDiffsToWeeks(diffsInPercentageValues, related_weeks):
    aggregatedDiffs = np.zeros(53, dtype=float)
    for i in range(len(related_weeks)):
        cur_week = related_weeks[i]
        # -1 because week is 1-53 and arr is 0-52
        aggregatedDiffs[cur_week - 1] += diffsInPercentageValues[i]
    return aggregatedDiffs


def getSingleStockWeeklyDifference(hist):
    diffsInPercentage = getDiffsInPercentage(hist)
    diffsInPercentageValues = diffsInPercentage.values
    related_weeks = diffsInPercentage.index.week
    aggregatedDiffs = clusterDiffsToWeeks(diffsInPercentageValues, related_weeks)
    return aggregatedDiffs


def getAllWeeklyDifferences(hists):
    all_tickers_differences_sum = np.zeros(53)
    for hist in hists:
        single_stock_data = getSingleStockWeeklyDifference(hist)
        if not np.isnan(single_stock_data).any():
            all_tickers_differences_sum += single_stock_data
        elif np.isinf(single_stock_data).any():
            print("Unexpected inf value!")
    stocks_count = len(hists)
    avgDiffs = all_tickers_differences_sum / stocks_count
    return avgDiffs;


def getAllMonthDifferences(stock_hists_arr):
    all_tickers_differences_sum = np.zeros(12)
    for hist in stock_hists_arr:
        single_stock_data = getSingleStockMonthDifference(hist)
        if not np.isnan(single_stock_data).any():
            all_tickers_differences_sum += single_stock_data
    stocks_count = len(stock_hists_arr)
    avgDiffs = all_tickers_differences_sum / stocks_count
    return avgDiffs;


def filterBrokenTags(stock_tag, period):
    ticker = yf.Ticker(stock_tag)
    hist = ticker.history(period=period)
    return hist.empty == False


def getHistObjects(stock_tag, period):
    ticker = yf.Ticker(stock_tag)
    hist = ticker.history(period=period)
    return hist


def writeToExcel(daily, monthly, period):
    with open('stocks_file.csv', mode='w') as stocks_file:
        stocks_writer = csv.writer(stocks_file, delimiter=',')  # lineterminator='\n'
        stocks_writer.writerow([period])
        stocks_writer.writerow(daily)
        stocks_writer.writerow(monthly)


def plotGraphs(aggregated_day_diffs, aggregated_weekly_diffs, aggregated_month_diff):
    # print("Daily change as function of the day in the week: from monday to saturday.")
    # print(aggregated_day_diffs);
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    plt.figure(1)
    plt.bar(days, aggregated_day_diffs)
    plt.title("Change by day in the week")


    # print("Weekly change as function of the week in the year")
    # print(aggregated_weekly_diffs)
    weeks = range(53)
    plt.figure(2)
    plt.bar(weeks, aggregated_weekly_diffs)
    plt.title("Change by week in the year")


    # print("Monthly change as function of the day in the month in the year: from January to December.")
    # print(aggregated_month_diff)
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
              "November", "December"]
    plt.figure(3)
    plt.bar(months, aggregated_month_diff)
    plt.title("Change by month in the year")
    plt.show()


def generateGraphsFromSymbols(wanted_time_range, symbols_array):
    symbols_hists = list(map(lambda x: getHistObjects(x, wanted_time_range), symbols_array))
    hists_filtered = list(filter(lambda hist: hist.empty == False, symbols_hists))
    aggregated_day_diffs = getAllDayDifferences(hists_filtered)
    aggregated_weekly_diffs = getAllWeeklyDifferences(hists_filtered)
    aggregated_month_diff = getAllMonthDifferences(hists_filtered)
    plotGraphs(aggregated_day_diffs, aggregated_weekly_diffs, aggregated_month_diff)


generateGraphsFromSymbols("10y", SP500_symbol)
