# ft_trainsendence

// for the beta_branch
git checkout beta_register_login

// setup only once
// start
python3 -m pip install --user virtualenv
python3 -m virtualenv venv
source venv/bin/activate
pip install django
// end


cd myproject
cd bigproject
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
