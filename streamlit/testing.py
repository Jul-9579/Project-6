from datetime import datetime

date = datetime.strptime(article.get("date"), '%b %d, %Y - %H:%M')
print(date)