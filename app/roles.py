from enum import Enum

class UserRole(Enum):
    ADMIN = "Admin"
    MANAGER = "Property Manager"
    CONTRACTOR = "Contractor"

ALL_ROLES = [role.value for role in UserRole]
