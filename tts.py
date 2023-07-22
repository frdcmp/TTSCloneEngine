import streamlit as st
import subprocess

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"Error: {e}"

def main():
    st.title("Terminal Command Execution App")
    
    # Text input for the terminal command
    command = st.text_input("Enter the terminal command:")
    
    # Button to execute the command
    if st.button("Execute Command"):
        if command:
            st.write("Executing command...")
            output = execute_command(command)
            st.code(output, language="text")
        else:
            st.write("Please enter a command in the text input above.")

if __name__ == "__main__":
    main()
