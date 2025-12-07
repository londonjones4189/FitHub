########
# swapper endpoints
########


from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection.db import db
swapper = Blueprint('swapper', __name__)


#-----User Story 1------
#As a Swapper, I want to filter clothes listed as available for swap and filter by size, condition, style, and tags.

@swapper.route('/listings/up_for_swap', methods=['GET'])
def get_up_for_swap_listings():
    cursor = db.get_db().cursor()

    the_query = '''
        SELECT
            i.ItemID, i.Title, i.Category, i.Description, i.Size, i.Condition, u.Name as OwnerName,
            i.ListedAt
        FROM Items i
        JOIN Users u ON i.OwnerID = u.UserID
        WHERE i.IsAvailable = 1 AND i.Type = 'Swap'
        ORDER BY i.ListedAt DESC;
    '''

    cursor.execute(the_query)
    items = cursor.fetchall()

    item_ids = [item['ItemID'] for item in items]
    tags_dict = {}
    
    if item_ids:
        placeholders = ', '.join(['%s'] * len(item_ids))
        tags_query = f'''
            SELECT it.ItemID, t.Title
            FROM ItemTags it
            JOIN Tags t ON it.TagID = t.TagID
            WHERE it.ItemID IN ({placeholders})
        '''
        cursor.execute(tags_query, item_ids)
        tag_rows = cursor.fetchall()
        
        for row in tag_rows:
            item_id = row['ItemID']
            if item_id not in tags_dict:
                tags_dict[item_id] = []
            tags_dict[item_id].append(row['Title'])

    for item in items:
        item_id = item['ItemID']
        item['Tags'] = ', '.join(tags_dict.get(item_id, []))

    the_response = make_response(jsonify(items), 200)
    the_response.mimetype = "application/json"
    return the_response

@swapper.route('/listings/filter', methods=['GET'])
def get_filter_listings():
    category = request.args.get('category')
    size = request.args.get('size')
    condition = request.args.get('condition')
    tags = request.args.get('tags')

    cursor = db.get_db().cursor()

    the_query = '''
        SELECT DISTINCT
            i.ItemID, i.Title, i.Category, i.Description, i.Size, i.Condition, u.Name as OwnerName,
            i.ListedAt
        FROM Items i
        JOIN Users u ON i.OwnerID = u.UserID
        LEFT JOIN ItemTags it ON i.ItemID = it.ItemID
        LEFT JOIN Tags t ON it.TagID = t.TagID
        WHERE i.IsAvailable = 1 AND i.Type = 'Swap'
    '''

    query_params = []

    if category:
        the_query += ' AND i.Category = %s'
        query_params.append(category)

    if size:
        the_query += ' AND i.Size = %s'
        query_params.append(size)

    if condition:
        conditions = condition.split(',')
        placeholders = ', '.join(['%s'] * len(conditions))
        the_query += f' AND i.Condition IN ({placeholders})'
        query_params.extend(conditions)

    if tags:
        tag_list = tags.split(',')
        placeholders = ', '.join(['%s'] * len(tag_list))
        the_query += f' AND t.Title IN ({placeholders}) OR t.Title IS NULL'
        query_params.extend(tag_list)

    the_query += ' ORDER BY i.ListedAt DESC;'

    cursor.execute(the_query, query_params)
    items = cursor.fetchall()

    item_ids = [item['ItemID'] for item in items]
    tags_dict = {}
    
    if item_ids:
        placeholders = ', '.join(['%s'] * len(item_ids))
        tags_query = f'''
            SELECT it.ItemID, t.Title
            FROM ItemTags it
            JOIN Tags t ON it.TagID = t.TagID
            WHERE it.ItemID IN ({placeholders})
        '''
        cursor.execute(tags_query, item_ids)
        tag_rows = cursor.fetchall()
        
        for row in tag_rows:
            item_id = row['ItemID']
            if item_id not in tags_dict:
                tags_dict[item_id] = []
            tags_dict[item_id].append(row['Title'])

    for item in items:
        item_id = item['ItemID']
        item['Tags'] = ', '.join(tags_dict.get(item_id, []))

    the_response = make_response(jsonify(items), 200)
    the_response.mimetype = "application/json"
    return the_response

