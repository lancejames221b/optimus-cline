#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Building Cline GUI...${NC}"

# Check for required tools
if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm is required but not installed.${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}node is required but not installed.${NC}"
    exit 1
fi

# Install dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
npm install

# Build VSCode extension
echo -e "${GREEN}Building VSCode extension...${NC}"
cd vscode-extension
npm install
npm run build
cd ..

# Build Electron app
echo -e "${GREEN}Building Electron app...${NC}"
npm run build

# Create installation package
echo -e "${GREEN}Creating installation package...${NC}"
mkdir -p dist/cline-gui

# Copy CLI scripts
cp -r ../bin dist/cline-gui/
chmod +x dist/cline-gui/bin/*

# Copy VSCode extension
cp -r vscode-extension/dist dist/cline-gui/vscode-extension

# Create install script
cat > dist/cline-gui/install.sh << 'INSTALL'
#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Installing Cline GUI...${NC}"

# Install CLI tools
mkdir -p ~/.cline/bin
cp -r bin/* ~/.cline/bin/
chmod +x ~/.cline/bin/*

# Add to PATH if not already added
if ! grep -q "export PATH=\$PATH:~/.cline/bin" ~/.zshrc; then
    echo -e "\n# Cline utility scripts" >> ~/.zshrc
    echo "export PATH=\$PATH:~/.cline/bin" >> ~/.zshrc
    echo -e "${GREEN}Added scripts to PATH${NC}"
fi

# Install VSCode extension
CODE_EXT_DIR="$HOME/.vscode/extensions/cline-vscode"
mkdir -p "$CODE_EXT_DIR"
cp -r vscode-extension/* "$CODE_EXT_DIR/"
echo -e "${GREEN}Installed VSCode extension${NC}"

# Install Electron app
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
echo "1. Run 'source ~/.zshrc' to update PATH"
echo "2. Restart VSCode to activate extension"
echo "3. Launch Cline GUI from Applications"
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

# Remove CLI tools
rm -rf ~/.cline

# Remove from PATH
sed -i '' '/# Cline utility scripts/d' ~/.zshrc
sed -i '' '/export PATH=\$PATH:~/.cline\/bin/d' ~/.zshrc

# Remove VSCode extension
rm -rf "$HOME/.vscode/extensions/cline-vscode"

# Remove Electron app
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    rm -rf /Applications/Cline.app
else
    # Linux
    rm -f ~/.local/bin/cline-gui.AppImage
    rm -f ~/.local/share/applications/cline-gui.desktop
fi

echo -e "${GREEN}Uninstallation complete!${NC}"
echo "Please restart your terminal and VSCode"
UNINSTALL

chmod +x dist/cline-gui/uninstall.sh

echo -e "${GREEN}Build complete!${NC}"
echo -e "Installation package created in ${BLUE}dist/cline-gui/${NC}"
echo "To install:"
echo "1. cd dist/cline-gui"
echo "2. ./install.sh"
