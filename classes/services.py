
import os, json,sys
from flask import jsonify, request, Response, json
from werkzeug.datastructures import Headers
import requests 
from data_models import BookShelf, Book, BookBookshelves, BookLanguages, Language, BookSubjects, Subjects, Format, Author, BookAuthors
from sqlalchemy.sql import func, and_,or_, distinct
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import re
from bs4 import BeautifulSoup

FILE_PATH = str(os.path.realpath(__file__))
FILE_PATH = FILE_PATH.replace("services.pyc", "")
FILE_PATH = FILE_PATH.replace("services.pyo", "")
FILE_PATH = FILE_PATH.replace("services.py", "")


class register_services:
    print('                    Registered Services')
    print('-------------------------------------------------------------------')
    def __init__(self, app, API, KEY):
        self.app = app
        self.API = API
        self.KEY = KEY
        # self.API_URL = API + '/v1/services/'
        self.dManagers = self.app.config["Managers"]["DataManager"]
        self.dEngines = self.app.config["Managers"]["Engine"]

        self.URL = "http://skunkworks.ignitesol.com:8000/books​"

        # self.app.add_url_rule(API + '/v1/services/sendfresponse', 'sendfresponse', self.sendfresponse, methods=['GET','POST'])

        self.app.add_url_rule(API + '/services/getsummarydata', 'getsummarydata', self.get_summary_data, methods=['POST'])


    def get_params(self, request):
        return request.json if (request.method == 'POST') else request.args

    def sendfresponse(self):
        params = self.get_params(request)
        if params != False:
            fname = params.get('name')
            # print FILE_PATH
            # print fname

            fPath = FILE_PATH + fname

            file = open(fPath, 'rb').read()
            response = Response()
            response.data = file
            response.status_code = 200
            response.headers = Headers()
            response.headers['Pragma'] = 'public'
            response.headers['Expires'] = '0'
            response.headers['Cache-Control'] = 'public'
            response.headers['Content-Description'] = 'File Transfer'
            response.headers['Content-Type'] = 'application/octet-stream'#'text/plain' #'application/vnd.ms-excel' #'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = 'attachment; filename='+fname
            response.headers['Content-Transfer-Encoding'] = 'binary'
            # response.headers['X-Key'] = self.KEY

            os.remove(fPath)

            return response
        else:
            return False

    def getdictresult(self, labels, query_result):
        result = []

        for node in query_result:
            row = {}
            for key, value in zip(labels, node):
                row.setdefault(str(key), str(value))
            result.append(row)
        return result

    def getdistinctvalues(self, query_result):
        result = []

        for node in query_result:
            for key in node:
                result.append(str(key))
        result = list(set(result))
        return result

    def get_summary_data(self):
        params = self.get_params(request)
        result = {}

        topic = params.get("topic", None)
        pageFrom = params.get("pageFrom", 0)
        pageTo = params.get("pageTo", 25)
        search = params.get("search", None)

        all_data = []


        bookshelf_search_result = []
        book_search_result = []
        subject_search_result = []
        author_search_result = []
        bookids = []
        pg = self.dManagers.getSession()

        if search != None:
            book_query = pg.query(Book.id).filter( Book.title.like('%'+search+'%') ).all()
            bookids = self.getdistinctvalues(book_query)
            # print("Bookids: ", bookids)

            subject_query = pg.query(Subjects.id).filter( Subjects.name.like('%'+search+'%') ).all()
            subjectids = self.getdistinctvalues(subject_query)
            # print("Subjectids: ", subjectids)

            author_query = pg.query(Author.id).filter( Author.name.like('%'+search+'%') ).all()
            authorids = self.getdistinctvalues(author_query)
            # print("Authorids: ", authorids)

            if len(subjectids) > 0:
                sub_query = pg.query(BookSubjects.book_id).filter(BookSubjects.subject_id.in_(subjectids)).all()
                bookids.extend(self.getdistinctvalues(sub_query))
                # print("if subject: ", bookids)

            if len(authorids) > 0:
                auth_query = pg.query(BookAuthors.book_id).filter(BookAuthors.author_id.in_(tuple(authorids))).all()
                bookids.extend(self.getdistinctvalues(auth_query))
                # print("if author: ", bookids)

            if len(bookids) > 0:
                shelf_query = pg.query(BookBookshelves.bookshelf_id).filter(BookBookshelves.book_id.in_(tuple(bookids))).all()
                bookshelf_search_ids = self.getdistinctvalues(shelf_query)

                bookshelf_filter = []
                bookshelf_filter.append(BookShelf.name.like('%'+topic+'%'))
                if search != None:
                    bookshelf_filter.append(BookShelf.id.in_(tuple(bookshelf_search_ids)))
                bookshelf_result = pg.query(BookShelf.id).filter(and_(*bookshelf_filter)).all()
                bookshelf_search_result = self.getdistinctvalues(bookshelf_result)

        # filters = params.get("filters", []);
        # print(filters)
        
        # r = requests.post(url = "http://skunkworks.ignitesol.com:8000/books", params = params)
        # data = r.json() 
        # print(data.keys())

        # for key in data.keys():
        #     print(key,'---',data[key])
        #     if key != "results":
        #         result.setdefault(key, data[key])

        # print("search: ", search)
        if topic != None:
            # Recieve data as per topic from bookshelf
            bookshelf_ids = []
            if len(bookshelf_search_result) > 0:
                bookshelf_ids = bookshelf_search_result
            else:
                bookshelf_result = pg.query(BookShelf.id).filter(BookShelf.name.like('%'+topic+'%')).all()
                bookshelf_ids = self.getdistinctvalues(bookshelf_result)

            # print(bookshelf_ids)

            #Getting Book ids
            bookshelves_result = pg.query(BookBookshelves.book_id).filter(BookBookshelves.bookshelf_id.in_(tuple(bookshelf_ids))).all()
            book_ids = self.getdistinctvalues(bookshelves_result)
            # print(book_ids)
            
            index = 1
            popularity_result = pg.query(Book.id).filter(Book.id.in_(tuple(book_ids))).order_by(Book.download_count.desc()).slice(pageFrom, pageTo).all()
            for rec in popularity_result:
                _id = rec[0]
                book_details = {}
                #Getting Book Details
                book_result = pg.query(Book.download_count, Book.media_type, Book.title).filter( Book.id == str(_id) ).all()
                book_list = self.getdictresult(["download_count", "media_type", "title"], book_result)
                book_details = book_list[0]
                # print(book_details)

                #language ids
                language_result = pg.query(BookLanguages.language_id).filter(BookLanguages.book_id == _id).all()
                language_ids = self.getdistinctvalues(language_result)

                lang_result = pg.query(Language.code).filter(Language.id.in_(tuple(language_ids)))
                lang_codes = self.getdistinctvalues(lang_result)
                book_details.setdefault("language", lang_codes[0])

                #Subjects
                subject_results = pg.query(BookSubjects.subject_id).filter(BookSubjects.book_id == _id).all()
                subject_ids = self.getdistinctvalues(subject_results)

                sub_results = pg.query(Subjects.name).filter(Subjects.id.in_(tuple(subject_ids))).all()
                subject_names = self.getdistinctvalues(sub_results)
                book_details.setdefault("subject", subject_names)

                #Format
                format_result = pg.query(Format.mime_type, Format.url).filter(Format.book_id == _id).all()
                format_data = self.getdictresult(["mime_type", "url"], format_result)
                book_details.setdefault("format", format_data)

                # Author
                author_results = pg.query(BookAuthors.author_id).filter(BookAuthors.book_id == _id).all()
                author_ids = self.getdistinctvalues(author_results)

                auth_results = pg.query(Author.birth_year, Author.death_year, Author.name).filter( Author.id.in_(tuple(author_ids)) ).all()
                auth_details = self.getdictresult(["birth_year", "death_year", "name"], auth_results)
                # book_details.setdefault("author", auth_details[0])

                if len(auth_details) > 0:
                    book_details.setdefault("author", auth_details[0])
                else:
                    book_details = {}

                # imgFormat = "text/html; charset=utf-8"
                # imgURL = ""
                # for fr in format_data:
                #     if fr["mime_type"] == imgFormat:
                #         imgURL = fr["url"].strip()
                
                # if imgURL not in [None, ""]:
                #     print(imgURL,'---')
                #     response = requests.get(url=imgURL)
                #     soup = BeautifulSoup(response.text, 'html.parser')
                #     img_tags = soup.find_all('img')
                #     urls = [img['src'] for img in img_tags]
                #     for url in urls:
                #         filename = re.search(r'/([\w_-]+[.](jpg|gif|png))$', url)
                #         with open(filename.group(1), 'wb') as f:
                #             if 'http' not in url:
                #                 # sometimes an image source can be relative 
                #                 # if it is provide the base url which also happens 
                #                 # to be the site variable atm. 
                #                 url = '{}{}'.format(imgURL, url)
                #             response = requests.get(url)
                #             f.write(response.content)


                #     with open('pic'+str(index)+'.jpg', 'wb') as handle:
                #         response = requests.get(imgURL, stream=True)
                #         if not response.ok:
                #             print(response)

                #         for block in response.iter_content(1024):
                #             if not block:
                #                 break
                #             handle.write(block)

                index += 1
                if book_details != {}:
                    all_data.append(book_details)


        self.dManagers.closeSession(pg)
    
        return jsonify(Result = all_data)
