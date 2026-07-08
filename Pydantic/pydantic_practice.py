from pydantic import BaseModel, Field, field_validator,computed_field

class User(BaseModel):
    name: str
    email: str
    age: int
    country: str = Field(default="India", description="Country of the user")

    @field_validator("email")
    @classmethod
    def reject_invalid_emails(cls, value):
        if "@" not in value:
            raise ValueError("Invalid email address")

        blocked_domains = ["example.com", "test.com"]
        user_domain = value.split("@")[-1].lower()

        if user_domain in blocked_domains:
            raise ValueError("Email domain is blocked")

        return value.lower()
    @computed_field
    @property
    def is_adult(self) -> bool:
        return self.age >= 18
    
    @computed_field
    @property
    def citizenship(self) -> str:
        return "Indian" if self.country.lower() == "india" else "Non-Indian"
    

user_pydantic = User(
    name="Satish Tirumani",
    email="satish.tirumani@convera.com",
    age=4
)

print(user_pydantic)