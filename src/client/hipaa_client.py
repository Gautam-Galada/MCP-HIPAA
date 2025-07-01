import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from .ui_handler import UIHandler
from .input_processor import InputProcessor

class HIPAAMedicalClient:
    def __init__(self):
        self.session=None
        self.user_role= None
        self.current_patient = None
        self.ui_handler = UIHandler()
        self.input_processor = InputProcessor()
        
    async def connect(self, server_path="server.py"):
        server_params = StdioServerParameters(
            command="python",
            args=[server_path]
        )
        self.stdio_client = stdio_client(server_params)
        read, write = await self.stdio_client.__aenter__()
        self.client_session = ClientSession(read, write)
        self.session = await self.client_session.__aenter__()
        await self.session.initialize()
    async def disconnect(self):
        if self.session:
            await self.client_session.__aexit__(None, None, None)
            await self.stdio_client.__aexit__(None, None, None)
            
    def select_role(self): self.user_role = self.ui_handler.display_role_selection()
    
    async def start_conversation(self):
        greeting = self.ui_handler.get_greeting(self.user_role)
        print(f"\n Agent: {greeting}")
        while True:
            user_input = input(f"\n👤 {self.user_role.title()}: ").strip()
            
            if user_input.lower() == "quit":
                print("Agent: Thank you for using the HIPAA Medical Smart Agent. Goodbye!")
                break
            
            if not user_input:continue
            patient_id = self.input_processor.extract_patient_id(user_input)
            if patient_id:self.current_patient = patient_id
            await self.process_user_input(user_input)
    
    async def process_user_input(self, user_input):
        try:
            if self.input_processor.is_patient_info_request(user_input):await self.handle_patient_info_request(user_input)
            elif self.input_processor.is_xray_request(user_input):await self.handle_xray_request(user_input)
            else:await self.handle_general_chat(user_input)
                
        except Exception as e:
            print(f"Agent: I apologize, but I encountered an error: {str(e)}")
    
    async def handle_patient_info_request(self, user_input):
        patient_id = self.current_patient or self.input_processor.extract_patient_id(user_input)
        
        if not patient_id:
            print(" Agent: Please specify which patient you'd like information about (e.g., 'patient 1').")
            return
        
        try:
            result = await self.session.call_tool("get_patient_info", {
                "patient_id": patient_id,
                "user_role": self.user_role,
                "query": user_input
            })
            
            response = self._extract_response_text(result)
            print(f" Agent: {response}")
            
        except Exception as e:
            print(f" Agent: I couldn't retrieve patient information: {str(e)}")
    
    async def handle_xray_request(self, user_input):
        patient_id = self.current_patient or self.input_processor.extract_patient_id(user_input)
        
        if not patient_id:
            print("Agent: Please specify which patient's X-ray you'd like me to analyze (e.g., 'analyze xray for patient 1').")
            return
        
        try:
            result = await self.session.call_tool("analyze_xray", {
                "patient_id": patient_id,
                "user_role": self.user_role,
                "query": user_input
            })
            
            response = self._extract_response_text(result)
            print(f"Agent: {response}")
            
        except Exception as e:
            print(f"Agent: I couldn't analyze the X-ray: {str(e)}")
    
    async def handle_general_chat(self, user_input):
        try:
            result = await self.session.call_tool("chat_with_agent", {
                "user_role": self.user_role,
                "message": user_input,
                "patient_context": self.current_patient or ""
            })
            
            response = self._extract_response_text(result)
            print(f" Agent: {response}")
            
        except Exception as e:
            print(f" Agent: I couldn't process your request: {str(e)}")
    
    def _extract_response_text(self, result):
        if hasattr(result, 'content') and result.content:
            for content in result.content:
                if hasattr(content, 'text'):
                    return content.text
                else:
                    return str(content)
        return "I apologize, but I couldn't generate a proper response."
    
    async def run(self):
        try:
            print("Connecting to HIPAA Medical Smart Agent...")
            await self.connect()
            print("Connected successfully!")
            
            self.select_role()
            await self.start_conversation()
            
        except KeyboardInterrupt:
            print("\nSession interrupted by user")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await self.disconnect()
            print("Disconnected from server")