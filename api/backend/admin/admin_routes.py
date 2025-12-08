from flask import Blueprint, request, jsonify, make_response
from backend.db_connection import db

admin = Blueprint('admin', __name__)

# Helper Functions
# ============================================================================

def success_response(message, data=None, status_code=200):
    """Create a standardized success response"""
    response_data = {"message": message}
    if data is not None:
        response_data["data"] = data
    the_response = make_response(jsonify(response_data), status_code)
    the_response.mimetype = 'application/json'
    return the_response


def error_response(message, status_code=500):
    """Create a standardized error response"""
    the_response = make_response(jsonify({"error": message}), status_code)
    the_response.mimetype = 'application/json'
    return the_response



# REPORT ROUTES
# ============================================================================
@admin.route('/reports', methods=['GET'])
def get_reports():
    status_filter = request.args.get('status', 'all')

    cursor = db.get_db().cursor()

    if status_filter == 'pending':
        cursor.execute("""
            SELECT ReportID, Severity, Note, ReportedItem, ReportedUser, Resolved, ResolvedAt
            FROM Reports
            WHERE Resolved = 0
            ORDER BY ReportID DESC;
        """)
    elif status_filter == 'resolved':
        cursor.execute("""
            SELECT ReportID, Severity, Note, ReportedItem, ReportedUser, Resolved, ResolvedAt
            FROM Reports
            WHERE Resolved = 1
            ORDER BY ResolvedAt DESC;
        """)
    else:
        cursor.execute("""
            SELECT ReportID, Severity, Note, ReportedItem, ReportedUser, Resolved, ResolvedAt
            FROM Reports
            ORDER BY Resolved, ReportID DESC;
        """)

    data = cursor.fetchall()
    return success_response("Reports retrieved successfully", data)



# USER STORY 1 — Resolve Report
# As an Admin, I want to mark a report as resolved,
# so I can track which issues have been addressed.
@admin.route('/reports/<int:report_id>/resolve', methods=['PUT'])
def resolve_report(report_id):
    """Resolve a report (legacy endpoint)"""
    cursor = db.get_db().cursor()
    cursor.execute("""
        UPDATE Reports
        SET Resolved = 1, ResolvedAt = NOW()
        WHERE ReportID = %s;
    """, (report_id,))
    db.get_db().commit()
    return success_response("Report resolved")



# ============================================================================
# USER ROUTES
# ============================================================================

# USER STORY 2 — Update User Role
# As an Admin, I want to update user roles,
# so I can manage user permissions and access levels.
@admin.route('/users/<int:user_id>/role', methods=['PUT'])
def update_user_role(user_id):
    """
    Update a user's role
    Request body: {"role": "admin"|"data analyst"|"swapper"|"taker"}
    """
    data = request.json
    if not data or 'role' not in data:
        return error_response("Role is required", 400)
    
    new_role = data.get("role")
    cursor = db.get_db().cursor()
    cursor.execute("""
        UPDATE Users
        SET Role = %s
        WHERE UserID = %s;
    """, (new_role, user_id))
    
    db.get_db().commit()
    return success_response("User role updated")


# USER STORY 3 — Activate/Deactivate User (Unified Endpoint)
# As an Admin, I want to activate or deactivate user accounts,
# so I can control who has access to the platform.
@admin.route('/users/<int:user_id>/status', methods=['PUT'])
def update_user_status(user_id):
    """
    Update a user's active status
    Request body: {"active": true|false}
    """
    data = request.json or {}
    is_active = data.get('active', True)
    
    cursor = db.get_db().cursor()
    cursor.execute("""
        UPDATE Users
        SET IsActive = %s
        WHERE UserID = %s;
    """, (1 if is_active else 0, user_id))
    
    db.get_db().commit()
    message = "User activated" if is_active else "User deactivated"
    return success_response(message)


# ============================================================================
# ANNOUNCEMENT ROUTES
# ============================================================================

@admin.route('/create_announcements', methods=['POST'])
def create_announcement():
    """
    Create a new announcement
    Request body: {"announcer_id": int, "message": string}
    """
    data = request.json
    if not data:
        return error_response("Request body is required", 400)
    
    announcer = data.get("announcer_id")
    message = data.get("message")
    
    if not announcer or not message:
        return error_response("announcer_id and message are required", 400)
    
    cursor = db.get_db().cursor()
    
    cursor.execute("""
        INSERT INTO Announcements (AnnouncerID, Message, AnnouncedAt)
        VALUES (%s, %s, NOW());
    """, (announcer, message))
    
    announcement_id = cursor.lastrowid
    
    cursor.execute("""
        INSERT INTO AnnouncementsReceived (AnnouncementID, UserID)
        SELECT %s, UserID FROM Users WHERE IsActive = 1;
    """, (announcement_id,))

    db.get_db().commit()
    
    return success_response(
        "Announcement created",
        {"announcement_id": announcement_id},
        status_code=201
    )


