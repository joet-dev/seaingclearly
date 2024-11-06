
colours = {
    "bg-primary": "#181818",
    "bg-secondary": "#636363",

    "text-primary": "#f2f2f2",
    "text-secondary": "#919191",

    "border": "#333",
    "border-focus": "#636363",

    "std": "#636363",
    "hover": "#005ba1",
    "selected": "#0061ae",
}

asset_paths = {
    "prawn": r"assets\prawn\prawn.png",
    "folder": r"assets\folder.png",
}

settings = {
    "file_match_pattern" : [r"*.mp4", r"*.avi", r"*.mov", r"*.jpg", r"*.jpeg", r"*.png", r"*.gif"],
}

template_styles = {
    "primary-background" : {
        "background-color": colours['bg-primary']
    },
    "secondary-background" : {
        "background-color": colours['bg-secondary']
    },

    "primary-colour": {
        "color": colours['text-primary'],
    },
    "secondary-colour": {
        "color": colours['text-secondary'],
    },

    "ele": {
        "border": f"2px solid {colours['std']}",
        "background-color": colours['std'],
    },
    "ele-hover": {
        "border": f"2px solid {colours['hover']}",
        "background-color": f"{colours['hover']}",
    },
    "ele-selected": {
        "border": f"2px solid {colours['selected']}",
        "background-color": f"{colours['selected']}",
    },

    "checkbox": {
        "padding": "5px 0px 5px 0px"
    },
    
    "border": {
        "border": f"2px solid {colours['border']}",
        "border-radius": "3px",
        "padding": "5px",
    },

    "border-focus": {
        "border": f"2px solid {colours['border-focus']}",
    },

    "button": {
        "border-radius": "3px",
        "padding": "4px",
    },

    "label-header": {
        "background-color": "transparent",
        "font-size": "14px",
        "font-weight": "700",
        "margin": "0px 0px 6px 0px",
        "color": colours['text-primary'],
    },
    
    "label-sub": {
        "background-color": "transparent",
        "font-size": "12px",
        "font-weight": "400",
        "margin": "0px 0px 6px 0px",
        "color": colours['text-secondary'],
    },

    "scrollbar": {
        "border": "1px solid grey",
        "border-radius": "5px",
        "background": "#1a1a1a",
        "margin": "0px 0px 0px 0px",
    },
    "hor-scrollbar": {
        "height": "10px",
    },
    "vert-scrollbar": {
        "width": "10px",
    },
    "scrollbar-thumb": {
        "background": "#2b2b2b",
        "border-radius": "5px",
    },
    "scrollbar-add-line": {
        "background": "none",
        "width": "0px",
        "height": "0px",
        "subcontrol-position": "bottom",
        "subcontrol-origin": "margin",
    },
    "scrollbar-sub-line": {
        "background": "none",
        "width": "0px",
        "height": "0px",
        "subcontrol-position": "top",
        "subcontrol-origin": "margin",
    },

    "group-box": {
        "margin-top": "7px",
        "padding": "10px",
        "font-size": "14px",
        "font-weight": "700",
        "color": "#f4f4f4",
    },
}



