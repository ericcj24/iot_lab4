# iot_lab4
1. after setting up Amazon aws account, user in iot core. create account access token using the website (you can created with root user account)
2. open aws cloudshell on the website, set up remote access token by entering, enter access id and key when prompted
```
aws configure
```
3. download this repo, with following structure
```
lab4
    certs
    keys
    vehicles
    lab4_emulator_client.py
    process_emission.py
    createThing-Cert.py
    
```
4. move createThing-Cert.py to your user home directory
```
cd lab4
move createThing-Cert.py ../
```
5. install couple dependency
```
pip install pandas
pip install AWSIoTPythonSDK
```
6. run creatThing-Cert.py, this will create 5 'things', and keys, certs associated with each of the thing.
```
python creatThing-Cert.py
```
7. move all 5 certs to the certs folder, move all 5 keys to the keys folder. feel free to delete existing files in the directory (those were generated when i was running it)
8. now run emulator, when promted, enter 's' it will publish, when done, enter 'd'
```
python lab4_emulator_client.py
```
