__author__ = 'akshat'
import pycurl, json
from io import BytesIO

kimono_url = 'https://www.kimonolabs.com/api/dkp3od1q?apikey=bd28c0ebca062a3e1dcc4e7d567e7bc9'

c = pycurl.Curl()
data = BytesIO()
c.setopt(c.URL, kimono_url)
c.setopt(c.WRITEFUNCTION, data.write)
c.perform()
dictionary = json.loads(data.getvalue())


articles_dir = '/home/akshat/data/hindu/plain_text'

hindu_data = dictionary['results']['collection1']
count = 0
for article in hindu_data:
    try:
        text =''
        for key in article:
            text += ' ' + article[key]

        filename = 'hindu_' + str(count)
        filepath = articles_dir + '/' + filename + '.txt'
        writer = file(filepath, 'w')
        text = text.encode('ascii', 'ignore')
        writer.write(text)
        count += 1
    except Exception, e:
        print str(e)