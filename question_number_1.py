# Crop Your Image Application -> Upload, crop, rotate, flip and save pictures

import tkinter as tk
import ttkbootstrap as ttk # bootstrap for better UI display
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class CropYourImage:
    def __init__(self, root):
        self.root = root
        self.root.title("Crop Your Image")
        self.root.geometry("1000x650")
        self.root.configure(bg="#F0F2F5")

        # Initialization for the image and canvas objects
        self.original_picture = None
        self.background_orginal = None
        self.resized_picture = None #displays resized image 
        self.cropped_pil_pic = None # PIL image of the cropped image
        self.current_resized_cropped = None
        
        # Object IDs for original picture, cropped rectangle and pictures
        self.canvas_pic_id = None
        self.rectangle_pic_id = None
        self.cropped_pic_id = None

        # Coordinates of cropped rectangle borders
        self.crop_start_x = 0
        self.crop_start_y = 0

        # Display dimensions and scales of the picture
        self.scale_ratio = 0
        self.display_pic_x = 0
        self.display_pic_y = 0
        self.display_pic_width = 0
        self.display_pic_height = 0

        
        self.reference_picture = [] # Keep references of pictures to remove garbage collection
        self.app_background() # Load background picture of the application
        self.app_gui() # Sets up GUI components for the app

    # Load background of the application
    def app_background(self):
        try:
            self.background_orginal = Image.open("background.jpeg")
        except Exception:
            self.background_orginal = None

    # Create all GUI components 
    def app_gui(self):
        # Labels of application
        label_of_app = ttk.Label(
            self.root,
            text="Welcome to Crop Your Image App",
            font=("Helvetica", 18, "bold"),
            anchor="center",
            bootstyle="primary",
            background="#F0F2F5"
        )
        label_of_app.pack(pady=(15, 0))

        # Main frame containing all components of application
        main_frame = tk.Frame(self.root, bg="#F0F2F5")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(15, 0))

        #Frame to show the image displayed area
        canvas_frame = tk.Frame(main_frame, bg="white", bd=2, relief=tk.RIDGE)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Frame to display orginal and cropped picture
        self.canvas = tk.Canvas(canvas_frame, highlightthickness=0, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame to display buttons and slider
        control_frame = tk.Frame(self.root, bg="#f0f0f0")
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        #Button to choose and upload an image file
        upload_pic_btn = ttk.Button(
            control_frame,
            text=" ⬆️Upload Image",
            bootstyle="success-outline",
            width=18,
            command=self.upload_picture
        )
        upload_pic_btn.pack(side=tk.LEFT, padx=15, pady=10)
       
       # Button to download cropped picture
        self.download_button = ttk.Button(
            control_frame,
            text="⬇️Download",
            bootstyle="success-outline",
            width=16,
            command=self.download_cropped_picture
        )
        self.download_button.pack(side=tk.LEFT, padx=15, pady=10)

        # Button to clear cropped picture
        clear_crop_button = ttk.Button(
            control_frame,
            text="🧹 Clear Crop",
            bootstyle="danger-outline",
            width=16,
            command=self.clear_cropped_area
        )
        clear_crop_button.pack(side=tk.LEFT, padx=15, pady=10)

        # Buttons to rotate cropped picture
        rotate_left_button = ttk.Button(
            control_frame, text="⟲ Rotate Left", bootstyle="info-outline", width=14, command=self.rotate_picture_left
        )
        rotate_left_button.pack(side=tk.LEFT, padx=5)

        rotate_right_button = ttk.Button(
            control_frame, text="⟳ Rotate Right", bootstyle="info-outline", width=14, command=self.rotate_picture_right
        )
        rotate_right_button.pack(side=tk.LEFT, padx=5)

        # Buttons to flip cropped picture
        flip_button = ttk.Button(control_frame, text="Flip H", bootstyle="info-outline", width=8, command=self.flip_picture)
        flip_button.pack(side=tk.LEFT, padx=5)

        # Show label for the Slider and display resized value
        self.resize_label_value = tk.StringVar(value="Resize Cropped Image:")
        resize_label = ttk.Label(control_frame, textvariable=self.resize_label_value, font=('Helvetica', 10))
        resize_label.pack(side=tk.LEFT, padx=(15, 5), pady=10)

        # Show label for displaying current slider value
        self.slider_value = ttk.Label(control_frame, font=('Helvetica', 10))
        self.slider_value.pack(side=tk.LEFT, padx=(0, 10), pady=10)

        # Resize slider to change the size of the cropped image
        self.resize_slider = ttk.Scale(
            control_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            length=200,
            bootstyle="success",
            command=self.move_slider
        )
        self.resize_slider.set(100)
        self.resize_slider.pack(side=tk.LEFT, padx=(5, 15), pady=10)
        self.resize_slider.bind("<ButtonRelease-1>", self.slider_warning)

        # Bindings
        self.root.bind("<Configure>", self.update_displayed_picture) # Bind window resize to update picture display
        self.canvas.bind("<ButtonPress-1>", self.start_crop) # Starts cropping while pressing mouse
        self.canvas.bind("<B1-Motion>", self.update_crop) # Updates cropped rectangle when dragging
        self.canvas.bind("<ButtonRelease-1>", self.end_crop) # Finalize crop while releasing mouse

    # To upload the picture and display in the main screen
    def upload_picture(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if path:
            self.original_picture = Image.open(path)
            self.reset_after_new_upload()
            self.update_displayed_picture()

    # Reset screen when a new picture is uploaded
    def reset_after_new_upload(self):
        """Reset state variables after loading a new image."""
        self.cropped_pil_pic = None
        self.current_resized_cropped = None
        self.resize_slider.set(100)
        self.resize_label_value.set("Resize Cropped Image:")
        self.download_button.config(state=tk.DISABLED)
        self.canvas.delete("all")

    # Display background, resize the image and main image on the screen
    def update_displayed_picture(self, event=None):
        """Resize and display the original image and background on canvas."""
        self.canvas.delete("all")

        # Display background picture
        if self.background_orginal:
            cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
            bg_resized = self.background_orginal.resize((cw, ch), Image.Resampling.LANCZOS)
            self.canvas.bg_img = ImageTk.PhotoImage(bg_resized)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas.bg_img)

        # Display the uploaded original picture
        if self.original_picture:
            max_w = self.canvas.winfo_width() // 2 - 20
            max_h = self.canvas.winfo_height() - 40

            self.resized_picture = self.original_picture.copy()
            self.resized_picture.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
            self.scale_ratio = self.original_picture.width / self.resized_picture.width

            img_tk = ImageTk.PhotoImage(self.resized_picture)
            self.canvas.image = img_tk 
            self.canvas_pic_id = self.canvas.create_image(10, 10, anchor=tk.NW, image=img_tk)

            # Saves displayed image position and size for cropping
            self.display_pic_x, self.display_pic_y = 10, 10
            self.display_pic_width, self.display_pic_height = self.resized_picture.size

    # Displays the crop rectangle when mouse is pressed on the picture
    def start_crop(self, event):
        self.crop_start_x = event.x
        self.crop_start_y = event.y 
        # Removes previous cropped rectangle if exists
        if self.rectangle_pic_id:
            self.canvas.delete(self.rectangle_pic_id)
        # Creates new cropped rectangle starting at the press position
        self.rectangle_pic_id = self.canvas.create_rectangle(
            self.crop_start_x, self.crop_start_y, self.crop_start_x, self.crop_start_y,
            outline='#FF4C4C', width=2, dash=(4, 2)
        )

    # Updates cropped size dynamically as mouse dragged
    def update_crop(self, event):
        """Update crop rectangle during mouse drag, constrained inside image boundaries."""
        if self.rectangle_pic_id:
            x = min(max(event.x, self.display_pic_x), self.display_pic_x + self.display_pic_width)
            y = min(max(event.y, self.display_pic_y), self.display_pic_y + self.display_pic_height)
            self.canvas.coords(self.rectangle_pic_id, self.crop_start_x, self.crop_start_y, x, y)

    # Finalize cropping on mouse release, crop original picture after valid selection
    def end_crop(self, event):
        if not self.rectangle_pic_id:
            return
         # Gives coordinates of displayed picture area
        x = min(max(event.x, self.display_pic_x), self.display_pic_x + self.display_pic_width)
        y = min(max(event.y, self.display_pic_y), self.display_pic_y + self.display_pic_height)

        # Update rectangle coordinates on canvas
        self.canvas.coords(self.rectangle_pic_id, self.crop_start_x, self.crop_start_y, x, y)
        x0, y0, x1, y1 = self.canvas.coords(self.rectangle_pic_id)

        # Calculates cropped area relative to displayed picture
        cropped_x0 = max(x0 - self.display_pic_x, 0)
        cropped_y0 = max(y0 - self.display_pic_y, 0)
        cropped_x1 = max(x1 - self.display_pic_x, 0)
        cropped_y1 = max(y1 - self.display_pic_y, 0)

        # Using scale ratio, scales cropped coordinate back to original picture coordinates 
        x0_org = max(0, min(int(cropped_x0 * self.scale_ratio), self.original_picture.width))
        y0_org = max(0, min(int(cropped_y0 * self.scale_ratio), self.original_picture.height))
        x1_org = max(0, min(int(cropped_x1 * self.scale_ratio), self.original_picture.width))
        y1_org = max(0, min(int(cropped_y1 * self.scale_ratio), self.original_picture.height))

        # Crops the picture only if dragged area is valid
        if x1_org > x0_org and y1_org > y0_org:
            self.cropped_pil_pic = self.original_picture.crop((x0_org, y0_org, x1_org, y1_org))
            self.resize_slider.set(100)
            self.resize_label_value.set("Resize Cropped Image:")
            self.display_cropped_picture(self.cropped_pil_pic)
            self.download_button.config(state=tk.NORMAL)

        # Removes cropped rectangle
        self.canvas.delete(self.rectangle_pic_id)
        self.rectangle_pic_id = None

    # Displays the cropped pciture resized from slider
    def display_cropped_picture(self, cropped_img):
        if self.cropped_pic_id:
            self.canvas.delete(self.cropped_pic_id)

        padding = 10
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Put maximum size of right half of the screen
        max_width = (canvas_width // 2) - 2 * padding
        max_height = canvas_height - 2 * padding

        scale_percent = max(self.resize_slider.get(), 0)  # Range 0-100

        # Calculate resized size from slider scale
        w = max(1, int(cropped_img.width * scale_percent / 100))
        h = max(1, int(cropped_img.height * scale_percent / 100))

        # Fits cropped picture to maximum available size
        w = min(w, max_width)
        h = min(h, max_height)

        resized_crop = cropped_img.resize((w, h), Image.Resampling.LANCZOS)
        self.current_resized_cropped = resized_crop

        img_tk = ImageTk.PhotoImage(resized_crop)

        # Prevents garbage collection of pictures
        self.reference_picture.clear()
        self.reference_picture.append(img_tk)
        
        # Fit picture on right half
        x = canvas_width // 2 + padding
        y = padding
        self.cropped_pic_id = self.canvas.create_image(x, y, anchor=tk.NW, image=img_tk)

    # Move slider to resize the cropped picture
    def move_slider(self, val):
        percent = int(float(val))
        self.slider_value.config(text=f"{percent}%")
        if self.cropped_pil_pic:
            # Delay to avoid flooding updates while dragging
            self.root.after(50, lambda: self.display_cropped_picture(self.cropped_pil_pic))

    # Shows warning when slider is released before cropping picture
    def slider_warning(self, event):
        if not self.cropped_pil_pic:
            messagebox.showwarning("Resize Image", "No cropped image to resize!")
            self.resize_slider.set(100)

     # Saves the recent resized cropped picture
    def download_cropped_picture(self):
        if not self.current_resized_cropped:
            messagebox.showwarning("Save Image", "No image to save!")
            return
        # Opens file dialog to choose location and file type to save cropped picture
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg;*.jpeg")]
        )
        if path:
            try:
                self.current_resized_cropped.save(path)
                messagebox.showinfo("Save Image", f"Image saved to:\n{path}")
            except Exception as e:
                messagebox.showerror("Save Image", f"Failed to save:\n{str(e)}")

    #  Clear the cropped picture and reset the frame displaying only original picture
    def clear_cropped_area(self):
        if not self.cropped_pil_pic:
            messagebox.showwarning("Clear Crop", "No image to clear!")
            return
        # Reset cropping related state variables
        self.crop_start_x = self.crop_start_y = 0
        self.rectangle_pic_id = None
        self.cropped_pil_pic = None
        self.current_resized_cropped = None
        # Clear all canvas cropped image, rectangle
        self.canvas.delete("all")
        # Redraw the original picture and background
        self.update_displayed_picture()
    
    # Flip the cropped image and creates mirror effect
    def flip_picture(self):
        if self.cropped_pil_pic:
            self.cropped_pil_pic = self.cropped_pil_pic.transpose(Image.FLIP_LEFT_RIGHT)
            self.display_cropped_picture(self.cropped_pil_pic)

    # Rotates the cropped picture 90 degrees counter-clockwise
    def rotate_picture_left(self):
        if self.cropped_pil_pic:
            self.cropped_pil_pic = self.cropped_pil_pic.rotate(90, expand=True)
            self.display_cropped_picture(self.cropped_pil_pic)

    
    # Rotate the cropped image 90 degrees clockwise
    def rotate_picture_right(self):
        if self.cropped_pil_pic:
            self.cropped_pil_pic = self.cropped_pil_pic.rotate(-90, expand=True)
            self.display_cropped_picture(self.cropped_pil_pic)

# Initialize the application window and run Crop Your Image app
if __name__ == "__main__":
    app_root = ttk.Window(themename="minty")
    CropYourImage(app_root)
    app_root.mainloop()