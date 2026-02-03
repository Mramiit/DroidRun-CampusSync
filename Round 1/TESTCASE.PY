import asyncio
import os  # <--- 1. Add this import
from pydantic import BaseModel, Field
from droidrun import DroidAgent, DroidrunConfig

# <--- 2. Set your key here (before Config is created)
os.environ["GOOGLE_API_KEY"] = "AIzaSyA27v2WwM1WL2H7UYUfTcjaay_IoomNjcU"

# 1. Define output structure
class ContactInfo(BaseModel):
    """Contact information from device."""
    name: str = Field(description="Full name of the contact")
    phone: str = Field(description="Phone number")
    email: str = Field(description="Email address", default="Not provided")

# 2. Create agent with output_model
async def main():
    # The config will now automatically pick up the key from os.environ
    config = DroidrunConfig() 

    agent = DroidAgent(
        goal="Find John Smith's contact information",
        config=config,
        output_model=ContactInfo,
    )

    # 3. Run and access structured output
    result = await agent.run()

    if result.success and result.structured_output:
        contact: ContactInfo = result.structured_output
        print(f"Name: {contact.name}")
        print(f"Phone: {contact.phone}")
        print(f"Email: {contact.email}")

asyncio.run(main())