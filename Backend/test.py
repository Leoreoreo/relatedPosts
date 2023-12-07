from datetime import datetime


def calculate_weeks(d1, d2):
    # Convert the date strings to datetime objects
    d1 = datetime.strptime(d1, '%Y-%m-%d %H:%M:%S')
    d2 = datetime.strptime(d2, '%Y-%m-%d %H:%M:%S')

    # Calculate the difference between d2 and d1
    date_diff = d2 - d1

    # Calculate the number of weeks
    weeks = date_diff.days // 7

    # If there is a remainder, add 1 to the weeks count
    if date_diff.days % 7 != 0:
        weeks += 1

    return weeks





if __name__ == '__main__':
    for i in range(7+1):
        print(i)