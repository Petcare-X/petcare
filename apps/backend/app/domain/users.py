from datetime import datetime, date

class Users:
    def __init__(self, 
                id: int, 
                name: str,
                email: str,
                phone_number: str,
                password: str,
                birth_date: date,
                photo_url: str,
                created_at: datetime,
                updated_at: datetime):
            self.id = id,
            self.name = name,
            self.email = email,
            self.phone_number = phone_number,
            self.password = password,
            self.birth_date = birth_date,
            self.photo_url = photo_url,
            self.created_at = created_at,
            self.updated_at = updated_at