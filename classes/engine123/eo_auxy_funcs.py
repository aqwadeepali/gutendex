from pandas import read_sql_query
from elib import str2date
from numpy import NaN
from sqlalchemy import *
from sqlalchemy.dialects import postgresql
from eo_data_models import *
import datetime

def get_class_by_tablename(tablename):
    for table in Base._decl_class_registry.values():
        if hasattr(table, '__tablename__') and table.__tablename__ == tablename:
            return table


def build_query(table, source=['*'], filters=None, groupby=False, values=None, limit=None, offset=None, sort=None,
                extra_filter=None, between_filter=None, ignore_null=False):
    if not isinstance(source, list):
        raise ValueError
    if values is not None and not isinstance(values, list):
        raise ValueError

    class_table = get_class_by_tablename(table)
    select_obj = get_select(class_table, source, values)
    where_obj = get_where(class_table, filters, between_filter, ignore_null, extra_filter)
    groupby_obj = get_group_by(groupby, class_table, source)
    offset_obj = get_offset(offset)
    limit_obj = get_limit(limit)
    sort_obj = get_sort(class_table, sort)
    query = select(select_obj).where(and_(*where_obj)).\
            group_by(*groupby_obj).offset(offset_obj).\
            limit(limit_obj).order_by(sort_obj)

    return query


def fire_query(the_instance, table, source=['*'], filters=None, groupby=False, values=None, limit=None, offset=None, sort=None,
               extra_filter=None, between_filter=None, ignore_null=False):
    if not isinstance(source, list):
        raise ValueError
    if values is not None and not isinstance(values, list):
        raise ValueError

    class_table = get_class_by_tablename(table)
    select_obj = get_select(class_table, source, values)
    where_obj = get_where(class_table, filters, between_filter, ignore_null, extra_filter)
    groupby_obj = get_group_by(groupby, class_table, source)
    offset_obj = get_offset(offset)
    limit_obj = get_limit(limit)
    sort_obj = get_sort(class_table, sort)
    query = select(select_obj).where(and_(*where_obj)).\
            group_by(*groupby_obj).offset(offset_obj).\
            limit(limit_obj).order_by(sort_obj)

    # Create a connection
    connection = the_instance.engine.connect()
    df = read_sql_query(query, connection)
    connection.close()
    # Close the connection

    # print str(table) + ', ' + str(source) + ', ' + str(filters) + ', ' + str(groupby) + ', ' + str(values) + ', ' + str(limit) + ', ' + str(offset) + ', ' + str(extra_filter) + ', ' + str(ignore_null)
    # print (str(query.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})))

    return df


def get_where(class_table, filters, between_filter, ignore_null, extra_filter):
    where_obj = []

    if filters:
        for column, value in filters.iteritems():
            if type(value) == list:
                columns = column.split('_')
                if len(columns) == 3 and columns[0].lower() == 'cct':
                    lat = get_column(class_table, columns[1])
                    lon = get_column(class_table, columns[2])
                    where_obj.append(func.concat(lat, '_', lon).in_(tuple(value)))
                else:
                    where_obj.append(get_column(class_table, column).in_(tuple(value)))
            else:
                where_obj.append(get_column(class_table, column) == value)

    if between_filter:
        for bfilt in between_filter:
            where_obj.append(between(get_column(class_table, bfilt['columnname']), bfilt['start'], bfilt['end']))

    if ignore_null:
        for column in ignore_null:
            where_obj.append(get_column(class_table, column).isnot(None))

    if extra_filter:
        for column, value in extra_filter.iteritems():
            where_obj.append(get_column(class_table, column).ilike("%%" + str(value).strip() + "%%"))

    return where_obj


def get_select(class_table, source, values):
    select_obj = []
    if source[0] == '*':
        # print ('***********************')

        pass
    elif source[0] == 'COUNT(*)':
        select_obj.append(func.count().label('count'))
    else:
        for column in source:
            if 'name' in column and 'label' in column:
                select_obj.append(get_column(class_table, column["name"]).label(column["label"]))

            elif 'DISTINCT' in column.upper():
                column_name = column[column.find("(") + 1:column.find(")")]
                column = get_column(class_table, column_name)
                select_obj.append(distinct(column))
            else:
                select_obj.append(get_column(class_table, column))

    if values:
        for value in values:
            for k, v in value.iteritems():
                column = get_column(class_table, k)
                aggregation = v.get('agg')
                label = v.get('as')
                if label == None:
                    label = k
                if aggregation.upper() == 'CARDINALITY':
                    select_obj.append(func.count(distinct(column)).label(label))
                if aggregation.upper() == 'COUNT':
                    select_obj.append(func.count(column).label(label))
                if aggregation.upper() == 'SUM':
                    select_obj.append(func.sum(column).label(label))
                if aggregation.upper() == 'AVG':
                    select_obj.append(func.avg(column).label(label))

    return select_obj


def get_group_by(group_by, class_table, source):
    groupby_obj = []
    if group_by:
        if source[0] != '*':
            for column in source:
                groupby_obj.append(get_column(class_table, column))

    return groupby_obj


def get_offset(offset):
    if offset != None:
        return int(offset)
    else:
        return None
    return offset


def get_limit(limit):
    if limit != None:
        return int(limit)
    else:
        return None


def get_sort(class_table, sort):
    if sort:
        if sort['order'] == 'asc':
            return asc(get_column(class_table, sort['field']))
        else:
            return desc(get_column(class_table, sort['field']))
    else:
        return None


def get_column(classModel, column):
    return getattr(classModel, column.lower())


def date_to_month_year_key(x):
    if x is NaN:
        return x
    date = str2date(x[:10])
    year = date.year.__str__()
    month = date.strftime("%B")

    output = month[:3] + '-' + year[-2:]
    return output


# UPDATE Or INSERT
def sql_upsert_query(the_instance, table, dataFrame, set_values={}, set_values_bool=[], identifiers=[]):
    upsert = False
    query_set = ''
    query_whr = ''
    try:
        # If row exists try Update else Insert
        dict_set_values = {key: sval for key, sval in set_values.iteritems() if
                           key not in identifiers and key not in set_values_bool and sval != None}
        with the_instance.engine.begin() as conn:
            query_set = ' SET '
            if dict_set_values:
                query_set += ' , '.join(sval + '=' + '\'' + dict_set_values[sval] + '\'' for sval in dict_set_values)
            if set_values_bool:
                if dict_set_values:
                    query_set += ' , '
                query_set += ' , '.join(sval + '=' + '\'' + str(set_values[sval]) + '\'' for sval in set_values_bool)
            if identifiers:
                query_whr = ' WHERE ' + ' and '.join(
                    whrkey + '=' + '\'' + set_values[whrkey] + '\'' for whrkey in identifiers)
            update_query = " UPDATE " + table + query_set + query_whr
            updated = conn.execute(update_query)

        # IMPORTANT - if_exists= should be always 'append'. | the other values are fail and replace
        if updated.rowcount == 0:
            dataFrame.to_sql(table, the_instance.engine, if_exists='append', index=False)
        upsert = True
    except Exception as e:
        print("Error", e)
        upsert = False
    finally:
        return upsert


#convert date to str
def datetostr(datestr):
    if isinstance(datestr, datetime.datetime):
        return datestr.__str__()