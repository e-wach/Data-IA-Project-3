import streamlit as st
import requests
import json
from datetime import datetime
import os

AGENT_API = os.getenv("AGENT_API", "default-api")


# Initialize session state for storing bet amount and API response
if 'bet_amount' not in st.session_state:
    st.session_state.bet_amount = None
if 'api_response' not in st.session_state:
    st.session_state.api_response = None

# Show title and welcome message
st.title("🏀🧠 BetMaestro")
st.write("Welcome!")
st.write("Get betting recommendations for next week's NBA games.")

# Function to format and display betting strategy
def display_betting_strategy(strategy_data):
    st.subheader("📊 Your Betting Strategy")
    
    try:
        # Parse the strategy data if it's a string
        if isinstance(strategy_data, str):
            strategy_data = json.loads(strategy_data)
        
        # Get the estrategia list from the response
        bets = strategy_data.get('estrategia', [])
        
        if not bets:
            st.error("No betting recommendations found in the response")
            return
            
        for bet in bets:
            # Split the teams to highlight the recommended one
            teams = bet['partido'].split(" vs ")
            recommended_team = bet['ganador']
            
            # Display teams with the recommended one in orange
            if teams[0] == recommended_team:
                # st.markdown(f"**Recommended Bet:** :orange[{teams[0]}] vs {teams[1]} ({bet['date']})")
                st.markdown(f"**Recommended Bet:** :orange[{teams[0]}] vs {teams[1]}")
            else:
                # st.markdown(f"**Recommended Bet:** {teams[0]} vs :orange[{teams[1]}] ({bet['date']})")
                st.markdown(f"**Recommended Bet:** {teams[0]} vs :orange[{teams[1]}]")
            
            st.write(f"**Bookmaker:** {bet['casa_de_apuestas']}")
            st.write(f"**Odds:** {bet['odds']}")
            st.write(f"**Bet Amount:** {bet['cantidad_a_apostar']}")
            st.write(f"**Potential Return:** {bet['cantidad_a_apostar'] * bet['odds']:.2f}")
            st.markdown("---")  # Add a separator between bets
                
    except json.JSONDecodeError as e:
        st.error(f"Error parsing betting strategy: {e}")
        st.write("Raw response:", strategy_data)
    except Exception as e:
        st.error(f"Error displaying betting strategy: {e}")
        st.write("Raw response:", strategy_data)

# Main interface
if st.session_state.bet_amount is None:
    bet_amount = st.number_input(
        "Enter the amount you want to bet:",
        min_value=10,
        step=10
    )
    
    if st.button("Get Betting Strategy"):
        API_URL = f"{AGENT_API}/predict"
        
        try:
            payload = {"betting_amount": bet_amount}
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()
            
            # Parse the response
            try:
                api_response = response.json()
                st.session_state.api_response = api_response
                st.session_state.bet_amount = bet_amount
                
                # Display the betting strategy
                display_betting_strategy(st.session_state.api_response)
                
            except json.JSONDecodeError as e:
                st.error(f"Error parsing API response: {e}")
                st.write("Raw response:", response.text)    
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error calling the API: {e}")
else:
    # Display the current betting strategy
    display_betting_strategy(st.session_state.api_response)
    
    # Ask if user wants to continue
    if st.button("Get New Strategy"):
        st.session_state.bet_amount = None
        st.session_state.api_response = None
        st.experimental_rerun()
