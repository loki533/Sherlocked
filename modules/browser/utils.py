from datetime import datetime, timedelta


def chrome_time(value):

    if value == 0:
        return "Never"
    
     #chrome stores the date as in microseconds passed since 1601
     #what this function does is , it converts ms -> seconds -> years 
     #returns the years passed since 1601 , as readable date

    epoch = datetime(1601, 1, 1)

    return epoch + timedelta(microseconds=value)