#-----User Story 1------

#-----User Story 2------
#As a Swapper, I want to be able to cancel a swap and have my swapped clothing become available again.

@swapper.route('/cancel_swap/<int:OrderID>/<int:UserID>/', methods=['DELETE'])
def cancel_swap(OrderID, UserID):
    try:
        cursor = db.get_db().cursor()

        # Update items to be available again
        cursor.execute('''
            UPDATE Items i
            INNER JOIN OrderItems oi ON i.ItemID = oi.ItemID
            SET i.IsAvailable = 1
            WHERE oi.OrderID = %s
            AND i.OwnerID = %s;
        ''', (OrderID, UserID))
        
        # Delete related records
        cursor.execute("DELETE FROM Feedback WHERE OrderID = %s;", (OrderID,))
        cursor.execute("DELETE FROM OrderItems WHERE OrderID = %s;", (OrderID,))
        cursor.execute("DELETE FROM Orders WHERE OrderID = %s AND (GivenByID = %s OR ReceiverID = %s);", (OrderID, UserID, UserID))
        
        db.get_db().commit()

        the_response = make_response(jsonify({"message": "Swap cancelled and item is now available for swap."}))
        the_response.status_code = 200
        the_response.mimetype = 'application/json'
        return the_response

    except Exception as e:
        db.get_db().rollback()
        the_response = make_response(jsonify({"error": str(e)}))
        the_response.status_code = 500
        return the_response

#-----User Story 3------
# As a Swapper, I want to be able to track the status of my sending and receiving packages of my swap.
@swapper.route('/track_swap/<int:UserID>/', methods=['GET'])
def track_swap(UserID):
    cursor = db.get_db().cursor()

    the_query = '''
         SELECT
            o.OrderID,
            CASE
                WHEN o.GivenByID = %s THEN 'Sending'
                WHEN o.ReceiverID = %s THEN 'Receiving'
            END AS SwapDirection,
            s.Carrier,
            s.TrackingNum,
            s.DateShipped,
            s.DateArrived,
            CASE
                WHEN s.DateArrived IS NOT NULL THEN 'Delivered'
                WHEN s.DateShipped IS NOT NULL THEN 'In Transit'
                ELSE 'Pending'
            END AS Status
        FROM Orders o
        LEFT JOIN Shippings s ON o.ShippingID = s.ShippingID
        WHERE o.GivenByID = %s OR o.ReceiverID = %s
        ORDER BY o.CreatedAt DESC;
    '''

    cursor.execute(the_query, (UserID, UserID, UserID, UserID))
    theData = cursor.fetchall()

    the_response = make_response(jsonify(theData))
    the_response.status_code = 200
    the_response.mimetype = 'application/json'
    return the_response

#-----User Story 4------
# As a Swapper, I want to be able to upload clothing items as listings and list them as for a swap or a take.
@swapper.route('/upload_listing/', methods=['POST'])
def upload_listing():
    try:
        cursor = db.get_db().cursor()
        data = request.get_json()

        title = data['Title']
        category = data['Category']
        description = data['Description']
        size = data['Size']
        item_type = data['Type']
        condition = data['Condition']
        owner_id = data['OwnerID']

        the_query = '''
            INSERT INTO Items (Title, Category, Description, Size, Type, Condition, OwnerID, IsAvailable)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 1);
        '''

        cursor.execute(the_query, (title, category, description, size, item_type, condition, owner_id))
        db.get_db().commit()    
        the_response = make_response(jsonify({"message": "Listing uploaded successfully."}))
        the_response.status_code = 200
        the_response.mimetype = 'application/json'
        return the_response

    except Exception as e:
        db.get_db().rollback()
        the_response = make_response(jsonify({"error": str(e)}))
        the_response.status_code = 500
        return the_response





   



