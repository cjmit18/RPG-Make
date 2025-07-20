#!/usr/bin/env python3
"""Test script to debug right-click context menu functionality."""

import tkinter as tk
import traceback
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_right_click():
    """Test basic right-click functionality."""
    print("=== Testing Basic Right-Click ===")
    
    root = tk.Tk()
    root.title("Right-Click Test")
    root.geometry("400x300")
    
    # Create test frame
    frame = tk.Frame(root, bg="#34495e", relief=tk.RAISED, bd=2)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Add label
    label = tk.Label(frame, text="Right-click me!", font=("Arial", 14), bg="#34495e", fg="white")
    label.pack(expand=True)
    
    def test_context_menu(event):
        print(f"Right-click detected at ({event.x}, {event.y})")
        print(f"Root coordinates: ({event.x_root}, {event.y_root})")
        
        try:
            # Create context menu
            menu = tk.Menu(root, tearoff=0)
            menu.add_command(label="Test Option 1", command=lambda: print("Option 1 clicked"))
            menu.add_command(label="Test Option 2", command=lambda: print("Option 2 clicked"))
            menu.add_separator()
            menu.add_command(label="Close Menu", command=lambda: print("Menu closed"))
            
            # Show menu
            menu.tk_popup(event.x_root, event.y_root)
            print("Menu displayed successfully")
            
        except Exception as e:
            print(f"Error showing menu: {e}")
            traceback.print_exc()
        finally:
            try:
                menu.grab_release()
            except:
                pass
    
    # Bind right-click events
    frame.bind("<Button-3>", test_context_menu)
    frame.bind("<ButtonRelease-3>", test_context_menu)
    label.bind("<Button-3>", test_context_menu)
    label.bind("<ButtonRelease-3>", test_context_menu)
    
    print("Right-click test window opened. Try right-clicking on the frame or label.")
    print("Check console for debug output.")
    print("Close the window when done testing.")
    
    root.mainloop()

def test_equipment_slot_simulation():
    """Test simulating the equipment slot right-click functionality."""
    print("\n=== Testing Equipment Slot Simulation ===")
    
    root = tk.Tk()
    root.title("Equipment Slot Right-Click Test")
    root.geometry("500x400")
    root.configure(bg="black")
    
    # Create equipment slots frame
    slots_frame = tk.Frame(root, bg="black")
    slots_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Equipment slot data (similar to demo.py)
    slots_data = [
        ("⚔️", "Weapon", "weapon"),
        ("🛡️", "Shield", "offhand"),
        ("👕", "Armor", "body"),
        ("💍", "Ring", "ring"),
    ]
    
    def create_context_menu(slot_type, display_name):
        """Create context menu for equipment slot."""
        def show_context_menu(event):
            print(f"Right-click on {display_name} slot ({slot_type})")
            
            try:
                menu = tk.Menu(root, tearoff=0)
                menu.add_command(label=f"📋 {display_name} Slot", state="disabled")
                menu.add_separator()
                menu.add_command(
                    label=f"🗑️ Unequip {display_name}", 
                    command=lambda: print(f"Unequipping {display_name}")
                )
                menu.add_command(
                    label="🔍 Inspect Item", 
                    command=lambda: print(f"Inspecting {display_name}")
                )
                menu.add_command(
                    label="🎒 View Inventory", 
                    command=lambda: print("Opening inventory")
                )
                
                menu.tk_popup(event.x_root, event.y_root)
                print(f"Context menu shown for {display_name}")
                
            except Exception as e:
                print(f"Error showing {display_name} context menu: {e}")
                traceback.print_exc()
            finally:
                try:
                    menu.grab_release()
                except:
                    pass
        
        return show_context_menu
    
    # Create equipment slots
    for i, (icon, name, slot_type) in enumerate(slots_data):
        row = i // 2
        col = i % 2
        
        # Create slot frame
        slot_frame = tk.Frame(slots_frame, bg="#34495e", relief=tk.RAISED, bd=1)
        slot_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        # Configure column weights
        slots_frame.grid_columnconfigure(col, weight=1)
        
        # Icon label
        icon_label = tk.Label(slot_frame, text=icon, font=("Arial", 14), bg="#34495e", fg="white")
        icon_label.grid(row=0, column=0, padx=5)
        
        # Text frame
        text_frame = tk.Frame(slot_frame, bg="#34495e")
        text_frame.grid(row=0, column=1, padx=5, sticky="w")
        
        # Name label
        name_label = tk.Label(text_frame, text=name, font=("Arial", 8, "bold"), bg="#34495e", fg="lightgray")
        name_label.pack(anchor="w")
        
        # Item label
        item_label = tk.Label(text_frame, text="(Empty)", font=("Arial", 8), bg="#34495e", fg="gray")
        item_label.pack(anchor="w")
        
        # Add context menu to slot frame
        context_handler = create_context_menu(slot_type, name)
        slot_frame.bind("<Button-3>", context_handler)
        slot_frame.bind("<ButtonRelease-3>", context_handler)
        
        # Also bind to child widgets
        for child in [icon_label, text_frame, name_label, item_label]:
            child.bind("<Button-3>", context_handler)
            child.bind("<ButtonRelease-3>", context_handler)
    
    print("Equipment slot simulation opened. Try right-clicking on different slots.")
    print("Check console for debug output.")
    print("Close the window when done testing.")
    
    root.mainloop()

def test_demo_integration():
    """Test the actual demo right-click functionality."""
    print("\n=== Testing Demo Integration ===")
    
    try:
        # Import demo modules
        from demo import SimpleGameDemo
        
        print("Creating demo instance...")
        demo = SimpleGameDemo()
        
        print("Demo created successfully. Starting demo...")
        print("Try right-clicking on equipment slots in the Character Stats tab.")
        print("Look for any error messages in the console.")
        
        demo.run()
        
    except Exception as e:
        print(f"Error running demo: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("Right-Click Functionality Test")
    print("=" * 40)
    
    test_choice = input("Choose test:\n1. Basic right-click\n2. Equipment slot simulation\n3. Demo integration\nChoice (1-3): ").strip()
    
    if test_choice == "1":
        test_basic_right_click()
    elif test_choice == "2":
        test_equipment_slot_simulation()
    elif test_choice == "3":
        test_demo_integration()
    else:
        print("Invalid choice. Running basic test...")
        test_basic_right_click()
