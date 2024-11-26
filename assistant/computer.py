import os
import logging
import pyautogui
import pytesseract
import numpy as np
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
        
        return None

class ComputerController:
    """Controls computer through mouse and keyboard"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.screen = ScreenAnalyzer()
        
        # Configure PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5  # Add small delay between actions
    
    def move_to(self, x: int, y: int, duration: float = 0.5):
        """Move mouse to location"""
        try:
            pyautogui.moveTo(x, y, duration=duration)
        except Exception as e:
            self.logger.error(f"Mouse move failed: {e}")
            raise
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None,
             duration: float = 0.5):
        """Click at location or current position"""
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y, duration=duration)
            else:
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
            self.move_to(x, y, duration)
            self.click()
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

# Example usage:
"""
def main():
    controller = ComputerController()
    
    # Find and click a button
    if controller.click_text("Submit", partial=True):
        print("Clicked Submit button")
    
    # Type some text
    controller.type_text("Hello, World!")
    
    # Use keyboard shortcut
    controller.hotkey('command', 'c')  # Copy
    
if __name__ == '__main__':
    main()
"""
