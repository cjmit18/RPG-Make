"""
Basic Tkinter Start Menu - Direct tkinter implementation to test functionality
"""
import tkinter as tk
from tkinter import messagebox
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(str(project_root))

class BasicStartMenu:
    """Basic tkinter start menu without the modular system"""
    
    def __init__(self):
        self.root = None
    
    def create_menu(self):
        """Create basic tkinter menu"""
        self.root = tk.Tk()
        self.root.title("🎮 RPG Game Menu")
        self.root.geometry("600x400")
        
        # Center the window
        self.root.eval('tk::PlaceWindow . center')
        
        # Create widgets
        title_label = tk.Label(self.root, text="Welcome to RPG Adventure!", 
                              font=('Arial', 16, 'bold'))
        title_label.pack(pady=30)
        
        subtitle_label = tk.Label(self.root, text="Choose your action:", 
                                 font=('Arial', 12))
        subtitle_label.pack(pady=10)
        
        # Buttons with consistent styling
        button_style = {'width': 20, 'height': 2, 'font': ('Arial', 11)}
        
        new_game_btn = tk.Button(self.root, text="New Game", 
                                command=self.new_game, **button_style)
        new_game_btn.pack(pady=5)
        
        load_game_btn = tk.Button(self.root, text="Load Game", 
                                 command=self.load_game, **button_style)
        load_game_btn.pack(pady=5)
        
        settings_btn = tk.Button(self.root, text="Settings", 
                                command=self.settings, **button_style)
        settings_btn.pack(pady=5)
        
        exit_btn = tk.Button(self.root, text="Exit", 
                            command=self.exit_game, **button_style)
        exit_btn.pack(pady=5)
        
        # Copyright label at bottom
        copyright_label = tk.Label(self.root, text="© 2025 RPG Adventure Game", 
                                  font=('Arial', 9), fg='gray')
        copyright_label.pack(side='bottom', pady=10)
    
    def new_game(self):
        """Handle new game"""
        messagebox.showinfo("New Game", "🎮 Starting new adventure!\n\nThis would open character creation.")
        print("New game started")
    
    def load_game(self):
        """Handle load game"""
        messagebox.showinfo("Load Game", "💾 Loading your saved adventure!\n\nThis would show save files.")
        print("Game loaded")
    
    def settings(self):
        """Handle settings"""
        messagebox.showinfo("Settings", "⚙️ Opening game settings...\n\nThis would show the settings dialog.")
        print("Settings opened")
    
    def exit_game(self):
        """Handle exit"""
        if messagebox.askyesno("Exit Game", "🚪 Are you sure you want to exit?\n\nYour adventure awaits!"):
            print("Exiting game...")
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """Run the menu"""
        print("🎮 Creating Basic Start Menu...")
        self.create_menu()
        
        print("✅ Menu created successfully")
        print("🚀 Launching menu window...")
        print("💡 Click the buttons to test functionality")
        
        # Run the tkinter main loop
        try:
            self.root.mainloop()
            print("👋 Menu closed")
        except Exception as e:
            print(f"Error running menu: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main function"""
    try:
        menu = BasicStartMenu()
        menu.run()
    except KeyboardInterrupt:
        print("\nMenu interrupted")
    except Exception as e:
        print(f"Startup error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
