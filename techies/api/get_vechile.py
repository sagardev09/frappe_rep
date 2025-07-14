import frappe
from frappe import _
from frappe.utils import now_datetime

@frappe.whitelist(allow_guest=True)
def get_vehicle_info(user):
    if not user:
        frappe.throw(_("User is required"))

    vehicle_data = frappe.get_all(
        "Vehicle Information",
        filters={"driver": user},
        fields=["*"]
    )

    if not vehicle_data:
        return {"message": "No vehicle information found for this user."}

    return {"vehicles": vehicle_data, "message": "Vehicle information retrieved successfully."}

def test():
 data =  get_vehicle_info("yash@mugen.ae")    
 print(data)


@frappe.whitelist(allow_guest=True)
def update_vehicle_location(**kwargs):
    """Create or update a document based on vehicle field filter"""
    vehicle_id = kwargs.get('vechile')
    driver = kwargs.get('driver')
    
    if not vehicle_id:
        return {"error": "Vehicle ID is required"}
    
    # Convert battery_level to string if percentage
    if 'battery_level' in kwargs and isinstance(kwargs['battery_level'], int):
        kwargs['battery_level'] = f"{kwargs['battery_level']}%"
    
    # Check if document exists by filtering on vechile field
    doc_name = frappe.db.get_value("Vechile Location", {"vechile": vehicle_id}, "name")
    
    if doc_name:
        # Update existing document
        doc = frappe.get_doc("Vechile Location", doc_name)

        route_name = update_vehicle_route(
        vehicle=vehicle_id,
        driver=driver,
        timestamp=kwargs.get('timestamp'),
        latitude=kwargs.get('latitude'),
        longitude=kwargs.get('longitude'),
        speed=kwargs.get('speed'),
        battery_level=kwargs.get('battery_level')
    )
        
        # Update fields from kwargs
        for key, value in kwargs.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        
        doc.last_updated = now_datetime()
        doc.save()
        
        return {
            "status": "updated",
            "vehicle": vehicle_id,
            "document_name": doc_name,
            "next_update_in": 30
        }
    else:
        # Create new document
        doc = frappe.new_doc("Vechile Location")
        doc.vechile = vehicle_id

        route_name = update_vehicle_route(
        vehicle=vehicle_id,
        driver=driver,
        timestamp=kwargs.get('timestamp'),
        latitude=kwargs.get('latitude'),
        longitude=kwargs.get('longitude'),
        speed=kwargs.get('speed'),
        battery_level=kwargs.get('battery_level')
    )
        
        # Set all fields from kwargs
        for key, value in kwargs.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        
        doc.last_updated = now_datetime()
        doc.insert()
        
        return {
            "status": "created",
            "vehicle": vehicle_id,
            "route_name": route_name,
            "document_name": doc.name,
            "next_update_in": 30
        }

def update_vehicle_route(vehicle, driver, timestamp, latitude, longitude, **kwargs):
    """
    Internal function to update vehicle route tracking
    Called from update_vehicle_location API
    """
    date = frappe.utils.getdate(timestamp)
    
    # Find or create Vehicle Route for this vehicle and date
    route_name = frappe.db.get_value("Vehicle Route", {
        "vehicle": vehicle,
        "date": date
    })
    
    if not route_name:
        # Create new Vehicle Route
        route = frappe.new_doc("Vehicle Route")
        route.vehicle = vehicle
        route.driver = driver
        route.date = date
        route.insert()
        route_name = route.name
    
    # Add location point to child table
    route = frappe.get_doc("Vehicle Route", route_name)
    
    route.append("locations", {
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": timestamp,
        "speed": kwargs.get("speed"),
        "battery_level": kwargs.get("battery_level"),
        # Add any additional fields from kwargs
    })
    
    route.save()
    
    return route_name        
    
@frappe.whitelist(allow_guest=True)
def get_live_locations(route_name=None, last_minutes=5):
    """Called from admin webapp"""
    
    # Convert last_minutes to integer if it's a string
    try:
        last_minutes = int(last_minutes) if last_minutes is not None else 5
    except (ValueError, TypeError):
        last_minutes = 5  # Default fallback
    
    # Ensure positive value
    if last_minutes <= 0:
        last_minutes = 5
    
    from datetime import datetime, timedelta
    
    # Calculate cutoff time
    cutoff_time = datetime.now() - timedelta(minutes=last_minutes)
    
    print(f"Cutoff time for filtering: {cutoff_time}")
    
    # Build filters - since timestamp is a datetime field, use datetime object directly
    filters = [
        ["timestamp", ">=", cutoff_time]
    ]
    
    if route_name:
        filters.append(["bus.route_name", "=", route_name])
    
    # Get locations with datetime filtering
    locations = frappe.get_all("Vechile Location",
        fields=["*"],
        filters=filters,
        order_by="timestamp desc"
    )
    
    print(f"Found {len(locations)} locations within last {last_minutes} minutes")
    
    # Debug: print each location's timestamp
    for location in locations:
        print(f"Location: {location['vechile']} at {location['timestamp']}")
    
    return {"locations": locations}


