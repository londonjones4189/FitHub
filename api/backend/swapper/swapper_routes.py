########
# swapper endpoints
########


from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db
swapper = Blueprint('swappers', __name__)


#-----User Story 1------
#As a Swapper, I want to filter clothes listed as available for swap and filter by size, condition, style, and tags.


@swapper.route('/listings/<SizeFilter>/<ConditionFilter>/<TagFilter>/', methods=['GET'])
def get_all_listings():
    cursor = db.get_db().cursor()

    the_query = '''
        SET @SizeFilter = 'M';
        SET @ConditionFilter = 'Good';
        SET @TagFilter = 'Vintage';


        SELECT DISTINCT i.ItemID, i.Title, i.Category, i.Description, i.Size, i.`Condition`, i.`Type`, u.Name AS OwnerName
        FROM Items i
        INNER JOIN Users u ON i.OwnerID = u.UserID
        LEFT JOIN ItemTags it ON i.ItemID = it.ItemID
        LEFT JOIN Tags t ON it.TagID = t.TagID
        WHERE i.IsAvailable = 1
            AND i.`Type` = 'Swap'
            AND i.Size = @SizeFilter
            AND i.`Condition` = @ConditionFilter
            AND t.Title = @TagFilter;

    '''
    cursor.execute(the_query)
    theData = cursor.fetchall()

    the_response = make_response(jsonify(theData))
    the_response.status_code = 200
    the_response.mimetype = 'application/json'
    return the_response
#-----User Story 1------

#-----User Story 2------
#As a Swapper, I want to be able to cancel a swap and have my swapped clothing become available again.

@swapper.route('/cancel_swap/<int:ItemID>/', methods=['DELETE'])
def cancel_swap(OrderID, UserID):
    cursor = db.get_db().cursor()

    the_query = '''
        SET @OrderIDToCancel = 1;
        SET @MyUserID = 1;


        UPDATE Items i
        INNER JOIN OrderItems oi ON i.ItemID = oi.ItemID
        SET i.IsAvailable = 1
        WHERE oi.OrderID = @OrderIDToCancel
        AND i.OwnerID = @MyUserID;

        DELETE FROM Feedback WHERE OrderID = @OrderIDToCancel;
        DELETE FROM OrderItems WHERE OrderID = @OrderIDToCancel;
        DELETE FROM Orders WHERE OrderID = @OrderIDToCancel AND (GivenByID = @MyUserID OR ReceiverID = @MyUserID);

    '''
    cursor.execute(the_query, (OrderID, UserID))
    db.get_db().commit()

    the_response = make_response(jsonify({"message": "Swap cancelled and item is now available for swap."}))
    the_response.status_code = 200
    the_response.mimetype = 'application/json'
    return the_response

#-----User Story 3------
# As a Swapper, I want to be able to track the status of my sending and receiving packages of my swap.
@swapper.route('/track_swap/<int:OrderID>/', methods=['GET'])
def track_swap(OrderID):
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
    cursor = db.get_db().cursor()
    data = request.get_json()

    title = the_data['Title']
    category = the_data['Category']
    description = the_data['Description']
    size = the_data['Size']
    item_type = the_data['Type']
    condition = the_data['Condition']
    owner_id = the_data['OwnerID']

    the_query = '''
        INSERT INTO Items (Title, Category, Description, Size, Type, Condition, OwnerID, IsAvailable)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 1);
    '''

    cursor.execute(the_query, (title, category, description, size, item_type, condition, owner_id))
    db.get_db().commit()    
    the_response = make_response(jsonify({"message": "Listing uploaded successfully."}))





   




