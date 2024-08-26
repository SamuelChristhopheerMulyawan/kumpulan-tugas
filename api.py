from fastapi import FastAPI,HTTPException
import json
import random
app = FastAPI()
def load_data():
    try:
        with open('data.json', 'r') as datafile:
            return json.load(datafile)
    except FileNotFoundError:
        return []  # Jika file tidak ada, kembalikan list kosong

@app.post('/add')
async def addpass(link: str, username: str, passwd: str, genpass: bool):
    if genpass:
        lower = "abcdefghijklmnopqrstuvwxyz"
        upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        number = "0123456789"
        symbol = ";:,.<>?/|+=-_`~!@#$%^&*"
        passwd = ""
        for _ in range(20):
            choice = random.randint(0, 3)
            if choice == 0:
                passwd += random.choice(lower)
            elif choice == 1:
                passwd += random.choice(upper)
            elif choice == 2:
                passwd += random.choice(number)
            elif choice == 3:
                passwd += random.choice(symbol)
        newdata = {"link": link, "username": username, "passwd": passwd}
    else:
        newdata = {"link": link, "username": username, "passwd": passwd}
    
    # Muat data yang ada
    loaddata = load_data()
    loaddata.append(newdata)

    # Tulis kembali data ke file
    with open('data.json', 'w') as datafile:
        json.dump(loaddata, datafile, indent=4)

    return {"message": "Data added successfully"}
@app.get('/read')
async def read():
    result = []
    data = load_data()
    for readdata in data:
        # Pastikan readdata adalah dictionary
        if isinstance(readdata, dict):
            link = readdata.get('link', 'N/A')
            username = readdata.get('username', 'N/A')
            password = readdata.get('passwd', 'N/A')
            result.append(f"===================================\nLink: {link}\nUsername: {username}\nPassword: {password}\n==========================================")
    return "\n".join(result)

@app.put('/edit')
async def edit(linktarget:str, link:str,username:str,passwd:str, changepass:bool):
    data = load_data()
    for loaded_data in data:
        if linktarget == loaded_data['link']:
            if changepass == True:
                needup = {"link": f"{link}", "username": f"{username}", "passwd": f"{passwd}"}
            else:
                passwd= loaded_data['passwd']
                needup = {"link": f"{link}", "username": f"{username}", "passwd": f"{passwd}"}
            loaded_data.update(needup)
            with open('data.json', 'w') as datafile:
                json.dump(data, datafile, indent=4)

@app.delete('/delete')
async def delete(linktarget:str):
    loadeddata = load_data()
    deleted_data = [data for data in loadeddata if data['link'] != linktarget]
    if len(deleted_data) == len(loadeddata):
         raise HTTPException(status_code=404, detail="Data not found")
    with open('data.json', 'w') as datafile:
        json.dump(deleted_data, datafile, indent=4)