@admin.route('/announcements', methods=['GET'])
def get_announcements():
    """
    Get all announcements with announcer info
    """
    cursor = db.get_db().cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            a.AnnouncementID,
            a.Message AS message,
            a.AnnouncedAt AS announced_at,
            u.Name AS announcer_name,
            u.UserID AS announcer_id
        FROM Announcements a
        JOIN Users u ON a.AnnouncerID = u.UserID
        ORDER BY a.AnnouncedAt DESC;
    """)

    data = cursor.fetchall()

    return success_response("Announcements retrieved", data)


# ============================================================================
# ITEM ROUTES
# ============================================================================

@admin.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Delete a specific item and all related records"""
    try:
        cursor = db.get_db().cursor()
        
        cursor.execute("DELETE FROM Images WHERE ItemID = %s;", (item_id,))
        cursor.execute("DELETE FROM ItemTags WHERE ItemID = %s;", (item_id,))
        cursor.execute("DELETE FROM OrderItems WHERE ItemID = %s;", (item_id,))
        cursor.execute("DELETE FROM Reports WHERE ReportedItem = %s;", (item_id,))
        cursor.execute("DELETE FROM Items WHERE ItemID = %s;", (item_id,))
        
        db.get_db().commit()
        return success_response("Item removed")
    
    except Exception as e:
        db.get_db().rollback()
        return error_response(str(e), 500)


@admin.route('/items/duplicates', methods=['GET', 'DELETE'])
def handle_duplicate_items():
    """Get or delete duplicate items (keeps the first occurrence) which will help stop scam sellers"""

    if request.method == 'GET':
        try:
            cursor = db.get_db().cursor()
            cursor.execute("""
                SELECT 
                    i.*,
                    duplicate_counts.DuplicateCount
                FROM Items i
                JOIN (
                    SELECT 
                        Title, 
                        Category, 
                        Size, 
                        `Condition`, 
                        `Type`, 
                        OwnerID,
                        COUNT(*) AS DuplicateCount,
                        MIN(ItemID) AS KeepID
                    FROM Items
                    GROUP BY 
                        Title, 
                        Category, 
                        Size, 
                        `Condition`, 
                        `Type`, 
                        OwnerID
                    HAVING COUNT(*) > 1
                ) duplicate_counts
                ON  i.Title = duplicate_counts.Title
                AND i.Category = duplicate_counts.Category
                AND i.Size = duplicate_counts.Size
                AND i.`Condition` = duplicate_counts.`Condition`
                AND i.`Type` = duplicate_counts.`Type`
                AND i.OwnerID = duplicate_counts.OwnerID
                ORDER BY i.Title, i.ItemID;
            """)

            duplicates = cursor.fetchall()
            return success_response(
                "Duplicate items retrieved",
                duplicates
            )

        except Exception as e:
            return error_response(str(e), 500)

    elif request.method == 'DELETE':
        try:
            cursor = db.get_db().cursor()
            cursor.execute("""
                DELETE i FROM Items i
                JOIN (
                    SELECT 
                        Title, 
                        Category, 
                        Size, 
                        `Condition`, 
                        `Type`, 
                        OwnerID,
                        MIN(ItemID) AS KeepID
                    FROM Items
                    GROUP BY 
                        Title, 
                        Category, 
                        Size, 
                        `Condition`, 
                        `Type`, 
                        OwnerID
                    HAVING COUNT(*) > 1
                ) base
                ON  i.Title = base.Title
                AND i.Category = base.Category
                AND i.Size = base.Size
                AND i.`Condition` = base.`Condition`
                AND i.`Type` = base.`Type`
                AND i.OwnerID = base.OwnerID
                AND i.ItemID != base.KeepID;
            """)

            rows_deleted = cursor.rowcount
            db.get_db().commit()

            return success_response(
                f"Removed {rows_deleted} duplicate item(s)",
                {"deleted_count": rows_deleted}
            )

        except Exception as e:
            db.get_db().rollback()
            return error_response(str(e), 500)


"""
Grabs all listings
"""
@admin.route('/items', methods=['GET'])
def get_listings():
    cursor = db.get_db().cursor()

    the_query = '''
        SELECT
            i.ItemID, i.Title, i.Category, i.Description, i.Size, i.Condition, u.Name as OwnerName,
            i.ListedAt
        FROM Items i
        JOIN Users u ON i.OwnerID = u.UserID
        WHERE i.IsAvailable = 1
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

