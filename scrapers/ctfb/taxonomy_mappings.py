"""
Central Texas Food Bank - Taxonomy Term Mappings
Maps Drupal taxonomy IDs to human-readable names
"""

# Service types (field_services)
SERVICE_TYPES = {
    '2': 'Food Pantry',
    '3': 'Delivered Grocery',
    '4': 'Help paying for food/food vouchers',
    '1445': 'Mobile',
    '1779': 'Senior Program',
}

# Amenities (field_amenity)
AMENITIES = {
    '1702': 'Groceries',
    '1703': 'Hot Meal',
    '1704': 'Kid Meals',
}


def get_service_name(service_id):
    """Get human-readable service name from ID"""
    return SERVICE_TYPES.get(str(service_id), f'Unknown Service ({service_id})')


def get_amenity_name(amenity_id):
    """Get human-readable amenity name from ID"""
    return AMENITIES.get(str(amenity_id), f'Unknown Amenity ({amenity_id})')


def map_services(service_ids):
    """Convert list of service IDs to human-readable names"""
    if not service_ids:
        return []
    return [get_service_name(sid) for sid in service_ids]


def map_amenities(amenity_ids):
    """Convert list of amenity IDs to human-readable names"""
    if not amenity_ids:
        return []
    return [get_amenity_name(aid) for aid in amenity_ids]
