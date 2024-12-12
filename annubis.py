import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
import paramiko
import os
import stat
import shutil

# Definir los colores
BG_COLOR = "#faf7ef"  # Color de fondo general (blanco)
LABEL_COLOR = "#212121"  # Color del texto de etiquetas (gris oscuro)
ENTRY_BG_COLOR = "#F7F7F7"  # Color de fondo de los campos de entrada (gris claro)
BUTTON_COLOR = "#0070C9"  # Color de los botones (azul)
BUTTON_HOVER_COLOR = "#005BB5"  # Color de los botones en hover (azul más oscuro)
BUTTON_TEXT_COLOR = "#FFFFFF"  # Color del texto de los botones (blanco)
TABLE_HEADER_COLOR = "#212121"  # Color del encabezado de la tabla (gris oscuro)
TABLE_ROW_COLOR = "#FFFFFF"  # Color de las filas de la tabla (blanco)
SELECTED_ROW_COLOR = "#E1E1E1"  # Color de la fila seleccionada (gris claro)


# Configuración de la base de datos
db_config = {
    'user': 'admin',
    'password': 'annubisCoSFTP1234!',
    'host': '200.234.228.42',
    'database': 'annubis'
}

# Configuración SFTP
sftp_config = {
    'host': '200.234.228.42',
    'username': 'root',
    'password': '8549BSCjavi',
    'port': 22  # Cambia si es necesario
}

sftp_dir = '/var/www/html/img/'

# Función para conectarse a la base de datos
def connect_to_db():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error conectando a la base de datos: {err}")
        return None

# Función para insertar datos en la base de datos
def insert_data():
    connection = connect_to_db()
    if connection is None:
        return

    cursor = connection.cursor()
    query = ("INSERT INTO productos "
             "(color, cost, description, modelo, name, nom_collection, type) "
             "VALUES (%s, %s, %s, %s, %s, %s, %s)")
    data = (entry_color.get(), entry_cost.get(), entry_description.get(1.0, tk.END).strip(),
            entry_modelo.get(), entry_name.get(), entry_nom_collection.get(), entry_type.get())

    try:
        cursor.execute(query, data)
        connection.commit()
        load_data()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error insertando datos: {err}")
    finally:
        cursor.close()
        connection.close()

# Función para cargar datos de la base de datos y mostrarlos en la tabla
def load_data():
    connection = connect_to_db()
    if connection is None:
        return

    cursor = connection.cursor()
    query = "SELECT * FROM productos"

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        update_table(rows)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error cargando datos: {err}")
    finally:
        cursor.close()
        connection.close()

# Función para actualizar la tabla con los datos de la base de datos
def update_table(rows):
    for row in tree.get_children():
        tree.delete(row)
    for row in rows:
        tree.insert("", tk.END, values=row)

# Función para eliminar una fila de la base de datos
def delete_data():
    selected_item = tree.focus()  # Obtener el ítem seleccionado en la tabla
    if not selected_item:
        messagebox.showwarning("Advertencia", "Por favor selecciona un registro para eliminar.")
        return

    connection = connect_to_db()
    if connection is None:
        return

    cursor = connection.cursor()
    try:
        # Obtener el ID del ítem seleccionado
        item_id = tree.item(selected_item)['values'][0]  # Suponiendo que el ID es el primer valor

        query = "DELETE FROM productos WHERE id = %s"
        cursor.execute(query, (item_id,))
        connection.commit()
        load_data()
        messagebox.showinfo("Éxito", "Registro eliminado correctamente.")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error eliminando registro: {err}")
    finally:
        cursor.close()
        connection.close()

# Función para editar una fila de la base de datos
def edit_data():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("Advertencia", "Por favor selecciona un registro para editar.")
        return

    item_values = tree.item(selected_item)['values']
    entry_id.set(item_values[0])
    entry_color.delete(0, tk.END)
    entry_color.insert(0, item_values[1])
    entry_cost.delete(0, tk.END)
    entry_cost.insert(0, item_values[2])
    entry_description.delete(1.0, tk.END)
    entry_description.insert(tk.END, item_values[3])
    entry_modelo.delete(0, tk.END)
    entry_modelo.insert(0, item_values[4])
    entry_name.delete(0, tk.END)
    entry_name.insert(0, item_values[5])
    entry_nom_collection.delete(0, tk.END)
    entry_nom_collection.insert(0, item_values[6])
    entry_type.delete(0, tk.END)
    entry_type.insert(0, item_values[7])

    update_button.grid(row=0, column=3, padx=10, pady=5)

