Installation instruction

1. Install prerequisites.
<code>sudo apt-get install python3 python3-pip virtualenvwrapper</code>
2. Make virtualenv 
<code>mkvirtualenv -p /usr/bin/python3 <venv-name></code>
3. Set into the virtual environment.
<code>workon <venv-name></code>
4. Clone gitlab repo
<code>git clone git@gitlab-ssh.sumatosoft.com:spend-matters/spend-matters.git</code>
5. Install other requirements using pip package manager
 <code>pip install -r requirements.txt</code>
6. Create <code>.env</code> file and add information accordingly <code>.env.dist</code> file
Note: you need to have exist mysql database at your machine
7. From root directory of cloning project (where file manage.py is stored) run command
<code>python manage.py runserver</code>

If no errors status - project are running


Link to Swagger

<code>http://localhost/api/doc/swagger/</code>