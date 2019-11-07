sudo apt update
sudo apt install git
sudo apt install python3-pip -y
sudo pip3 install fastapi
sudo pip3 install uvicorn
sudo pip3 install email-validator
git clone https://github.com/IagoMendes/CloudComputing.git
cd CloudComputing/APS1
uvicorn main:app --reload --host 0.0.0.0