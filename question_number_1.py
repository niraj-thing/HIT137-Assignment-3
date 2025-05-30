import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class ImageCropperApp:
    """
    A Tkinter-based Image Cropper Application with upload, crop, resize, and save features.
    Implements encapsulation for cleaner code organization.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Image Cropper with Resize and Save")
        self.root.geometry("1000x650")
        self.root.configure(bg="#F0F2F5")

        # Initialize image and canvas variables
        self.original_img = None
        self.bg_original = None
        self.resized_img = None
        self.cropped_pil = None
        self.current_resized_cropped = None

        self.canvas_img_id = None
        self.rect_id = None
        self.cropped_img_id = None

        self.start_x = 0
        self.start_y = 0

        self.scale_ratio = 0
        self.img_display_x = 0
        self.img_display_y = 0
        self.img_display_width = 0
        self.img_display_height = 0

        self.image_refs = []  # Keep image references alive

        self._load_background()
        self._setup_gui()

    def _load_background(self):
        """Load background image if available."""
        try:
            self.bg_original = Image.open("background.jpeg")
        except Exception:
            self.bg_original = None

    def _setup_gui(self):
        """Create and layout all GUI components."""
        # Welcome label at the top
        welcome_label = ttk.Label(
            self.root,
            text="Welcome to Image Cropper App",
            font=("Helvetica", 18, "bold"),
            anchor="center",
            bootstyle="primary",
            background="#F0F2F5"
        )
        welcome_label.pack(pady=(15, 0))

        main_frame = tk.Frame(self.root, bg="#F0F2F5")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(15, 0))

        # Canvas container
        canvas_frame = tk.Frame(main_frame, bg="white", bd=2, relief=tk.RIDGE)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, highlightthickness=0, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Control buttons and slider
        control_frame = tk.Frame(self.root, bg="#f0f0f0")
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        upload_btn = ttk.Button(
            control_frame,
            text=" ⬆️Upload Image",
            bootstyle="success-outline",
            width=18,
            command=self.image_uploader
        )
        upload_btn.pack(side=tk.LEFT, padx=15, pady=10)

        self.save_button = ttk.Button(
            control_frame,
            text="⬇️Download",
            bootstyle="success-outline",
            width=16,
            command=self.save_image
        )
        self.save_button.pack(side=tk.LEFT, padx=15, pady=10)

        clear_crop_btn = ttk.Button(
            control_frame,
            text="🧹 Clear Crop",
            bootstyle="danger-outline",
            width=16,
            command=self.clear_crop_area
        )
        clear_crop_btn.pack(side=tk.LEFT, padx=15, pady=10)

        rotate_left_btn = ttk.Button(
            control_frame, text="⟲ Rotate Left", bootstyle="info-outline", width=14, command=self.rotate_left
        )
        rotate_left_btn.pack(side=tk.LEFT, padx=5)

        rotate_right_btn = ttk.Button(
            control_frame, text="⟳ Rotate Right", bootstyle="info-outline", width=14, command=self.rotate_right
        )
        rotate_right_btn.pack(side=tk.LEFT, padx=5)

        

        flip_h_btn = ttk.Button(control_frame, text="Flip H", bootstyle="info-outline", width=8, command=self.flip_horizontal)
        flip_h_btn.pack(side=tk.LEFT, padx=5)

        # Slider label and value display
        self.resize_label_var = tk.StringVar(value="Resize Cropped Image:")
        resize_label = ttk.Label(control_frame, textvariable=self.resize_label_var, font=('Helvetica', 10))
        resize_label.pack(side=tk.LEFT, padx=(15, 5), pady=10)

        self.slider_value = ttk.Label(control_frame, font=('Helvetica', 10))
        self.slider_value.pack(side=tk.LEFT, padx=(0, 10), pady=10)

        self.resize_slider = ttk.Scale(
            control_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            length=200,
            bootstyle="success",
            command=self.on_resize_slider
        )
        self.resize_slider.set(100)
        self.resize_slider.pack(side=tk.LEFT, padx=(5, 15), pady=10)
        self.resize_slider.bind("<ButtonRelease-1>", self.on_slider_release)

        # Bindings
        self.root.bind("<Configure>", self.update_displayed_image)
        self.canvas.bind("<ButtonPress-1>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.update_crop)
        self.canvas.bind("<ButtonRelease-1>", self.end_crop)

    def image_uploader(self):
        """Open file dialog and load an image."""
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if path:
            self.original_img = Image.open(path)
            self.reset_after_new_image()
            self.update_displayed_image()

    def reset_after_new_image(self):
        """Reset state variables after loading a new image."""
        self.cropped_pil = None
        self.current_resized_cropped = None
        self.resize_slider.set(100)
        self.resize_label_var.set("Resize Cropped Image:")
        self.save_button.config(state=tk.DISABLED)
        self.canvas.delete("all")

    def update_displayed_image(self, event=None):
        """Resize and display the original image and background on canvas."""
        self.canvas.delete("all")

        if self.bg_original:
            cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
            bg_resized = self.bg_original.resize((cw, ch), Image.Resampling.LANCZOS)
            self.canvas.bg_img = ImageTk.PhotoImage(bg_resized)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas.bg_img)

        if self.original_img:
            max_w = self.canvas.winfo_width() // 2 - 20
            max_h = self.canvas.winfo_height() - 40

            self.resized_img = self.original_img.copy()
            self.resized_img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
            self.scale_ratio = self.original_img.width / self.resized_img.width

            img_tk = ImageTk.PhotoImage(self.resized_img)
            self.canvas.image = img_tk  # Keep reference
            self.canvas_img_id = self.canvas.create_image(10, 10, anchor=tk.NW, image=img_tk)

            # Store displayed image position and size for cropping bounds
            self.img_display_x, self.img_display_y = 10, 10
            self.img_display_width, self.img_display_height = self.resized_img.size

    def start_crop(self, event):
        """Start drawing crop rectangle on mouse press, constrained inside image."""
        self.start_x = event.x
        self.start_y = event.y
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='#FF4C4C', width=2, dash=(4, 2)
        )

    def update_crop(self, event):
        """Update crop rectangle during mouse drag, constrained inside image boundaries."""
        if self.rect_id:
            x = min(max(event.x, self.img_display_x), self.img_display_x + self.img_display_width)
            y = min(max(event.y, self.img_display_y), self.img_display_y + self.img_display_height)
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, x, y)

    def end_crop(self, event):
        """Finalize crop rectangle on mouse release and crop the original image if valid."""
        if not self.rect_id:
            return

        # Clamp coordinates inside image area
        x = min(max(event.x, self.img_display_x), self.img_display_x + self.img_display_width)
        y = min(max(event.y, self.img_display_y), self.img_display_y + self.img_display_height)

        self.canvas.coords(self.rect_id, self.start_x, self.start_y, x, y)
        x0, y0, x1, y1 = self.canvas.coords(self.rect_id)

        crop_x0 = max(x0 - self.img_display_x, 0)
        crop_y0 = max(y0 - self.img_display_y, 0)
        crop_x1 = max(x1 - self.img_display_x, 0)
        crop_y1 = max(y1 - self.img_display_y, 0)

        ox0 = max(0, min(int(crop_x0 * self.scale_ratio), self.original_img.width))
        oy0 = max(0, min(int(crop_y0 * self.scale_ratio), self.original_img.height))
        ox1 = max(0, min(int(crop_x1 * self.scale_ratio), self.original_img.width))
        oy1 = max(0, min(int(crop_y1 * self.scale_ratio), self.original_img.height))

        if ox1 > ox0 and oy1 > oy0:
            self.cropped_pil = self.original_img.crop((ox0, oy0, ox1, oy1))
            self.resize_slider.set(100)
            self.resize_label_var.set("Resize Cropped Image:")
            self.show_cropped_image(self.cropped_pil)
            self.save_button.config(state=tk.NORMAL)

        self.canvas.delete(self.rect_id)
        self.rect_id = None

    def show_cropped_image(self, cropped_img):
        """
        Display the cropped image resized according to the slider value,
        positioned on the right half of the canvas with padding.
        """
        if self.cropped_img_id:
            self.canvas.delete(self.cropped_img_id)

        padding = 10
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        max_width = (canvas_width // 2) - 2 * padding
        max_height = canvas_height - 2 * padding

        scale_percent = max(self.resize_slider.get(), 0)  # Range 0-100

        w = max(1, int(cropped_img.width * scale_percent / 100))
        h = max(1, int(cropped_img.height * scale_percent / 100))

        # Ensure cropped image fits max available space
        w = min(w, max_width)
        h = min(h, max_height)

        resized_crop = cropped_img.resize((w, h), Image.Resampling.LANCZOS)
        self.current_resized_cropped = resized_crop

        img_tk = ImageTk.PhotoImage(resized_crop)

        # Prevent garbage collection of image
        self.image_refs.clear()
        self.image_refs.append(img_tk)

        x = canvas_width // 2 + padding
        y = padding
        self.cropped_img_id = self.canvas.create_image(x, y, anchor=tk.NW, image=img_tk)

    def on_resize_slider(self, val):
        """Update display of slider value and resized cropped image on slider move."""
        percent = int(float(val))
        self.slider_value.config(text=f"{percent}%")
        if self.cropped_pil:
            # Delay to avoid flooding updates while dragging
            self.root.after(50, lambda: self.show_cropped_image(self.cropped_pil))

    def on_slider_release(self, event):
        """Warn user if no cropped image when releasing slider."""
        if not self.cropped_pil:
            messagebox.showwarning("Resize Image", "No cropped image to resize!")
            self.resize_slider.set(100)

    def save_image(self):
        """Save the currently resized cropped image to a user-specified file."""
        if not self.current_resized_cropped:
            messagebox.showwarning("Save Image", "No image to save!")
            return
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

    def clear_crop_area(self):
        """Clear the cropped image and reset the canvas display."""
        if not self.cropped_pil:
            messagebox.showwarning("Clear Crop", "No image to clear!")
            return

        self.start_x = self.start_y = 0
        self.rect_id = None
        self.cropped_pil = None
        self.current_resized_cropped = None
        self.canvas.delete("all")
        self.update_displayed_image()
    
    def flip_horizontal(self):
        if self.cropped_pil:
            self.cropped_pil = self.cropped_pil.transpose(Image.FLIP_LEFT_RIGHT)
            self.show_cropped_image(self.cropped_pil)

    def rotate_left(self):
        """ Rotate the cropped image 90 degrees counter-clockwise."""
        if self.cropped_pil:
            self.cropped_pil = self.cropped_pil.rotate(90, expand=True)
            self.show_cropped_image(self.cropped_pil)

    def rotate_right(self):
        """Rotate the cropped image 90 degrees clockwise."""
        if self.cropped_pil:
            self.cropped_pil = self.cropped_pil.rotate(-90, expand=True)
            self.show_cropped_image(self.cropped_pil)

if __name__ == "__main__":
    app_root = ttk.Window(themename="minty")
    ImageCropperApp(app_root)
    app_root.mainloop()