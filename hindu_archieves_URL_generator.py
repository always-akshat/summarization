__author__ = 'akshat'

day = 1
month = 01
year = 2009

for year in range(2009, 2015):
    for month in range(01, 13):
        for day in range( 01, 32):
            print 'http://www.thehindu.com/archive/web/' +str(year) +'/' +str(month) + '/' + str(day)
