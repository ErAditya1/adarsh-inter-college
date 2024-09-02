echo "BUILD START"
Python 3.12.1 -m pip install -r requirements.txt
python 3.12.1 manage.py collectstatic --noinput --clear
echo "Build END"