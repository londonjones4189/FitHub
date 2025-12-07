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

# USER STORY 1 — View Pending Reports with filtering
@admin.route('/reports', methods=['GET'])
def get_reports():
    """
    Get all reports with optional filtering
    Query params: ?status=pending|resolved
    """
    status_filter = request.args.get('status', 'all')
    
    cursor = db.get_db().cursor()
    
    if status_filter == 'pending':
        cursor.execute("""
            SELECT ReportID, Severity, Note, ReportedItem, Resolved, ResolvedAt
            FROM Reports
            WHERE Resolved = 0
            ORDER BY ReportID DESC;
        """)
    elif status_filter == 'resolved':
        cursor.execute("""
            SELECT ReportID, Severity, Note, ReportedItem, Resolved, ResolvedAt
            FROM Reports
            WHERE Resolved = 1
            ORDER BY ResolvedAt DESC;
        """)
    else:
        cursor.execute("""
            SELECT ReportID, Severity, Note, ReportedItem, Resolved, ResolvedAt
            FROM Reports
            ORDER BY Resolved, ReportID DESC;
        """)
    
    data = cursor.fetchall()
    return success_response("Reports retrieved successfully", data)


# USER STORY 1 — View Pending Reports (Legacy Endpoint)
# As an Admin, I want to view pending reports in a simple format,
# so I can quickly see what needs my attention.
@admin.route('/reports/pending', methods=['GET'])
def get_pending_reports():
    """Get all pending (unresolved) reports"""
    cursor = db.get_db().cursor()
    cursor.execute("""
        SELECT ReportID, Severity, Note, ReportedItem
        FROM Reports
        WHERE Resolved = 0
        ORDER BY ReportID DESC;
    """)
    data = cursor.fetchall()
    return success_response("Pending reports retrieved", data)


# USER STORY 1 — Resolve/Unresolve Reports (Unified Endpoint)
# As an Admin, I want to resolve or unresolve reports,
# so I can manage the status of reported issues.
@admin.route('/reports/<int:report_id>', methods=['PUT'])
def update_report(report_id):
    """
    Update a report (resolve/unresolve)
    Request body: {"resolved": true|false}
    """
    data = request.json or {}
    resolved = data.get('resolved', True)
    
    cursor = db.get_db().cursor()
    
    if resolved:
        cursor.execute("""
            UPDATE Reports
            SET Resolved = 1, ResolvedAt = NOW()
            WHERE ReportID = %s;
        """, (report_id,))
        message = "Report resolved"
    else:
        cursor.execute("""
            UPDATE Reports
            SET Resolved = 0, ResolvedAt = NULL
            WHERE ReportID = %s;
        """, (report_id,))
        message = "Report unresolved"
    
    db.get_db().commit()
    return success_response(message)


# USER STORY 1 — Resolve Report (Legacy Endpoint)
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


# USER STORY 1 — Unresolve Report (Legacy Endpoint)
# As an Admin, I want to mark a resolved report as unresolved,
# so I can reopen issues that need further attention.
@admin.route('/reports/<int:report_id>/unresolve', methods=['PUT'])
def unresolve_report(report_id):
    """Unresolve a report (legacy endpoint)"""
    cursor = db.get_db().cursor()
    cursor.execute("""
        UPDATE Reports
        SET Resolved = 0, ResolvedAt = NULL
        WHERE ReportID = %s;
    """, (report_id,))
    db.get_db().commit()
    return success_response("Report unresolved")


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


# USER STORY 3 — Activate User (Legacy Endpoint)
# As an Admin, I want to activate user accounts,
# so I can restore access for users who were previously deactivated.
@admin.route('/users/<int:user_id>/activate', methods=['PUT'])
def activate_user(user_id):
    """Activate a user (legacy endpoint)"""
    cursor = db.get_db().cursor()
    cursor.execute("""
        UPDATE Users
        SET IsActive = 1
        WHERE UserID = %s;
    """, (user_id,))
    
    db.get_db().commit()
    return success_response("User activated")


# USER STORY 3 — Deactivate User (Legacy Endpoint)
# As an Admin, I want to deactivate user accounts,
# so I can restrict access for problematic or inactive users.
@admin.route('/users/<int:user_id>/deactivate', methods=['PUT'])
def deactivate_user(user_id):
    """Deactivate a user (legacy endpoint)"""
    cursor = db.get_db().cursor()
    cursor.execute("""
        UPDATE Users
        SET IsActive = 0
        WHERE UserID = %s;
    """, (user_id,))
    
    db.get_db().commit()
    return success_response("User deactivated")


# ============================================================================
# ANNOUNCEMENT ROUTES
# ============================================================================

@admin.route('/announcements', methods=['POST'])
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


# ============================================================================
# ANALYTICS ROUTES
# ============================================================================

# USER STORY 5 — Analytics Summary
# As an Admin, I want to view analytics summary,
# so I can monitor key platform metrics like total users, listings, and open reports.
@admin.route('/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Get analytics summary with key metrics"""
    cursor = db.get_db().cursor()
    cursor.execute("""
        SELECT
            (SELECT COUNT(*) FROM Users) AS TotalUsers,
            (SELECT COUNT(*) FROM Items) AS TotalListings,
            (SELECT COUNT(*) FROM Reports WHERE Resolved = 0) AS OpenReports;
    """)
    data = cursor.fetchall()
    return success_response("Analytics summary retrieved", data)


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


@admin.route('/items/duplicates', methods=['DELETE'])
def delete_duplicate_items():
    """Delete duplicate items (keeps the first occurrence)"""
    try:
        cursor = db.get_db().cursor()
        cursor.execute("""
            DELETE i FROM Items i
            JOIN (
                SELECT Title, OwnerID, MIN(ItemID) AS KeepID
                FROM Items
                GROUP BY Title, OwnerID
                HAVING COUNT(*) > 1
            ) base
            ON i.Title = base.Title
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
