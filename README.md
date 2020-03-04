Installation instruction

1. Install prerequisites.
sudo apt-get install python3 python3-pip virtualenvwrapper
2. Make virtualenv 
mkvirtualenv -p /usr/bin/python3 <venv-name>
3. Set into the virtual environment.
workon <venv-name>
4. Clone gitlab repo
git clone git@gitlab-ssh.sumatosoft.com:spend-matters/spend-matters.git
5. Install other requirements using pip package manager
 pip install -r requirements.txt
6. Create .env file and add information accordingly .env.dist file
Note: you need to have exist mysql database at your machine
7. From root dirrectory of cloning project (where file manage.py is stored) run command
python manage.py runserver

If no errors status - project are runing