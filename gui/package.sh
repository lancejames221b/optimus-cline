#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Packaging Cline GUI...${NC}"

# Check for required tools
if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm is required but not installed.${NC}"
    exit 1
fi

# Clean previous builds
echo -e "${GREEN}Cleaning previous builds...${NC}"
rm -rf dist/

# Install dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
npm install

# Update package.json for distribution
cat > package.json << 'EOF'
{
  "name": "cline-gui",
  "version": "1.0.0",
  "description": "GUI interface for Cline task management",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "build": "electron-builder",
    "pack": "electron-builder --dir",
    "dist": "electron-builder"
  },
  "build": {
    "appId": "com.cline.gui",
    "productName": "Cline",
    "directories": {
      "output": "dist"
    },
    "files": [
      "**/*",
      "!**/node_modules/*/{CHANGELOG.md,README.md,README,readme.md,readme}",
      "!**/node_modules/*/{test,__tests__,tests,powered-test,example,examples}",
      "!**/node_modules/*.d.ts",
      "!**/node_modules/.bin",
      "!**/*.{iml,o,hprof,orig,pyc,pyo,rbc,swp,csproj,sln,xproj}",
      "!.editorconfig",
      "!**/._*",
      "!**/{.DS_Store,.git,.hg,.svn,CVS,RCS,SCCS,.gitignore,.gitattributes}",
      "!**/{__pycache__,thumbs.db,.flowconfig,.idea,.vs,.nyc_output}",
      "!**/{appveyor.yml,.travis.yml,circle.yml}",
      "!**/{npm-debug.log,yarn.lock,.yarn-integrity,.yarn-metadata.json}"
    ],
    "mac": {
      "category": "public.app-category.developer-tools",
      "icon": "build/icon.icns",
      "target": ["dmg", "zip"],
      "darkModeSupport": true
    },
    "linux": {
      "category": "Development",
      "icon": "build/icon.png",
      "target": ["AppImage", "deb"],
      "desktop": {
        "Name": "Cline",
        "Comment": "Task Management GUI",
        "Categories": "Development"
      }
    },
    "win": {
      "icon": "build/icon.ico",
      "target": ["nsis", "portable"]
    }
  },
  "dependencies": {
    "electron-store": "^8.1.0",
    "keytar": "^7.9.0",
    "ws": "^8.2.3"
  },
  "devDependencies": {
    "electron": "^20.0.0",
    "electron-builder": "^23.3.3"
  }
}
EOF

# Create icons directory
mkdir -p build
echo -e "${GREEN}Creating application icons...${NC}"

# Build the application
echo -e "${GREEN}Building application...${NC}"
npm run build

# Create distribution package
echo -e "${GREEN}Creating distribution package...${NC}"
mkdir -p dist/cline-gui
cp -r {main.js,index.html,styles.css,renderer.js,preload.js} dist/cline-gui/
cp -r build dist/cline-gui/

# Create installation script
cat > dist/cline-gui/install.sh << 'INSTALL'
#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Installing Cline GUI...${NC}"

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    cp -r Cline.app /Applications/
    echo -e "${GREEN}Installed Cline GUI to Applications${NC}"
else
    # Linux
    mkdir -p ~/.local/share/applications
    cp -r cline-gui.AppImage ~/.local/bin/
    cp cline-gui.desktop ~/.local/share/applications/
    echo -e "${GREEN}Installed Cline GUI${NC}"
fi

echo -e "${BLUE}Installation complete!${NC}"
echo "Launch Cline GUI from your applications menu"
INSTALL

chmod +x dist/cline-gui/install.sh

# Create uninstall script
cat > dist/cline-gui/uninstall.sh << 'UNINSTALL'
#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Uninstalling Cline GUI...${NC}"

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    rm -rf /Applications/Cline.app
else
    # Linux
    rm -f ~/.local/bin/cline-gui.AppImage
    rm -f ~/.local/share/applications/cline-gui.desktop
fi

echo -e "${GREEN}Uninstallation complete!${NC}"
UNINSTALL

chmod +x dist/cline-gui/uninstall.sh

echo -e "${GREEN}Package created successfully!${NC}"
echo -e "Distribution package available in ${BLUE}dist/cline-gui/${NC}"
echo "To install:"
echo "1. cd dist/cline-gui"
echo "2. ./install.sh"
