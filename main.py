import os
import sys
from agents import Agent, Runner
from tools import search_doctors

def main():
    # Check for API Key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not found.")
        print("Please set it: export OPENAI_API_KEY='sk-ப்புகள்'")
        sys.exit(1)

    print("Initializing Doctor Listing Agent...")
    
    # Create the agent
    doctor_agent = Agent(
        name="DoctorFinder",
        instructions=(
            "You are a helpful assistant specialized in finding doctors. "
            "Use the 'search_doctors' tool to find healthcare providers based on the user's criteria "
            "(name, location, specialty). "
            "IMPORTANT: The API requires specific taxonomy descriptions. Map common terms to official ones:\n"
            "- 'Cardiologist' -> 'Cardiovascular Disease'\n"
            "- 'Dermatologist' -> 'Dermatology'\n"
            "- 'ENT' -> 'Otolaryngology'\n"
            "When displaying results, present them in a clean, readable format. "
            "If no doctors are found, suggest broadening the search criteria."
        ),
        tools=[search_doctors]
    )

    print("Doctor Finder is ready! (Type 'quit' or 'exit' to stop)")
    print("-" * 50)

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ["quit", "exit"]:
                print("Goodbye!")
                break
            
            if not user_input:
                continue

            print("Agent: Thinking...", end="", flush=True)
            
            # Run the agent
            result = Runner.run_sync(doctor_agent, user_input)
            
            # Clear "Thinking..." line
            print("\r" + " " * 20 + "\r", end="")
            
            print(f"Agent: {result.final_output}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
