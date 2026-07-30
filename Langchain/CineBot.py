
# Cinebot - Movie Booking Agent
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.agents.structured_output import ProviderStrategy, ToolStrategy
from langchain_core.tools import tool
from langchain.agents import create_agent

class BookingRequest(BaseModel):
    customer_name: str = Field(..., description="Name of the customer making the booking")
    movie_title: str = Field(..., description="Title of the movie to be booked")
    number_of_tickets: int = Field(..., description="Number of tickets to be booked")
    date: str = Field(..., description="Date of the movie booking in YYYY-MM-DD format")
    time: str = Field(..., description="Time of the movie booking in HH:MM format")
    action: str = Field(..., description="Action to be performed: 'book' or 'cancel'") 

load_dotenv()


@tool
def peek_show_times(movie_title: str) -> str:
    """
    Peek at the show times for a given movie title.
    """
    # In a real implementation, this function would query a movie database or API
    # to retrieve the show times for the specified movie title.
    # For demonstration purposes, we'll return a static response.
    return f"Show times for '{movie_title}': 1:00 PM, 4:00 PM, 7:00 PM, 10:00 PM"

model = init_chat_model(
    model_provider="fireworks",
    model="accounts/fireworks/models/kimi-k3",
    api_key=os.getenv("FIREWORKS_API_KEY"),
    base_url="https://api.fireworks.ai/inference/v1"
)
model.bind_tools([peek_show_times], strategy=ToolStrategy(BookingRequest))

model.invoke("Hello, I am Cinebot, your movie booking assistant. How can I help you today?")

print("Cinebot is ready to assist you with movie bookings!")
print("-----------------------------------------------------------------")

booking_requests = [
    "Hi, I would like to book tickets for the movie 'Inception' for 2 adults and 1 child on July 15th at 7 PM.name is Haasith",
    "Can you book me a seat for the movie 'The Matrix' for 1 adult on August 20th at 9 PM?, I am Satish",
    "URGENT: I need to cancel  my booking of 10 tickets for 'Avatar' on September 5th at 6 PM. Please confirm the cancellation under Gayathri.",
    "Cancel my booking for 'Titanic' on October 10th at 8 PM. I am Ramesh and I had booked 3 tickets.",
]

for message in booking_requests:
    response = model.invoke("Extract the booking details from the following message: " + message)
    print(response)
    print("-----------------------------------------------------------------")
    
    
from langchain.agents import create_agent

booking_agent = create_agent(
    model=model,
    tools=[peek_show_times],
    response_format=ToolStrategy(BookingRequest)
)

booking_response = booking_agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "I want to book 2 tickets for 'Interstellar' "
                    "on November 12th at 5 PM. My name is Ananya."
                ),
            }
        ]
    }
)
booking = booking_response["structured_response"]

print(booking)

class NewBooking(BaseModel):
    customer_name: str = Field(..., description="Name of the customer making the booking")
    movie_title: str = Field(..., description="Title of the movie to be booked")
    number_of_tickets: int = Field(..., description="Number of tickets to be booked")
    date: str = Field(..., description="Date of the movie booking in YYYY-MM-DD format")
    time: str = Field(..., description="Time of the movie booking in HH:MM format")
    
class CancelBooking(BaseModel):
    customer_name: str = Field(..., description="Name of the customer making the cancellation")
    movie_title: str = Field(..., description="Title of the movie to be canceled")
    booking_id: int = Field(..., description="ID of the booking to be canceled")

from typing import Union

class BookingOperations(BaseModel):
    operations: list[Union[NewBooking, CancelBooking]] = Field(
        description="All booking and cancellation operations requested"
    )
    


union_agent = create_agent(
    model=model,
    tools=[peek_show_times],
    response_format=ToolStrategy(BookingOperations)
    )
booking_response = union_agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "I want to book 3 tickets for 'The Dark Knight' "
                    "on December 1st at 8 PM. My name is Priya."
                ),
            },
            {
                "role": "user",
                "content": (
                    "I want to cancel 5 tickets for 'Titanic' "
                    "on August 1st at 8 PM. My booking ID is 12345. "
                    "My name is Ramesh."
                ),
            },
        ]
    }
)
    
result = booking_response["structured_response"]

for operation in result.operations:
    if isinstance(operation, NewBooking):
        print(
            f"New Booking Request: {operation.customer_name} wants to book "
            f"{operation.number_of_tickets} tickets for "
            f"'{operation.movie_title}' on {operation.date} at {operation.time}."
        )

    elif isinstance(operation, CancelBooking):
        print(
            f"Cancellation Request: {operation.customer_name} wants to cancel "
            f"booking ID {operation.booking_id} for "
            f"'{operation.movie_title}'."
        )

    print("*" * 60)