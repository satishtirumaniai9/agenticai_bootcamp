
# Cinebot - Movie Booking Agent
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.agents.structured_output import ProviderStrategy, ToolStrategy
from langchain_core.tools import tool
from langchain.agents import create_agent

from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from typing import Callable

from langchain.tools import tool, ToolRuntime
from langchain_core.messages import HumanMessage

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
# model.bind_tools([peek_show_times], strategy=ToolStrategy(BookingRequest))

# model.invoke("Hello, I am Cinebot, your movie booking assistant. How can I help you today?")

# print("Cinebot is ready to assist you with movie bookings!")
# print("-----------------------------------------------------------------")

# booking_requests = [
#     "Hi, I would like to book tickets for the movie 'Inception' for 2 adults and 1 child on July 15th at 7 PM.name is Haasith",
#     "Can you book me a seat for the movie 'The Matrix' for 1 adult on August 20th at 9 PM?, I am Satish",
#     "URGENT: I need to cancel  my booking of 10 tickets for 'Avatar' on September 5th at 6 PM. Please confirm the cancellation under Gayathri.",
#     "Cancel my booking for 'Titanic' on October 10th at 8 PM. I am Ramesh and I had booked 3 tickets.",
# ]

# for message in booking_requests:
#     response = model.invoke("Extract the booking details from the following message: " + message)
#     print(response)
#     print("-----------------------------------------------------------------")
    
    
from langchain.agents import create_agent

# booking_agent = create_agent(
#     model=model,
#     tools=[peek_show_times],
#     response_format=ToolStrategy(BookingRequest)
# )

# booking_response = booking_agent.invoke(
#     {
#         "messages": [
#             {
#                 "role": "user",
#                 "content": (
#                     "I want to book 2 tickets for 'Interstellar' "
#                     "on November 12th at 5 PM. My name is Ananya."
#                 ),
#             }
#         ]
#     }
# )
# booking = booking_response["structured_response"]

# print(booking)

# class NewBooking(BaseModel):
#     customer_name: str = Field(..., description="Name of the customer making the booking")
#     movie_title: str = Field(..., description="Title of the movie to be booked")
#     number_of_tickets: int = Field(..., description="Number of tickets to be booked")
#     date: str = Field(..., description="Date of the movie booking in YYYY-MM-DD format")
#     time: str = Field(..., description="Time of the movie booking in HH:MM format")
    
# class CancelBooking(BaseModel):
#     customer_name: str = Field(..., description="Name of the customer making the cancellation")
#     movie_title: str = Field(..., description="Title of the movie to be canceled")
#     booking_id: int = Field(..., description="ID of the booking to be canceled")

# from typing import Union

# class BookingOperations(BaseModel):
#     operations: list[Union[NewBooking, CancelBooking]] = Field(
#         description="All booking and cancellation operations requested"
#     )
    


# union_agent = create_agent(
#     model=model,
#     tools=[peek_show_times],
#     response_format=ToolStrategy(BookingOperations)
#     )
# booking_response = union_agent.invoke(
#     {
#         "messages": [
#             {
#                 "role": "user",
#                 "content": (
#                     "I want to book 3 tickets for 'The Dark Knight' "
#                     "on December 1st at 8 PM. My name is Priya."
#                 ),
#             },
#             {
#                 "role": "user",
#                 "content": (
#                     "I want to cancel 5 tickets for 'Titanic' "
#                     "on August 1st at 8 PM. My booking ID is 12345. "
#                     "My name is Ramesh."
#                 ),
#             },
#         ]
#     }
# )
    
# result = booking_response["structured_response"]

# for operation in result.operations:
#     if isinstance(operation, NewBooking):
#         print(
#             f"New Booking Request: {operation.customer_name} wants to book "
#             f"{operation.number_of_tickets} tickets for "
#             f"'{operation.movie_title}' on {operation.date} at {operation.time}."
#         )

#     elif isinstance(operation, CancelBooking):
#         print(
#             f"Cancellation Request: {operation.customer_name} wants to cancel "
#             f"booking ID {operation.booking_id} for "
#             f"'{operation.movie_title}'."
#         )

#     print("*" * 60)
    