def update_data():
    connection = connect_to_db()
    if connection is None:
        return

    cursor = connection.cursor()
    query = ("UPDATE productos SET color = %s, cost = %s, description = %s, modelo = %s, name = %s, nom_collection = %s, type = %s WHERE id = %s")
    data = (entry_color.get(), entry_cost.get(), entry_description.get(1.0, tk.END).strip(),
            entry_modelo.get(), entry_name.get(), entry_nom_collection.get(), entry_type.get(), entry_id.get())

    try:
        cursor.execute(query, data)
        connection.commit()
        load_data()
        clear_entries()
        messagebox.showinfo("Éxito", "Registro actualizado correctamente.")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error actualizando datos: {err}")
    finally:
        cursor.close()
        connection.close()

# Función para limpiar los campos de entrada
def clear_entries():
    entry_id.set("")
    entry_color.delete(0, tk.END)
    entry_cost.delete(0, tk.END)
    entry_description.delete(1.0, tk.END)
    entry_modelo.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_nom_collection.delete(0, tk.END)
    entry_type.delete(0, tk.END)
    update_button.grid_forget()

# Función para conectarse por SFTP
def connect_to_sftp():
    try:
        transport = paramiko.Transport((sftp_config['host'], sftp_config['port']))
        transport.connect(username=sftp_config['username'], password=sftp_config['password'])
        sftp = paramiko.SFTPClient.from_transport(transport)
        return sftp
    except Exception as e:
        messagebox.showerror("Error", f"Error conectando por SFTP: {e}")
        return None

# Función para cargar archivos del directorio SFTP
def load_sftp_files():
    sftp = connect_to_sftp()
    if sftp is None:
        return

    try:
        files = sftp.listdir_attr(sftp_dir)
        sorted_files = sorted(files, key=lambda x: x.st_mode)
        update_sftp_listbox(sorted_files)
    except Exception as e:
        messagebox.showerror("Error", f"Error cargando archivos SFTP: {e}")
    finally:
        sftp.close()

# Función para actualizar el Listbox con los archivos SFTP
def update_sftp_listbox(files):
    sftp_listbox.delete(0, tk.END)
    for item in files:
        if stat.S_ISDIR(item.st_mode):
            sftp_listbox.insert(tk.END, f"[DIR] {item.filename}")
        else:
            sftp_listbox.insert(tk.END, item.filename)

# Función para subir una carpeta al servidor SFTP de manera recursiva
def upload_recursive(sftp, local_path, remote_path, progressbar):
    try:
        sftp.mkdir(remote_path)
    except IOError:
        pass  # Si el directorio ya existe

    total_files = sum(len(files) for _, _, files in os.walk(local_path))
    progressbar["maximum"] = total_files

    for root, dirs, files in os.walk(local_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_file_path, local_path)
            remote_file_path = os.path.join(remote_path, relative_path).replace("\\", "/")

            try:
                sftp.put(local_file_path, remote_file_path)
                progressbar["value"] += 1
            except Exception as e:
                messagebox.showerror("Error", f"Error subiendo archivo {file}: {e}")

        for dir in dirs:
            local_dir_path = os.path.join(root, dir)
            relative_path = os.path.relpath(local_dir_path, local_path)
            remote_dir_path = os.path.join(remote_path, relative_path).replace("\\", "/")

            try:
                sftp.mkdir(remote_dir_path)
            except IOError:
                pass  # Si el directorio ya existe

# Función para iniciar la carga de una carpeta
def start_upload_folder():
    folder_path = filedialog.askdirectory()
    if not folder_path:
        return

    sftp = connect_to_sftp()
    if sftp is None:
        return

    remote_path = os.path.join(sftp_dir, os.path.basename(folder_path)).replace("\\", "/")
    
    progress_window = tk.Toplevel(root)
    progress_window.title("Subiendo Carpeta")
    progressbar = ttk.Progressbar(progress_window, mode="determinate")
    progressbar.pack(fill=tk.X, padx=10, pady=10)

    try:
        upload_recursive(sftp, folder_path, remote_path, progressbar)
        messagebox.showinfo("Éxito", "Carpeta subida correctamente")
    except Exception as e:
        messagebox.showerror("Error", f"Error subiendo carpeta: {e}")
    finally:
        sftp.close()
        progress_window.destroy()
        load_sftp_files()

