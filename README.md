#LPMC Site

###Getting Started  
- Clone the project down with submodules  
````
git clone --recursive git@github.com:LearnProgramming/lpmc-site.git
````
- It would be best to install dependencies just for the project by using a virtual environment.  
````
pyvenv-3.3 venv
````  
````
source venv/bin/activate
````
- Install dependencies from the requirements file  
````
pip3 install -r requirements.txt
````
- Finally copy the config.yaml.example to config.yaml and fill in the info for the server
- You can now run the server  
````
./server.py
````  
Visit http://localhost:8888 or the specified port in config.yaml