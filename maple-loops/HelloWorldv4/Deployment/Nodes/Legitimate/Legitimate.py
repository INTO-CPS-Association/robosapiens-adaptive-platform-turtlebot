import time
import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, parent_dir)

from Realization.MAPLEK import Legitimate
def main(args=None):

    node = Legitimate(config='config.yaml')
    node.start()

if __name__ == '__main__':
    main()
    try:
       while True:
           time.sleep(1)
    except:
       exit()