# coding: utf-8
from sqlalchemy import Column, Integer, SmallInteger, String, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

def get_column(classModel, column):
    return getattr(classModel, column.lower())


class BookShelf(Base):
    __tablename__ = 'books_bookshelf'
    id = Column(String, primary_key=True)
    name = Column(String)

    def toJSON(self):
        json = {
            'id': self.id,
            'name': self.name
        }
        return json


class Book(Base):
    __tablename__ = 'books_book'

    id = Column(String, primary_key=True)
    download_count  = Column(String)
    gutenberg_id = Column(String)
    media_type = Column(String)
    title = Column(String)
    
    def toJSON(self):
        json = {
            'id': self.id,
            'download_count': self.download_count,
            'gutenberg_id': self.gutenberg_id,
            'media_type': self.media_type,
            'title': self.title
        }
        return json

class BookBookshelves(Base):
    __tablename__ = 'books_book_bookshelves'

    id = Column(String, primary_key=True)
    book_id = Column(String)
    bookshelf_id = Column(String)
    
    def toJSON(self):
        json = {
            'id': self.id,
            'book_id': self.book_id,
            'bookshelf_id': self.bookshelf_id
        }
        return json

class BookLanguages(Base):
    __tablename__ = 'books_book_languages'

    id = Column(String, primary_key=True)
    book_id = Column(String)
    language_id = Column(String)
    
    def toJSON(self):
        json = {
            'id': self.id,
            'book_id': self.book_id,
            'language_id': self.language_id
        }
        return json

class Language(Base):
    __tablename__ = 'books_language'

    id = Column(String, primary_key=True)
    code = Column(String)
    
    def toJSON(self):
        json = {
            'code': self.code,
            'id': self.id
        }
        return json


class BookSubjects(Base):
    __tablename__ = 'books_book_subjects'

    id = Column(String, primary_key=True)
    book_id = Column(String)
    subject_id = Column(String)
    
    def toJSON(self):
        json = {
            'id': self.id,
            'book_id': self.book_id,
            'subject_id': self.subject_id
        }
        return json


class Subjects(Base):
    __tablename__ = 'books_subject'

    id = Column(String, primary_key=True)
    name = Column(String)

    def toJSON(self):
        json = {
            'id':self.id,
            'name': self.name
        }
        return json


class Format(Base):
    __tablename__ = 'books_format'

    id = Column(String, primary_key=True)
    mime_type = Column(String)
    url = Column(String)
    book_id = Column(String)

    def toJSON(self):
        json = {
            'id': self.id,
            'mime_type': self.mime_type,
            'url': self.url,
            'book_id': self.book_id
        }
        return json

class Author(Base):
    __tablename__ = 'books_author'

    id = Column(Integer, primary_key=True)
    birth_year = Column(String)
    death_year = Column(String)
    name = Column(String)

    def toJSON(self):
        json = {
            'id':self.id,
            'birth_year': self.birth_year,
            'death_year': self.death_year,
            'name': self.name
        }
        return json

class BookAuthors(Base):
    __tablename__ = 'books_book_authors'

    id = Column(String, primary_key=True)
    book_id = Column(String)
    author_id = Column(String)

    def toJSON(self):
        json = {
            'id': self.id,
            'book_id': self.book_id,
            'author_id': self.author_id
        }
        return json

