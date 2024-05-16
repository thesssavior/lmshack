    def update_list(items, check_vars):
        updated_list = []
        for i, item in enumerate(items):
            if check_vars[i].get():
                updated_list.append(item)
        return updated_list

    def create_grid_for_each_item(items):
        import tkinter as tk
        root = tk.Tk()
        root.title("Grid for Each Item")

        check_vars = [tk.IntVar(value=1) for _ in range(len(items))]  # List to store IntVars for each checkbox

        for index, item in enumerate(items):
            # Create a new frame for each item
            frame = tk.Frame(root)
            frame.grid(row=index, column=0, sticky="w")

            # Create a checkbox for the item
            checkbox = tk.Checkbutton(frame, variable=check_vars[index])
            checkbox.grid(row=0, column=0, padx=5)

            # Create a label displaying the item
            label = tk.Label(frame, text=item)
            label.grid(row=0, column=1)

        def on_button_click():
            global tuple_list
            tuple_list = update_list(items=items, check_vars=check_vars)
            print(tuple_list)  # Print the updated list for demonstration purposes
