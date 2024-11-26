import os
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path

class GlobalSettings:
    """Manages global system settings"""
    
    def __init__(self):
        # Define settings locations
        self.settings_dir = os.path.expanduser('~/.cline')
        self.settings_file = os.path.join(self.settings_dir, 'settings.json')
        self.keys_file = '/Volumes/SeXternal/keys.txt'
        
        # Create settings directory if needed
        os.makedirs(self.settings_dir, exist_ok=True)
        
        # Load settings
        self.settings = self._load_settings()
        
        # Load API keys
        self.api_keys = self._load_api_keys()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file) as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading settings: {e}")
        return {}
    
    def _save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving settings: {e}")
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from keys file"""
        keys = {}
        if os.path.exists(self.keys_file):
            try:
                with open(self.keys_file) as f:
                    current_section = None
                    for line in f:
                        line = line.strip()
                        if line.startswith('[') and line.endswith(']'):
                            current_section = line[1:-1]
                        elif '=' in line and current_section == 'AI Models':
                            key, value = line.split('=', 1)
                            keys[key.strip()] = value.strip()
            except Exception as e:
                logging.error(f"Error loading API keys: {e}")
        return keys
    
    def _save_api_keys(self):
        """Save API keys to keys file"""
        try:
            # Read existing content
            with open(self.keys_file) as f:
                lines = f.readlines()
            
            # Find or create AI Models section
            ai_section_start = -1
            ai_section_end = -1
            for i, line in enumerate(lines):
                if line.strip() == '[AI Models]':
                    ai_section_start = i
                elif ai_section_start >= 0 and line.strip().startswith('['):
                    ai_section_end = i
                    break
            
            if ai_section_start == -1:
                # Add section at start
                lines.insert(0, '\n[AI Models]\n')
                ai_section_start = 0
                ai_section_end = 1
            elif ai_section_end == -1:
                # Section is at end
                ai_section_end = len(lines)
            
            # Create new key lines
            key_lines = []
            for key, value in self.api_keys.items():
                key_lines.append(f'{key}={value}\n')
            
            # Replace section content
            lines[ai_section_start+1:ai_section_end] = key_lines
            
            # Write back to file
            with open(self.keys_file, 'w') as f:
                f.writelines(lines)
            
            # Also update eWitness keys file
            ewitness_keys = '/Volumes/SeXternal/221B/Code/eWitness/keys.txt'
            if os.path.exists(ewitness_keys):
                with open(ewitness_keys, 'w') as f:
                    f.writelines(lines)
                
        except Exception as e:
            logging.error(f"Error saving API keys: {e}")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any):
        """Set a setting value"""
        self.settings[key] = value
        self._save_settings()
    
    def get_api_key(self, key: str) -> Optional[str]:
        """Get an API key"""
        return self.api_keys.get(key)
    
    def set_api_key(self, key: str, value: str):
        """Set an API key"""
        self.api_keys[key] = value
        self._save_api_keys()
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings"""
        return self.settings.copy()
    
    def get_all_api_keys(self) -> Dict[str, str]:
        """Get all API keys"""
        return self.api_keys.copy()

# Global settings instance
settings = GlobalSettings()
