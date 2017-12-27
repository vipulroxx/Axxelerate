import pymysql.cursors
import credentials
import hashlib



class AxxeleratePipeline(object):

    def __init__(self):
        print("init AxxeleratePipeline")
        self.connectToDb()

    def connectToDb(self):
        self.connection = pymysql.connect(host = credentials.host,
                                     user = credentials.user,
                                     password = credentials.password,
                                     db = credentials.db,
                                     cursorclass = pymysql.cursors.DictCursor)

    def insert_url(self, url, cursor):
        sql_url_filter = "SELECT `ID` FROM pages WHERE `url` = %s"
        cursor.execute(sql_url_filter, url)
        pageID = 0
        result = cursor.fetchone()
        if (result == None):
            sql_url_title = "INSERT INTO `pages` (`url`) VALUES (%s)"
            cursor.execute(sql_url_title, (url))
            pageID = cursor.lastrowid
        else:
            pageID = result["ID"]
        return pageID

    def process_item(self, item, spider):
        try:
            with self.connection.cursor() as cursor:

                urlHash = hashlib.md5(item['url']).hexdigest()
                sql_url_title = "INSERT INTO `pages` (`url`, `title`, `urlHash`) VALUES (%s,%s,%s)"
                cursor.execute(sql_url_title, (item['url'], item['title'], urlHash))
                pageID = cursor.lastrowid

                placeHolders = []
                valuesToInsert = []

                for word in item['keywords']:
                    valuesToInsert.append(word)
                    valuesToInsert.append(pageID)
                    placeHolders.append("(%s,%s)")

                if len(placeHolders) > 0:
                    sql_keywords = "INSERT INTO `keywords` (`word`, `pageID`) VALUES " + (",".join(placeHolders))
                    cursor.execute(sql_keywords, valuesToInsert)

                linksToInsert = []
                placeHolders = []
                for url in item['linksTo']:
                    linksToInsert.append(urlHash)
                    linksToInsert.append(hashlib.md5(url).hexdigest())
                    placeHolders.append("(%s,%s)")

                if len(placeHolders) > 0:
                    sql_links = "INSERT INTO `linksTo` (`fromHash`, `toHash`) VALUES " + (",".join(placeHolders))
                    cursor.execute(sql_links, linksToInsert)

            self.connection.commit()

        except pymysql.OperationalError as e:
            print("caught pymysql.OperationError: ")
            print(e)
            print("reconnecting to DB")
            connectToDb()
            process_item(self, item, spider)
        except Exception as e: 
            print("GGGGRRRRRRRRRRRRRRRRRRRR")
            print(e)
            pass
        return item
