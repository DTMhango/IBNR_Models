import sys
from streamlit.web import cli as stcli


if __name__ == '__main__':
    sys.argv = ["streamlit", "run", "C:/Users/mhang/Documents/IBNR APP/Home.py"]
    sys.exit(stcli.main())
