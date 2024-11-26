import os
import logging
import subprocess
import pyautogui
import pytesseract
import applescript
from PIL import Image, ImageGrab
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

class ElementType(Enum):
    """Types of UI elements"""
    BUTTON = "button"
    TEXT_FIELD = "text_field"
    LINK = "link"
    MENU = "menu"
    ICON = "icon"
    TEXT = "text"
    WINDOW = "window"
    OTHER = "other"

@dataclass
class UIElement:
    """Represents a UI element on screen"""
    type: ElementType
    text: Optional[str]
    location: Tuple[int, int]
    size: Tuple[int, int]
    confidence: float
    image: Optional[Image.Image] = None
    accessibility_description: Optional[str] = None

class ScreenAnalyzer:
    """Analyzes screen content and finds UI elements"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configure OCR
        if os.path.exists('/usr/local/bin/tesseract'):
            pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
        
        # Initialize PyAutoGUI safely
        pyautogui.FAILSAFE = True
        
        # Cache for recent analysis
        self.last_analysis: Optional[Dict[str, Any]] = None
        
        # Check accessibility permissions
        self._check_permissions()
    
    def _check_permissions(self):
        """Check and request necessary permissions"""
        try:
            script = '''
            tell application "System Events"
                set UI_enabled to UI elements enabled
            end tell
            '''
            applescript.AppleScript(script).run()
        except Exception as e:
            self.logger.warning(
                f"Accessibility permissions not granted: {e}. "
                "Please enable in System Settings > Privacy & Security > Accessibility"
            )
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> Image.Image:
        """Capture screen or region"""
        try:
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()
            return screenshot
        except Exception as e:
            self.logger.error(f"Screen capture failed: {e}")
            raise
    
    def find_text(self, screenshot: Image.Image) -> List[Dict[str, Any]]:
        """Find text in screenshot using OCR"""
        try:
            # Get OCR data with bounding boxes
            data = pytesseract.image_to_data(
                screenshot,
                output_type=pytesseract.Output.DICT
            )
            
            results = []
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                if int(data['conf'][i]) > 60:  # Confidence threshold
                    text = data['text'][i].strip()
                    if text:
                        results.append({
                            'text': text,
                            'confidence': float(data['conf'][i]),
                            'location': (
                                int(data['left'][i]),
                                int(data['top'][i])
                            ),
                            'size': (
                                int(data['width'][i]),
                                int(data['height'][i])
                            )
                        })
            return results
            
        except Exception as e:
            self.logger.error(f"OCR failed: {e}")
            raise
    
    def find_ui_elements(self, screenshot: Optional[Image.Image] = None) -> List[UIElement]:
        """Find UI elements in screenshot"""
        if not screenshot:
            screenshot = self.capture_screen()
        
        elements = []
        
        # Find text elements
        text_elements = self.find_text(screenshot)
        for elem in text_elements:
            # Analyze text to determine element type
            text = elem['text'].lower()
            if any(word in text for word in ['click', 'submit', 'ok', 'cancel']):
                elem_type = ElementType.BUTTON
            elif any(word in text for word in ['menu', 'file', 'edit', 'view']):
                elem_type = ElementType.MENU
            else:
                elem_type = ElementType.TEXT
            
            elements.append(UIElement(
                type=elem_type,
                text=elem['text'],
                location=elem['location'],
                size=elem['size'],
                confidence=elem['confidence']
            ))
        
        # Use AppleScript to get accessibility descriptions
        try:
            script = '''
            tell application "System Events"
                set frontApp to first application process whose frontmost is true
                set elements to entire contents of frontApp
                set output to {}
                repeat with elem in elements
                    try
                        set desc to description of elem
                        set pos to position of elem
                        set sz to size of elem
                        copy {desc, pos, sz} to end of output
                    end try
                end repeat
                return output
            end tell
            '''
            result = applescript.AppleScript(script).run()
            if result:
                for desc, pos, size in result:
                    elements.append(UIElement(
                        type=ElementType.OTHER,
                        text=None,
                        location=pos,
                        size=size,
                        confidence=1.0,
                        accessibility_description=desc
                    ))
        except Exception as e:
            self.logger.error(f"AppleScript error: {e}")
        
        # Cache analysis
        self.last_analysis = {
            'timestamp': 'now',
            'elements': elements
        }
        
        return elements
    
    def find_element_by_text(self, text: str, partial: bool = False) -> Optional[UIElement]:
        """Find UI element by text content"""
        elements = self.find_ui_elements()
        
        for element in elements:
            if element.text:
                if partial and text.lower() in element.text.lower():
                    return element
                elif text.lower() == element.text.lower():
                    return element
            elif element.accessibility_description:
                if partial and text.lower() in element.accessibility_description.lower():
                    return element
                elif text.lower() == element.accessibility_description.lower():
                    return element
        
        return None

class ComputerController:
    """Controls computer through mouse, keyboard, and AppleScript"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.screen = ScreenAnalyzer()
        
        # Configure PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5  # Add small delay between actions
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen size"""
        return pyautogui.size()
    
    def move_to(self, x: int, y: int, duration: float = 0.5):
        """Move mouse to location"""
        try:
            # Ensure coordinates are within screen bounds
            size = self.get_screen_size()
            x = max(0, min(x, size[0]-1))
            y = max(0, min(y, size[1]-1))
            pyautogui.moveTo(x, y, duration=duration)
        except Exception as e:
            self.logger.error(f"Mouse move failed: {e}")
            raise
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None,
             duration: float = 0.5):
        """Click at location or current position"""
        try:
            if x is not None and y is not None:
                self.move_to(x, y, duration)
            pyautogui.click()
        except Exception as e:
            self.logger.error(f"Click failed: {e}")
            raise
    
    def type_text(self, text: str, interval: float = 0.1):
        """Type text with optional interval"""
        try:
            pyautogui.write(text, interval=interval)
        except Exception as e:
            self.logger.error(f"Typing failed: {e}")
            raise
    
    def press_key(self, key: str):
        """Press a keyboard key"""
        try:
            pyautogui.press(key)
        except Exception as e:
            self.logger.error(f"Key press failed: {e}")
            raise
    
    def hotkey(self, *keys):
        """Press multiple keys together"""
        try:
            pyautogui.hotkey(*keys)
        except Exception as e:
            self.logger.error(f"Hotkey failed: {e}")
            raise
    
    def click_element(self, element: UIElement, duration: float = 0.5):
        """Click on a UI element"""
        try:
            # Calculate center of element
            x = element.location[0] + element.size[0] // 2
            y = element.location[1] + element.size[1] // 2
            
            # Move and click
            self.click(x, y, duration)
        except Exception as e:
            self.logger.error(f"Element click failed: {e}")
            raise
    
    def click_text(self, text: str, partial: bool = False,
                  duration: float = 0.5) -> bool:
        """Find and click text on screen"""
        element = self.screen.find_element_by_text(text, partial)
        if element:
            self.click_element(element, duration)
            return True
        return False
    
    def activate_app(self, app_name: str):
        """Activate application"""
        try:
            script = f'''
            tell application "{app_name}"
                activate
            end tell
            '''
            applescript.AppleScript(script).run()
        except Exception as e:
            self.logger.error(f"App activation failed: {e}")
            raise
    
    def chrome_command(self, command: str):
        """Run Chrome command via AppleScript"""
        try:
            script = f'''
            tell application "Google Chrome"
                activate
                delay 0.5
                {command}
            end tell
            '''
            applescript.AppleScript(script).run()
        except Exception as e:
            self.logger.error(f"Chrome command failed: {e}")
            raise
    
    def vscode_command(self, command: str):
        """Run VSCode command via AppleScript"""
        try:
            script = f'''
            tell application "Visual Studio Code"
                activate
                delay 0.5
                {command}
            end tell
            '''
            applescript.AppleScript(script).run()
        except Exception as e:
            self.logger.error(f"VSCode command failed: {e}")
            raise
    
    def get_running_apps(self) -> List[str]:
        """Get list of running applications"""
        try:
            script = '''
            tell application "System Events"
                get name of every process where background only is false
            end tell
            '''
            result = applescript.AppleScript(script).run()
            return result if result else []
        except Exception as e:
            self.logger.error(f"Failed to get running apps: {e}")
            raise