# Función para iniciar la carga de un archivo
def start_upload_file():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    sftp = connect_to_sftp()
    if sftp is None:
        return

    remote_path = os.path.join(sftp_dir, os.path.basename(file_path)).replace("\\", "/")

    try:
        sftp.put(file_path, remote_path)
        messagebox.showinfo("Éxito", "Archivo subido correctamente")
    except Exception as e:
        messagebox.showerror("Error", f"Error subiendo archivo: {e}")
    finally:
        sftp.close()
        load_sftp_files()

# Función para eliminar un archivo del servidor SFTP
def delete_file():
    selected_file = sftp_listbox.get(tk.ACTIVE)
    if not selected_file or selected_file.startswith("[DIR] "):
        messagebox.showwarning("Advertencia", "Por favor selecciona un archivo para eliminar.")
        return

    sftp = connect_to_sftp()
    if sftp is None:
        return

    try:
        remote_path = os.path.join(sftp_dir, selected_file).replace("\\", "/")
        sftp.remove(remote_path)
        load_sftp_files()  # Actualizar lista de archivos después de eliminar
        messagebox.showinfo("Éxito", "Archivo eliminado correctamente")
    except Exception as e:
        messagebox.showerror("Error", f"Error eliminando archivo: {e}")
    finally:
        sftp.close()

# Función para eliminar una carpeta y su contenido del servidor SFTP
def delete_folder():
    selected_item = sftp_listbox.get(tk.ACTIVE)
    if not selected_item or not selected_item.startswith("[DIR] "):
        messagebox.showwarning("Advertencia", "Por favor selecciona una carpeta para eliminar.")
        return

    sftp = connect_to_sftp()
    if sftp is None:
        return

    def delete_recursive(sftp, remote_path):
        for item in sftp.listdir_attr(remote_path):
            item_path = os.path.join(remote_path, item.filename).replace("\\", "/")
            if stat.S_ISDIR(item.st_mode):
                delete_recursive(sftp, item_path)
            else:
                sftp.remove(item_path)
        sftp.rmdir(remote_path)

    try:
        selected_item = selected_item.replace("[DIR] ", "")
        remote_path = os.path.join(sftp_dir, selected_item).replace("\\", "/")
        delete_recursive(sftp, remote_path)
        load_sftp_files()  # Actualizar lista de archivos después de eliminar
        messagebox.showinfo("Éxito", "Carpeta eliminada correctamente")
    except Exception as e:
        messagebox.showerror("Error", f"Error eliminando carpeta: {e}")
    finally:
        sftp.close()

# Crear ventana principal
root = tk.Tk()
root.title("AnnubisCo ADMIN")
root.geometry("800x600")
root.configure(bg=BG_COLOR)

# Estilo de la tabla
style = ttk.Style()
# Estilo para la cabecera de la tabla (encabezados)
style.configure("Treeview.Heading", background=TABLE_HEADER_COLOR, foreground="#000000", font=('Arial', 10, 'bold'))

# Estilo para las filas de la tabla
style.configure("Treeview", background=BG_COLOR, foreground=LABEL_COLOR, rowheight=25, fieldbackground=TABLE_ROW_COLOR)

# Mapa para el color de fondo de la fila seleccionada
style.map("Treeview", background=[("selected", SELECTED_ROW_COLOR)])
# Crear tabla de productos
tree_frame = tk.Frame(root, bg=BG_COLOR)
tree_frame.pack(fill=tk.BOTH, expand=True)

columns = ("ID", "Color", "Cost", "Description", "Modelo", "Name", "Collection", "Type")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor=tk.CENTER)
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Crear frame para el formulario de entrada
form_frame = tk.Frame(root, bg=BG_COLOR)
form_frame.pack(fill=tk.X, padx=10, pady=10)

entry_id = tk.StringVar()
tk.Label(form_frame, text="Color:", bg=BG_COLOR, fg=LABEL_COLOR).grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
entry_color = tk.Entry(form_frame, bg=ENTRY_BG_COLOR)
entry_color.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

tk.Label(form_frame, text="Cost:", bg=BG_COLOR, fg=LABEL_COLOR).grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
entry_cost = tk.Entry(form_frame, bg=ENTRY_BG_COLOR)
entry_cost.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

tk.Label(form_frame, text="Description:", bg=BG_COLOR, fg=LABEL_COLOR).grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
entry_description = tk.Text(form_frame, height=4, width=30, bg=ENTRY_BG_COLOR)
entry_description.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

