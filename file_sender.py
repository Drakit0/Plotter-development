from flask import Flask, render_template, request, send_file
import os
import time

app = Flask(__name__)

@app.route("/")
def root():
    return render_template("index.html")

@app.route("/upload/", methods=["POST"])
def upload_gcode():
    file = request.files["file"]
    
    if file.filename == "":
        return {"message": "No file uploaded"}
    
    if not file.filename.endswith(".gcode"):
        return {"message": "Invalid file type. Please upload a G-code file."}
        
    save_dir = "shared_documents"
    
    os.makedirs(save_dir, exist_ok=True)
    
    lines = 0

    filename = file.filename.replace(".gcode","")
    
    files = os.listdir(save_dir)
    
    clean_files = {}
    
    for old_file in files:
        
        old_file = old_file.replace(".txt","")
        file_ver = int(old_file.split("_")[-1])
        old_file = old_file.replace("_"+str(file_ver),"")
        
        if old_file in clean_files.keys():
            clean_files[old_file] += 1
            
        else:
            clean_files[old_file] = 1
    
    if filename in clean_files.keys():
        
        filename = filename + "_" + str(clean_files[filename]+1) + ".txt"
        
    else:
        filename = filename + "_1.txt" 

    with open(save_dir + "/" + filename, "wb") as new_file:
        for line in file:
            if line.strip().startswith(b"G"):
                new_file.write(line)
                
                lines += 1
        
    return render_template("redirect.html", api_response= {"filename": filename.replace(save_dir+"/",""), "file_size": lines, "message": "File saved successfully"})


if __name__ == "__main__":
    app.run(host = "0.0.0.0",debug=True)
