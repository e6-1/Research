"""Pulls data from Yahoo!Finance and computes lower-partial moments surrounding keynotes."""
from yahoo_finance import Share
from datetime import datetime
from datetime import timedelta
import pandas as pd
import plotly
from plotly.graph_objs import Scatter, Layout
from pprint import pprint


def main():
    apple = Share('AAPL')
    keynotes = get_keynotes()

    scatters = []
    for i, event in enumerate(keynotes['events']):
        clustered = keynotes['events'][event]
        if event.weekday() == 6:
            study_start = event - timedelta(days=185)  # Back 30 business days
            study_end = event + timedelta(days=43)  # Forward 30 business days
        elif event.weekday() == 5:
            study_start = event - timedelta(days=186)  # Back 30 business days
            study_end = event + timedelta(days=44)  # Forward 30 business days
        else:
            study_start = event - timedelta(days=182)  # Back 30 business days
            study_end = event + timedelta(days=42)  # Forward 30 business days
        study_info = apple.get_historical(study_start.strftime('%Y-%m-%d'), study_end.strftime('%Y-%m-%d'))
        study_returns = get_returns(study_info)
        lpms = []
        for j in range(len(study_returns)):
            lpm = lower_partial_moment(2, 0.0005, study_returns[:j])
            lpms.append(lpm)
        if clustered:
            color = 'rgba(255, 182, 193, .9)'
        else:
            color = 'rgba(152, 0, 0, .8)'
        scatter = Scatter(
            x=range(len(lpms)),
            y=lpms,
            name='Event {0}'.format(i),
            mode='markers',
            marker=dict(
                size=10,
                color=color,
                line=dict(
                    width=2,
                    color='rgb(0, 0, 0)'
                )
        ))
        scatters.append(scatter)
    plotly.offline.plot({
        "data": scatters,
        "layout": Layout(title="Lower-Partial Moments")
    })


def get_returns(historical_info):
    """Gets the returns based on yahoo historical info."""
    returns = []
    for i, entry in enumerate(historical_info):
        if i == 0:
            continue
        previous_close = float(historical_info[i - 1]['Close'])
        current_close = float(entry['Close'])
        entry_return = (current_close - previous_close) / previous_close
        returns.append(entry_return)
    return returns


def lower_partial_moment(alpha, tolerance, stock_returns):
    """Calculates the lower partial moment."""
    lower_partials = [max([0, tolerance - stock_return])**alpha for stock_return in stock_returns]
    sum_max = sum(lower_partials)
    if sum_max == 0:
        return 0
    lpm = sum_max / float(len(lower_partials))
    return lpm


def get_keynotes():
    """Gets lists of keynote invitation/event dates."""
    invites = [
        "March 10, 2016",
        "August 27, 2015",
        "February 27, 2015",
        "October 8, 2014",
        "August 28, 2014",
        "October 15, 2013",
        "September 3, 2013",
        "October 16, 2012",
        "September 4, 2012",
        "February 28, 2012",
        "January 12, 2012",
        "September 27, 2011",
        "February 22, 2011",
        "October 13, 2010",
        "August 25, 2010",
        "April 5, 2010",
        "January 18, 2010",
        "August 31, 2009",
        "October 9, 2008",
        "September 2, 2008",
        "February 27, 2008",
        "September 5, 2007",
        "July 31, 2007",
        "March 20, 2007",
        "September 5, 2006",
        "February 21, 2006",
        "October 14, 2005",
        "October 4, 2005",
        "August 29, 2005",
    ]

    events = {
        "March 21, 2016": False,
        "September 9, 2015": False,
        "March 9, 2015": False,
        "October 16, 2014": True,
        "September 9, 2014": True,
        "October 22, 2013": True,
        "September 10, 2013": True,
        "October 23, 2012": True,
        "September 12, 2012": True,
        "March 7, 2012": False,
        "January 19, 2012": False,
        "October 4, 2011": False,
        "March 2, 2011": False,
        "October 20, 2010": True,
        "September 1, 2010": True,
        "April 8, 2010": False,
        "January 27, 2010": False,
        "September 9, 2009": False,
        "October 14, 2008": True,
        "September 9, 2008": True,
        "March 6, 2008": False,
        "September 12, 2007": True,
        "August 7, 2007": True,
        "April 15, 2007": False,
        "September 12, 2006": False,
        "February 28, 2006": False,
        "October 19, 2005": True,
        "October 12, 2005": True,
        "September 7, 2005": True
    }

    invites_dt = [datetime.strptime(invite, '%B %d, %Y') for invite in invites]

    events_dt = {}
    for event in events:
        event_dt = datetime.strptime(event, '%B %d, %Y')
        events_dt[event_dt] = events[event]

    keynotes = {
        'invites': invites_dt,
        'events': events_dt
    }
    return keynotes

if __name__ == '__main__':
    main()