# @tool
# def check_show_times(movie_title: str) -> str: 
#     """
#     Check the show times for a given movie title.
    
#     Args:
#         movie_title (str): The title of the movie to check show times for.
#     """
#     fake_show_times = {
#         "Inception": ["1:00 PM", "4:00 PM", "7:00 PM", "10:00 PM"],
#         "The Matrix": ["12:00 PM", "3:00 PM", "6:00 PM", "9:00 PM"],
#         "Avatar": ["11:00 AM", "2:00 PM", "5:00 PM", "8:00 PM"],
#         "Titanic": ["10:00 AM", "1:00 PM", "4:00 PM", "7:00 PM"],
#         "Interstellar": ["12:30 PM", "3:30 PM", "6:30 PM", "9:30 PM"],
#         "The Dark Knight": ["11:30 AM", "2:30 PM", "5:30 PM", "8:30 PM"],
#     }
#     show_times = fake_show_times.get(movie_title, [])
#     if show_times:
#         return f"Show times for '{movie_title}': {', '.join(show_times)}"
#     else:
#         return f"No show times available for '{movie_title}'."

# class MovieShows(BaseModel):
#     movie_title: str = Field(
#         ...,
#         description="Title of the movie",
#     )
#     date: str = Field(
#         ...,
#         description="Requested date in YYYY-MM-DD format",
#     )
#     requested_time: str = Field(
#         ...,
#         description="Requested show time",
#     )
#     available: bool = Field(
#         ...,
#         description="Whether the movie is available at the requested time",
#     )
#     available_show_times: list[str] = Field(
#         ...,
#         description="Available show times for the movie",
#     )

# show_times_agent = create_agent(
#     model=model,
#     tools=[check_show_times],
#    system_prompt=(
#         "You are Cinebot, a movie booking assistant. "
#         "Always use the check_show_times tool before checking availability. "
#         "Compare the requested time with the show times returned by the tool. "
#         "Set available to true only when the requested time exactly matches "
#         "one of the available show times."
#     ),
#     response_format=ToolStrategy(MovieShows),
# )

# response = show_times_agent.invoke(
#     {
#         "messages": [
#             {
#                 "role": "user",
#                 "content": (
#                     "Is Interstellar available for booking on November 12th "
#                     "at 5 PM at Downtime Cinemas?"
#                 ),
#             }
#         ]
#     }
# )

# print(response["structured_response"])



# @tool
# def get_last_movie_mentioned(runtime: ToolRuntime) -> str:
#     """
#     Extract the last movie title mentioned in the user's message.
    
#     Args:
#         runtime (ToolRuntime): The runtime context containing the conversation history.
#     """
#     pass

# print(get_last_movie_mentioned.args)



@tool
def standard_booking(movie_title:str) -> str:
    """
    Standard booking tool for a given movie title.
    
    Args:
        movie_title (str): The title of the movie to book.
    """
    return f"Booking confirmed for '{movie_title}'. Enjoy your movie!"

@tool
def vip_booking(movie_title:str) -> str:
    """
    VIP booking tool for a given movie title.
    
    Args:
        movie_title (str): The title of the movie to book.
    """
    return f"VIP booking confirmed for '{movie_title}'. Enjoy your exclusive experience!"

@wrap_model_call
def gate_vip_tools(request:ModelRequest, handler:Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
    """
    Middleware to gate VIP booking tools based on user role.
    
    Args:
        request (ModelRequest): The model request containing the conversation context.
        handler (Callable): The next handler in the middleware chain.
    """
    
    is_vip = request.state.get("is_vip_member", False)
    
    if not is_vip:
        allowed_tools = [t for t in request.tools if t.name != "vip_booking"]
        request = request.override(tools=allowed_tools)
    else:
        allowed_tools = request.tools  # Allow all tools for VIP members
        request = request.override(tools=allowed_tools)
    return handler(request)

gated_agent = create_agent(
    model=model,
    tools=[standard_booking, vip_booking],
    middleware=[gate_vip_tools])

result_regular = gated_agent.invoke({"messages": [{"role": "user", "content": "Book me a VIP tickets for 'Inception'."}], "state": {"is_vip_member": True}})    

print(result_regular["messages"][-1].content)  # Should allow VIP booking
