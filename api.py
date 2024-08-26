from fastapi import FastAPI, Depends, HTTPException, Request, Response
from pydantic import BaseModel
import json
import random

from itsdangerous import URLSafeSerializer
key = "W1th@dm1nP0w3r1c@nd0@nyth1n9"
serializer = URLSafeSerializer(key)
def get_session(req : Request):
    get_session = req.cookies.get("session")
    if get_session:
        try:
            return serializer.loads(get_session)
        except: 
            raise HTTPException(status_code=403, detail="Session NOT found may be you need login again")
    return {}
app = FastAPI()
def load_data():
    try:
        with open('data.json', 'r') as datafile:
            return json.load(datafile)
    except FileNotFoundError:
        return []  # Jika file tidak ada, kembalikan list kosong
@app.post('/login')
async def login(username: str, password: str , response : Response):
    data = load_data()
    user = next((user for user in data if user['uname'] == username and user['upasswd'] == password  ), None)
    if user:
        session = {"uname": user['uname']}
        set_session = serializer.dumps(session)
        response.set_cookie(key="session", value=set_session)
        return "Login Success now you can access your data"
    else: 
        raise HTTPException(status_code=401, detail="Invalid Username or Password")

@app.post('/signup')
async def signup(username: str, password: str, validation_password : str, session_data: dict = Depends(get_session)):
    session_retrieve = session_data.get("uname")
    if session_retrieve:
        return {"Message": "Please logout"}
    else:
        data = load_data()
        if password == validation_password:
            newdata = {"uname": username, "upasswd": password, "data": []}
            data.append(newdata)
            with open('data.json', 'w') as datafile:
                json.dump(data, datafile, indent=4)
            return {"message": "Successfully Create Account"}
        else:
            return {"message": "Password not match"}

@app.post('/add')
async def addpass(link: str, username: str, passwd: str, genpass: bool, session_data: dict = Depends(get_session)):
    session_retrieve = session_data.get("uname")
    if session_retrieve:
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
        user = next((user for user in loaddata if user['uname'] == session_retrieve), None)
        if user:
            user["data"].append(newdata)
            with open('data.json', 'w') as datafile:
                json.dump(loaddata, datafile, indent=4)

            return {"message": "Data added successfully"}
    else:
        raise HTTPException(status_code=401, detail= "Unauthorized Please Login or signup")
@app.get('/read')
async def read(session_data : dict = Depends(get_session)):
    session_retrieve = session_data.get("uname")
    if session_retrieve:
        result = []
        data = load_data()
        user = next((user for user in data if user['uname'] == session_retrieve), None)
        if user:
            for readdata in user['data']:
        # Pastikan readdata adalah dictionary
                if isinstance(readdata, dict):
                    link = readdata.get('link', 'N/A')
                    username = readdata.get('username', 'N/A')
                    password = readdata.get('passwd', 'N/A')
                    result.append(f"""
===================================
Link: {link}
Username: {username}
Password: {password}
===================================
""")
        return "\n".join(result)
    else:
        raise HTTPException(status_code=401,detail= "Unauthorized Please Login or signup")

@app.put('/edit')
async def edit(linktarget:str, link:str,username:str,passwd:str, changepass:bool, session_data: dict = Depends(get_session)):
    session_retrieve = session_data.get("uname")
    if session_retrieve:
        data = load_data()
        user = next((user for user in data if user['uname'] == session_retrieve), None)
        if user:
            for loaded_data in user['data']:
                if linktarget == loaded_data['link']:
                    if changepass == True:
                        needup = {"link": f"{link}", "username": f"{username}", "passwd": f"{passwd}"}
                    else:
                        passwd= loaded_data['passwd']
                        needup = {"link": f"{link}", "username": f"{username}", "passwd": f"{passwd}"}
                    loaded_data.update(needup)
                    with open('data.json', 'w') as datafile:
                        json.dump(data, datafile, indent=4)
                    return {"message": "Password Update Successs"}
                else:
                    raise HTTPException(status_code=404, detail="Data not Found")
    else:
        raise HTTPException(status_code=401,detail= "Unauthorized Please Login or signup")

@app.delete('/delete')
async def delete(linktarget: str, session_data: dict = Depends(get_session)):
    session_retrieve = session_data.get("uname")
    if session_retrieve:
        loadeddata = load_data()
        user = next((user for user in loadeddata if user['uname'] == session_retrieve), None)
        if user:
            # Filter data yang ingin dihapus berdasarkan 'link'
            updated_data = [data for data in user['data'] if data['link'] != linktarget]
            if len(updated_data) == len(user['data']):
                raise HTTPException(status_code=404, detail="Data not found")
            # Update data pengguna dengan data yang telah diperbarui
            user['data'] = updated_data
            with open('data.json', 'w') as datafile:
                json.dump(loadeddata, datafile, indent=4)
            return {"message": "Data deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    else:
        raise HTTPException(status_code=401, detail="Unauthorized. Please login or signup")
    
@app.post('/logout')
async def logout(response: Response):
    response.delete_cookie(key="session")
    return {"message": "Bye-bye"}

