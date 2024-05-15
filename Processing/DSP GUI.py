import PySimpleGUI as psg
import PySimpleGUI as sg
import csv,os
import random
import pandas as pd
#import tableDetect
#import tablecrop
import cv2
import numpy as np
import preprocess
import tensorflow as tf
#https://www.youtube.com/watch?v=ETHtvd-_FJg&ab_channel=TheCSClassroom


def predict_Model(model, directory):
    number = ''
    i=0
    numbers = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isdir(filepath) and "converted" in filepath:
            items = sorted(os.listdir(filepath), key=lambda x: int(x.split('.')[0]))
            print(items)
            for item in items:
                if i%6==0 and i!=0:
                    numbers.append(number)
                    number = ''
                img_paths = os.path.join(filepath,item)
                img= cv2.imread(img_paths)[:,:,0]
                mean = np.mean(img)
                if mean > 0:
                    img = np.array([img])
                    prediction = model.predict(img)
                    number = number + str(np.argmax(prediction))
                i+=1
            numbers.append(number)
    return numbers

def add_comma(numbers):
    deci_numbers = []
    for number in numbers:
        if len(number)<6:
            x = len(number)-3
            number = number[:x] + '.' + number[x:] 
        else:
            number = number[:3] + '.' + number[3:]
        deci_numbers.append(number)
    return deci_numbers

    


def edit_cell(window, key, row, col, justify='left'):

    global textvariable, edit, data

    def callback(event, row, col, text, key):
        global edit
        widget = event.widget
        if key == 'Focus_Out':
            text = widget.get()
            print(text)
        widget.destroy()
        widget.master.destroy()
        print(row)
        values = list(table.item(row, 'values'))
        values[col] = text
        try:
            data[row-1][col] = text
        except:
            print("Out of bounds")
        print(data)
  
        table.item(row, values=values)
        edit = False

    if edit or row <= 0:
        return

    edit = True
    root = window.TKroot
    table = window[key].Widget
    text = table.item(row, "values")[col]
    x, y, width, height = table.bbox(row, col)


    frame = sg.tk.Frame(root)
    frame.place(x=x+5, y=y+145, anchor="nw", width=width, height=height)

  
    textvariable = sg.tk.StringVar()
    textvariable.set(text)
    
    entry = sg.tk.Entry(frame, textvariable=textvariable, justify=justify)
    entry.pack()
    entry.select_range(0, sg.tk.END)
    entry.icursor(sg.tk.END)
    entry.focus_force()
    entry.bind("<FocusOut>", lambda e, r=row, c=col, t=text, k='Focus_Out':callback(e, r, c, t, k))
    entry.bind("<Escape>", lambda e, r=row, c=col, t=text, k='Escape':callback(e, r, c, t, k))

   
   
def generate_table():
   global edit,data, pdf_address
   edit = False 
   
   rows = 19
   cols = 1
   data = [[random.randint(1, 100) for _ in range(cols)] for _ in range(rows)]
   temp_headings = ['Data']
   
   working_directory = os.getcwd();

   sg.set_options(dpi_awareness= True)
   layout = [
      [psg.Text('Choose an input file:', font=('Arial Bold', 10), size=(20, 1), justification='left')],
      [psg.InputText(key="-FILE_PATH-"), 
      psg.FileBrowse(initial_folder=working_directory, file_types=[("All Picture Types", "*.pdf *.jpeg *.png")]), psg.Button("Submit")],
      [psg.Text('Enter the heading:',  font=('Arial Bold', 10), size=(20, 1), justification='left')],
      [psg.InputText(key = '-HEADING-')],
      [psg.Text('Click blocks to edit data:',  font=('Arial Bold', 10), size=(20, 1), justification='left'), psg.Push(), psg.Button(("Save"))],
      [psg.Table(
      values = data,
      headings = temp_headings,
      max_col_width= 10,
      font = ("Times New Roman", 15),
      auto_size_columns= True,
      justification= 'right',
      num_rows=20,
      #alternating_row_color= sg.theme_button_color()[1],
      key = "-TABLE-",
      expand_x = True, 
      expand_y = True, 
      enable_click_events= True)], 
      [psg.Text('Cell clicked'), psg.T(key = '-CLICKED_CELL-')], 
      ]   
   
   window = sg.Window('File Loader', layout,size=(715,500), resizable= True,finalize = True)
   
   while True:
      print()
      event, value = window.read();
      if event in (sg.WIN_CLOSED, 'Exit'):
         break
      elif event == "Submit":
        pdf_address = value["-FILE_PATH-"]
        # if "png" in pdf_address or "jpg" in pdf_address:
        #     tableDetect.OutlineTable(pdf_address)
        # else:
        #     (tableDetect.OutlineTable(tableDetect.convertPdftoImage(pdf_address)))

        #tablecrop.CropNumbers()
        #preprocess.preprocess(working_directory)
        data = add_comma(predict_Model(tf.keras.models.load_model('Models/SGD_batch64_epoch50_learning_rate_0.03_momentum0.8_.model'), working_directory))
        data = [[element] for element in data]
        # numbers = []
        # for d in data:
        #     try:
        #         # Attempt to convert the string to float
        #         converted_value = float(d)
        #         print(converted_value) 
        #         numbers.append(d)
        #     except ValueError:
        #         print("Could not convert the string to a float.")
        window['-TABLE-'].update(values=data)
        
      elif event == "Save":
            filename = psg.popup_get_file('Save as', save_as=True, file_types=(("CSV Files", "*.csv"),))
            if filename:
                with open(filename, 'w', newline='') as csvfile:
                    heading_value = value["-HEADING-"]
                    headings = [heading_value]
                    writer = csv.writer(csvfile)
                    writer.writerow(headings)
                    writer.writerows(data)
            psg.popup('Saved')
      elif isinstance(event,tuple):
         if isinstance(event[2][0], int) and event[2][0]>-1:
            cell = row, col = event[2]
         window['-CLICKED_CELL-'].update(cell)
         edit_cell(window, '-TABLE-', row+1, col, justify='right')
   window.close()
   
generate_table()
      