# Alternative version using Frappe's date handling (recommended)
@frappe.whitelist(allow_guest=True)
def get_live_locations_v2(route_name=None, last_minutes=5):
    """Called from admin webapp - Alternative version using Frappe date utilities"""
    
    # Convert last_minutes to integer if it's a string
    try:
        last_minutes = int(last_minutes) if last_minutes is not None else 5
    except (ValueError, TypeError):
        last_minutes = 5
    
    if last_minutes <= 0:
        last_minutes = 5
    
    from datetime import datetime, timedelta
    import frappe.utils
    
    # Calculate cutoff time
    cutoff_time = datetime.now() - timedelta(minutes=last_minutes)
    
    # Convert to Frappe's datetime format
    cutoff_time_frappe = frappe.utils.get_datetime(cutoff_time)
    
    print(f"Cutoff time for filtering: {cutoff_time_frappe}")
    
    # Build filters - using Frappe's date comparison
    filters = [
        ["timestamp", ">=", cutoff_time_frappe]
    ]
    
    if route_name:
        filters.append(["bus.route_name", "=", route_name])
    
    locations = frappe.get_all("Vechile Location",
        fields=["*"],
        filters=filters,
        order_by="timestamp desc"
    )
    
    print(f"Found {len(locations)} locations")
    
    return {"locations": locations}

@frappe.whitelist(allow_guest=True)
def get_vehicle_routes(vehicle=None, driver=None, date=None, from_date=None, to_date=None, page_length=20, page=1):
    """
    Fetch vehicle routes with filtering options
    Args:
        vehicle: Filter by vehicle ID
        driver: Filter by driver ID
        date: Specific date (YYYY-MM-DD format)
        from_date: Start date range (YYYY-MM-DD)
        to_date: End date range (YYYY-MM-DD)
        page_length: Number of results per page
        page: Page number
    Returns:
        List of routes with location points
    """
    # Validate date filters
    if date and (from_date or to_date):
        frappe.throw("Use either 'date' or date range ('from_date'+'to_date'), not both")
    
    # Build filters
    filters = []
    
    if vehicle:
        filters.append(["vehicle", "=", vehicle])
    
    if driver:
        filters.append(["driver", "=", driver])
    
    if date:
        filters.append(["date", "=", date])
    elif from_date or to_date:
        if from_date:
            filters.append(["date", ">=", from_date])
        if to_date:
            filters.append(["date", "<=", to_date])
    
    # Get paginated routes
    routes = frappe.get_all("Vehicle Route",
        fields=["name", "vehicle", "driver", "date"],
        filters=filters,
        limit_start=(page - 1) * page_length,
        limit_page_length=page_length,
        order_by="date desc"
    )
    
    # Get location details for each route
    for route in routes:
        locations = frappe.get_all("Vehicle Sub Route",
            fields=["latitude", "longitude", "timestamp", "speed", "battery_level"],
            filters={"parent": route["name"]},
            order_by="timestamp"
        )
        
        # Calculate route statistics
        valid_speeds = []
        for loc in locations:
            try:
                if loc.get("speed"):
                    speed = float(loc["speed"])
                    valid_speeds.append(speed)
                    loc["speed"] = speed  # Update with converted value
            except (ValueError, TypeError):
                continue
        
        route["locations"] = locations
        
        # Calculate route statistics
        if locations:
            stats = {
                "point_count": len(locations),
                "first_timestamp": locations[0]["timestamp"],
                "last_timestamp": locations[-1]["timestamp"],
                "avg_speed": None,
                "max_speed": None
            }
            
            if valid_speeds:
                stats["avg_speed"] = sum(valid_speeds) / len(valid_speeds)
                stats["max_speed"] = max(valid_speeds)
            
            route["stats"] = stats
    
    return {
        "routes": routes,
        "pagination": {
            "page": page,
            "page_length": page_length,
            "total": frappe.db.count("Vehicle Route", filters=filters)
        }
    }

@frappe.whitelist(allow_guest=True)
def get_all_users():
    """
    Fetch all users (email only)
    Returns:
        List of users with email addresses
    """
    users = frappe.get_all("User",
        fields=["email"],
        filters={"enabled": 1},  # Only active users
        order_by="email"
    )
    
    return {
        "users": users,
        "count": len(users)
    }

@frappe.whitelist(allow_guest=True)
def get_all_vehicles():
    """
    Fetch all vehicle documents (name only)
    Returns:
        List of vehicle document names
    """
    vehicles = frappe.get_all("Vehicle Information",
        fields=["name"],
        order_by="name"
    )
    
    return {
        "vehicles": vehicles,
        "count": len(vehicles)
    }
	

def test():
    # Example test call
    data = get_vehicle_routes(vehicle="9fb3433ir3",date="2025-06-28")
    print(data)    

