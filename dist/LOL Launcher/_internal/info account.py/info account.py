import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import Riot_API
from PIL import Image, ImageTk, ImageDraw
import requests
import pyperclip
import io
import os
from datetime import datetime

# ============================================================================
# CONFIGURATION - Palette Tokyo Night
# ============================================================================
class Theme:
    """Centralized theme configuration"""
    BG_DARK = "#0f111a"
    BG = "#1a1b26"
    SECONDARY = "#1f2335"
    ACCENT = "#bb9af7"
    ACCENT_2 = "#7aa2f7"
    ACCENT_3 = "#73daca"
    TEXT = "#c0caf5"
    TEXT_MUTED = "#565f89"
    HIGHLIGHT = "#414868"
    SUCCESS = "#9ece6a"
    INFO = "#7dcfff"
    WARNING = "#e0af68"
    ERROR = "#f7768e"
    BUTTON = "#4d5579"
    BUTTON_HOVER = "#5e68a0"
    COPY_BUTTON = "#2c3e50"
    COPY_HOVER = "#34495e"
    BORDER = "#2d3651"


# ============================================================================
# EXTERNAL LINKS CONFIGURATION
# ============================================================================
class ExternalLinks:
    """Centralized external links configuration"""
    
    @staticmethod
    def get_all():
        """Get all external links configuration"""
        return [
            {
                "id": "opgg",
                "name": "OP.GG",
                "short_desc": "Statistiche dettagliate",
                "long_desc": "Statistiche complete, cronologia partite, classifiche",
                "icon": "📊",
                "color": Theme.ACCENT
            },
            {
                "id": "ugg",
                "name": "U.GG",
                "short_desc": "Guide e builds",
                "long_desc": "Build ottimali, guide campioni, meta analysis",
                "icon": "🎯",
                "color": Theme.INFO
            },
            {
                "id": "lolgraph",
                "name": "League of Graphs",
                "short_desc": "Analisi approfondite",
                "long_desc": "Analisi approfondite, confronti, trend",
                "icon": "📈",
                "color": Theme.SUCCESS
            },
            {
                "id": "porofessor",
                "name": "Porofessor",
                "short_desc": "Live game analysis",
                "long_desc": "Analisi live game, suggerimenti in tempo reale",
                "icon": "⚡",
                "color": Theme.WARNING
            }
        ]
    
    @staticmethod
    def get_by_id(link_id):
        """Get specific link by ID"""
        return next((link for link in ExternalLinks.get_all() if link["id"] == link_id), None)


# ============================================================================
# UTILITY CLASSES
# ============================================================================
class HoverEffect:
    """Reusable hover effect manager"""
    @staticmethod
    def apply(widget, bg_normal, bg_hover, fg_normal=None, fg_hover=None, 
              children_recursive=False):
        """Apply hover effect to widget and optionally its children"""
        def on_enter(event):
            widget.config(bg=bg_hover)
            if fg_hover and hasattr(widget, 'config'):
                try:
                    widget.config(fg=fg_hover)
                except:
                    pass
            if children_recursive:
                HoverEffect._update_children_bg(widget, bg_hover)
        
        def on_leave(event):
            widget.config(bg=bg_normal)
            if fg_normal and hasattr(widget, 'config'):
                try:
                    widget.config(fg=fg_normal)
                except:
                    pass
            if children_recursive:
                HoverEffect._update_children_bg(widget, bg_normal)
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    @staticmethod
    def _update_children_bg(widget, bg_color):
        """Helper to update background of child widgets"""
        for child in widget.winfo_children():
            if isinstance(child, (tk.Label, tk.Frame)):
                try:
                    child.config(bg=bg_color)
                except:
                    pass