tk.Label(form_frame, text="Modelo:", bg=BG_COLOR, fg=LABEL_COLOR).grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
entry_modelo = tk.Entry(form_frame, bg=ENTRY_BG_COLOR)
entry_modelo.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

tk.Label(form_frame, text="Name:", bg=BG_COLOR, fg=LABEL_COLOR).grid(row=1, column=2, padx=5, pady=5, sticky=tk.E)
entry_name = tk.Entry(form_frame, bg=ENTRY_BG_COLOR)
entry_name.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)

tk.Label(form_frame, text="Collection:", bg=BG_COLOR, fg=LABEL_COLOR).grid(row=2, column=2, padx=5, pady=5, sticky=tk.E)
entry_nom_collection = tk.Entry(form_frame, bg=ENTRY_BG_COLOR)
entry_nom_collection.grid(row=2, column=3, padx=5, pady=5, sticky=tk.W)

tk.Label(form_frame, text="Type:", bg=BG_COLOR, fg=LABEL_COLOR).grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
entry_type = tk.Entry(form_frame, bg=ENTRY_BG_COLOR)
entry_type.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

# Botón para insertar datos
def on_enter(e):
    e.widget['background'] = BUTTON_HOVER_COLOR

def on_leave(e):
    e.widget['background'] = BUTTON_COLOR

button_frame = tk.Frame(root, bg=BG_COLOR)
button_frame.pack(fill=tk.X, padx=10, pady=10)

insert_button = tk.Button(button_frame, text="Agregar Producto", bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, command=insert_data)
insert_button.grid(row=0, column=0, padx=10, pady=5)
insert_button.bind("<Enter>", on_enter)
insert_button.bind("<Leave>", on_leave)

delete_button = tk.Button(button_frame, text="Eliminar Producto", bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, command=delete_data)
delete_button.grid(row=0, column=1, padx=10, pady=5)
delete_button.bind("<Enter>", on_enter)
delete_button.bind("<Leave>", on_leave)

edit_button = tk.Button(button_frame, text="Editar Producto", bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, command=edit_data)
edit_button.grid(row=0, column=2, padx=10, pady=5)
edit_button.bind("<Enter>", on_enter)
edit_button.bind("<Leave>", on_leave)

update_button = tk.Button(button_frame, text="Actualizar Producto", bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, command=update_data)
update_button.grid(row=0, column=3, padx=10, pady=5)
update_button.bind("<Enter>", on_enter)
update_button.bind("<Leave>", on_leave)
update_button.grid_forget()





# Crear frame para la gestión de archivos SFTP
sftp_frame = tk.Frame(root, bg=BG_COLOR)
sftp_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

sftp_listbox = tk.Listbox(sftp_frame, selectmode=tk.SINGLE, bg=ENTRY_BG_COLOR)
sftp_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

sftp_button_frame = tk.Frame(sftp_frame, bg=BG_COLOR)
sftp_button_frame.pack(fill=tk.X, padx=10, pady=10)

upload_folder_button = tk.Button(sftp_button_frame, text="Subir Carpeta", bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, command=start_upload_folder)
upload_folder_button.grid(row=0, column=0, padx=10, pady=5)
upload_folder_button.bind("<Enter>", on_enter)
upload_folder_button.bind("<Leave>", on_leave)

upload_file_button = tk.Button(sftp_button_frame, text="Subir Archivo", bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, command=start_upload_file)
upload_file_button.grid(row=0, column=1, padx=10, pady=5)
upload_file_button.bind("<Enter>", on_enter)
upload_file_button.bind("<Leave>", on_leave)

delete_file_button = tk.Button(sftp_button_frame, text="Eliminar Archivo", bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, command=delete_file)
delete_file_button.grid(row=0, column=2, padx=10, pady=5)
delete_file_button.bind("<Enter>", on_enter)
delete_file_button.bind("<Leave>", on_leave)

delete_folder_button = tk.Button(sftp_button_frame, text="Eliminar Carpeta", bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, command=delete_folder)
delete_folder_button.grid(row=0, column=3, padx=10, pady=5)
delete_folder_button.bind("<Enter>", on_enter)
delete_folder_button.bind("<Leave>", on_leave)

# Cargar datos iniciales
load_data()
load_sftp_files()

# Ejecutar la aplicación
root.mainloop()
