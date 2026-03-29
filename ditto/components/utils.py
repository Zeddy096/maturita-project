def bind_scroll_recursive(widget, canvas):
    def _on_mousewheel(event):

        # linux (button 4 & 5)
        if hasattr(event, "num"):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            return

        # windows / touchpad
        if hasattr(event, "delta") and event.delta:
            canvas.yview_scroll(int(-1 * (event.delta / 240)), "units")

    widget.bind("<MouseWheel>", _on_mousewheel)
    widget.bind("<Button-4>", _on_mousewheel)
    widget.bind("<Button-5>", _on_mousewheel)

    for child in widget.winfo_children():
        bind_scroll_recursive(child, canvas)