class ScrollableFrame:
    """Reusable scrollable frame component"""
    def __init__(self, parent, bg=Theme.BG):
        self.canvas = tk.Canvas(parent, bg=bg, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(parent, orient="vertical", 
                                      command=self.canvas.yview)
        self.frame = tk.Frame(self.canvas, bg=bg)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.canvas_window = self.canvas.create_window((0, 0), 
                                                       window=self.frame, 
                                                       anchor="nw")
        
        # Bind configuration
        self.frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Setup mousewheel
        self._setup_mousewheel()
    
    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _setup_mousewheel(self):
        """Configure mousewheel scrolling"""
        def on_mousewheel(event):
            try:
                if self.canvas.winfo_exists():
                    self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass
        
        def on_enter(event):
            self.canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        def on_leave(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        def cleanup(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        self.canvas.bind("<Enter>", on_enter)
        self.canvas.bind("<Leave>", on_leave)
        self.canvas.bind("<Destroy>", cleanup)
        
        if self.scrollbar:
            self.scrollbar.bind("<Enter>", on_enter)
            self.scrollbar.bind("<Leave>", on_leave)


class WidgetFactory:
    """Factory for creating styled widgets"""
    
    @staticmethod
    def create_label(parent, text="", font=("Segoe UI", 10), 
                    fg=Theme.TEXT, bg=Theme.BG, **kwargs):
        """Create styled label"""
        return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, **kwargs)
    
    @staticmethod
    def create_frame(parent, bg=Theme.BG, **kwargs):
        """Create styled frame"""
        return tk.Frame(parent, bg=bg, **kwargs)
    
    @staticmethod
    def create_button(parent, text, command, style="primary", **kwargs):
        """Create modern styled button"""
        styles = {
            "primary": {"bg": Theme.ACCENT, "hover": Theme.ACCENT_2, "fg": "white"},
            "secondary": {"bg": Theme.BUTTON, "hover": Theme.BUTTON_HOVER, "fg": Theme.TEXT},
            "success": {"bg": Theme.SUCCESS, "hover": "#7fb069", "fg": "white"},
            "info": {"bg": Theme.INFO, "hover": "#5eb8e6", "fg": "white"}
        }
        
        style_config = styles.get(style, styles["primary"])
        
        btn = tk.Button(parent, text=text, command=command,
                       bg=style_config["bg"], fg=style_config["fg"],
                       activebackground=style_config["hover"],
                       font=("Segoe UI", 10, "bold"), bd=0, 
                       padx=20, pady=10, cursor="hand2", relief="flat", **kwargs)
        
        HoverEffect.apply(btn, style_config["bg"], style_config["hover"])
        return btn
    
    @staticmethod
    def create_copy_button(parent, value, root):
        """Create copy button with hover effect"""
        btn = tk.Button(parent, text="📋", bg=Theme.COPY_BUTTON, fg="white",
                       activebackground=Theme.COPY_HOVER, bd=0, width=3, height=1,
                       cursor="hand2", font=("Segoe UI", 9),
                       command=lambda: copy_to_clipboard(value, root))
        
        def on_enter(e):
            btn.config(background=Theme.COPY_HOVER, text="✓")
        
        def on_leave(e):
            btn.config(background=Theme.COPY_BUTTON, text="📋")
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn


# ============================================================================
# CLIPBOARD & NOTIFICATIONS
# ============================================================================
def copy_to_clipboard(text, parent):
    """Copy text to clipboard and show notification"""
    try:
        pyperclip.copy(str(text))
        show_toast_notification(parent, "Testo copiato negli appunti!", 
                              fg_color=Theme.SUCCESS)
    except Exception as e:
        show_toast_notification(parent, "Errore durante la copia", 
                              fg_color=Theme.ERROR)


def show_toast_notification(parent, message, duration=2000, 
                           fg_color=Theme.TEXT, bg_color=Theme.BG_DARK):
    """Show temporary toast notification"""
    if not parent or not parent.winfo_exists():
        return
    
    toast = tk.Toplevel(parent)
    toast.overrideredirect(True)
    toast.configure(bg=bg_color)
    toast.attributes('-topmost', True)
    
    # Position
    toast.update_idletasks()
    x = toast.winfo_screenwidth() - 320
    y = toast.winfo_screenheight() - 120
    toast.geometry(f"300x60+{x}+{y}")
    
    # Content
    border_frame = WidgetFactory.create_frame(toast, bg=Theme.BORDER, padx=1, pady=1)
    border_frame.pack(fill="both", expand=True)
    
    content_frame = WidgetFactory.create_frame(border_frame, bg=bg_color)
    content_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Icon
    icon_text = {"success": "✓", "warning": "⚠", "error": "✗"}.get(
        "success" if fg_color == Theme.SUCCESS else 
        "warning" if fg_color == Theme.WARNING else 
        "error" if fg_color == Theme.ERROR else "info", "ℹ")
    
    WidgetFactory.create_label(content_frame, text=icon_text, 
                              font=("Segoe UI", 14, "bold"),
                              fg=fg_color, bg=bg_color).pack(side="left", padx=(0, 10))
    
    WidgetFactory.create_label(content_frame, text=message, 
                              font=("Segoe UI", 10),
                              fg=Theme.TEXT, bg=bg_color,
                              wraplength=250).pack(side="left", fill="both", expand=True)
    
    # Animation
    toast._destroyed = False
    toast.attributes('-alpha', 0.0)
    _animate_fade(toast, 0.0, 1.0, 10, True)
    
    # Auto close
    toast.after(duration - 300, lambda: _animate_fade(toast, 1.0, 0.0, 10, False))
    toast.after(duration, lambda: _safe_destroy(toast))


def _animate_fade(window, alpha, target, steps, fade_in):
    """Animate window fade in/out"""
    if getattr(window, '_destroyed', True) or not window.winfo_exists():
        return
    
    if (fade_in and alpha < target) or (not fade_in and alpha > target):
        delta = (target / steps) if fade_in else (-1.0 / steps)
        alpha += delta
        try:
            window.attributes('-alpha', alpha)
            window.after(20, lambda: _animate_fade(window, alpha, target, steps, fade_in))
        except tk.TclError:
            pass


def _safe_destroy(widget):
    """Safely destroy widget"""
    if not getattr(widget, '_destroyed', True) and widget.winfo_exists():
        widget._destroyed = True
        widget.destroy()


# ============================================================================
# DATA DRAGON & PROFILE LOADING
# ============================================================================
def get_latest_ddragon_version():
    """Get latest Data Dragon version"""
    try:
        response = requests.get("https://ddragon.leagueoflegends.com/api/versions.json", 
                              timeout=5)
        if response.status_code == 200:
            return response.json()[0]
    except Exception as e:
        print(f"Error fetching version: {e}")
    return "latest"


def load_profile_icon(icon_id, size=(120, 120), ddragon_version="latest"):
    """Load profile icon with circular mask"""
    try:
        icon_url = f"http://ddragon.leagueoflegends.com/cdn/{ddragon_version}/img/profileicon/{icon_id}.png"
        response = requests.get(icon_url, stream=True, timeout=10)
        
        if response.status_code == 200:
            img = Image.open(io.BytesIO(response.content))
            img = img.resize(size, Image.Resampling.LANCZOS)
            
            # Create circular mask
            mask = Image.new('L', size, 0)
            ImageDraw.Draw(mask).ellipse((0, 0) + size, fill=255)
            img.putalpha(mask)
            
            return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error loading icon: {e}")
    
    return _create_default_icon(size)


def _create_default_icon(size=(120, 120)):
    """Create default icon placeholder"""
    img = Image.new('RGBA', size, Theme.SECONDARY)
    draw = ImageDraw.Draw(img)
    
    center = (size[0]//2, size[1]//2)
    radius = min(size)//2 - 10
    
    draw.ellipse([center[0]-radius, center[1]-radius,
                  center[0]+radius, center[1]+radius],
                 fill=Theme.ACCENT, outline=Theme.ACCENT_2, width=3)
    
    return ImageTk.PhotoImage(img)


def get_riot_id(account_info):
    """Build Riot ID from account info"""
    if 'gameName' in account_info and 'tagLine' in account_info:
        return f"{account_info['gameName']}#{account_info['tagLine']}"
    return None


def open_profile(riot_id, platform):
    """Open summoner profile on external sites"""
    if not riot_id or '#' not in riot_id:
        return
    
    try:
        game_name, tag_line = riot_id.split('#')
        urls = {
            "opgg": f"https://www.op.gg/summoners/euw/{game_name}-{tag_line}",
            "lolgraph": f"https://www.leagueofgraphs.com/summoner/euw/{game_name}-{tag_line}",
            "ugg": f"https://u.gg/lol/profile/euw1/{game_name}-{tag_line}/overview",
            "porofessor": f"https://porofessor.gg/live/euw/{game_name}-{tag_line}"
        }
        
        if platform in urls:
            webbrowser.open(urls[platform])
    except Exception as e:
        print(f"Error opening profile: {e}")


# ============================================================================
# CARD COMPONENTS
# ============================================================================
def create_clickable_label(parent, text, font, fg, bg, click_action=None, 
                          hover_color=None):
    """Create clickable label with optional hover effect"""
    label = WidgetFactory.create_label(parent, text=text, font=font, fg=fg, bg=bg,
                                      cursor="hand2" if click_action else "arrow")
    
    if click_action:
        label.bind("<Button-1>", lambda e: click_action())
        if hover_color:
            HoverEffect.apply(label, bg, bg, fg, hover_color)
    
    return label


def create_stat_card(parent, title, value, color, icon, clickable=False, 
                    click_action=None):
    """Create statistic card"""
    card = WidgetFactory.create_frame(parent, bg=Theme.SECONDARY, padx=20, pady=15)
    
    # Colored border
    WidgetFactory.create_frame(card, height=3, bg=color).pack(fill="x", pady=(0, 10))
    
    # Header
    header = WidgetFactory.create_frame(card, bg=Theme.SECONDARY)
    header.pack(fill="x", pady=(0, 5))
    
    WidgetFactory.create_label(header, text=icon, font=("Segoe UI", 18),
                              fg=color, bg=Theme.SECONDARY).pack(side="left")
    WidgetFactory.create_label(header, text=title, font=("Segoe UI", 10),
                              fg=Theme.TEXT_MUTED, bg=Theme.SECONDARY).pack(side="right")
    
    # Value
    value_label = WidgetFactory.create_label(card, text=str(value), 
                                            font=("Segoe UI", 20, "bold"),
                                            fg=Theme.TEXT, bg=Theme.SECONDARY)
    value_label.pack(anchor="w")
    
    if clickable and click_action:
        value_label.configure(cursor="hand2")
        card.configure(cursor="hand2")
        
        hint = WidgetFactory.create_label(card, text="(clicca per copiare)",
                                         font=("Segoe UI", 8),
                                         fg=Theme.TEXT_MUTED, bg=Theme.SECONDARY,
                                         cursor="hand2")
        hint.pack(anchor="w", pady=(2, 0))
        
        # Apply click and hover
        for widget in [card, value_label, hint]:
            widget.bind("<Button-1>", lambda e: click_action())
        
        HoverEffect.apply(card, Theme.SECONDARY, Theme.HIGHLIGHT, 
                         children_recursive=True)
        HoverEffect.apply(value_label, Theme.SECONDARY, Theme.HIGHLIGHT, 
                         Theme.TEXT, color)
    
    return card


def create_tool_card(parent, tool_data):
    """Create external tool card"""
    card = WidgetFactory.create_frame(parent, bg=Theme.SECONDARY, 
                                     padx=20, pady=20, cursor="hand2")
    
    # Border
    WidgetFactory.create_frame(card, height=3, 
                              bg=tool_data["color"]).pack(fill="x", pady=(0, 15))
    
    # Header
    header = WidgetFactory.create_frame(card, bg=Theme.SECONDARY)
    header.pack(fill="x", pady=(0, 10))
    
    WidgetFactory.create_label(header, text=tool_data["icon"], 
                              font=("Segoe UI", 20),
                              fg=tool_data["color"], 
                              bg=Theme.SECONDARY).pack(side="left")
    WidgetFactory.create_label(header, text=tool_data["name"], 
                              font=("Segoe UI", 14, "bold"),
                              fg=Theme.TEXT, 
                              bg=Theme.SECONDARY).pack(side="left", padx=(10, 0))
    
    # Description
    WidgetFactory.create_label(card, text=tool_data["desc"], 
                              font=("Segoe UI", 10),
                              fg=Theme.TEXT_MUTED, bg=Theme.SECONDARY,
                              wraplength=250, justify="left").pack(anchor="w")
    
    # Button
    WidgetFactory.create_button(card, "Apri", tool_data["action"], 
                               "primary").pack(anchor="w", pady=(15, 0))
    
    # Hover effect
    HoverEffect.apply(card, Theme.SECONDARY, Theme.HIGHLIGHT, 
                     children_recursive=True)
    card.bind("<Button-1>", lambda e: tool_data["action"]())
    
    return card


def create_info_card(parent, title, content, icon="ℹ"):
    """Create information card"""
    card_frame = WidgetFactory.create_frame(parent, bg=Theme.SECONDARY, 
                                           padx=15, pady=15)
    card_frame.pack(fill="x", pady=5)
    
    # Top border
    WidgetFactory.create_frame(card_frame, height=3, 
                              bg=Theme.ACCENT).pack(fill="x", pady=(0, 10))
    
    # Header
    header_frame = WidgetFactory.create_frame(card_frame, bg=Theme.SECONDARY)
    header_frame.pack(fill="x", pady=(0, 10))
    
    WidgetFactory.create_label(header_frame, text=icon, font=("Segoe UI", 16),
                              fg=Theme.ACCENT, 
                              bg=Theme.SECONDARY).pack(side="left", padx=(0, 10))
    WidgetFactory.create_label(header_frame, text=title, 
                              font=("Segoe UI", 12, "bold"),
                              fg=Theme.TEXT, 
                              bg=Theme.SECONDARY).pack(side="left")
    
    # Content
    WidgetFactory.create_label(card_frame, text=content, font=("Segoe UI", 10),
                              fg=Theme.TEXT_MUTED, bg=Theme.SECONDARY,
                              wraplength=400, justify="left").pack(anchor="w")
    
    return card_frame


# ============================================================================
# MAIN WINDOW COMPONENTS
# ============================================================================
def create_status_bar(parent):
    """Create status bar"""
    status_frame = WidgetFactory.create_frame(parent, bg=Theme.BG_DARK, height=30)
    status_frame.pack(side="bottom", fill="x")
    status_frame.pack_propagate(False)
    
    # Separator
    WidgetFactory.create_frame(status_frame, height=1, 
                              bg=Theme.BORDER).pack(side="top", fill="x")
    
    content_frame = WidgetFactory.create_frame(status_frame, bg=Theme.BG_DARK)
    content_frame.pack(fill="both", expand=True, padx=15, pady=5)
    
    status_label = WidgetFactory.create_label(content_frame, text="Pronto",
                                             font=("Segoe UI", 9),
                                             fg=Theme.TEXT_MUTED, 
                                             bg=Theme.BG_DARK)
    status_label.pack(side="left")
    
    # Timestamp
    timestamp_label = WidgetFactory.create_label(content_frame, text="",
                                                font=("Segoe UI", 8),
                                                fg=Theme.TEXT_MUTED,
                                                bg=Theme.BG_DARK)
    timestamp_label.pack(side="right")
    
    # Update timestamp
    def update_timestamp():
        if not parent.winfo_exists():
            return
        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            timestamp_label.config(text=current_time)
            parent.after(1000, update_timestamp)
        except tk.TclError:
            pass
    
    update_timestamp()
    
    WidgetFactory.create_label(content_frame, text="League Info Viewer v2.5",
                              font=("Segoe UI", 8),
                              fg=Theme.ACCENT, 
                              bg=Theme.BG_DARK).pack(side="right", padx=(0, 15))
    
    return status_label


def create_header(parent, account_info, riot_id, ddragon_version, root):
    """Create modern header"""
    header_frame = WidgetFactory.create_frame(parent, bg=Theme.BG_DARK, height=200)
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)
    
    gradient_frame = WidgetFactory.create_frame(header_frame, bg=Theme.BG_DARK)
    gradient_frame.pack(fill="both", expand=True, padx=30, pady=20)
    
    header_content = WidgetFactory.create_frame(gradient_frame, bg=Theme.BG_DARK)
    header_content.pack(fill="both", expand=True)
    
    # Left - Profile
    _create_header_profile(header_content, account_info, ddragon_version)
    
    # Center - Info
    _create_header_info(header_content, account_info, riot_id, ddragon_version, root)
    
    # Right - Actions
    _create_header_actions(header_content, riot_id, root)


def _create_header_profile(parent, account_info, ddragon_version):
    """Create header profile section"""
    left_section = WidgetFactory.create_frame(parent, bg=Theme.BG_DARK)
    left_section.pack(side="left", fill="y")
    
    if "profileIconId" in account_info:
        profile_icon = load_profile_icon(account_info['profileIconId'], 
                                        (100, 100), ddragon_version)
        
        icon_container = WidgetFactory.create_frame(left_section, bg=Theme.ACCENT, 
                                                   padx=3, pady=3)
        icon_container.pack()
        
        icon_label = WidgetFactory.create_label(icon_container, image=profile_icon, 
                                               bg=Theme.ACCENT)
        icon_label.image = profile_icon
        icon_label.pack()
        
        if "summonerLevel" in account_info:
            level_container = WidgetFactory.create_frame(left_section, bg=Theme.SUCCESS,
                                                        padx=8, pady=4)
            level_container.pack(pady=(10, 0))
            
            WidgetFactory.create_label(level_container, 
                                      text=f"LV. {account_info['summonerLevel']}",
                                      font=("Segoe UI", 10, "bold"),
                                      bg=Theme.SUCCESS, fg="white").pack()


def _create_header_info(parent, account_info, riot_id, ddragon_version, root):
    """Create header info section"""
    center_section = WidgetFactory.create_frame(parent, bg=Theme.BG_DARK)
    center_section.pack(side="left", fill="both", expand=True, padx=30)
    
    if riot_id:
        # Riot ID - clickable
        name_frame = WidgetFactory.create_frame(center_section, bg=Theme.BG_DARK)
        name_frame.pack(anchor="w", pady=(10, 5))
        
        riot_id_label = create_clickable_label(name_frame, riot_id,
                                              font=("Segoe UI", 28, "bold"),
                                              fg=Theme.TEXT, bg=Theme.BG_DARK,
                                              click_action=lambda: copy_to_clipboard(riot_id, root),
                                              hover_color=Theme.ACCENT)
        riot_id_label.pack(side="left")
        
        hint_label = create_clickable_label(name_frame, "(clicca per copiare)",
                                           font=("Segoe UI", 8),
                                           fg=Theme.TEXT_MUTED, bg=Theme.BG_DARK,
                                           click_action=lambda: copy_to_clipboard(riot_id, root))
        hint_label.pack(side="left", padx=(10, 0), pady=(10, 0))
        
        # Info columns
        _create_info_columns(center_section, account_info, root)


def _create_info_columns(parent, account_info, root):
    """Create info columns"""
    info_container = WidgetFactory.create_frame(parent, bg=Theme.BG_DARK)
    info_container.pack(anchor="w", pady=10, fill="x")
    
    left_info = WidgetFactory.create_frame(info_container, bg=Theme.BG_DARK)
    left_info.pack(side="left", anchor="nw")
    
    right_info = WidgetFactory.create_frame(info_container, bg=Theme.BG_DARK)
    right_info.pack(side="left", anchor="nw", padx=(40, 0))
    
    # Gather info
    useful_info = []
    if "profileIconId" in account_info:
        useful_info.append(("🖼️", "Icona Profilo", f"ID {account_info['profileIconId']}"))
    if "summonerId" in account_info:
        sid = str(account_info['summonerId'])
        useful_info.append(("🆔", "ID Evocatore", sid[:12] + "..." if len(sid) > 12 else sid))
    if "accountId" in account_info:
        aid = str(account_info['accountId'])
        useful_info.append(("📱", "ID Account", aid[:12] + "..." if len(aid) > 12 else aid))
    
    try:
        ddragon_ver = get_latest_ddragon_version()
        if ddragon_ver and ddragon_ver != "latest":
            useful_info.append(("📄", "Patch Corrente", ddragon_ver))
    except:
        pass
    
    # Display info
    for i, (icon, label, value) in enumerate(useful_info):
        parent_frame = left_info if i < 2 else right_info
        
        info_item = WidgetFactory.create_frame(parent_frame, bg=Theme.BG_DARK)
        info_item.pack(anchor="w", pady=2, fill="x")
        
        WidgetFactory.create_label(info_item, text=icon, font=("Segoe UI", 12),
                                  fg=Theme.ACCENT, 
                                  bg=Theme.BG_DARK).pack(side="left", padx=(0, 8))
        WidgetFactory.create_label(info_item, text=f"{label}:", 
                                  font=("Segoe UI", 10, "bold"),
                                  fg=Theme.TEXT_MUTED, 
                                  bg=Theme.BG_DARK).pack(side="left", padx=(0, 8))
        
        value_label = WidgetFactory.create_label(info_item, text=value,
                                                font=("Segoe UI", 10),
                                                fg=Theme.TEXT, bg=Theme.BG_DARK)
        value_label.pack(side="left")
        
        # Make IDs clickable
        if "ID" in label:
            value_label.configure(cursor="hand2")
            if "Evocatore" in label:
                value_label.bind("<Button-1>", 
                               lambda e: copy_to_clipboard(account_info['summonerId'], root))
            elif "Account" in label:
                value_label.bind("<Button-1>", 
                               lambda e: copy_to_clipboard(account_info['accountId'], root))


def _create_header_actions(parent, riot_id, root):
    """Create header actions section"""
    right_section = WidgetFactory.create_frame(parent, bg=Theme.BG_DARK)
    right_section.pack(side="right", fill="y", padx=(20, 0))
    
    # Essential actions only
    WidgetFactory.create_button(right_section, "🔄 Aggiorna",
                               lambda: refresh_account_info(root),
                               "info").pack(fill="x", pady=3)
    
    if riot_id:
        WidgetFactory.create_button(right_section, "📋 Copia Riot ID",
                                   lambda: copy_to_clipboard(riot_id, root),
                                   "success").pack(fill="x", pady=3)


# ============================================================================
# TAB CREATION
# ============================================================================
def create_dashboard_tab(notebook, account_info, riot_id, root=None):
    """Create dashboard tab"""
    tab_frame = WidgetFactory.create_frame(notebook, bg=Theme.BG)
    notebook.add(tab_frame, text="📊 Dashboard")
    
    scrollable = ScrollableFrame(tab_frame, bg=Theme.BG)
    
    dashboard_content = WidgetFactory.create_frame(scrollable.frame, bg=Theme.BG,
                                                  padx=20, pady=20)
    dashboard_content.pack(fill="both", expand=True)
    
    # Stats section
    stats_frame = WidgetFactory.create_frame(dashboard_content, bg=Theme.BG)
    stats_frame.pack(fill="x", pady=(0, 20))
    
    WidgetFactory.create_label(stats_frame, text="📊 Panoramica Account",
                              font=("Segoe UI", 16, "bold"),
                              fg=Theme.TEXT, bg=Theme.BG).pack(anchor="w", pady=(0, 15))
    
    stats_row = WidgetFactory.create_frame(stats_frame, bg=Theme.BG)
    stats_row.pack(fill="x")
    
    # Stat cards
    create_stat_card(stats_row, "Livello Evocatore",
                    account_info.get('summonerLevel', 'N/A'),
                    Theme.SUCCESS, "🏆").pack(side="left", fill="both", 
                                             expand=True, padx=(0, 10))
    
    if riot_id:
        create_stat_card(stats_row, "Riot ID", riot_id, Theme.ACCENT, "👤",
                        clickable=True,
                        click_action=lambda: copy_to_clipboard(riot_id, root)).pack(
                            side="left", fill="both", expand=True, padx=(0, 10))
    
    create_stat_card(stats_row, "Regione", "EUW", Theme.INFO, "🌍").pack(
        side="left", fill="both", expand=True)
    
    # Info/shortcuts section instead of links
    _create_dashboard_shortcuts(dashboard_content)


def _create_dashboard_shortcuts(parent):
    """Create shortcuts info section for dashboard"""
    shortcuts_frame = WidgetFactory.create_frame(parent, bg=Theme.BG)
    shortcuts_frame.pack(fill="x", pady=20)
    
    WidgetFactory.create_label(shortcuts_frame, text="⚡ Azioni Rapide",
                              font=("Segoe UI", 16, "bold"),
                              fg=Theme.TEXT, bg=Theme.BG).pack(anchor="w", pady=(0, 15))
    
    # Info cards
    info_items = [
        {
            "title": "Collegamenti Esterni",
            "content": "Trova statistiche dettagliate, guide e analisi nel tab 🛠️ Strumenti",
            "icon": "🔗"
        },
        {
            "title": "Scorciatoie Tastiera",
            "content": "F5: Aggiorna dati • Ctrl+Q: Esci dall'applicazione",
            "icon": "⌨️"
        },
        {
            "title": "Dettagli Account",
            "content": "Visualizza tutte le informazioni tecniche nel tab 📋 Dettagli Account",
            "icon": "ℹ️"
        }
    ]
    
    for item in info_items:
        create_info_card(shortcuts_frame, item["title"], item["content"], item["icon"])


def create_details_tab(notebook, account_info, root):
    """Create details tab"""
    tab_frame = WidgetFactory.create_frame(notebook, bg=Theme.BG)
    notebook.add(tab_frame, text="📋 Dettagli Account")
    
    scrollable = ScrollableFrame(tab_frame, bg=Theme.BG)
    
    content = WidgetFactory.create_frame(scrollable.frame, bg=Theme.BG,
                                        padx=30, pady=20)
    content.pack(fill="both", expand=True)
    
    # Title
    title_frame = WidgetFactory.create_frame(content, bg=Theme.BG)
    title_frame.pack(fill="x", pady=(0, 20))
    
    WidgetFactory.create_label(title_frame, text="📋 Informazioni Dettagliate",
                              font=("Segoe UI", 18, "bold"),
                              fg=Theme.TEXT, bg=Theme.BG).pack(side="left")
    
    # Table
    table_frame = WidgetFactory.create_frame(content, bg=Theme.SECONDARY,
                                            padx=2, pady=2)
    table_frame.pack(fill="both", expand=True)
    
    # Header
    header_frame = WidgetFactory.create_frame(table_frame, bg=Theme.HIGHLIGHT, pady=12)
    header_frame.pack(fill="x")
    
    WidgetFactory.create_label(header_frame, text="PROPRIETÀ",
                              font=("Segoe UI", 11, "bold"),
                              fg=Theme.TEXT, 
                              bg=Theme.HIGHLIGHT).pack(side="left", padx=20)
    WidgetFactory.create_label(header_frame, text="VALORE",
                              font=("Segoe UI", 11, "bold"),
                              fg=Theme.TEXT,
                              bg=Theme.HIGHLIGHT).pack(side="left", padx=(200, 0))
    
    # Rows
    _create_detail_rows(table_frame, account_info, root)


def _create_detail_rows(parent, account_info, root):
    """Create detail table rows"""
    priority_keys = ['summonerId', 'gameName', 'tagLine', 'summonerLevel',
                    'accountId', 'puuid', 'profileIconId']
    sorted_keys = priority_keys + [k for k in account_info.keys() 
                                  if k not in priority_keys]
    
    for i, key in enumerate(sorted_keys):
        if key not in account_info:
            continue
        
        value = account_info[key]
        bg_color = Theme.BG if i % 2 == 0 else Theme.SECONDARY
        
        row_frame = WidgetFactory.create_frame(parent, bg=bg_color, pady=10)
        row_frame.pack(fill="x")
        
        # Key
        WidgetFactory.create_label(row_frame, text=_format_key(key),
                                  font=("Segoe UI", 10, "bold"),
                                  fg=Theme.ACCENT_2, 
                                  bg=bg_color).pack(side="left", padx=20)
        
        # Value
        value_str = _format_value(value)
        WidgetFactory.create_label(row_frame, text=value_str,
                                  font=("Segoe UI", 10),
                                  fg=Theme.TEXT, bg=bg_color,
                                  wraplength=400, justify="left").pack(side="left",
                                                                      padx=(200, 0))
        
        # Copy button
        copy_btn = WidgetFactory.create_copy_button(row_frame, value_str, root)
        copy_btn.pack(side="right", padx=20)


def create_tools_tab(notebook, riot_id):
    """Create tools tab"""
    tab_frame = WidgetFactory.create_frame(notebook, bg=Theme.BG)
    notebook.add(tab_frame, text="🛠️ Strumenti")
    
    content = WidgetFactory.create_frame(tab_frame, bg=Theme.BG, padx=30, pady=20)
    content.pack(fill="both", expand=True)
    
    # External links section
    links_section = WidgetFactory.create_frame(content, bg=Theme.BG)
    links_section.pack(fill="x", pady=(0, 30))
    
    WidgetFactory.create_label(links_section, text="🌐 Collegamenti Esterni",
                              font=("Segoe UI", 16, "bold"),
                              fg=Theme.TEXT, bg=Theme.BG).pack(anchor="w", pady=(0, 15))
    
    tools_grid = WidgetFactory.create_frame(links_section, bg=Theme.BG)
    tools_grid.pack(fill="x")
    
    # Use centralized links configuration
    all_links = ExternalLinks.get_all()
    
    for i, link in enumerate(all_links):
        # Add action to link data
        tool_data = link.copy()
        tool_data['desc'] = tool_data['long_desc']
        tool_data['action'] = lambda l=link: open_profile(riot_id, l['id'])
        
        tool_card = create_tool_card(tools_grid, tool_data)
        tool_card.grid(row=i//2, column=i%2, sticky="ew", padx=10, pady=10)
    
    tools_grid.grid_columnconfigure(0, weight=1)
    tools_grid.grid_columnconfigure(1, weight=1)
    
    # Info section
    _create_info_section(content)


def _create_info_section(parent):
    """Create info section"""
    info_section = WidgetFactory.create_frame(parent, bg=Theme.BG)
    info_section.pack(fill="x", pady=20)
    
    WidgetFactory.create_label(info_section, text="ℹ️ Informazioni",
                              font=("Segoe UI", 16, "bold"),
                              fg=Theme.TEXT, bg=Theme.BG).pack(anchor="w", pady=(0, 15))
    
    info_cards = [
        {"title": "Scorciatoie Tastiera",
         "content": "F5: Aggiorna dati\nCtrl+Q: Esci dall'applicazione",
         "icon": "⌨️"},
        {"title": "Regione Supportata",
         "content": "Attualmente supporta solo EUW\nSupporto per altre regioni in arrivo",
         "icon": "🌍"}
    ]
    
    for info in info_cards:
        create_info_card(info_section, info["title"], info["content"], info["icon"])


# ============================================================================
# HELPERS
# ============================================================================
def _format_key(key):
    """Format keys for display"""
    key_mappings = {
        'gameName': 'Nome Giocatore', 'tagLine': 'Tag',
        'summonerLevel': 'Livello Evocatore', 'summonerId': 'ID Evocatore',
        'accountId': 'ID Account', 'puuid': 'PUUID',
        'profileIconId': 'ID Icona Profilo'
    }
    return key_mappings.get(key, key.replace('_', ' ').title())


def _format_value(value):
    """Format values for display"""
    if isinstance(value, bool):
        return "Sì" if value else "No"
    elif value is None:
        return "Non disponibile"
    elif isinstance(value, (int, float)) and len(str(value)) > 10:
        return f"{value:,}".replace(',', '.')
    return str(value)


def center_window(window):
    """Center window on screen"""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def refresh_account_info(root):
    """Refresh account info"""
    try:
        if root and root.winfo_exists():
            show_toast_notification(root, "Aggiornamento in corso...",
                                  fg_color=Theme.INFO, duration=1000)
        
        root.destroy()
        
        lockfile_data = Riot_API.get_lockfile_data()
        account_info = Riot_API.get_account_info(lockfile_data)
        show_account_info(account_info)
    except Exception as e:
        messagebox.showerror("Errore", f"Errore durante l'aggiornamento: {str(e)}")


# ============================================================================
# MAIN WINDOW
# ============================================================================
def show_account_info(account_info):
    """Show account info with renewed interface"""
    if not account_info:
        messagebox.showerror("Errore", 
                           "Impossibile ottenere le informazioni dell'account.")
        return
    
    ddragon_version = get_latest_ddragon_version()
    riot_id = get_riot_id(account_info)
    
    # Create window
    root = tk.Tk()
    root.title("League Info Viewer - Dashboard")
    root.geometry("1200x800")
    root.configure(bg=Theme.BG)
    root.minsize(1000, 700)
    
    if os.path.exists("icon.ico"):
        root.iconbitmap("icon.ico")
    
    # Configure ttk styles
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Custom.TNotebook", background=Theme.BG, borderwidth=0,
                   tabmargins=[0, 5, 0, 0])
    style.configure("Custom.TNotebook.Tab", background=Theme.SECONDARY,
                   foreground=Theme.TEXT_MUTED, padding=[20, 10],
                   borderwidth=0, focuscolor="none")
    style.map("Custom.TNotebook.Tab",
             background=[("selected", Theme.HIGHLIGHT), ("active", Theme.BUTTON)],
             foreground=[("selected", Theme.TEXT), ("active", Theme.TEXT)])
    
    # Main container
    main_container = WidgetFactory.create_frame(root, bg=Theme.BG)
    main_container.pack(fill="both", expand=True)
    
    # Header
    create_header(main_container, account_info, riot_id, ddragon_version, root)
    
    # Content
    content_frame = WidgetFactory.create_frame(main_container, bg=Theme.BG)
    content_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    # Notebook
    notebook = ttk.Notebook(content_frame, style="Custom.TNotebook")
    notebook.pack(fill="both", expand=True)
    
    # Tabs
    create_dashboard_tab(notebook, account_info, riot_id, root)
    create_details_tab(notebook, account_info, root)
    create_tools_tab(notebook, riot_id)
    
    # Status bar
    status_label = create_status_bar(root)
    
    # Center window
    center_window(root)
    
    # Update status
    status_text = f"Connesso come {riot_id}" if riot_id else "Pronto"
    status_label.config(text=status_text)
    
    # Keybindings
    root.bind('<F5>', lambda e: refresh_account_info(root))
    root.bind('<Control-q>', lambda e: root.quit())
    
    root.protocol("WM_DELETE_WINDOW", lambda: root.destroy())
    
    root.mainloop()


def main():
    """Main entry point"""
    try:
        lockfile_data = Riot_API.get_lockfile_data()
        account_info = Riot_API.get_account_info(lockfile_data)
        show_account_info(account_info)
    except Exception as e:
        messagebox.showerror("Errore", f"Si è verificato un errore: {str(e)}")


if __name__ == "__main__":
    main()
