def filter_dbquery_by_time_from_and_to(dbquery, ot, do):
    response = []
    for db_data in dbquery:
        if db_data.time >= ot and db_data.time <= do:
            response.append(db_data)
    return response
